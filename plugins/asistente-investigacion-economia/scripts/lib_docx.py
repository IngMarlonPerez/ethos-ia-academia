# -*- coding: utf-8 -*-
"""Librería para armar un trabajo teórico UNEMI en Word sobre la plantilla/carátula del grupo (sin tocarla).
Texto con cursivas (*...*), ecuaciones nativas ($$...$$ con mini-LaTeX de mathlib), tablas, figuras PNG, notas APA y referencias.

Uso típico (ver ejemplo_hpe/05_construir_documento.py):
    from lib_docx import *
    set_figuras(r".../03_Graficos")
    cuerpo = P("Texto con *cursiva* y $$c+v+p$$") + CAPT("Tabla 1","Título") + TABLE(filas, anchos) + NOTE("Elaboración propia.")
    ensamblar(PLANTILLA, SALIDA, {"PARAID_1": lambda xml: xml + cuerpo, "PARAID_2": ""})
Reglas aprendidas: escribir los .py con la herramienta Write (los heredocs de bash corrompen \\n y \\), usar python -I y PYTHONUTF8=1.
"""
import os, re, struct, sys, zipfile
from xml.sax.saxutils import escape
from lxml import etree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathlib import omath, tr  # noqa: E402

_FIGS = ["."]
IMGS = []  # (rId, archivo)


def set_figuras(carpeta):
    _FIGS[0] = carpeta
    IMGS.clear()


def rich(text, sz=24, b=False):
    """Texto → runs de Word. *cursiva*, $$ecuación$$."""
    out = ""
    for k, part in enumerate(re.split(r"\$\$(.+?)\$\$", text)):
        if k % 2:
            out += omath(part)
        elif part:
            for j, seg in enumerate(re.split(r"\*(.+?)\*", part)):
                if seg:
                    out += tr(seg, b, j % 2 == 1, sz)
    return out


def P(t, line=276):
    return ('<w:p><w:pPr><w:spacing w:before="0" w:after="80" w:line="%d" w:lineRule="auto"/><w:ind w:firstLine="567"/><w:jc w:val="both"/></w:pPr>%s</w:p>'
            % (line, rich(t)))


def _h(t, color, sz, lvl, before=200, after=60):
    rp = '<w:rPr><w:b/><w:bCs/><w:color w:val="%s"/><w:sz w:val="%d"/><w:szCs w:val="%d"/><w:lang w:val="es-EC"/></w:rPr>' % (color, sz, sz)
    return ('<w:p><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="%d" w:after="%d" w:line="240" w:lineRule="auto"/><w:outlineLvl w:val="%d"/>%s</w:pPr><w:r>%s<w:t>%s</w:t></w:r></w:p>'
            % (before, after, lvl, rp, rp, escape(t)))


def H1(t): return _h(t, "1A3A7A", 30, 1, 200, 80)       # igual a «Introducción» de la plantilla UNEMI
def SEC(t): return _h(t, "2D5AA0", 26, 2)                 # sección numerada del desarrollo


def BY(t):
    return '<w:p><w:pPr><w:keepNext/><w:spacing w:before="0" w:after="60" w:line="240" w:lineRule="auto"/></w:pPr>%s</w:p>' % tr(t, False, True, 19)


def H2(t):
    return '<w:p><w:pPr><w:keepNext/><w:spacing w:before="100" w:after="40" w:line="260" w:lineRule="auto"/></w:pPr>%s</w:p>' % tr(t, True, False, 24)


def EQ(t):
    return ('<w:p><w:pPr><w:keepLines/><w:spacing w:before="20" w:after="20" w:line="276" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>'
            '<m:oMathPara><m:oMathParaPr><m:jc m:val="center"/></m:oMathParaPr>%s</m:oMathPara></w:p>' % omath(t))


def CAPT(label, title):
    """Rótulo APA: «Tabla 1» en negrita y título en cursiva, encima de la tabla o figura."""
    return ('<w:p><w:pPr><w:keepNext/><w:spacing w:before="100" w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>%s</w:p>'
            '<w:p><w:pPr><w:keepNext/><w:spacing w:before="0" w:after="40" w:line="240" w:lineRule="auto"/></w:pPr>%s</w:p>'
            % (tr(label, True, False, 22), tr(title, False, True, 22)))


def NOTE(t):
    return ('<w:p><w:pPr><w:spacing w:before="20" w:after="100" w:line="240" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr>%s%s</w:p>'
            % (tr("Nota. ", False, True, 18), rich(t, 18)))


def PB():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def REF(t):
    return ('<w:p><w:pPr><w:spacing w:before="0" w:after="60" w:line="259" w:lineRule="auto"/><w:ind w:left="567" w:hanging="567"/><w:jc w:val="left"/></w:pPr>%s</w:p>'
            % rich(t, 22))


def TABLE(rows, widths, sz=18, head_fill="DCE6F2", first_col_bold=True):
    """widths en twips; el área útil de la plantilla UNEMI mide ~8650."""
    b = "".join('<w:%s w:val="single" w:sz="4" w:space="0" w:color="1A3A7A"/>' % x for x in ("top", "left", "bottom", "right", "insideH", "insideV"))
    x = ('<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>%s</w:tblBorders><w:tblLayout w:type="fixed"/>'
         '<w:tblCellMar><w:left w:w="60" w:type="dxa"/><w:right w:w="60" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>%s</w:tblGrid>'
         % (sum(widths), b, "".join('<w:gridCol w:w="%d"/>' % w for w in widths)))
    for r, row in enumerate(rows):
        hd = r == 0
        x += "<w:tr>" + ('<w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>' if hd else "<w:trPr><w:cantSplit/></w:trPr>")
        for c, (w, cell) in enumerate(zip(widths, row)):
            shade = '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % head_fill if hd else ('<w:shd w:val="clear" w:color="auto" w:fill="F4F7FB"/>' if c == 0 else "")
            x += ('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s<w:vAlign w:val="center"/></w:tcPr><w:p><w:pPr><w:spacing w:before="20" w:after="20" w:line="228" w:lineRule="auto"/>'
                  '<w:ind w:firstLine="0"/><w:jc w:val="%s"/></w:pPr>%s</w:p></w:tc>' % (w, shade, "center" if hd else "left", rich(cell, sz, hd or (first_col_bold and c == 0))))
        x += "</w:tr>"
    return x + "</w:tbl>"


def IMG(fname, width_cm):
    """Inserta un PNG de la carpeta de figuras (alto proporcional). Registra la relación para ensamblar()."""
    with open(os.path.join(_FIGS[0], fname), "rb") as f:
        h = f.read(24)
    w, hgt = struct.unpack(">II", h[16:24])
    cx = int(width_cm * 360000); cy = int(cx * hgt / w)
    n = len(IMGS) + 1; rid = "rIdHPE%d" % n
    IMGS.append((rid, fname))
    return ('<w:p><w:pPr><w:keepNext/><w:spacing w:before="20" w:after="20" w:line="240" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
            '<wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" distT="0" distB="0" distL="0" distR="0">'
            '<wp:extent cx="%d" cy="%d"/><wp:docPr id="%d" name="Figura %d" descr="%s"/><wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="%d" name="%s"/><pic:cNvPicPr/></pic:nvPicPr>'
            '<pic:blipFill><a:blip xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>' % (cx, cy, 900 + n, n, escape(fname), 900 + n, escape(fname), rid, cx, cy))


def sub_para(doc, para_id, repl):
    """Sustituye el párrafo de la plantilla con w14:paraId=para_id por repl(xml_original) (str o función)."""
    m = re.search(r'<w:p [^>]*w14:paraId="%s".*?</w:p>' % para_id, doc, re.S)
    assert m, "paraId no encontrado: " + para_id
    nuevo = repl(m.group(0)) if callable(repl) else repl
    return doc[:m.start()] + nuevo + doc[m.end():]


def listar_parrafos(plantilla):
    """Ayuda para elegir los paraId a sustituir: imprime id y texto de cada párrafo de la plantilla."""
    doc = zipfile.ZipFile(plantilla).read("word/document.xml").decode("utf8")
    for m in re.finditer(r'<w:p [^>]*w14:paraId="([0-9A-F]+)".*?</w:p>', doc, re.S):
        t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", m.group(0)))
        print(m.group(1), "|", t[:70], "| [salto de página]" if 'w:type="page"' in m.group(0) else "")


def ensamblar(plantilla, salida, sustituciones, margen_inferior_ultima_seccion=True):
    """Copia la plantilla (sin modificarla) a salida con las sustituciones de párrafos y las figuras registradas por IMG()."""
    z = zipfile.ZipFile(plantilla)
    doc = z.read("word/document.xml").decode("utf8")
    for pid, rep in sustituciones.items():
        doc = sub_para(doc, pid, rep)
    if margen_inferior_ultima_seccion:  # la plantilla UNEMI trae margen inferior de 280 twips: se vuelve legible
        doc = re.sub(r'(<w:pgMar w:top="1320" w:right="\d+" w:bottom=")280(")', r"\g<1>1300\2", doc)
    etree.fromstring(doc.encode("utf8"))
    rels = z.read("word/_rels/document.xml.rels").decode("utf8")
    add = "".join('<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/hpe_%s"/>' % (rid, fn) for rid, fn in IMGS)
    rels = rels.replace("</Relationships>", add + "</Relationships>")
    tmp = salida + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in z.infolist():
            if it.filename == "word/document.xml":
                zo.writestr(it, doc.encode("utf8"))
            elif it.filename == "word/_rels/document.xml.rels":
                zo.writestr(it, rels.encode("utf8"))
            else:
                zo.writestr(it, z.read(it.filename))
        for rid, fn in IMGS:
            zo.write(os.path.join(_FIGS[0], fn), "word/media/hpe_" + fn)
    os.replace(tmp, salida)
    return salida
