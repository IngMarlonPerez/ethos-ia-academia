"""Generador de documentos Word (.docx) sobre la hoja membretada de la empresa.

Parte del membrete de la empresa (encabezado con logo, pie con contacto, marca de agua y numeración «Página X de Y», ver
crear_membrete.py) y reemplaza solo el cuerpo. Sin dependencias fuera de la biblioteca estándar + Pillow.

    from mdoc import MDoc, set_marca
    set_marca(primario="0A1A2E", acento="00D6FB", secundario="5B6B72")      # colores de empresa.json → marca
    d = MDoc(template="Membrete.docx")                                       # o variable de entorno MEMBRETE_DOCX
    d.title("INVENTARIO DE ACTIVOS", "Actividad 3 · Levantamiento de red")
    d.ficha([("Responsable", "Nombre Apellido"), ("Fecha", "09/10/2026")])
    d.h1("1. Objetivo"); d.p("Texto con **negrita**, ~~cursiva~~, `codigo` y [[campo por completar]] (resaltado en amarillo).")
    d.bullets(["uno", "dos"]); d.table(["A", "B"], [["1", "2"]], widths=[1, 3])
    d.image("figura.png", 16, "Figura 1. ..."); d.callout("Aviso", kind="warn"); d.signatures(("Nombre", "Cargo"), ("Nombre", "Cargo"))
    d.save("salida.docx", title="...", creator="RAZÓN SOCIAL S.A.S.")
"""
import os, re, shutil, tempfile, zipfile
from xml.sax.saxutils import escape
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.environ.get("MEMBRETE_DOCX")

NAVY, GRAY, INK, CYAN, CYAN_TXT, LINE = "0A1A2E", "5B6B72", "1F2933", "00D6FB", "00A3CC", "C9D3DC"
GREEN, AMBER, RED = "1E8E3E", "C27803", "B3261E"
TEXT_W = 9026  # ancho útil A4 con márgenes de 2,54 cm, en dxa
_PSTYLE = None  # estilo de párrafo al insertar el contenido tras una carátula ajena (ver cover.py)
_NUMID = 1      # numId de las viñetas
EMU_CM = 360000
NSDECL = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
          'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"')

def set_marca(primario=None, acento=None, secundario=None, acento_texto=None):
    """Aplica los colores de la marca (RRGGBB) a títulos, tablas y llamadas."""
    global NAVY, CYAN, GRAY, CYAN_TXT
    NAVY = (primario or NAVY).lstrip("#").upper()
    CYAN = (acento or CYAN).lstrip("#").upper()
    GRAY = (secundario or GRAY).lstrip("#").upper()
    CYAN_TXT = (acento_texto or acento_texto or CYAN_TXT).lstrip("#").upper()


STATUS_COLORS = {"Completado": GREEN, "En ejecución": AMBER, "Planificado": GRAY, "Alta": RED, "Media": AMBER,
                 "Baja": GREEN, "Crítica": RED, "Verificado": GREEN, "Por confirmar": AMBER, "Pendiente": AMBER}


def _run(text, color=INK, sz=19, b=False, i=False, code=False, hl=None):
    rpr = ""
    if code:
        rpr += '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>'
    if b:
        rpr += "<w:b/><w:bCs/>"
    if i:
        rpr += "<w:i/><w:iCs/>"
    rpr += f'<w:color w:val="{color}"/><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    if hl:
        rpr += f'<w:highlight w:val="{hl}"/>'
    return f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


_TOK = re.compile(r"(\*\*.+?\*\*|~~.+?~~|`.+?`|\[\[.+?\]\])")


def rich(text, color=INK, sz=19, b=False):
    """**negrita**, ~~cursiva~~, `código`, [[marcador por completar]] (resaltado en amarillo)."""
    out = []
    for part in _TOK.split(text):
        if not part:
            continue
        if part.startswith("**"):
            out.append(_run(part[2:-2], color, sz, b=True))
        elif part.startswith("~~"):
            out.append(_run(part[2:-2], color, sz, b=b, i=True))
        elif part.startswith("`"):
            out.append(_run(part[1:-1], "0B4F6C", sz - 1, b=b, code=True))
        elif part.startswith("[["):
            out.append(_run("[" + part[2:-2] + "]", INK, sz, b=b, hl="yellow"))
        else:
            out.append(_run(part, color, sz, b=b))
    return "".join(out)


def _p(runs, jc=None, before=0, after=0, keep=False, extra="", ind="", line=None):
    ppr = (f'<w:pStyle w:val="{_PSTYLE}"/>' if _PSTYLE else "") + ("<w:keepNext/>" if keep else "") + extra
    ppr += f'<w:spacing w:before="{before}" w:after="{after}"' + (f' w:line="{line}" w:lineRule="auto"' if line else "") + "/>" + ind
    if jc:
        ppr += f'<w:jc w:val="{jc}"/>'
    return f"<w:p><w:pPr>{ppr}</w:pPr>{runs}</w:p>"


def _borders(color=LINE, sz=4):
    return "<w:tblBorders>" + "".join(f'<w:{s} w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                                       for s in ("top", "left", "bottom", "right", "insideH", "insideV")) + "</w:tblBorders>"


def _tbl(cols, rows_xml, mar=(60, 80), borders=True):
    grid = "".join(f'<w:gridCol w:w="{c}"/>' for c in cols)
    b = _borders() if borders else "<w:tblBorders>" + "".join(f'<w:{s} w:val="nil"/>' for s in ("top", "left", "bottom", "right", "insideH", "insideV")) + "</w:tblBorders>"
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{sum(cols)}" w:type="dxa"/>{b}<w:tblLayout w:type="fixed"/>'
            f'<w:tblCellMar><w:top w:w="{mar[0]}" w:type="dxa"/><w:left w:w="{mar[1]}" w:type="dxa"/>'
            f'<w:bottom w:w="{mar[0]}" w:type="dxa"/><w:right w:w="{mar[1]}" w:type="dxa"/></w:tblCellMar>'
            f'<w:tblLook w:val="0000" w:firstRow="0" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="1" w:noVBand="1"/>'
            f'</w:tblPr><w:tblGrid>{grid}</w:tblGrid>{rows_xml}</w:tbl>')


def _tc(w, content, fill=None, va="top", left_bar=None):
    shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else ""
    bar = f'<w:tcBorders><w:left w:val="single" w:sz="24" w:space="0" w:color="{left_bar}"/></w:tcBorders>' if left_bar else ""
    return f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{bar}{shd}<w:vAlign w:val="{va}"/></w:tcPr>{content}</w:tc>'


def _tr(cells, header=False, split=False):
    return "<w:tr><w:trPr>" + ("" if split else "<w:cantSplit/>") + ("<w:tblHeader/>" if header else "") + f"</w:trPr>{cells}</w:tr>"


class MDoc:
    def __init__(self, template=None, embed=False):
        """embed=True: el contenido se insertará tras una carátula ajena (cover.insertar_tras_caratula). Los párrafos usan el
        estilo 'EmpresaNormal' para no heredar sangría de primera línea, justificado ni interlineado del documento base."""
        global _PSTYLE, _NUMID
        _PSTYLE = "EmpresaNormal" if embed else None
        _NUMID = 901 if embed else 1
        self.embed = embed
        self.template = template or TEMPLATE
        if not self.template or not os.path.exists(self.template):
            raise FileNotFoundError("Indica el membrete: MDoc(template='Membrete.docx') o la variable de entorno MEMBRETE_DOCX")
        self.body = []
        self.media = []  # (nombre_en_zip, ruta_origen, rid)
        self._pid = 200

    # ---------- bloques ----------
    def title(self, text, subtitle=None):
        self.body.append(_p(_run(text, NAVY, 30, b=True), jc="center", after=40))
        if subtitle:
            self.body.append(_p(_run(subtitle, CYAN_TXT, 20, b=True), jc="center", after=140))

    def h1(self, text):
        bdr = f'<w:pBdr><w:left w:val="single" w:sz="24" w:space="6" w:color="{CYAN}"/></w:pBdr>'
        self.body.append(_p(_run(text, NAVY, 23, b=True), before=300, after=140, keep=True, extra=bdr))

    def h2(self, text):
        self.body.append(_p(_run(text, NAVY, 20, b=True), before=200, after=80, keep=True))

    def p(self, text, jc="both", after=100, sz=19, color=INK, keep=False):
        self.body.append(_p(rich(text, color, sz), jc=jc, after=after, keep=keep, line=270))

    def small(self, text, after=80):
        self.body.append(_p(rich(text, GRAY, 16), after=after))

    def bullets(self, items, sz=19, after=50):
        for it in items:
            self.body.append(_p(rich(it, INK, sz), after=after, line=265,
                                extra=f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{_NUMID}"/></w:numPr>',
                                ind='<w:ind w:left="500" w:hanging="260"/>'))
        self.body.append(_p("", after=40))

    def spacer(self, after=120):
        self.body.append(_p("", after=after))

    def page_break(self):
        self.body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    def callout(self, text, kind="info"):
        color, fill = {"info": (CYAN, "EAF8FC"), "warn": (AMBER, "FFF6E0"), "bad": (RED, "FDECEA"), "ok": (GREEN, "E8F5EC")}[kind]
        paras = "".join(_p(rich(t, INK, 18), after=40, line=260) for t in text.split("\n"))
        self.body.append(_tbl([TEXT_W], _tr(_tc(TEXT_W, paras, fill=fill, left_bar=color)), borders=False, mar=(90, 140)))
        self.body.append(_p("", after=100))

    def ficha(self, rows, label_w=2300):
        """Cuadro 'ficha del documento' (clave: valor)."""
        cols = [label_w, TEXT_W - label_w]
        xml = "".join(_tr(_tc(cols[0], _p(_run(k, NAVY, 17, b=True)), fill="F3F7F9") + _tc(cols[1], _p(rich(v, INK, 17))))
                      for k, v in rows)
        self.body.append(_tbl(cols, xml))
        self.body.append(_p("", after=100))

    def table(self, headers, rows, widths=None, sz=16, status_col=None, bold_first=False, keep=None):
        """keep=True mantiene la tabla en una sola página; por defecto se activa si tiene 8 filas o menos."""
        keep = (len(rows) <= 8) if keep is None else keep
        n = len(headers)
        widths = widths or [1] * n
        tot = sum(widths)
        cols = [round(TEXT_W * w / tot) for w in widths]
        cols[-1] += TEXT_W - sum(cols)
        xml = _tr("".join(_tc(c, _p(_run(h, "FFFFFF", sz - 1, b=True), keep=keep), fill=NAVY, va="center") for c, h in zip(cols, headers)), header=True)
        for ri, row in enumerate(rows):
            cells = ""
            kp = keep and ri < len(rows) - 1
            for ci, (c, val) in enumerate(zip(cols, row)):
                val = str(val)
                if status_col is not None and ci == status_col:
                    cont = _p(_run(val, STATUS_COLORS.get(val, INK), sz, b=True), jc="center", keep=kp)
                else:
                    cont = "".join(_p(rich(t, INK, sz, b=(bold_first and ci == 0)), after=20, keep=kp) for t in val.split("\n"))
                cells += _tc(c, cont, fill=("F7FAFC" if ri % 2 else None))
            xml += _tr(cells)
        self.body.append(_tbl(cols, xml, mar=(55, 70)))
        self.body.append(_p("", after=100))

    def image(self, path, width_cm=15.9, caption=None):
        w, h = Image.open(path).size
        cx = int(width_cm * EMU_CM)
        cy = round(cx * h / w)
        rid = f"rIdImg{len(self.media) + 1}"
        name = f"img_{len(self.media) + 1}_{os.path.basename(path)}".replace(" ", "_")
        self.media.append((name, path, rid))
        self._pid += 1
        pic = (f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
               f'<wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="{self._pid}" name="{escape(os.path.basename(path))}" descr="{escape(caption or "")}"/>'
               f'<wp:cNvGraphicFramePr><a:graphicFrameLocks {NSDECL} noChangeAspect="1"/></wp:cNvGraphicFramePr>'
               f'<a:graphic {NSDECL}><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic>'
               f'<pic:nvPicPr><pic:cNvPr id="{self._pid}" name="{escape(name)}"/><pic:cNvPicPr><a:picLocks noChangeAspect="1"/></pic:cNvPicPr></pic:nvPicPr>'
               f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
               f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
               f'</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>')
        self.body.append(_p(pic, jc="center", before=60, after=40, keep=bool(caption)))
        if caption:
            self.body.append(_p(_run(caption, GRAY, 16, i=True), jc="center", after=140))

    # ---------- elementos de formato APA 7 ----------
    def apa_label(self, kind, n, title):
        """Rótulo APA 7 sobre una tabla o figura: «Tabla 1» en negrita y el título en cursiva, en líneas separadas."""
        self.body.append(_p(_run(f"{kind} {n}", INK, 19, b=True), keep=True, after=0, before=120))
        self.body.append(_p(_run(title, INK, 19, i=True), keep=True, after=60))

    def nota(self, text):
        """«Nota.» APA 7 bajo una tabla o figura (fuente y aclaraciones)."""
        self.body.append(_p(_run("Nota. ", INK, 16, i=True) + rich(text, INK, 16), jc="left", after=140))

    def refs(self, items):
        """Lista de referencias APA 7 con sangría francesa; `items` ya viene en orden alfabético. Cursiva con ~~…~~."""
        for it in items:
            self.body.append(_p(rich(it, INK, 18), jc="left", after=80, ind='<w:ind w:left="720" w:hanging="720"/>'))

    def signatures(self, left, right):
        """left/right = (nombre, cargo1, cargo2...)"""
        def firma(nombre, *lineas):
            bdr = f'<w:pBdr><w:top w:val="single" w:sz="8" w:space="4" w:color="{NAVY}"/></w:pBdr>'
            out = _p("", after=0) * 4
            out += _p(_run(nombre, NAVY, 19, b=True), jc="center", extra=bdr, ind='<w:ind w:left="500" w:right="500"/>', keep=True)
            for l in lineas:
                out += _p(_run(l, GRAY, 17), jc="center")
            return out
        half = TEXT_W // 2
        self.body.append(_tbl([half, TEXT_W - half], _tr(_tc(half, firma(*left)) + _tc(TEXT_W - half, firma(*right))), borders=False, mar=(0, 60)))

    # ---------- salida ----------
    def save(self, out_path, title="Documento", creator="Empresa"):
        tmp = tempfile.mkdtemp(prefix="mdoc_")
        try:
            with zipfile.ZipFile(self.template) as z:
                z.extractall(tmp)
            doc_p = os.path.join(tmp, "word", "document.xml")
            doc = open(doc_p, encoding="utf-8").read()
            start = doc.index("<w:body>") + len("<w:body>")
            sect = re.search(r"<w:sectPr>.*?</w:sectPr>", doc, re.S).group(0)
            doc = doc[:start] + "".join(self.body) + sect + "</w:body></w:document>"
            open(doc_p, "w", encoding="utf-8").write(doc)
            # imágenes
            if self.media:
                os.makedirs(os.path.join(tmp, "word", "media"), exist_ok=True)
                rels_p = os.path.join(tmp, "word", "_rels", "document.xml.rels")
                rels = open(rels_p, encoding="utf-8").read()
                add = ""
                for name, src, rid in self.media:
                    shutil.copy(src, os.path.join(tmp, "word", "media", name))
                    add += (f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                            f'Target="media/{name}"/>')
                open(rels_p, "w", encoding="utf-8").write(rels.replace("</Relationships>", add + "</Relationships>"))
            # metadatos (autoría = la empresa)
            core = os.path.join(tmp, "docProps", "core.xml")
            c = open(core, encoding="utf-8").read()
            c = re.sub(r"<dc:creator>.*?</dc:creator>", f"<dc:creator>{escape(creator)}</dc:creator>", c)
            c = re.sub(r"<cp:lastModifiedBy>.*?</cp:lastModifiedBy>", f"<cp:lastModifiedBy>{escape(creator)}</cp:lastModifiedBy>", c)
            if "<dc:title>" in c:
                c = re.sub(r"<dc:title>.*?</dc:title>", f"<dc:title>{escape(title)}</dc:title>", c)
            else:
                c = c.replace("<dc:creator>", f"<dc:title>{escape(title)}</dc:title><dc:creator>", 1)
            open(core, "w", encoding="utf-8").write(c)
            # empaquetar ([Content_Types].xml primero)
            if os.path.exists(out_path):
                os.remove(out_path)
            os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
            with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
                z.write(os.path.join(tmp, "[Content_Types].xml"), "[Content_Types].xml")
                for root, _, files in os.walk(tmp):
                    for f in files:
                        full = os.path.join(root, f)
                        arc = os.path.relpath(full, tmp).replace("\\", "/")
                        if arc != "[Content_Types].xml":
                            z.write(full, arc)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return out_path
