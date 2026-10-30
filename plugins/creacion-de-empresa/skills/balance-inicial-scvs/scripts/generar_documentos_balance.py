#!/usr/bin/env python
"""Documentos del balance inicial de una S.A.S. ecuatoriana, sobre el membrete de la empresa, listos para que firme el contador.

Genera en la carpeta de salida (un .docx por documento, 1 página cada uno):
  01_Asiento_Diario_Apertura_<CLAVE>.docx
  02_Declaracion_Capital_Suscrito_por_Pagar_<CLAVE>.docx      (modalidad "por_pagar": reemplaza al comprobante de depósito)
  02_Comprobante_Ingreso_Capital_<CLAVE>.docx                 (modalidad "pagado": recibo de ingreso del capital en efectivo)
  03_Estados_Financieros_Iniciales_<CLAVE>.docx               (para el contador y el archivo; no se sube al portal)

Uso:
    python generar_documentos_balance.py --empresa empresa.json --balance balance.json --membrete Membrete.docx --salida "Balance Inicial SCVS" [--pdf]

balance.json (ver referencias/balance_ejemplo.json):
    fecha_apertura, fecha_firma (AAAA-MM-DD), modalidad_capital ("pagado" | "por_pagar"), capital_suscrito, acciones, valor_nominal,
    expediente, tramite, inscripcion_numero, inscripcion_fecha, plazo_pago_meses, accionistas[{nombre, identificacion, acciones}],
    contador{nombre, identificacion, registro} (vacío = líneas para llenar a mano), ciiu_principal, numero_comprobante, cuenta_efectivo.

Requiere python-docx y Pillow. Con --pdf convierte con Word (Windows), igual que la skill papeleria-membretada.
"""
import argparse
import calendar
import datetime as dt
import io
import json
import os
import sys

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

# ---------------------------------------------------------------- configuración (se rellena en main) ----
NAVY, GRAY, LINE, FILL_SOFT = "0A1A2E", "5B6B72", "C9D3DA", "EEF3F6"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]
# Nombres del plan de cuentas oficial de la SCVS (estables)
PLAN = {"1": "ACTIVO", "101": "Activo corriente", "10101": "Efectivo y equivalentes de efectivo", "1010101": "Caja",
        "102": "Activos no corrientes", "2": "PASIVO", "201": "Pasivo corriente", "202": "Pasivo no corriente",
        "3": "PATRIMONIO NETO", "301": "Capital", "30101": "Capital suscrito o asignado",
        "30102": "(-) Capital suscrito no pagado, acciones en tesorería", "401": "Ingresos de actividades ordinarias",
        "501": "Costo de ventas y producción", "502": "Gastos", "707": "Ganancia (pérdida) neta del período",
        "801": "Resultado integral total del año"}
BASE = None


# ---------------------------------------------------------------- utilidades de texto ----
def fecha_larga(d):
    return f"{d.day:02d} de {MESES[d.month - 1]} de {d.year}"


def fecha_corta(d):
    return d.strftime("%d/%m/%Y")


def sumar_meses(d, n):
    m = d.month - 1 + n
    y, m = d.year + m // 12, m % 12 + 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def _letras(n):
    u = ["", "UN", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE", "DIEZ", "ONCE", "DOCE", "TRECE",
         "CATORCE", "QUINCE", "DIECISÉIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE", "VEINTE", "VEINTIÚN", "VEINTIDÓS",
         "VEINTITRÉS", "VEINTICUATRO", "VEINTICINCO", "VEINTISÉIS", "VEINTISIETE", "VEINTIOCHO", "VEINTINUEVE"]
    d = ["", "", "", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"]
    c = ["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS", "SEISCIENTOS", "SETECIENTOS",
         "OCHOCIENTOS", "NOVECIENTOS"]
    if n == 0:
        return "CERO"
    if n == 100:
        return "CIEN"
    if n >= 1_000_000:
        mm, r = divmod(n, 1_000_000)
        return ("UN MILLÓN" if mm == 1 else _letras(mm) + " MILLONES") + (" " + _letras(r) if r else "")
    if n >= 1000:
        k, r = divmod(n, 1000)
        return ("MIL" if k == 1 else _letras(k) + " MIL") + (" " + _letras(r) if r else "")
    partes = []
    if n >= 100:
        partes.append(c[n // 100])
        n %= 100
    if n >= 30:
        partes.append(d[n // 10] + (" Y " + u[n % 10] if n % 10 else ""))
    elif n > 0:
        partes.append(u[n])
    return " ".join(partes)


def monto_en_letras(x):
    ent, cts = int(x), round((x - int(x)) * 100)
    return f"{_letras(ent)} CON {cts:02d}/100 DÓLARES DE LOS ESTADOS UNIDOS DE AMÉRICA"


def usd(x):
    return f"{x:,.2f}".replace(",", "")


# ---------------------------------------------------------------- utilidades de formato Word ----
def fmt(run, size=10, bold=False, italic=False, color=None):
    color = color or NAVY
    run.font.name = "Arial"
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for att in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(att), "Arial")
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)
    return run


_AL = {"left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER, "right": WD_ALIGN_PARAGRAPH.RIGHT,
       "justify": WD_ALIGN_PARAGRAPH.JUSTIFY}


def para(container, parts, align="left", before=0, after=4, line=1.15, keep_next=False):
    p = container.add_paragraph()
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing, pf.keep_with_next = Pt(before), Pt(after), line, keep_next
    p.alignment = _AL[align]
    for text, f in ([(parts, {})] if isinstance(parts, str) else parts):
        fmt(p.add_run(text), **f)
    return p


def cell_para(cell, parts, align="left", before=1, after=1):
    p = cell.paragraphs[0] if (len(cell.paragraphs) == 1 and not cell.paragraphs[0].text) else cell.add_paragraph()
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), 1.05
    p.alignment = _AL[align]
    for text, f in ([(parts, {})] if isinstance(parts, str) else parts):
        fmt(p.add_run(text), **f)
    return p


def shade(cell, fill):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    cell._element.get_or_add_tcPr().append(shd)


def table_borders(table, color=None, size=4, inside=True):
    color = color or LINE
    borders = OxmlElement("w:tblBorders")
    visibles = ["top", "left", "bottom", "right"] + (["insideH", "insideV"] if inside else [])
    for edge in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        el = OxmlElement(f"w:{edge}")
        if edge in visibles:
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), str(size))
            el.set(qn("w:color"), color)
        else:
            el.set(qn("w:val"), "nil")
        el.set(qn("w:space"), "0")
        borders.append(el)
    table._element.tblPr.append(borders)


def fixed_widths(table, widths):
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblpr = table._element.tblPr
    tblw = tblpr.find(qn("w:tblW"))
    if tblw is None:
        tblw = OxmlElement("w:tblW")
        tblpr.append(tblw)
    tblw.set(qn("w:w"), str(sum(widths)))
    tblw.set(qn("w:type"), "dxa")
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblpr.append(layout)
    for i, gc in enumerate(table._element.tblGrid.findall(qn("w:gridCol"))):
        gc.set(qn("w:w"), str(widths[i]))
    for row in table.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for i, cell in enumerate(row.cells):
            cell.width = Cm(widths[i] / 567.0)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def top_border(paragraph, color=None, size=6):
    pbdr = OxmlElement("w:pBdr")
    top = OxmlElement("w:top")
    top.set(qn("w:val"), "single")
    top.set(qn("w:sz"), str(size))
    top.set(qn("w:space"), "4")
    top.set(qn("w:color"), color or NAVY)
    pbdr.append(top)
    paragraph._p.get_or_add_pPr().append(pbdr)


MAX_PX = {"logo_horizontal": 900, "isotipo": 320, "marca_agua": 700}
FLATTEN = {"marca_agua": 48}


def shrink_images(doc):
    """El portal de la SCVS limita el peso por página: se reducen las imágenes del membrete."""
    from PIL import Image
    for part in doc.part.package.iter_parts():
        stem = os.path.splitext(os.path.basename(str(part.partname)))[0]
        if stem not in MAX_PX:
            continue
        img = Image.open(io.BytesIO(part.blob))
        if img.width <= MAX_PX[stem]:
            continue
        img = img.resize((MAX_PX[stem], round(img.height * MAX_PX[stem] / img.width)), Image.LANCZOS)
        if stem in FLATTEN:
            fondo = Image.new("RGB", img.size, (255, 255, 255))
            fondo.paste(img, mask=img.convert("RGBA").getchannel("A"))
            img = fondo.quantize(colors=FLATTEN[stem], method=Image.Quantize.MEDIANCUT)
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        part._blob = buf.getvalue()


def base_doc():
    doc = Document(BASE)
    shrink_images(doc)
    body = doc.element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)
    return doc


def titulo(doc, texto, subtitulo=None):
    para(doc, [(texto, dict(size=14, bold=True))], align="center", before=2, after=2, keep_next=True)
    if subtitulo:
        para(doc, [(subtitulo, dict(size=9.5, color=GRAY))], align="center", after=10, keep_next=True)


def tabla_datos(doc, filas):
    t = doc.add_table(rows=len(filas), cols=4)
    for r, fila in enumerate(filas):
        for c, txt in enumerate(fila):
            es_clave = c in (0, 2)
            shade(t.rows[r].cells[c], FILL_SOFT if es_clave else "FFFFFF")
            cell_para(t.rows[r].cells[c], [(txt, dict(size=8.5, bold=es_clave, color=NAVY if es_clave else "1F2A33"))])
    table_borders(t)
    fixed_widths(t, [1900, 2700, 1600, 2826])
    para(doc, "", after=6)


def firmas(doc, izquierda, derecha):
    """Cada lado: (leyenda, [líneas]); la primera línea va en negrita. Deja espacio para la firma electrónica."""
    t = doc.add_table(rows=1, cols=2)
    table_borders(t, inside=False, size=0, color="FFFFFF")
    for idx, (leyenda, lineas) in enumerate((izquierda, derecha)):
        cell = t.rows[0].cells[idx]
        cell_para(cell, [(leyenda, dict(size=8, color=GRAY))], align="center", before=0, after=0)
        linea = cell_para(cell, "", before=30, after=2)
        linea.paragraph_format.left_indent = Cm(0.7)
        linea.paragraph_format.right_indent = Cm(0.7)
        top_border(linea)
        for i, txt in enumerate(lineas):
            cell_para(cell, [(txt, dict(size=8.5 if i else 9, bold=(i == 0), color=NAVY if i < 2 else GRAY))],
                      align="center", before=0, after=0)
    fixed_widths(t, [4513, 4513])
    for cell in t.rows[0].cells:
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    # Word exige un párrafo tras la última tabla; de 1 pt para no crear una hoja en blanco.
    fin = doc.add_paragraph()
    fin.paragraph_format.space_before = Pt(0)
    fin.paragraph_format.space_after = Pt(0)
    fin.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    fin.paragraph_format.line_spacing = Pt(1)
    rpr = OxmlElement("w:rPr")
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "2")
    rpr.append(sz)
    fin._p.get_or_add_pPr().append(rpr)


# ---------------------------------------------------------------- contexto ----
class Ctx:
    def __init__(self, empresa, b):
        self.e, self.b = empresa, b
        self.razon = empresa["razon_social"]
        self.ruc = empresa["ruc"]
        self.rep = empresa["representante"]
        dom = empresa.get("domicilio", {})
        self.domicilio = ", ".join(x for x in (dom.get("ciudad"), dom.get("provincia")) if x) + f" – {dom.get('pais', 'Ecuador')}"
        self.clave = (empresa.get("clave_archivos") or (empresa.get("nombre_comercial") or self.razon).split()[0]).upper()
        self.apertura = dt.date.fromisoformat(b["fecha_apertura"])
        self.firma = dt.date.fromisoformat(b["fecha_firma"])
        self.insc_fecha = dt.date.fromisoformat(b.get("inscripcion_fecha", b["fecha_apertura"]))
        self.pagado = b["modalidad_capital"] == "pagado"
        self.cap = float(b["capital_suscrito"])
        self.acc = b["acciones"]
        self.vn = float(b.get("valor_nominal", 1))
        self.plazo = sumar_meses(self.insc_fecha, b.get("plazo_pago_meses", 24))
        self.accionistas = b["accionistas"]
        self.ciudad_firma = empresa.get("domicilio", {}).get("ciudad", "")
        cont = b.get("contador", {})
        self.f_gerente = [self.rep["nombre"].upper(), f"{self.rep.get('cargo', 'Gerente General')} – Representante Legal",
                          f"C.C. {self.rep.get('identificacion', '__________')}", self.razon]
        self.f_contador = [(cont.get("nombre") or "CONTADOR(A)").upper() if cont.get("nombre") else "CONTADOR(A)",
                           cont.get("nombre") and "Contador(a)" or "Nombre: ______________________________",
                           f"C.C. / RUC: {cont['identificacion']}" if cont.get("identificacion") else "C.C. / RUC: __________________________",
                           f"Registro profesional N.º: {cont['registro']}" if cont.get("registro") else "Registro profesional N.º: _______________"]
        self.datos = [("Razón social", self.razon, "RUC", self.ruc),
                      ("Expediente SCVS", b.get("expediente", ""), "Trámite SCVS", b.get("tramite", "")),
                      ("Inscripción societaria", f"N.º {b.get('inscripcion_numero', '')} · {fecha_corta(self.insc_fecha)}",
                       "Domicilio", self.domicilio),
                      ("Representante legal", f"{self.rep['nombre']} ({self.rep.get('cargo', 'Gerente General')})", "C.C.",
                       self.rep.get("identificacion", ""))]
        nombres = [a["nombre"] for a in self.accionistas]
        self.accionistas_txt = nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " y " + nombres[-1]


# ---------------------------------------------------------------- 01 asiento ----
def asiento(c, salida):
    doc = base_doc()
    titulo(doc, "ASIENTO DE DIARIO DE APERTURA N.º 001", "Constitución de la compañía y suscripción del capital social")
    pagado = usd(c.cap) if c.pagado else "0.00"
    tabla_datos(doc, c.datos + [
        ("Capital suscrito", f"USD {usd(c.cap)} ({c.acc} acciones de USD {usd(c.vn)})", "Capital pagado",
         f"USD {usd(c.cap)}" if c.pagado else f"USD 0.00 (por pagar USD {usd(c.cap)})"),
        ("Fecha del asiento", fecha_larga(c.apertura), "Marco contable", "NIIF para las PYMES · Plan de Cuentas SCVS")])
    cuenta_ef = c.b.get("cuenta_efectivo", "1010101")
    if c.pagado:
        filas = [(fecha_corta(c.apertura), cuenta_ef, "Caja" if cuenta_ef == "1010101" else "Efectivo", usd(c.cap), ""),
                 ("", "30101", "Capital suscrito o asignado", "", usd(c.cap))]
        glosa = (f"Por la constitución de {c.razon}, inscrita en el Registro de Sociedades de la Superintendencia de "
                 f"Compañías, Valores y Seguros con el N.º {c.b.get('inscripcion_numero', '')} el {fecha_larga(c.insc_fecha)}, y la "
                 f"suscripción y pago en numerario de su capital social de USD {usd(c.cap)}, dividido en {c.acc} acciones "
                 f"ordinarias y nominativas de USD {usd(c.vn)} cada una, suscritas por {c.accionistas_txt}.")
        nota = None
    else:
        filas = [(fecha_corta(c.apertura), "30102", "(-) Capital suscrito no pagado, acciones en tesorería", usd(c.cap), ""),
                 ("", "30101", "Capital suscrito o asignado", "", usd(c.cap))]
        glosa = (f"Por la constitución de {c.razon}, inscrita en el Registro de Sociedades de la Superintendencia de "
                 f"Compañías, Valores y Seguros con el N.º {c.b.get('inscripcion_numero', '')} el {fecha_larga(c.insc_fecha)}, y la "
                 f"suscripción de su capital social de USD {usd(c.cap)}, dividido en {c.acc} acciones ordinarias y nominativas "
                 f"de USD {usd(c.vn)} cada una, suscritas por {c.accionistas_txt} (cláusula cuarta del acto constitutivo). "
                 f"A la fecha, el capital se encuentra íntegramente pendiente de pago y será depositado en la cuenta bancaria de "
                 f"la compañía hasta el {fecha_larga(c.plazo)} (cláusula quinta del acto constitutivo).")
        nota = ("el capital suscrito pendiente de pago se presenta como deducción del patrimonio y no como activo, conforme a "
                "la NIIF para las PYMES, Sección 22, párrafo 22.7 a).")
    widths = [1250, 950, 4226, 1300, 1300]
    t = doc.add_table(rows=len(filas) + 2, cols=5)
    for i, h in enumerate(["Fecha", "Código", "Cuenta", "Debe (USD)", "Haber (USD)"]):
        shade(t.rows[0].cells[i], NAVY)
        cell_para(t.rows[0].cells[i], [(h, dict(size=8.5, bold=True, color="FFFFFF"))], align="center" if i != 2 else "left")
    for r, fila in enumerate(filas, start=1):
        for i, txt in enumerate(fila):
            cell_para(t.rows[r].cells[i], [(txt, dict(size=9))], align="right" if i >= 3 else ("center" if i < 2 else "left"),
                      before=3, after=3)
    tot = t.rows[-1].cells
    for i in range(5):
        shade(tot[i], FILL_SOFT)
    cell_para(tot[2], [("TOTALES", dict(size=9, bold=True))], align="right", before=3, after=3)
    for i in (3, 4):
        cell_para(tot[i], [(usd(c.cap), dict(size=9, bold=True))], align="right", before=3, after=3)
    table_borders(t)
    fixed_widths(t, widths)
    para(doc, "", after=4)
    para(doc, [("Glosa: ", dict(size=9.5, bold=True)), (glosa, dict(size=9.5))], align="justify", after=6)
    if nota:
        para(doc, [("Nota: ", dict(size=9, bold=True, color=GRAY)), (nota, dict(size=9, color=GRAY))], align="justify", after=6)
    para(doc, [(f"Los suscritos declaran que el presente asiento refleja fielmente el registro contable de apertura de "
                f"{c.razon} y que la información consignada es veraz.", dict(size=9.5))], align="justify", after=14)
    firmas(doc, ("Aprobado por", c.f_gerente), ("Elaborado por", c.f_contador))
    doc.save(salida)


# ---------------------------------------------------------------- 02 declaración (capital por pagar) ----
def declaracion(c, salida):
    doc = base_doc()
    S = 9.5
    para(doc, [(f"{c.ciudad_firma}, {fecha_larga(c.firma)}", dict(size=S))], align="right", after=6)
    titulo(doc, "DECLARACIÓN DE CAPITAL SUSCRITO PENDIENTE DE PAGO",
           "Anexo del balance inicial, en lugar del comprobante de depósito del capital")
    tabla_datos(doc, c.datos[:3])
    para(doc, [("Señores", dict(size=S))], after=0, line=1.0)
    para(doc, [("SUPERINTENDENCIA DE COMPAÑÍAS, VALORES Y SEGUROS", dict(size=S, bold=True))], after=0, line=1.0)
    para(doc, [("Presente.-", dict(size=S))], after=5, line=1.0)
    para(doc, [("Yo, ", dict(size=S)), (c.rep["nombre"].upper(), dict(size=S, bold=True)),
               (f", con cédula de ciudadanía N.º {c.rep.get('identificacion', '__________')}, en mi calidad de "
                f"{c.rep.get('cargo', 'Gerente General')} y representante legal de ", dict(size=S)),
               (c.razon, dict(size=S, bold=True)),
               (f", RUC {c.ruc}, en relación con el anexo «Comprobante de depósito del capital» del balance inicial que se "
                "presenta en el Portal de Trámites de la Superintendencia de Compañías, Valores y Seguros, declaro bajo "
                "juramento:", dict(size=S))], align="justify", after=4)
    puntos = [
        f"Que, de conformidad con la cláusula cuarta (cuadro de suscripción y pago del capital social) del acto constitutivo de "
        f"la compañía, inscrito en el Registro de Sociedades con el N.º {c.b.get('inscripcion_numero', '')} el "
        f"{fecha_larga(c.insc_fecha)}, el capital suscrito asciende a {monto_en_letras(c.cap)} (USD {usd(c.cap)}), dividido en "
        f"{c.acc} acciones ordinarias y nominativas de USD {usd(c.vn)} cada una, suscritas por {c.accionistas_txt}, con capital "
        f"pagado en numerario de USD 0.00 y capital por pagar de USD {usd(c.cap)}.",
        f"Que la cláusula quinta del acto constitutivo establece que el capital por pagar será depositado en la cuenta que la "
        f"compañía abra en una institución bancaria, en un plazo máximo de {c.b.get('plazo_pago_meses', 24)} meses contado a partir "
        f"de la fecha de inscripción, es decir, hasta el {fecha_larga(c.plazo)}, en concordancia con el artículo innumerado "
        f"«Aportes en numerario» de la sección de las Sociedades por Acciones Simplificadas de la Ley de Compañías.",
        f"Que, en consecuencia, a la fecha del Estado de Situación Financiera Inicial ({fecha_larga(c.apertura)}) no se ha "
        f"efectuado depósito alguno del capital, por lo que no existe comprobante bancario que adjuntar. La presente declaración "
        f"se presenta en su lugar.",
        f"Que el capital consta registrado contablemente en la cuenta 30101 «Capital suscrito o asignado» por USD {usd(c.cap)} y el "
        f"saldo pendiente de pago en la cuenta 30102 «(-) Capital suscrito no pagado, acciones en tesorería» por USD "
        f"({usd(c.cap)}), presentado como deducción del patrimonio conforme a la NIIF para las PYMES, Sección 22, párrafo 22.7 a). "
        f"Por ello, a la fecha de constitución el total del activo, del pasivo y del patrimonio es de USD 0.00.",
        "Que la compañía presentará el comprobante de depósito y el asiento de diario de la integración del capital una vez "
        "efectuado el depósito y, a más tardar, dentro de los treinta días posteriores al vencimiento del plazo para el pago del "
        "capital suscrito, conforme al artículo 54 del Reglamento de las Sociedades por Acciones Simplificadas (Resolución "
        "N.º SCVS-INC-DNCDN-2020-0015)."]
    for i, txt in enumerate(puntos, start=1):
        p = para(doc, [(f"{i}.  ", dict(size=S, bold=True)), (txt, dict(size=S))], align="justify", after=2, line=1.05)
        p.paragraph_format.left_indent = Cm(0.6)
        p.paragraph_format.first_line_indent = Cm(-0.6)
    para(doc, [("Declaro que la información contenida en este documento es veraz y asumo la responsabilidad por su contenido, "
                "en los términos de la Ley Orgánica de Optimización y Eficiencia de Trámites Administrativos.", dict(size=S))],
         align="justify", before=2, after=4, line=1.05, keep_next=True)
    firmas(doc, ("Declarante", c.f_gerente), ("Certifica el registro contable del numeral 4", c.f_contador))
    doc.save(salida)


# ---------------------------------------------------------------- 02 comprobante de ingreso (capital pagado) ----
def comprobante(c, salida):
    doc = base_doc()
    num = c.b.get("numero_comprobante", "000000001")
    titulo(doc, f"COMPROBANTE DE INGRESO N.º {num}", "Aporte en numerario para el pago del capital suscrito")
    unico = len(c.accionistas) == 1
    a0 = c.accionistas[0]
    tabla_datos(doc, [
        ("Fecha de emisión", fecha_larga(c.apertura), "N.º comprobante", num),
        ("Recibido de", a0["nombre"] if unico else "Accionistas detallados", "C.C.", a0.get("identificacion", "") if unico else "—"),
        ("Calidad", "Accionista fundador" + (f" ({a0['acciones']} acciones)" if unico else "es"), "Forma de pago", "Efectivo"),
        ("Compañía", c.razon, "RUC", c.ruc)])
    para(doc, [("La suma de: ", dict(size=10, bold=True)), (f"{monto_en_letras(c.cap)} (USD {usd(c.cap)})", dict(size=10))], after=8)
    filas = [(str(i), f"Pago del capital social suscrito – {a['acciones']} acciones ordinarias y nominativas de USD {usd(c.vn)} c/u"
                      + ("" if unico else f" – {a['nombre']}"), usd(a["acciones"] * c.vn)) for i, a in enumerate(c.accionistas, 1)]
    t = doc.add_table(rows=len(filas) + 2, cols=3)
    for i, h in enumerate(["N.º", "Detalle", "V/. Total (USD)"]):
        shade(t.rows[0].cells[i], NAVY)
        cell_para(t.rows[0].cells[i], [(h, dict(size=8.5, bold=True, color="FFFFFF"))], align="left" if i == 1 else "center")
    for r, f in enumerate(filas, start=1):
        for i, txt in enumerate(f):
            cell_para(t.rows[r].cells[i], [(txt, dict(size=9))], align=["center", "left", "right"][i], before=3, after=3)
    tot = t.rows[-1].cells
    for i in range(3):
        shade(tot[i], FILL_SOFT)
    cell_para(tot[1], [("SUMA TOTAL", dict(size=9, bold=True))], align="right", before=3, after=3)
    cell_para(tot[2], [(usd(c.cap), dict(size=9, bold=True))], align="right", before=3, after=3)
    table_borders(t)
    fixed_widths(t, [800, 6226, 2000])
    para(doc, "", after=4)
    para(doc, [("Registro contable: ", dict(size=9.5, bold=True)),
               (f"Debe {c.b.get('cuenta_efectivo', '1010101')} Caja USD {usd(c.cap)} / Haber 30101 Capital suscrito o asignado "
                f"USD {usd(c.cap)} (Asiento de diario de apertura N.º 001).", dict(size=9.5))], align="justify", after=6)
    para(doc, [(f"Los suscritos certifican que la compañía recibió el valor detallado como pago íntegro del capital suscrito, "
                f"conforme a las cláusulas cuarta y quinta del acto constitutivo de {c.razon}, inscrito en el Registro de "
                f"Sociedades de la Superintendencia de Compañías, Valores y Seguros con el N.º {c.b.get('inscripcion_numero', '')} "
                f"el {fecha_larga(c.insc_fecha)}.", dict(size=9.5))], align="justify", after=16)
    izq = ([a0["nombre"].upper(), "Accionista fundador", f"C.C. {a0.get('identificacion', '__________')}", c.razon]
           if unico else c.f_gerente)
    firmas(doc, ("Entregué conforme", izq), ("Elaborado por", c.f_contador))
    doc.save(salida)


# ---------------------------------------------------------------- 03 estados financieros ----
def estados(c, salida):
    doc = base_doc()
    titulo(doc, "ESTADOS FINANCIEROS INICIALES",
           f"Al {fecha_larga(c.apertura)} (fecha de constitución) · En dólares de los Estados Unidos de América")
    tabla_datos(doc, c.datos[:2])

    def estado(titulo_estado, filas):
        para(doc, [(titulo_estado, dict(size=10, bold=True))], before=0, after=3, keep_next=True)
        t = doc.add_table(rows=len(filas) + 1, cols=3)
        for i, h in enumerate(["Código", "Cuenta", "USD"]):
            shade(t.rows[0].cells[i], NAVY)
            cell_para(t.rows[0].cells[i], [(h, dict(size=8.5, bold=True, color="FFFFFF"))],
                      align="left" if i == 1 else ("center" if i == 0 else "right"))
        for r, (codigo, cuenta, valor, estilo) in enumerate(filas, start=1):
            total = estilo == "total"
            if total:
                for i in range(3):
                    shade(t.rows[r].cells[i], FILL_SOFT)
            cell_para(t.rows[r].cells[0], [(codigo, dict(size=8, color=GRAY))], align="center", before=0, after=0)
            cell_para(t.rows[r].cells[1], [(cuenta, dict(size=8.5, bold=total or estilo == "grupo"))], before=0, after=0)
            cell_para(t.rows[r].cells[2], [(valor, dict(size=8.5, bold=total))], align="right", before=0, after=0)
        table_borders(t)
        fixed_widths(t, [1300, 6026, 1700])
        para(doc, "", after=2, line=1.0)

    cap, z = usd(c.cap), "0.00"
    if c.pagado:
        activo = [("101", PLAN["101"], cap, ""), ("10101", PLAN["10101"], cap, ""), ("1010101", PLAN["1010101"], cap, ""),
                  ("102", PLAN["102"], z, ""), ("", "TOTAL ACTIVO", cap, "total")]
        patrimonio = [("30101", PLAN["30101"], cap, ""), ("301", PLAN["301"], cap, ""), ("", "TOTAL PATRIMONIO NETO", cap, "total"),
                      ("", "TOTAL PASIVO + PATRIMONIO NETO", cap, "total")]
    else:
        activo = [("101", PLAN["101"], z, ""), ("10101", PLAN["10101"], z, ""), ("102", PLAN["102"], z, ""),
                  ("", "TOTAL ACTIVO", z, "total")]
        patrimonio = [("30101", PLAN["30101"], cap, ""), ("30102", PLAN["30102"], f"({cap})", ""), ("301", PLAN["301"], z, ""),
                      ("", "TOTAL PATRIMONIO NETO", z, "total"), ("", "TOTAL PASIVO + PATRIMONIO NETO", z, "total")]
    estado("ESTADO DE SITUACIÓN FINANCIERA INICIAL",
           [("1", PLAN["1"], "", "grupo")] + activo + [("2", PLAN["2"], "", "grupo"), ("201", PLAN["201"], z, ""),
           ("202", PLAN["202"], z, ""), ("", "TOTAL PASIVO", z, "total"), ("3", PLAN["3"], "", "grupo")] + patrimonio)
    estado("ESTADO DE RESULTADO INTEGRAL", [(k, PLAN[k], z, "total" if k == "801" else "") for k in ("401", "501", "502", "707", "801")])

    notas = [f"Información general: sociedad por acciones simplificada domiciliada en {c.ciudad_firma}, inscrita en el Registro de "
             f"Sociedades de la SCVS con el N.º {c.b.get('inscripcion_numero', '')} el {fecha_corta(c.insc_fecha)}."
             + (f" Actividad principal: {c.b['ciiu_principal']}." if c.b.get("ciiu_principal") else ""),
             "Bases de preparación: NIIF para las PYMES, en dólares de los Estados Unidos de América, con los códigos del Plan "
             "de Cuentas de la SCVS.",
             (f"Capital: suscrito y pagado USD {cap} ({c.acc} acciones de USD {usd(c.vn)}), aportado en numerario." if c.pagado else
              f"Capital: suscrito USD {cap} ({c.acc} acciones de USD {usd(c.vn)}), pagado USD 0.00. El saldo por pagar se presenta "
              f"como deducción del patrimonio (NIIF para las PYMES 22.7 a) y se paga hasta el {fecha_corta(c.plazo)} (cláusula quinta)."),
             "Resultados: la compañía no registró operaciones a la fecha de constitución."]
    para(doc, [("Notas", dict(size=9.5, bold=True))], before=0, after=2, keep_next=True)
    for i, txt in enumerate(notas, start=1):
        p = para(doc, [(f"{i}.  ", dict(size=8.5, bold=True)), (txt, dict(size=8.5))], align="justify", after=2, line=1.05,
                 keep_next=(i == len(notas)))
        p.paragraph_format.left_indent = Cm(0.6)
        p.paragraph_format.first_line_indent = Cm(-0.6)
    firmas(doc, ("Representante legal", c.f_gerente), ("Contador(a)", c.f_contador))
    doc.save(salida)


def main():
    global BASE, NAVY, GRAY
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--empresa", required=True)
    ap.add_argument("--balance", required=True)
    ap.add_argument("--membrete", required=True, help="Membrete .docx de la empresa (ver skill papeleria-membretada)")
    ap.add_argument("--salida", required=True)
    ap.add_argument("--pdf", action="store_true", help="exporta los .docx a PDF con Word (Windows)")
    a = ap.parse_args()
    empresa = json.load(open(a.empresa, encoding="utf-8"))
    b = json.load(open(a.balance, encoding="utf-8"))
    if b["modalidad_capital"] not in ("pagado", "por_pagar"):
        sys.exit('modalidad_capital debe ser "pagado" o "por_pagar"')
    suma = sum(x["acciones"] for x in b["accionistas"])
    if suma != b["acciones"]:
        sys.exit(f"Las acciones de los accionistas ({suma}) no suman {b['acciones']}")
    if abs(b["acciones"] * b.get("valor_nominal", 1) - b["capital_suscrito"]) > 0.005:
        sys.exit("acciones × valor_nominal no es igual al capital_suscrito")
    BASE = os.path.abspath(a.membrete)
    marca = empresa.get("marca", {})
    NAVY = (marca.get("color_primario") or NAVY).lstrip("#").upper()
    GRAY = (marca.get("color_secundario") or GRAY).lstrip("#").upper()
    os.makedirs(a.salida, exist_ok=True)
    c = Ctx(empresa, b)
    k = c.clave
    archivos = [(asiento, f"01_Asiento_Diario_Apertura_{k}.docx"),
                (comprobante if c.pagado else declaracion,
                 f"02_Comprobante_Ingreso_Capital_{k}.docx" if c.pagado else f"02_Declaracion_Capital_Suscrito_por_Pagar_{k}.docx"),
                (estados, f"03_Estados_Financieros_Iniciales_{k}.docx")]
    creados = []
    for fn, nombre in archivos:
        ruta = os.path.join(a.salida, nombre)
        fn(c, ruta)
        creados.append(ruta)
        print("OK", ruta)
    if a.pdf:
        aqui = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, os.path.join(aqui, "..", "..", "papeleria-membretada", "scripts"))
        from pdf_word import convertir
        for r in creados:
            print("PDF", convertir(r))


if __name__ == "__main__":
    main()
