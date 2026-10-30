"""Biblioteca para armar documentos Word en estilo APA 7 con python-docx.

Sale del script que construyó el trabajo integrador S7 (Sistema de Costeo, UNEMI) y sirve para cualquier trabajo.

Qué ofrece:
  - Cursor: inserta párrafos, títulos (niveles 1–5 APA), tablas APA, figuras APA, ecuaciones del editor de
    Word (OMML, editables con Alt+=), imágenes y saltos de página a partir de un párrafo ancla.
  - Marcado en el texto: **negrita**, *cursiva* y ==resaltado amarillo== (para marcadores que otra persona completa).
  - Espacio fijo antes del «%» (el signo no queda solo al inicio de una línea) y títulos que no quedan huérfanos.
  - Referencias en orden alfabético APA con sangría francesa.
  - Ecuaciones: m_t, m_texto, m_frac, m_sub, m_sup, m_raiz.

Uso típico (documento desde una plantilla con títulos existentes):
    from word_apa import Cursor, abrir, buscar_parrafo, referencias, m_frac, m_t
    doc = abrir("Plantilla.docx")                      # o abrir() para un documento nuevo con el perfil
    cur = Cursor(doc, buscar_parrafo(doc, "Desarrollo del tema"))
    cur.titulo("PARTE I. MARCO TEÓRICO", 1)
    cur.parrafo("Texto con *cursiva* y una cita (Autor, 2024).")
    cur.tabla(1, "Título en cursiva", ["Col 1", "Col 2"], [["a", "b"]], "Elaboración propia.")
    cur.ecuacion(m_t("PE=") + m_frac(m_t("CF"), m_t("MCu")))
    referencias(Cursor(doc, buscar_parrafo(doc, "Referencias")), lista_apa)
    doc.save("Trabajo.docx")

Perfiles de formato (PERFILES): "unemi" (Times New Roman 12, interlineado 1,5, justificado) y "apa" (APA 7 puro:
doble espacio, alineado a la izquierda). La guía de cada trabajo manda sobre ambos.
"""
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_LINE_SPACING
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.text.paragraph import Paragraph

PERFILES = {
    "unemi": {"fuente": "Times New Roman", "tam": 12, "interlineado": 1.5, "alineacion": WD_ALIGN_PARAGRAPH.JUSTIFY},
    "apa": {"fuente": "Times New Roman", "tam": 12, "interlineado": 2.0, "alineacion": WD_ALIGN_PARAGRAPH.LEFT},
}
PERFIL = dict(PERFILES["unemi"])
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def usar_perfil(nombre="unemi", **cambios):
    """Cambia el perfil de formato de todo lo que se inserte después (fuente, tam, interlineado, alineacion)."""
    PERFIL.clear()
    PERFIL.update(PERFILES[nombre])
    PERFIL.update(cambios)


# ---------------------------------------------------------------- utilidades de texto
def _run(par, texto, negrita=False, cursiva=False, tam=None, resaltado=False):
    r = par.add_run(texto)
    r.font.name = PERFIL["fuente"]
    r._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), PERFIL["fuente"])
    r.font.size = Pt(tam or PERFIL["tam"])
    r.bold = negrita or None
    r.italic = cursiva or None
    if resaltado:
        r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    return r


def texto_con_formato(par, texto, tam=None, negrita_base=False):
    """Admite **negrita**, *cursiva* y ==resaltado== dentro del texto."""
    texto = re.sub(r"(\d) %", "\\1\u00a0%", texto)
    for trozo in re.split(r"(==[^=]+==|\*\*[^*]+\*\*|\*[^*]+\*)", texto):
        if not trozo:
            continue
        if trozo.startswith("=="):
            _run(par, trozo[2:-2], negrita=True, tam=tam, resaltado=True)
        elif trozo.startswith("**"):
            _run(par, trozo[2:-2], negrita=True, tam=tam)
        elif trozo.startswith("*"):
            _run(par, trozo[1:-1], cursiva=True, negrita=negrita_base, tam=tam)
        else:
            _run(par, trozo, negrita=negrita_base, tam=tam)


def formato(par, alineacion=None, sangria=Cm(1.27), antes=Pt(0), despues=Pt(0), interlineado=None, francesa=False):
    pf = par.paragraph_format
    pf.alignment = PERFIL["alineacion"] if alineacion is None else alineacion
    inter = PERFIL["interlineado"] if interlineado is None else interlineado
    pf.line_spacing_rule = {1.0: WD_LINE_SPACING.SINGLE, 1.5: WD_LINE_SPACING.ONE_POINT_FIVE,
                            2.0: WD_LINE_SPACING.DOUBLE}.get(inter, WD_LINE_SPACING.MULTIPLE)
    if inter not in (1.0, 1.5, 2.0):
        pf.line_spacing = inter
    pf.space_before = antes
    pf.space_after = despues
    if francesa:
        pf.left_indent = Cm(1.27)
        pf.first_line_indent = Cm(-1.27)
    else:
        pf.left_indent = Cm(0)
        pf.first_line_indent = sangria


# ---------------------------------------------------------------- documento
def abrir(ruta=None):
    """Abre una plantilla .docx, o crea un documento nuevo con márgenes de 2,54 cm y el perfil activo."""
    doc = Document(ruta) if ruta else Document()
    if not ruta:
        for s in doc.sections:
            s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Cm(2.54)
        estilo = doc.styles["Normal"]
        estilo.font.name = PERFIL["fuente"]
        estilo.font.size = Pt(PERFIL["tam"])
    return doc


def buscar_parrafo(doc, texto):
    """Primer párrafo cuyo texto empieza con `texto` (ignora espacios y tabulaciones iniciales)."""
    for p in doc.paragraphs:
        if p.text.strip().startswith(texto):
            return p
    raise ValueError(f"No se encontró el párrafo «{texto}» en el documento")


class Cursor:
    """Inserta elementos uno tras otro a partir de un párrafo ancla (o al final si no hay ancla)."""

    def __init__(self, doc, ancla=None):
        self.doc = doc
        self.ultimo = ancla._p if ancla is not None else doc.add_paragraph()._p

    def _nuevo_parrafo(self):
        p = OxmlElement("w:p")
        self.ultimo.addnext(p)
        self.ultimo = p
        return Paragraph(p, self.doc._body)

    def parrafo(self, texto, **fmt):
        par = self._nuevo_parrafo()
        formato(par, **fmt)
        texto_con_formato(par, texto)
        return par

    def cita_en_bloque(self, texto, cita):
        """Cita textual de 40 palabras o más: bloque con sangría de 1,27 cm, sin comillas, cita al final."""
        par = self._nuevo_parrafo()
        formato(par, alineacion=PERFIL["alineacion"], sangria=Cm(0))
        par.paragraph_format.left_indent = Cm(1.27)
        texto_con_formato(par, f"{texto} {cita}")
        return par

    def titulo(self, texto, nivel):
        """Títulos APA 7: 1 centrado negrita · 2 izquierda negrita · 3 izquierda negrita cursiva ·
        4 con sangría, negrita, termina en punto · 5 con sangría, negrita cursiva, termina en punto."""
        par = self._nuevo_parrafo()
        izq, centro = WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER
        if nivel == 1:
            formato(par, alineacion=centro, sangria=Cm(0), antes=Pt(12), despues=Pt(6))
            _run(par, texto, negrita=True)
        elif nivel == 2:
            formato(par, alineacion=izq, sangria=Cm(0), antes=Pt(12), despues=Pt(6))
            _run(par, texto, negrita=True)
        elif nivel == 3:
            formato(par, alineacion=izq, sangria=Cm(0), antes=Pt(6))
            texto_con_formato(par, texto, negrita_base=True)
        else:
            formato(par, alineacion=izq, sangria=Cm(1.27), antes=Pt(6))
            _run(par, texto if texto.endswith(".") else texto + ".", negrita=True, cursiva=(nivel == 5))
        par.paragraph_format.keep_with_next = True
        return par

    def tabla(self, numero, titulo, encabezados, filas, nota, anchos=None, tam=None):
        """Tabla APA: «Tabla N» en negrita, título en cursiva, solo líneas horizontales, nota debajo."""
        p = self._nuevo_parrafo()
        formato(p, alineacion=WD_ALIGN_PARAGRAPH.LEFT, sangria=Cm(0), antes=Pt(12))
        _run(p, f"Tabla {numero}", negrita=True)
        p.paragraph_format.keep_with_next = True
        p = self._nuevo_parrafo()
        formato(p, alineacion=WD_ALIGN_PARAGRAPH.LEFT, sangria=Cm(0), despues=Pt(6))
        _run(p, titulo, cursiva=True)
        p.paragraph_format.keep_with_next = True

        t = self.doc.add_table(rows=1 + len(filas), cols=len(encabezados))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        _bordes_apa(t)
        for c, h in enumerate(encabezados):
            _celda(t.cell(0, c), h, negrita=True, centro=True, tam=tam)
        for r, fila in enumerate(filas, 1):
            for c, v in enumerate(fila):
                _celda(t.cell(r, c), v, negrita=(c == 0), tam=tam)
        if anchos:
            for fila in t.rows:
                for c, ancho in enumerate(anchos):
                    fila.cells[c].width = Cm(ancho)
        _repetir_encabezado(t.rows[0])
        for fila in t.rows:
            fila._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        self.ultimo.addnext(t._tbl)
        self.ultimo = t._tbl

        par = self._nuevo_parrafo()
        formato(par, alineacion=WD_ALIGN_PARAGRAPH.LEFT, sangria=Cm(0), antes=Pt(6), despues=Pt(12))
        _run(par, "Nota. ", cursiva=True)
        texto_con_formato(par, nota)
        return t

    def ecuacion(self, omml):
        """Ecuación del editor de Word. omml: contenido interno de <m:oMath> (usar las funciones m_*)."""
        par = self._nuevo_parrafo()
        formato(par, alineacion=WD_ALIGN_PARAGRAPH.CENTER, sangria=Cm(0), antes=Pt(6), despues=Pt(6))
        par._p.append(parse_xml(f'<m:oMathPara xmlns:m="{M_NS}"><m:oMath>{omml}</m:oMath></m:oMathPara>'))
        return par

    def figura(self, numero, titulo, ruta, nota, ancho_cm=15.5):
        """Figura APA: «Figura N» en negrita, título en cursiva, imagen y nota."""
        p = self._nuevo_parrafo()
        formato(p, alineacion=WD_ALIGN_PARAGRAPH.LEFT, sangria=Cm(0), antes=Pt(12))
        _run(p, f"Figura {numero}", negrita=True)
        p.paragraph_format.keep_with_next = True
        p = self._nuevo_parrafo()
        formato(p, alineacion=WD_ALIGN_PARAGRAPH.LEFT, sangria=Cm(0), despues=Pt(6))
        _run(p, titulo, cursiva=True)
        p.paragraph_format.keep_with_next = True
        self.imagen(ruta, ancho_cm).paragraph_format.keep_with_next = True
        par = self._nuevo_parrafo()
        formato(par, alineacion=WD_ALIGN_PARAGRAPH.LEFT, sangria=Cm(0), antes=Pt(6), despues=Pt(12))
        _run(par, "Nota. ", cursiva=True)
        texto_con_formato(par, nota)

    def imagen(self, ruta, ancho_cm=15):
        par = self._nuevo_parrafo()
        formato(par, alineacion=WD_ALIGN_PARAGRAPH.CENTER, sangria=Cm(0))
        par.add_run().add_picture(ruta, width=Cm(ancho_cm))
        return par

    def salto_pagina(self):
        par = self._nuevo_parrafo()
        br = OxmlElement("w:br")
        br.set(qn("w:type"), "page")
        par.add_run()._r.append(br)


def _celda(celda, texto, negrita=False, centro=False, tam=None):
    par = celda.paragraphs[0]
    formato(par, alineacion=WD_ALIGN_PARAGRAPH.CENTER if centro else WD_ALIGN_PARAGRAPH.LEFT, sangria=Cm(0), interlineado=1.0)
    texto_con_formato(par, str(texto), tam=tam, negrita_base=negrita)


def _bordes_apa(tabla):
    """APA: línea superior, línea bajo el encabezado y línea final; sin líneas verticales."""
    tblPr = tabla._tbl.tblPr
    bordes = OxmlElement("w:tblBorders")
    for lado, val in (("top", "single"), ("bottom", "single"), ("left", "nil"), ("right", "nil"),
                      ("insideH", "nil"), ("insideV", "nil")):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:val"), val)
        if val == "single":
            e.set(qn("w:sz"), "8")
            e.set(qn("w:color"), "000000")
        bordes.append(e)
    tblPr.append(bordes)
    for celda in tabla.rows[0].cells:
        tcb = OxmlElement("w:tcBorders")
        b = OxmlElement("w:bottom")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "8")
        b.set(qn("w:color"), "000000")
        tcb.append(b)
        celda._tc.get_or_add_tcPr().append(tcb)


def _repetir_encabezado(fila):
    h = OxmlElement("w:tblHeader")
    h.set(qn("w:val"), "true")
    fila._tr.get_or_add_trPr().append(h)


# ---------------------------------------------------------------- referencias
def _letras(texto):
    base = texto.lower().translate(str.maketrans("áéíóúüñøçàèìòùâêîôûäëïö", "aeiouunocaeiouaeiouaeio"))
    return re.sub(r"[^a-z0-9]", "", base)


def orden_apa(ref):
    """Clave de orden APA 7: letra por letra dentro del apellido del primer autor, sin espacios ni signos
    («da Silva» = «dasilva»); «nada precede a algo» (Loft antes que Loftus); luego iniciales, año y título."""
    apellido, _, resto = ref.replace("*", "").partition(",")
    return (_letras(apellido), _letras(resto))


def referencias(cur, lista):
    """Inserta la lista de referencias (texto con *cursivas*) ordenada y con sangría francesa. Quita duplicados."""
    unicas = {orden_apa(r): r for r in lista}
    for clave in sorted(unicas):
        cur.parrafo(unicas[clave], alineacion=WD_ALIGN_PARAGRAPH.LEFT, francesa=True)


# ---------------------------------------------------------------- ecuaciones (OMML)
def _esc(texto):
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def m_t(texto):
    """Texto matemático (cursiva de ecuación)."""
    return f'<m:r><m:t xml:space="preserve">{_esc(texto)}</m:t></m:r>'


def m_texto(texto):
    """Texto normal dentro de la ecuación, p. ej. «unidades»."""
    return f'<m:r><m:rPr><m:sty m:val="p"/></m:rPr><m:t xml:space="preserve">{_esc(texto)}</m:t></m:r>'


def m_frac(num, den):
    return f"<m:f><m:num>{num}</m:num><m:den>{den}</m:den></m:f>"


def m_sub(base, sub):
    return f"<m:sSub><m:e>{base}</m:e><m:sub>{sub}</m:sub></m:sSub>"


def m_sup(base, sup):
    return f"<m:sSup><m:e>{base}</m:e><m:sup>{sup}</m:sup></m:sSup>"


def m_raiz(contenido, indice=None):
    grado = f"<m:deg>{indice}</m:deg>" if indice else '<m:radPr><m:degHide m:val="1"/></m:radPr><m:deg/>'
    return f"<m:rad>{grado}<m:e>{contenido}</m:e></m:rad>"


if __name__ == "__main__":
    import sys
    salida = sys.argv[1] if len(sys.argv) > 1 else "prueba_word_apa.docx"
    doc = abrir()
    cur = Cursor(doc, doc.paragraphs[0] if doc.paragraphs else None)
    cur.titulo("Título de nivel 1", 1)
    cur.titulo("Título de nivel 2", 2)
    cur.parrafo("Párrafo con *cursiva*, **negrita** y un 34,55 % (Autor y Coautor, 2024). ==[Marcador]==")
    cur.titulo("Título de nivel 4", 4)
    cur.tabla(1, "Ejemplo de tabla APA", ["Variable", "Valor"], [["Precio", "$120,00"], ["Costo variable", "$65,00"]],
              "Elaboración propia.")
    cur.ecuacion(m_sub(m_t("PE"), m_t("u")) + m_t("=") + m_frac(m_t("CF"), m_t("P−") + m_sub(m_t("CV"), m_t("u"))))
    cur.titulo("Referencias", 1)
    referencias(cur, ["Zeta, A. (2024). Título. *Revista*, *1*(2), 3–4. https://doi.org/10.1/x",
                      "Álvarez, B. (2023). Título. *Revista*, *5*, Artículo 12. https://doi.org/10.1/y"])
    doc.save(salida)
    print("OK", salida)
