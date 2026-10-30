# -*- coding: utf-8 -*-
"""
docx_titulacion.py — insertar contenido en la plantilla oficial de
titulación (un .docx EXISTENTE) respetando su formato.

Principios (aprendidos en los Avances 1 y 2 de la tesis VicMar Data AI):
  - La plantilla oficial NUNCA se edita: se copia y el generador inserta.
  - Se ancla por PREFIJO DE TEXTO (buscar), nunca por índice de párrafo.
  - Figuras y tablas en APA 7: «Figura N»/«Tabla N» en negrita y título en
    cursiva ARRIBA, «Nota.» con la fuente DEBAJO; numeración automática;
    leyendas unidas a su objeto (keep_with_next) para que no queden huérfanas.
  - Las tablas repiten el encabezado al cruzar de página.
  - Una referencia nueva se inserta copiando SOLO el formato (pPr) de la
    vecina: copiar todo arrastra el hipervínculo del DOI de la otra.
  - Markdown mínimo en el texto: **negrita** y *cursiva*.

    from docx_titulacion import Insertor, abrir_copia, buscar
    doc = abrir_copia('Plantilla_ORIGINAL.docx')
    ins = Insertor(doc, perfil)            # formato tomado del perfil institucional
    a = ins.titulo(buscar(doc, 'Referencias'), '2. Análisis del caso', 1, antes=True)
"""
from __future__ import annotations

import ast
import copy
import re
from pathlib import Path

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Emu, Inches, Pt, RGBColor
from docx.text.paragraph import Paragraph


class Formato:
    """Formato del cuerpo. Por defecto, el de la UNEMI (Arial 12, 1,5, 10 pt después)."""

    def __init__(self, perfil: dict | None = None):
        f = (perfil or {}).get('formato', {})
        self.fuente = f.get('fuente', 'Arial')
        self.tam = Pt(f.get('tam_pt', 12))
        self.interlineado = f.get('interlineado', 1.5)
        self.despues = Pt(f.get('espacio_despues_pt', 10))
        self.titulo1 = Pt(f.get('titulo1_pt', 14))
        self.titulo2 = Pt(f.get('titulo2_pt', 12))
        self.fuente_codigo = f.get('fuente_codigo', 'Consolas')
        self.tam_codigo = Pt(f.get('tam_codigo_pt', 8.5))
        self.color_encabezado = f.get('color_encabezado_tabla', 'D9E2F3')


class Insertor:
    """Encadena inserciones después de un ancla (párrafo o tabla). Cada método
    devuelve el último elemento insertado, que sirve de ancla al siguiente."""

    def __init__(self, doc, perfil: dict | None = None):
        self.doc = doc
        self.body = doc.paragraphs[0]._parent
        self.f = Formato(perfil)
        self.n_figura = 0
        self.n_tabla = 0

    # ── internas ────────────────────────────────────────────────────────
    @staticmethod
    def _el(anchor):
        return anchor._p if hasattr(anchor, '_p') else anchor._tbl

    def _nuevo(self, estilo: str | None = 'Normal'):
        p = Paragraph(OxmlElement('w:p'), self.body)
        if estilo:
            try:
                p.style = estilo
            except KeyError:
                pass
        return p

    def _cuerpo(self, p, alineacion=WD_ALIGN_PARAGRAPH.JUSTIFY, despues=None):
        pf = p.paragraph_format
        pf.line_spacing = self.f.interlineado
        pf.space_after = self.f.despues if despues is None else despues
        if alineacion is not None:
            p.alignment = alineacion

    def _run(self, p, texto, negrita=False, cursiva=False, tam=None, fuente=None, color=None):
        r = p.add_run(texto)
        r.bold, r.italic = negrita, cursiva
        fuente = fuente or self.f.fuente
        r.font.name = fuente
        r.font.size = tam or self.f.tam
        r._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), fuente)
        if color:
            r.font.color.rgb = RGBColor(*color)
        return r

    def _markdown(self, p, texto, tam=None, negrita_base=False):
        for trozo in re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', str(texto)):
            if not trozo:
                continue
            if trozo.startswith('**') and trozo.endswith('**'):
                self._run(p, trozo[2:-2], negrita=True, tam=tam)
            elif trozo.startswith('*') and trozo.endswith('*') and len(trozo) > 2:
                self._run(p, trozo[1:-1], cursiva=True, negrita=negrita_base, tam=tam)
            else:
                self._run(p, trozo, negrita=negrita_base, tam=tam)

    def _poner(self, anchor, nuevo, antes=False):
        if antes:
            self._el(anchor).addprevious(self._el(nuevo))
        else:
            self._el(anchor).addnext(self._el(nuevo))
        return nuevo

    def _sombra(self, elemento_pr, color):
        s = OxmlElement('w:shd')
        s.set(qn('w:val'), 'clear')
        s.set(qn('w:color'), 'auto')
        s.set(qn('w:fill'), color)
        elemento_pr.append(s)

    # ── API ─────────────────────────────────────────────────────────────
    def titulo(self, anchor, texto, nivel=1, salto_pagina=False, antes=False):
        """Título con el estilo de la plantilla (Heading N). Con antes=True se
        inserta ANTES del ancla (útil para abrir una sección antes de «Referencias»)."""
        if salto_pagina:
            anchor = self.salto_pagina(anchor, antes=antes)
            antes = False
        p = self._nuevo(f'Heading {nivel}')
        self._run(p, texto, negrita=True, tam=self.f.titulo1 if nivel == 1 else self.f.titulo2)
        p.paragraph_format.space_after = self.f.despues
        p.paragraph_format.keep_with_next = True
        return self._poner(anchor, p, antes)

    def subtitulo(self, anchor, texto):
        p = self._nuevo()
        self._cuerpo(p)
        self._run(p, texto, negrita=True)
        p.paragraph_format.keep_with_next = True
        return self._poner(anchor, p)

    def parrafo(self, anchor, texto, alineacion=WD_ALIGN_PARAGRAPH.JUSTIFY, antes=False):
        p = self._nuevo()
        self._cuerpo(p, alineacion)
        self._markdown(p, texto)
        return self._poner(anchor, p, antes)

    def bloque(self, anchor, texto):
        """Un párrafo por cada bloque separado por una línea en blanco."""
        for t in [b.strip() for b in str(texto).strip().split('\n\n') if b.strip()]:
            anchor = self.parrafo(anchor, ' '.join(t.split('\n')))
        return anchor

    def vinetas(self, anchor, items, numeradas=False):
        for i, it in enumerate(items, 1):
            p = self._nuevo()
            self._cuerpo(p, despues=Pt(4))
            p.paragraph_format.left_indent = Inches(0.35)
            p.paragraph_format.first_line_indent = Inches(-0.2)
            self._run(p, f'{i}. ' if numeradas else '• ')
            self._markdown(p, it)
            anchor = self._poner(anchor, p)
        return anchor

    viñetas = vinetas

    def salto_pagina(self, anchor, antes=False):
        p = self._nuevo()
        p.add_run().add_break(WD_BREAK.PAGE)
        return self._poner(anchor, p, antes)

    def _leyenda(self, anchor, rotulo, titulo):
        p = self._nuevo()
        self._cuerpo(p, WD_ALIGN_PARAGRAPH.LEFT, despues=Emu(0))
        self._run(p, rotulo, negrita=True, tam=Pt(11))
        p.paragraph_format.keep_with_next = True
        anchor = self._poner(anchor, p)
        p = self._nuevo()
        self._cuerpo(p, WD_ALIGN_PARAGRAPH.LEFT, despues=Pt(4))
        self._run(p, titulo, cursiva=True, tam=Pt(11))
        p.paragraph_format.keep_with_next = True
        return self._poner(anchor, p)

    def _nota(self, anchor, nota):
        p = self._nuevo()
        self._cuerpo(p, WD_ALIGN_PARAGRAPH.LEFT)
        self._run(p, 'Nota. ', cursiva=True, tam=Pt(10))
        self._markdown(p, nota, tam=Pt(10))
        return self._poner(anchor, p)

    def figura(self, anchor, ruta_imagen, titulo, fuente='Elaboración propia.', ancho_pulgadas=6.2):
        self.n_figura += 1
        anchor = self._leyenda(anchor, f'Figura {self.n_figura}', titulo)
        p = self._nuevo()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(str(ruta_imagen), width=Inches(ancho_pulgadas))
        anchor = self._poner(anchor, p)
        return self._nota(anchor, fuente)

    def tabla(self, anchor, filas, titulo=None, nota='Elaboración propia.', anchos=None, tam=9):
        """Tabla APA 7. filas[0] es el encabezado."""
        if titulo:
            self.n_tabla += 1
            anchor = self._leyenda(anchor, f'Tabla {self.n_tabla}', titulo)
        t = self.doc.add_table(rows=len(filas), cols=len(filas[0]))
        try:
            t.style = 'Table Grid'
        except KeyError:
            pass
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, fila in enumerate(filas):
            for j, valor in enumerate(fila):
                celda = t.cell(i, j)
                celda.text = ''
                par = celda.paragraphs[0]
                par.paragraph_format.space_after = Emu(0)
                par.paragraph_format.line_spacing = 1.0
                self._markdown(par, valor, tam=Pt(tam), negrita_base=(i == 0))
                if i == 0:
                    self._sombra(celda._tc.get_or_add_tcPr(), self.f.color_encabezado)
        if anchos:
            for fila in t.rows:
                for j, ancho in enumerate(anchos):
                    fila.cells[j].width = Inches(ancho)
        tr_pr = t.rows[0]._tr.get_or_add_trPr()
        rep = OxmlElement('w:tblHeader')
        rep.set(qn('w:val'), 'true')
        tr_pr.append(rep)
        anchor = self._poner(anchor, t)
        return self._nota(anchor, nota) if nota else anchor

    def codigo(self, anchor, texto, titulo=None):
        """Código en fuente monoespaciada, fondo gris, interlineado sencillo."""
        if titulo:
            anchor = self.parrafo(anchor, titulo)
        for linea in str(texto).rstrip('\n').split('\n'):
            p = self._nuevo()
            pf = p.paragraph_format
            pf.space_after = pf.space_before = Emu(0)
            pf.line_spacing = 1.0
            self._run(p, linea if linea.strip() else ' ', fuente=self.f.fuente_codigo, tam=self.f.tam_codigo)
            self._sombra(p._p.get_or_add_pPr(), 'F2F2F2')
            anchor = self._poner(anchor, p)
        return self.parrafo(anchor, '')


# ── utilidades de documento ───────────────────────────────────────────────
def abrir_copia(plantilla: str | Path):
    """Abre la plantilla. Se guarda SIEMPRE con otro nombre (doc.save(salida))."""
    return docx.Document(str(plantilla))


def buscar(doc, prefijo: str, estilo: str | None = None, desde: int = 0):
    """Primer párrafo cuyo texto empieza con `prefijo` (y con `estilo`, si se da)."""
    for p in doc.paragraphs[desde:]:
        if p.text.strip().startswith(prefijo) and (estilo is None or (p.style is not None and p.style.name == estilo)):
            return p
    raise KeyError(f'No hay un párrafo que empiece con «{prefijo}»' + (f' y estilo {estilo}' if estilo else ''))


def reemplazar_texto(parrafo, nuevo: str):
    """Reemplaza el texto conservando el formato del primer run."""
    runs = parrafo.runs
    if not runs:
        parrafo.add_run(nuevo)
        return
    runs[0].text = nuevo
    for r in runs[1:]:
        r.text = ''


def eliminar(parrafo_o_tabla):
    el = parrafo_o_tabla._p if hasattr(parrafo_o_tabla, '_p') else parrafo_o_tabla._tbl
    el.getparent().remove(el)


def quitar_numeracion(parrafo):
    ppr = parrafo._p.pPr
    if ppr is not None and ppr.numPr is not None:
        ppr.remove(ppr.numPr)


def insertar_referencia(doc, antes_de_prefijo: str, partes: list[tuple[str, bool]], estilo: str = 'Bibliography'):
    """Inserta una referencia ANTES de la que empieza con `antes_de_prefijo`
    (orden alfabético). partes = [(texto, cursiva), …]."""
    refs = [p for p in doc.paragraphs if p.style is not None and p.style.name == estilo] or doc.paragraphs
    base = next(p for p in refs if p.text.startswith(antes_de_prefijo))
    nuevo = copy.deepcopy(base._p)
    base._p.addprevious(nuevo)
    for hijo in list(nuevo):          # conservar solo el formato del párrafo
        if hijo.tag != qn('w:pPr'):
            nuevo.remove(hijo)
    par = Paragraph(nuevo, base._parent)
    for texto, cursiva in partes:
        par.add_run(texto).italic = cursiva
    return par


def referencia_desde_markdown(texto_apa: str) -> list[tuple[str, bool]]:
    """'Autor. (2025). Título. *Revista, 4*(2), 1–9.' → partes para insertar_referencia."""
    return [(t[1:-1], True) if t.startswith('*') and t.endswith('*') else (t, False)
            for t in re.split(r'(\*[^*]+\*)', texto_apa) if t]


def contar_palabras(texto: str) -> int:
    return len(texto.split())


def huella_texto(ruta) -> str:
    """Huella del CONTENIDO (párrafos y tablas), no del archivo. Word vuelve a
    guardar el .docx al actualizar el índice (docx_a_pdf.ps1) y cambia su md5
    sin que nadie lo edite; la huella del texto solo cambia si alguien
    modificó el contenido. La tabla de contenido no cuenta."""
    import hashlib
    d = docx.Document(str(ruta))
    partes = [p.text for p in d.paragraphs if not (p.style is not None and p.style.name.lower().startswith(('toc', 'tdc')))]
    partes += [c.text for t in d.tables for f in t.rows for c in f.cells]
    return hashlib.sha1('\n'.join(partes).encode('utf-8')).hexdigest()


# ── código fuente leído EN VIVO (el documento no puede mostrar otro código) ──
def funcion_py(ruta, nombre: str, max_lineas: int = 60) -> str:
    """Fuente de una función, clase o asignación de un archivo Python (AST).
    Quita el docstring si la función es larga, para mostrar la lógica."""
    texto = Path(ruta).read_text(encoding='utf-8')
    for nodo in ast.walk(ast.parse(texto)):
        coincide = getattr(nodo, 'name', None) == nombre or any(
            getattr(t, 'id', None) == nombre for t in getattr(nodo, 'targets', []))
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Assign)) and coincide:
            seg = ast.get_source_segment(texto, nodo)
            if len(seg.split('\n')) > 25:
                seg = re.sub(r'\n(\s+)(\"\"\"|\'\'\')[\s\S]*?\2\n', '\n', seg, count=1)
            lineas = seg.split('\n')
            return '\n'.join(lineas[:max_lineas]) + ('\n    ...' if len(lineas) > max_lineas else '')
    raise KeyError(f'{nombre} no está en {ruta}')


def fragmento(ruta, desde: str, hasta: str, exacto: bool = False) -> str:
    """Líneas desde la primera que contiene `desde` hasta la primera posterior
    que contiene `hasta` (o que es exactamente `hasta`, sin espacios, con exacto=True).
    Sirve para JavaScript, SQL o cualquier texto."""
    lineas = Path(ruta).read_text(encoding='utf-8').split('\n')
    i = next(k for k, l in enumerate(lineas) if desde in l)
    j = next(k for k, l in enumerate(lineas[i + 1:], i + 1) if (l.strip() == hasta if exacto else hasta in l))
    bloque = lineas[i:j + 1]
    sangria = min(len(l) - len(l.lstrip()) for l in bloque if l.strip())
    return '\n'.join(l[sangria:] for l in bloque)
