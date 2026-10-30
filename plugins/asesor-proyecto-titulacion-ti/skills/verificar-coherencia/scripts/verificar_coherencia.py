# -*- coding: utf-8 -*-
"""
verificar_coherencia.py — control de calidad de un avance de titulación.

Falla (código de salida 1) si:
  1. Citas ↔ referencias: una referencia no se cita o una cita no tiene
     referencia (control propio) y, si está instalado el Asistente de
     Investigación Científica, su verificar_apa.py reporta errores.
  2. Cifras clave ↔ artefactos: una cifra de coherencia.json no aparece, con
     el valor que dice su artefacto JSON, en el Resumen y/o en el cuerpo.
  3. Páginas mínimas: una sección del perfil (hasta el avance actual) tiene
     menos páginas que el mínimo, medido en el PDF.
  4. Resumen: más palabras o palabras clave que las del perfil.
  5. Referencias: menos que el mínimo del perfil de los últimos N años.
  6. Trabajos previos: menos que el mínimo, sin lectura completa, sin página
     de evidencia, o sin columnas Arquitectura/Tecnologías.
  7. Requerimientos: trazabilidad incompleta (objetivo sin HU/RF/métrica, RF sin prueba).
  8. Arquitectura: el código viola las reglas de decisiones/arquitectura_reglas.json.
  9. Versiones: la versión elegida en una decisión tecnológica no coincide
     con la fijada en el código.
 10. Numeración: «Referencias» o «Anexos» llevan número (manual o automático),
     que el formato oficial no admite.

Las advertencias (AVISO) no hacen fallar, pero se deben revisar.

Uso (desde la carpeta del proyecto, después de generar el .docx y el .pdf):
    python verificar_coherencia.py [--config _automatizacion/coherencia.json] [--json informe.json]
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import os
import re
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLUGIN / 'scripts_comunes'))
from formato_es import n as fmt  # noqa: E402
from localizar_plugin import INVESTIGACION, ruta_en_plugin  # noqa: E402
from perfil import buscar_raiz, cargar_perfil, leer_json  # noqa: E402

errores: list[str] = []
avisos: list[str] = []
oks: list[str] = []

IGNORAR_CITAS = {'agosto', 'septiembre', 'mayo', 'enero', 'febrero', 'marzo', 'abril', 'junio', 'julio', 'octubre',
                 'noviembre', 'diciembre', 'milagro', 'crisp-dm', 'tabla', 'figura', 'python', 'sql server', 'windows',
                 'docker', 'cohortes', 'registro oficial', 'presentación', 'presentacion', 'ley', 'iso', 'version',
                 'versión', 'node', 'react', 'java', 'angular', 'scrum', 'uml', 'anexo', 'sprint'}


def _mod(ruta: Path, nombre: str):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sin_tildes(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()


def valor_ruta(datos, ruta: str):
    for parte in ruta.split('.'):
        if isinstance(datos, list):
            datos = datos[int(parte)]
        else:
            datos = datos[parte]
    return datos


# ── Lectura del documento ────────────────────────────────────────────────
def leer_documento(ruta_docx: Path, estilo_ref: str):
    import docx
    doc = docx.Document(str(ruta_docx))
    pars = doc.paragraphs
    refs = [p.text.strip() for p in pars if p.style is not None and p.style.name == estilo_ref and p.text.strip()]
    if not refs:  # sin estilo Bibliography: lo que está entre «Referencias» y «Anexos»
        dentro = False
        for p in pars:
            t = sin_tildes(p.text.strip()).rstrip('.')
            es_titulo = p.style is not None and ('heading' in p.style.name.lower() or 'título' in p.style.name.lower())
            if es_titulo and t in ('referencias', 'bibliografia', 'referencias bibliograficas'):
                dentro = True
                continue
            if dentro and es_titulo:
                break
            if dentro and p.text.strip():
                refs.append(p.text.strip())
    set_refs = set(refs)
    cuerpo = '\n'.join(p.text for p in pars if p.text.strip() not in set_refs)
    cuerpo += '\n' + '\n'.join(c.text for t in doc.tables for f in t.rows for c in f.cells)
    return doc, refs, cuerpo


def encontrar_resumen(doc, prefijo: str) -> tuple[str, str]:
    pars = [p for p in doc.paragraphs]
    if prefijo:
        res = next((p.text for p in pars if p.text.strip().startswith(prefijo)), '')
    else:
        res = ''
        for i, p in enumerate(pars):
            if sin_tildes(p.text.strip()) == 'resumen':
                for q in pars[i + 1:]:
                    t = q.text.strip()
                    if t and not sin_tildes(t).startswith('palabras clave'):
                        res = t
                        break
                break
    clave = next((p.text for p in pars if sin_tildes(p.text.strip()).startswith('palabras clave')), '')
    return res, clave


# ── 1. Citas ↔ referencias (control propio) ──────────────────────────────
def control_citas(refs: list[str], cuerpo: str, ignorar: set[str]):
    cuerpo_n = sin_tildes(cuerpo)
    pares: list[tuple[str, str]] = []
    for r in refs:
        primero = re.split(r'[,.(]', r, maxsplit=1)[0].strip()
        anio = re.search(r'\((\d{4})', r)
        pares.append((sin_tildes(primero), anio.group(1) if anio else ''))
    for apellido, anio in pares:
        clave = apellido.split()[-1] if apellido.split() else apellido
        if apellido not in cuerpo_n and clave not in cuerpo_n:
            errores.append(f'Referencia no citada en el texto: {apellido} ({anio})')
    patron = re.compile(r"([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñü'\-]+(?: [A-ZÁÉÍÓÚÑ][a-záéíóúñ\-]+)?)"
                        r"(?: et al\.| y [A-ZÁÉÍÓÚÑ][\w\-]+| & [A-ZÁÉÍÓÚÑ][\w\-]+)?,? \(?((?:19|20)\d{2})\)?")
    n_citas = 0
    for m in patron.finditer(cuerpo):
        apellido = sin_tildes(m.group(1))
        if apellido in ignorar or any(apellido.startswith(i) for i in ignorar):
            continue
        ventana = sin_tildes(cuerpo[max(0, m.start() - 160):m.end()])
        anio = m.group(2)
        if any(a.split() and a.split()[-1] in ventana and (not r or r == anio) for a, r in pares):
            n_citas += 1
            continue
        contexto = cuerpo[max(0, m.start() - 40):m.end() + 5].replace('\n', ' ')
        if re.search(r'et al\.|\(\w|, \d{4}\)| y \w+ \(', contexto):
            errores.append(f'Cita sin referencia: «{m.group(0)}» … {contexto!r}')
    oks.append(f'Citas ↔ referencias (control propio): {len(refs)} referencias, {n_citas} citas reconocidas.')


def control_apa_plugin(ruta_docx: Path, desde: int | None):
    script = ruta_en_plugin(INVESTIGACION, 'skills/redaccion-apa7/scripts/verificar_apa.py')
    if script is None:
        avisos.append('No está instalado el Asistente de Investigación Científica: se omitió verificar_apa.py '
                      '(solo corrió el control propio de citas).')
        return
    cmd = [sys.executable, str(script), str(ruta_docx)]
    if desde:
        cmd += ['--desde', str(desde), '--hasta', str(date.today().year)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                       env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    salida = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        oks.append('verificar_apa.py (APA 7): sin errores.' + (' Revisa sus advertencias.' if 'ADVERTENCIA' in salida.upper() else ''))
        if 'ADVERTENCIA' in salida.upper():
            avisos.append('verificar_apa.py reportó advertencias:\n' + _sangrar(salida))
    else:
        errores.append('verificar_apa.py (APA 7) reportó errores:\n' + _sangrar(salida))


def _sangrar(texto: str, max_lineas: int = 40) -> str:
    lineas = texto.splitlines()
    extra = f'\n      … ({len(lineas) - max_lineas} líneas más)' if len(lineas) > max_lineas else ''
    return '\n'.join('      ' + l for l in lineas[:max_lineas]) + extra


# ── 2. Cifras clave ↔ artefactos ─────────────────────────────────────────
def _cumple(valor, op, ref) -> bool:
    return {'>=': valor >= ref, '<=': valor <= ref, '==': valor == ref, '>': valor > ref, '<': valor < ref}[op]


def control_cifras(cifras: list[dict], raiz: Path, resumen: str, cuerpo: str):
    for c in cifras:
        if c.get('_ejemplo'):
            avisos.append(f"coherencia.json todavía tiene la cifra de ejemplo «{c.get('nombre')}»: reemplázala o bórrala.")
            continue
        archivos = sorted(glob.glob(str(raiz / c['archivo'])))
        datos = None
        for a in reversed(archivos):  # el más reciente (orden por nombre con fecha) que cumpla el filtro
            d = leer_json(a)
            if all(_cumple(valor_ruta(d, k), op, v) for k, (op, v) in c.get('filtro', {}).items()):
                datos = d
                break
        if datos is None:
            errores.append(f"Cifra «{c['nombre']}»: no hay artefacto {c['archivo']} que cumpla el filtro.")
            continue
        valor = valor_ruta(datos, c['ruta']) * c.get('escala', 1)
        texto = fmt(valor, c.get('decimales', 3))
        con_sufijo = texto + c.get('sufijo', '')
        donde = c.get('en', ['cuerpo'])
        if 'resumen' in donde and con_sufijo not in resumen:
            errores.append(f"Resumen: falta «{c['nombre']}» = {con_sufijo}")
        if 'cuerpo' in donde and texto not in cuerpo:
            errores.append(f"Cuerpo: falta «{c['nombre']}» = {texto}")
    if cifras:
        oks.append(f'Cifras clave revisadas: {len([c for c in cifras if not c.get("_ejemplo")])}.')


# ── 3. Páginas mínimas por sección (PDF) ─────────────────────────────────
def detectar_inicio(pdf) -> int:
    """Primera página después del índice (tabla de contenido)."""
    inicio_toc = None
    for i, pag in enumerate(pdf):
        lineas = [l.strip() for l in pag.get_text().splitlines()]
        if inicio_toc is None and any(sin_tildes(l) in ('tabla de contenido', 'indice', 'contenido', 'indice general')
                                      for l in lineas):
            inicio_toc = i
            continue
        if inicio_toc is not None:
            puntos = sum(1 for l in lineas if re.search(r'\.{5,}\s*\d*$', l))
            if puntos < 3:
                return i
    return 0


def lineas_unidas(texto: str) -> list[str]:
    """Con numeración automática de Word, el PDF pone el número del título en
    una línea («1.1») y el texto en la siguiente («Descripción»): se unen."""
    salida: list[str] = []
    pendiente = ''
    for linea in texto.splitlines():
        s = ' '.join(linea.split())
        if re.fullmatch(r'\d+(\.\d+)*\.?', s):
            pendiente = s
            continue
        if pendiente:
            s = f'{pendiente} {s}' if s else pendiente
            pendiente = ''
        salida.append(s)
    return salida


def control_paginas(pdf_ruta: Path, perfil: dict, avance: int, desde: int | None):
    import pymupdf
    pdf = pymupdf.open(str(pdf_ruta))
    inicio = desde if desde is not None else detectar_inicio(pdf)
    marcas = [s for s in perfil['secciones'] if s.get('marca_pdf')]
    pos: dict[str, tuple[int, int]] = {}
    for i, pag in enumerate(pdf):
        if i < inicio:
            continue
        for j, s in enumerate(lineas_unidas(pag.get_text())):
            for sec in marcas:
                m = ' '.join(sec['marca_pdf'].split())
                if sec['id'] not in pos and s.startswith(m) and len(s) < len(m) + 25:
                    pos[sec['id']] = (i + 1, j)
    orden = sorted(pos.items(), key=lambda kv: kv[1])
    for sec in perfil['secciones']:
        if not sec.get('min_paginas') or int(sec.get('avance', 99)) > avance:
            continue
        if sec['id'] not in pos:
            errores.append(f"No se encontró la sección «{sec['marca_pdf']}» en el PDF (desde la página {inicio + 1}).")
            continue
        k = [i for i, (sid, _) in enumerate(orden) if sid == sec['id']][0]
        if k + 1 >= len(orden):
            avisos.append(f"«{sec['marca_pdf']}»: no hay sección siguiente para medir sus páginas.")
            continue
        paginas = orden[k + 1][1][0] - pos[sec['id']][0]
        estado = 'OK ' if paginas >= sec['min_paginas'] else 'MAL'
        print(f"  {estado} {sec['marca_pdf']}: {paginas} páginas (mínimo {sec['min_paginas']})")
        if paginas < sec['min_paginas']:
            errores.append(f"{sec['marca_pdf']}: {paginas} páginas, mínimo {sec['min_paginas']}")
    oks.append(f'PDF: {len(pdf)} páginas; cuerpo desde la página {inicio + 1}.')


# ── 4–5. Resumen y referencias ───────────────────────────────────────────
def control_resumen(resumen: str, clave: str, perfil: dict):
    reglas = next((s.get('reglas', {}) for s in perfil['secciones'] if s['id'] == 'resumen'), {})
    if not resumen:
        errores.append('No se encontró el párrafo del Resumen.')
        return
    palabras = len(resumen.split())
    if reglas.get('max_palabras') and palabras > reglas['max_palabras']:
        errores.append(f"Resumen con {palabras} palabras (máximo {reglas['max_palabras']}).")
    else:
        oks.append(f'Resumen: {palabras} palabras.')
    if clave and reglas.get('max_palabras_clave'):
        items = [x for x in re.split(r'[,;]', clave.split(':', 1)[-1]) if x.strip()]
        if len(items) > reglas['max_palabras_clave']:
            errores.append(f"Palabras clave: {len(items)} (máximo {reglas['max_palabras_clave']}).")


def control_referencias(refs: list[str], perfil: dict):
    req = perfil.get('requisitos', {})
    minimo, anios = req.get('min_referencias'), req.get('anios_referencias')
    if not minimo:
        return
    hoy = date.today().year
    anio_ref = [int(m.group(1)) for r in refs if (m := re.search(r'\((\d{4})', r))]
    recientes = [a for a in anio_ref if not anios or a > hoy - anios]
    texto = f'de {hoy - anios + 1} a {hoy}' if anios else ''
    if len(recientes) < minimo:
        errores.append(f'Referencias {texto}: {len(recientes)} (mínimo {minimo}). Total en la lista: {len(refs)}.')
    else:
        oks.append(f'Referencias {texto}: {len(recientes)} de {len(refs)} (mínimo {minimo}).')


# ── 6–9. Datos del proyecto ──────────────────────────────────────────────
def control_trabajos_previos(ruta: Path, perfil: dict, cuerpo: str):
    mod = _mod(PLUGIN / 'skills/trabajos-previos/scripts/tabla_trabajos_previos.py', 'tabla_tp')
    e, a, resumen = mod.validar(leer_json(ruta), perfil, cuerpo)
    errores.extend(f'Trabajos previos: {x}' for x in e)
    avisos.extend(f'Trabajos previos: {x}' for x in a)
    if not e:
        oks.append(f'Trabajos previos: {resumen}')


def control_requerimientos(ruta: Path, perfil: dict, repo: Path | None):
    mod = _mod(PLUGIN / 'skills/analisis-requerimientos/scripts/trazabilidad.py', 'trazabilidad')
    e, a = mod.validar(leer_json(ruta), perfil, repo)
    errores.extend(f'Requerimientos: {x}' for x in e)
    avisos.extend(f'Requerimientos: {x}' for x in a)
    if not e:
        oks.append('Requerimientos: trazabilidad completa.')


def control_arquitectura(ruta_reglas: Path, repo: Path | None):
    if repo is None:
        avisos.append('Arquitectura: titulacion.json no indica "repositorio_codigo"; no se verificó el código.')
        return
    mod = _mod(PLUGIN / 'skills/decision-arquitectura/scripts/verificar_reglas.py', 'verificar_reglas')
    violaciones, notas = mod.verificar(leer_json(ruta_reglas), repo)
    errores.extend(f'Arquitectura: {v}' for v in violaciones)
    avisos.extend(f'Arquitectura: {x}' for x in notas)
    if not violaciones:
        oks.append('Arquitectura: el código cumple las reglas declaradas.')


def control_versiones(carpeta: Path, repo: Path | None):
    if repo is None:
        return
    mod = _mod(PLUGIN / 'skills/seleccion-tecnologica/scripts/matriz_decision.py', 'matriz_decision')
    e, a = mod.verificar_versiones(carpeta, repo)
    errores.extend(f'Versiones: {x}' for x in e)
    avisos.extend(f'Versiones: {x}' for x in a)


def control_matriz_lit_codigo(ruta: Path):
    import openpyxl
    wb = openpyxl.load_workbook(str(ruta), read_only=True)
    hoja = next((ws for ws in wb.worksheets if 'coherencia' in sin_tildes(ws.title)), None)
    if hoja is None:
        avisos.append(f'{ruta.name}: no tiene la hoja de coherencia literatura-código.')
        return
    filas = [r for r in hoja.iter_rows(values_only=True) if any(v not in (None, '') for v in r)]
    enc_i = next((i for i, r in enumerate(filas) if r and any(sin_tildes(str(v or '')).startswith('antecedente') for v in r)), None)
    if enc_i is None:
        avisos.append('Matriz literatura-código: no se encontró el encabezado «Antecedente».')
        return
    vacias = [str(r[0]) for r in filas[enc_i + 1:] if any(v in (None, '') for v in r[:5])]
    if vacias:
        errores.append(f'Matriz literatura-código: filas con celdas vacías: {", ".join(vacias[:8])}')
    else:
        oks.append(f'Matriz literatura-código: {len(filas) - enc_i - 1} filas completas.')


MARCAS_PENDIENTES = (r'⟦[^⟧]*⟧', r'\bCOMPLETAR\b', r'\bBORRADOR\b', r'\[\s*pendiente[^\]]*\]', r'X{4,}', r'…{3,}|\.{6,}')


def control_pendientes(doc):
    """Un documento entregable no lleva marcadores de dato pendiente ni texto de relleno de la plantilla
    (lección del Avance 2 de FlotaControl: se entregó con 25 marcadores ⟦…⟧ y la declaración sin llenar)."""
    textos = [p.text for p in doc.paragraphs]
    textos += [c.text for t in doc.tables for f in t.rows for c in f.cells]
    for s in doc.sections:
        textos += [p.text for p in s.header.paragraphs] + [p.text for p in s.footer.paragraphs]
    hallados = []
    for t in textos:
        for patron in MARCAS_PENDIENTES:
            for m in re.finditer(patron, t, flags=re.IGNORECASE if 'pendiente' in patron else 0):
                hallados.append(t[max(0, m.start() - 30):m.end() + 30].replace('\n', ' '))
    if hallados:
        unicos = list(dict.fromkeys(hallados))
        errores.append(f'{len(hallados)} marcadores de dato pendiente o texto de relleno: '
                       + ' | '.join(f'«…{h}…»' for h in unicos[:8]))
    else:
        oks.append('Sin marcadores de dato pendiente ni texto de relleno.')


def control_numeracion(doc, titulos=('Referencias', 'Anexos')):
    """Los títulos de Referencias y Anexos no llevan número (observación de tutora, UNEMI 2026)."""
    for par in doc.paragraphs:
        if not par.style.name.startswith(('Heading 1', 'Título 1')):
            continue
        texto = par.text.strip()
        if re.match(r'^\d+\.?\s*(' + '|'.join(titulos) + ')', texto):
            errores.append(f'Título numerado fuera del formato: «{texto}» (Referencias y Anexos no llevan número).')
        pPr = par._p.pPr
        if texto.startswith(titulos) and pPr is not None and pPr.numPr is not None:
            errores.append(f'Título con numeración automática: «{texto}». Quítala con quitar_numeracion().')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--config', default='_automatizacion/coherencia.json')
    ap.add_argument('--raiz', help='raíz del proyecto (por defecto, donde está titulacion.json)')
    ap.add_argument('--perfil', help='perfil a usar si no hay titulacion.json (p. ej. unemi)')
    ap.add_argument('--json', help='guardar el informe en este JSON')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')

    raiz = Path(a.raiz).resolve() if a.raiz else (buscar_raiz('.') or Path('.').resolve())
    config_ruta = Path(a.config) if Path(a.config).is_absolute() else raiz / a.config
    cfg = leer_json(config_ruta)
    proyecto = leer_json(raiz / 'titulacion.json') if (raiz / 'titulacion.json').exists() else {}
    perfil = cargar_perfil(a.perfil or proyecto.get('perfil', 'unemi'), raiz)
    avance = int(cfg.get('avance') or proyecto.get('avance_actual', 1))
    repo = None
    if proyecto.get('repositorio_codigo'):
        repo = Path(proyecto['repositorio_codigo'])
        repo = repo if repo.is_absolute() else (raiz / repo).resolve()
    comprobar = cfg.get('comprobar', {})

    ruta_docx = raiz / cfg['documento']
    doc, refs, cuerpo = leer_documento(ruta_docx, cfg.get('estilo_referencias', 'Bibliography'))
    resumen, clave = encontrar_resumen(doc, cfg.get('prefijo_resumen', ''))
    print(f'Documento: {ruta_docx.name} · Avance {avance} · Perfil {perfil["id"]}')

    anios = perfil.get('requisitos', {}).get('anios_referencias')
    if comprobar.get('citas_propias', True):
        control_citas(refs, cuerpo, IGNORAR_CITAS | {sin_tildes(x) for x in cfg.get('ignorar_citas', [])})
    if comprobar.get('apa_plugin_investigacion', True):
        control_apa_plugin(ruta_docx, date.today().year - anios + 1 if anios else None)
    control_cifras(cfg.get('cifras', []), raiz, resumen, cuerpo)
    if comprobar.get('resumen', True):
        control_resumen(resumen, clave, perfil)
    control_referencias(refs, perfil)
    if comprobar.get('numeracion_titulos', True):
        control_numeracion(doc)
    if comprobar.get('sin_pendientes', True):
        control_pendientes(doc)
    if comprobar.get('paginas_minimas', True):
        pdf = raiz / cfg['pdf'] if cfg.get('pdf') else None
        if pdf and pdf.exists():
            control_paginas(pdf, perfil, avance, cfg.get('paginas_desde'))
        else:
            errores.append(f'No existe el PDF {cfg.get("pdf")}: genéralo con docx_a_pdf.ps1 para medir las páginas.')
    for clave_cfg, funcion in [('trabajos_previos', lambda r: control_trabajos_previos(r, perfil, cuerpo)),
                               ('requerimientos', lambda r: control_requerimientos(r, perfil, repo)),
                               ('reglas_arquitectura', lambda r: control_arquitectura(r, repo))]:
        rel = comprobar.get(clave_cfg)
        if rel and (raiz / rel).exists():
            funcion(raiz / rel)
        elif rel and avance >= 2 and clave_cfg != 'trabajos_previos':
            avisos.append(f'No existe {rel}: no se verificó ({clave_cfg}).')
    if comprobar.get('versiones_adr') and (raiz / comprobar['versiones_adr']).is_dir():
        control_versiones(raiz / comprobar['versiones_adr'], repo)
    if comprobar.get('matriz_literatura_codigo') and (raiz / comprobar['matriz_literatura_codigo']).exists():
        control_matriz_lit_codigo(raiz / comprobar['matriz_literatura_codigo'])

    print('\nOK:')
    for o in oks:
        print('  ✓', o)
    if avisos:
        print('\nAVISOS (revisar):')
        for x in avisos:
            print('  !', x)
    if a.json:
        Path(a.json).write_text(json.dumps({'errores': errores, 'avisos': avisos, 'ok': oks}, indent=2, ensure_ascii=False),
                                encoding='utf-8')
    if errores:
        print('\nERRORES:')
        for e in errores:
            print('  ✗', e)
        return 1
    print('\nCoherencia verificada: sin errores.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
