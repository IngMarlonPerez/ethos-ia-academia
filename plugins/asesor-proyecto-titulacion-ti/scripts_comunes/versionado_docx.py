# -*- coding: utf-8 -*-
"""
versionado_docx.py — protege el Word del estudiante mientras se edita.

Adaptado del plugin «proyectos-academicos» (V. M. Lluilema Pisco) e integrado al Asesor.
Tres ideas:
  1. HUELLA de la zona protegida: portada y preliminares, encabezados y pies (XML e imágenes: logo, fondo),
     secciones y estilos. Se toma antes y se compara después de cada lote de cambios.
  2. SOLO INSERCIONES: comprueba que ningún párrafo que ya existía fue alterado o eliminado.
  3. RESTAURAR encabezados y pies de la plantilla oficial si un guardado los perdió.

Solo usa python-docx y lxml. Las funciones devuelven datos; los scripts CLI imprimen.
"""
import hashlib
import json
import os
import re
import zipfile
from collections import Counter

import docx
from docx.oxml.ns import qn
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
RE_INICIO = re.compile(r'^(RESUMEN|ABSTRACT|INTRODUCCI|CAP[IÍ]TULO|1\.?\s)', re.I)


def nivel_titulo(p):
    """0 si no es título; 1..9 según estilo Heading/Título o outlineLvl."""
    try:
        nombre = (p.style.name or '').lower()
    except Exception:
        nombre = ''
    if nombre.startswith(('toc', 'tdc', 'table of', 'tabla de ilustraciones')):
        return 0
    m = re.match(r'(?:heading|t[ií]tulo)\s*(\d)', nombre)
    if m:
        return int(m.group(1))
    ol = p._p.find('./' + qn('w:pPr') + '/' + qn('w:outlineLvl'))
    if ol is not None and ol.get(qn('w:val')) not in (None, '9'):
        return int(ol.get(qn('w:val'))) + 1
    return 0


# ------------------------------------------------------------------ verificación de inserciones
def firmas_parrafos(path):
    d = docx.Document(path)
    return Counter(etree.tostring(p._p) for p in d.paragraphs), d


def solo_inserciones(antes, despues):
    """Comprueba que ningún párrafo existente cambió: todo párrafo de `antes` sigue idéntico en `despues`.
    Devuelve lista de textos de párrafos alterados o eliminados (vacía = OK)."""
    a, da = firmas_parrafos(antes)
    b, _ = firmas_parrafos(despues)
    faltan = a - b
    textos = []
    for xml, n in faltan.items():
        el = etree.fromstring(xml)
        textos.append(''.join(t.text or '' for t in el.iter(qn('w:t')))[:100] or '(párrafo vacío o imagen)')
    return textos


# ------------------------------------------------------------------ huella de la zona protegida
def _sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode('utf8')).hexdigest()[:16]


def _norm_xml(b):
    """Forma canónica (C14N) sin atributos volátiles: ignora la declaración XML, el orden de atributos, los rsid y
    los identificadores de relación que Word o python-docx reescriben al guardar sin cambiar el contenido."""
    try:
        el = etree.fromstring(b if isinstance(b, bytes) else b.encode('utf8'))
        for e in el.iter():
            for at in list(e.attrib):
                local = at.split('}')[-1]
                if local.startswith('rsid') or local in ('id', 'embed', 'link', 'paraId', 'textId', 'anchorId', 'editId') \
                        and ('relationships' in at or 'w14' in at or 'wp14' in at):
                    del e.attrib[at]
        s = etree.tostring(el, method='c14n').decode('utf8')
    except Exception:
        s = b.decode('utf8') if isinstance(b, bytes) else b
    s = re.sub(r'\s(?:r:id|r:embed|r:link|w:rsid\w*|w14:paraId|w14:textId|wp14:\w+)="[^"]*"', '', s)
    return s


def _rels(z, parte):
    carpeta, nombre = os.path.split(parte)
    rp = f'{carpeta}/_rels/{nombre}.rels'
    if rp not in z.namelist():
        return {}
    x = z.read(rp).decode('utf8')
    out = {}
    for m in re.finditer(r'<Relationship\b([^>]*)/?>', x):
        at = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        out[at.get('Id')] = (at.get('Type', '').rsplit('/', 1)[-1], at.get('Target'), at.get('TargetMode'))
    return out


def secciones_zip(z):
    """Lista de secciones con referencias de encabezado/pie (resolviendo el destino) y propiedades."""
    doc = z.read('word/document.xml').decode('utf8')
    rels = _rels(z, 'word/document.xml')
    out = []
    for m in re.finditer(r'<w:sectPr\b.*?</w:sectPr>', doc, re.S):
        s = m.group(0)
        refs = {}
        for r in re.finditer(r'<w:(header|footer)Reference\b[^>]*?w:type="(\w+)"[^>]*?r:id="(\w+)"', s):
            refs[(r.group(1), r.group(2))] = 'word/' + rels.get(r.group(3), ('', ''))[1]
        for r in re.finditer(r'<w:(header|footer)Reference\b[^>]*?r:id="(\w+)"[^>]*?w:type="(\w+)"', s):
            refs[(r.group(1), r.group(3))] = 'word/' + rels.get(r.group(2), ('', ''))[1]
        pg = re.search(r'<w:pgSz[^>]*/>', s); mar = re.search(r'<w:pgMar[^>]*/>', s)
        out.append(dict(xml=s, refs=refs, titlePg='<w:titlePg' in s and '<w:titlePg w:val="0"' not in s,
                        pgSz=pg.group(0) if pg else '', pgMar=mar.group(0) if mar else '',
                        pgNum=(re.search(r'<w:pgNumType[^>]*/>', s) or [''])[0] if re.search(r'<w:pgNumType[^>]*/>', s) else ''))
    return out


def _efectivas(secs):
    """Referencias efectivas por sección (Word hereda de la sección anterior lo que falta)."""
    ef, prev = [], {}
    for s in secs:
        d = dict(prev); d.update(s['refs']); ef.append(d); prev = d
    return ef


def huella(path, inicio=RE_INICIO):
    """Huella de lo que nunca debe cambiar al editar: encabezados, pies (XML e imágenes), secciones,
    preliminares (portada, declaraciones, índices) y estilos."""
    z = zipfile.ZipFile(path)
    secs = secciones_zip(z)
    ef = _efectivas(secs)
    partes = {}
    for k, s in enumerate(ef):
        for (tipo, clase), parte in s.items():
            if parte in z.namelist():
                media = {t: _sha(z.read('word/' + tgt)) for _, (t, tgt, mode) in _rels(z, parte).items()
                         if mode != 'External' and ('word/' + tgt) in z.namelist()}
                partes[f'sec{k + 1}:{tipo}:{clase}'] = dict(parte=parte, xml=_sha(_norm_xml(z.read(parte))),
                                                            imagenes=sorted(media.values()))
    d = docx.Document(path)
    body = list(d.element.body)
    P = d.paragraphs
    ini = next((i for i, p in enumerate(P) if nivel_titulo(p) == 1 and inicio.match(p.text.strip())), None)
    if ini is None:   # sin Resumen/Introducción reconocible: la portada llega hasta el primer título de nivel 1
        ini = next((i for i, p in enumerate(P) if nivel_titulo(p) == 1), None)
    fin_pre = body.index(P[ini]._p) if ini is not None else 0
    pre = [_sha(_norm_xml(etree.tostring(e))) for e in body[:fin_pre]]
    img_pre = []
    rels = _rels(z, 'word/document.xml')
    for e in body[:fin_pre]:
        for b in e.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
            rid = b.get(f'{{{R}}}embed')
            if rid in rels and ('word/' + rels[rid][1]) in z.namelist():
                img_pre.append(_sha(z.read('word/' + rels[rid][1])))
    return dict(archivo=os.path.basename(path), secciones=[dict(pgSz=s['pgSz'], pgMar=s['pgMar'], titlePg=s['titlePg'],
                                                                 pgNum=s['pgNum'], refs=sorted(f'{a}:{b}' for a, b in s['refs']))
                                                            for s in secs],
                partes=partes, preliminares=dict(elementos=len(pre), hashes=pre, imagenes=img_pre,
                                                 texto_portada=[p.text.strip() for p in P[:40] if p.text.strip()][:14]),
                estilos=_sha(_norm_xml(z.read('word/styles.xml'))),
                numeracion=_sha(_norm_xml(z.read('word/numbering.xml'))) if 'word/numbering.xml' in z.namelist() else None)


def comparar_huellas(a, b, estricto_preliminares=True):
    """Devuelve lista de (nivel, detalle). a = antes/referencia, b = después."""
    dif = []
    if len(a['secciones']) != len(b['secciones']):
        dif.append(('FALLA', f"Número de secciones cambió: {len(a['secciones'])} -> {len(b['secciones'])}"))
    for k, (x, y) in enumerate(zip(a['secciones'], b['secciones'])):
        for campo in ('pgSz', 'pgMar', 'titlePg', 'pgNum', 'refs'):
            if _norm_xml(str(x[campo])) != _norm_xml(str(y[campo])):
                dif.append(('FALLA', f'Sección {k + 1}: cambió {campo} ({x[campo]} -> {y[campo]})'))
    for k, v in a['partes'].items():
        w = b['partes'].get(k)
        if not w:
            dif.append(('FALLA', f'Falta {k} (encabezado/pie que existía).'))
        else:
            if v['xml'] != w['xml']:
                dif.append(('FALLA', f'Cambió el contenido de {k}.'))
            if v['imagenes'] != w['imagenes']:
                dif.append(('FALLA', f'Cambiaron las imágenes de {k} (logo/fondo).'))
    for k in b['partes']:
        if k not in a['partes']:
            dif.append(('INFO', f'Nuevo {k}.'))
    pa, pb = a['preliminares'], b['preliminares']
    if pa['imagenes'] != pb['imagenes']:
        dif.append(('FALLA', 'Cambiaron las imágenes de la portada o de los preliminares.'))
    if pa['hashes'] != pb['hashes']:
        cambiados = sum(1 for x, y in zip(pa['hashes'], pb['hashes']) if x != y) + abs(len(pa['hashes']) - len(pb['hashes']))
        dif.append(('FALLA' if estricto_preliminares else 'INFO',
                    f'Cambiaron {cambiados} elementos de portada/preliminares/índice.'))
    if a['estilos'] != b['estilos']:
        dif.append(('INFO', 'styles.xml cambió (revisar que no se alteró el formato de la plantilla).'))
    if a.get('numeracion') != b.get('numeracion'):
        dif.append(('INFO', 'numbering.xml cambió (revisar numeración de títulos y listas).'))
    return dif


def comparar_con_plantilla(doc_path, plantilla_path):
    """¿El documento conserva los encabezados, pies e imágenes de portada de la plantilla original?"""
    zd, zt = zipfile.ZipFile(doc_path), zipfile.ZipFile(plantilla_path)
    efd, eft = _efectivas(secciones_zip(zd)), _efectivas(secciones_zip(zt))
    dif = []

    def firma(z, parte):
        if parte not in z.namelist():
            return None
        imgs = sorted(_sha(z.read('word/' + tgt)) for _, (t, tgt, mode) in _rels(z, parte).items()
                      if mode != 'External' and ('word/' + tgt) in z.namelist())
        return imgs

    necesarios = {}
    if eft:
        necesarios.update({k: v for k, v in eft[0].items()})
        for k, v in eft[-1].items():
            if k[1] != 'first':
                necesarios[k] = v
    ultimo_d = efd[-1] if efd else {}
    primero_d = efd[0] if efd else {}
    for (tipo, clase), parte_t in necesarios.items():
        dispon = primero_d if clase == 'first' else ultimo_d
        parte_d = dispon.get((tipo, clase))
        imgs_t = firma(zt, parte_t)
        if not parte_d:
            dif.append(('FALLA', f'Falta el {"encabezado" if tipo == "header" else "pie"} "{clase}" de la plantilla '
                                 f'({"fondo/portada" if clase == "first" else "páginas interiores"}).'))
        else:
            imgs_d = firma(zd, parte_d)
            if imgs_t and imgs_d is not None and not set(imgs_t) <= set(imgs_d):
                dif.append(('ADVERTENCIA', f'El {tipo} "{clase}" no tiene las mismas imágenes que la plantilla.'))
    return dif


# ------------------------------------------------------------------ restauración de encabezados y pies
_CT = {'png': 'image/png', 'jpeg': 'image/jpeg', 'jpg': 'image/jpeg', 'gif': 'image/gif', 'emf': 'image/x-emf',
       'wmf': 'image/x-wmf', 'svg': 'image/svg+xml', 'bmp': 'image/bmp', 'tif': 'image/tiff', 'tiff': 'image/tiff'}
_CT_PARTE = {'header': 'application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml',
             'footer': 'application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml'}


def restaurar_encabezados(doc_path, plantilla_path, salida, reemplazar=False):
    """Copia a `doc_path` los encabezados/pies (con sus imágenes: logos, franjas, fondo de portada) que le faltan
    respecto de la plantilla. Mapea: sección 1 del documento <- sección 1 de la plantilla (incluye la primera
    página/portada y titlePg); última sección <- pies/encabezados por defecto de la última sección de la plantilla.
    No toca el cuerpo. Devuelve la lista de acciones realizadas."""
    zd, zt = zipfile.ZipFile(doc_path), zipfile.ZipFile(plantilla_path)
    files = {n: zd.read(n) for n in zd.namelist()}
    secs_d, secs_t = secciones_zip(zd), secciones_zip(zt)
    eft, efd = _efectivas(secs_t), _efectivas(secs_d)
    acciones = []
    docxml = files['word/document.xml'].decode('utf8')
    drels = files['word/_rels/document.xml.rels'].decode('utf8')
    ct = files['[Content_Types].xml'].decode('utf8')
    ids = [int(x) for x in re.findall(r'Id="rId(\d+)"', drels)]
    siguiente = [max(ids) + 1 if ids else 1]
    copiadas = {}

    def copiar_parte(parte_t, tipo):
        if parte_t in copiadas:
            return copiadas[parte_t]
        k = 1
        while f'word/{tipo}_plantilla{k}.xml' in files:
            k += 1
        nueva = f'word/{tipo}_plantilla{k}.xml'
        files[nueva] = zt.read(parte_t)
        rels_t = _rels(zt, parte_t)
        if rels_t:
            filas = []
            for rid, (t, tgt, mode) in rels_t.items():
                if mode == 'External':
                    filas.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                                 f'relationships/{t}" Target="{tgt}" TargetMode="External"/>')
                    continue
                origen = 'word/' + tgt
                ext = tgt.rsplit('.', 1)[-1].lower()
                j = 1
                while f'word/media/plantilla_{tipo}{k}_{j}.{ext}' in files:
                    j += 1
                dest = f'media/plantilla_{tipo}{k}_{j}.{ext}'
                files['word/' + dest] = zt.read(origen)
                if f'Extension="{ext}"' not in nonlocal_ct[0] and ext.lower() not in nonlocal_ct[0].lower() and ext in _CT:
                    nonlocal_ct[0] = nonlocal_ct[0].replace('<Default ', f'<Default Extension="{ext}" ContentType="{_CT[ext]}"/><Default ', 1)
                filas.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                             f'relationships/{t}" Target="{dest}"/>')
            files[f'word/_rels/{os.path.basename(nueva)}.rels'] = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.'
                'openxmlformats.org/package/2006/relationships">' + ''.join(filas) + '</Relationships>').encode('utf8')
        nonlocal_ct[0] = nonlocal_ct[0].replace('</Types>', f'<Override PartName="/{nueva}" ContentType="{_CT_PARTE[tipo]}"/></Types>')
        rid = f'rId{siguiente[0]}'; siguiente[0] += 1
        nonlocal_rels[0] = nonlocal_rels[0].replace('</Relationships>', f'<Relationship Id="{rid}" Type="http://schemas.'
                                                    f'openxmlformats.org/officeDocument/2006/relationships/{tipo}" '
                                                    f'Target="{os.path.basename(nueva)}"/></Relationships>')
        copiadas[parte_t] = rid
        return rid

    nonlocal_ct, nonlocal_rels = [ct], [drels]
    n = len(secs_d)
    nuevos_sect = []
    for k, sd in enumerate(secs_d):
        deseado = {}
        if k == 0:
            deseado.update({c: v for c, v in eft[0].items()})
            if n == 1:
                deseado.update({c: v for c, v in eft[-1].items() if c[1] != 'first'})
                deseado.update({c: v for c, v in eft[0].items() if c[0] == 'header'})
                if ('header', 'first') in eft[0]:
                    deseado[('header', 'first')] = eft[0][('header', 'first')]
        elif k == n - 1:
            deseado.update({c: v for c, v in eft[-1].items() if c[1] != 'first'})
        s_xml = sd['xml']
        agregar = []
        for (tipo, clase), parte_t in sorted(deseado.items()):
            presente = (tipo, clase) in sd['refs'] or ((tipo, clase) in efd[k] and clase != 'first')
            if presente and not reemplazar:
                continue
            if reemplazar and (tipo, clase) in sd['refs']:
                s_xml = re.sub(rf'<w:{tipo}Reference\b(?=[^>]*w:type="{clase}")[^>]*/>', '', s_xml)
            rid = copiar_parte(parte_t, tipo)
            agregar.append(f'<w:{tipo}Reference w:type="{clase}" r:id="{rid}"/>')
            acciones.append(f'Sección {k + 1}: {"encabezado" if tipo == "header" else "pie"} "{clase}" copiado de la plantilla')
        if agregar:
            s_xml = re.sub(r'(<w:sectPr\b[^>]*>)', lambda m: m.group(1) + ''.join(agregar), s_xml, count=1)
        if any(c[1] == 'first' for c in deseado) and '<w:titlePg' not in s_xml and agregar:
            if re.search(r'<w:(textDirection|bidi|rtlGutter|docGrid|printerSettings)\b', s_xml):
                s_xml = re.sub(r'(<w:(?:textDirection|bidi|rtlGutter|docGrid|printerSettings)\b)', r'<w:titlePg/>\1', s_xml, count=1)
            else:
                s_xml = s_xml.replace('</w:sectPr>', '<w:titlePg/></w:sectPr>')
            acciones.append(f'Sección {k + 1}: activada "primera página diferente" (portada)')
        nuevos_sect.append((sd['xml'], s_xml))
    for viejo, nuevo in nuevos_sect:
        if viejo != nuevo:
            docxml = docxml.replace(viejo, nuevo, 1)
    files['word/document.xml'] = docxml.encode('utf8')
    files['[Content_Types].xml'] = nonlocal_ct[0].encode('utf8')
    files['word/_rels/document.xml.rels'] = nonlocal_rels[0].encode('utf8')
    orden = zd.namelist() + [x for x in files if x not in zd.namelist()]
    with zipfile.ZipFile(salida, 'w', zipfile.ZIP_DEFLATED) as zo:
        for nme in orden:
            zo.writestr(zd.getinfo(nme) if nme in zd.namelist() else nme, files[nme])
    return acciones




# ------------------------------------------------------------------ copias versionadas
def base_sin_version(nombre):
    """'Avance_2_v03.docx' -> 'Avance_2'; quita _vNN y _RESPALDO…"""
    return re.sub(r'(_v\d+|_RESPALDO.*)$', '', os.path.splitext(os.path.basename(nombre))[0])


def siguiente_version(carpeta, base, desde=2):
    """Primer número de versión libre para BASE_vNN.docx en `carpeta`. Empieza en `desde`: 2 para copias de trabajo
    (la 1 es el original) y 1 para el archivo automático de salidas anteriores del generador."""
    usados = [int(m.group(1)) for f in os.listdir(carpeta)
              if (m := re.fullmatch(re.escape(base) + r'_v(\d+)\.docx', f))]
    return max(usados, default=desde - 1) + 1


def crear_copia_versionada(original, version=None, destino=None, nombre=None, desde=2):
    """Copia los BYTES del original a BASE_vNN.docx (conserva portada, fondo, encabezado, pie y estilos) y guarda su
    huella en BASE_vNN.huella.json. El original nunca se modifica y nunca se sobrescribe una versión existente.
    Devuelve (ruta_docx, ruta_huella)."""
    import shutil
    base = nombre or base_sin_version(original)
    dest = destino or os.path.dirname(os.path.abspath(original))
    os.makedirs(dest, exist_ok=True)
    version = version or siguiente_version(dest, base, desde)
    salida = os.path.join(dest, f'{base}_v{version:02d}.docx')
    if os.path.exists(salida):
        raise FileExistsError(f'Ya existe {salida}: usar otra versión (nunca se sobrescribe).')
    shutil.copy2(original, salida)
    ruta_h = salida[:-5] + '.huella.json'
    with open(ruta_h, 'w', encoding='utf8') as f:
        json.dump(huella(salida), f, ensure_ascii=False, indent=1)
    return salida, ruta_h


# ------------------------------------------------------------------ aserciones (correcciones que no deben revertirse)
def texto_documento(path):
    """Todo el texto del documento: párrafos y celdas de tablas."""
    d = docx.Document(path)
    partes = [p.text for p in d.paragraphs]
    for t in d.tables:
        for fila in t.rows:
            for c in fila.cells:
                partes.append(c.text)
    return '\n'.join(partes)


def verificar_aserciones(path, aserciones):
    """`aserciones`: lista de {"descripcion", "contiene", "no_contiene"} (ambos opcionales).
    Devuelve la lista de las que NO se cumplen: señal de que un guardado desde un Word viejo revirtió una corrección."""
    texto = texto_documento(path)
    falla = []
    for a in aserciones:
        if a.get('contiene') and a['contiene'] not in texto:
            falla.append((a.get('descripcion', ''), f"falta «{a['contiene']}»"))
        if a.get('no_contiene') and a['no_contiene'] in texto:
            falla.append((a.get('descripcion', ''), f"reapareció «{a['no_contiene']}»"))
    return falla
