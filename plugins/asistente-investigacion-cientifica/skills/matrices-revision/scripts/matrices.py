"""Genera el Excel con las 4 matrices de una revisión sistemática (método PRISMA 2020).

Cada búsqueda del proyecto tiene un archivo de datos (copia de plantilla_datos.py) que arma el
diccionario d y llama a construir(d, salida). Hojas que produce:

  Guia                    cómo leer el libro
  M1_Busqueda_Registro    estrategia (base, ecuación, filtros, fecha, método, conteos) + registro bruto
  M2a_Cribado_titulo      decisión y criterio por título (todos los registros únicos)
  M2b_Cribado_resumen     decisión y criterio por resumen
  M2c_Elegibilidad        lectura del texto completo con puntaje 0–2 por pregunta
  M3_Extraccion           autor y año, objetivo, muestra, método, hallazgos, limitaciones, conclusiones,
                          aporte por pregunta y evidencia textual con página
  M4_Tematica             categorías o variables × autores que coinciden / discrepan, vacíos y síntesis
  M4b_Cruce               matriz cruzada autores × preguntas (puntajes)
  PRISMA_2020             números del flujo + diagrama PNG
  Referencias_APA         artículos incluidos con su referencia APA 7

Compatible con los datos anteriores (matriz_revision.py): los campos nuevos son opcionales.
"""
import os
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagrama_prisma import conteos_desde_datos, dibujar  # noqa: E402

AZUL = "1B3247"
NARANJA = "F28C28"
FILL_HEAD = PatternFill("solid", fgColor=AZUL)
FILL_DEC = {
    "Incluido": PatternFill("solid", fgColor="C6EFCE"),
    "Pasa": PatternFill("solid", fgColor="E2EFDA"),
    "Elegible": PatternFill("solid", fgColor="FFF2CC"),
    "No recuperado": PatternFill("solid", fgColor="F8CBAD"),
    "Excluido": PatternFill("solid", fgColor="EDEDED"),
}
FILL_PUNTAJE = {2: PatternFill("solid", fgColor="A9D08E"), 1: PatternFill("solid", fgColor="FFE699"),
                0: PatternFill("solid", fgColor="F2F2F2")}
BORDE = Border(*(Side(style="thin", color="B7B7B7"),) * 4)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTRO = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _relleno_decision(texto):
    for clave, fill in FILL_DEC.items():
        if str(texto).startswith(clave):
            return fill
    return None


def _tabla(ws, fila, encabezados, filas, anchos, col_decision=None):
    for c, h in enumerate(encabezados, 1):
        celda = ws.cell(row=fila, column=c, value=h)
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = FILL_HEAD
        celda.alignment = CENTRO
        celda.border = BORDE
    for r, datos in enumerate(filas, fila + 1):
        for c, v in enumerate(datos, 1):
            celda = ws.cell(row=r, column=c, value=v)
            celda.alignment = WRAP
            celda.border = BORDE
        if col_decision is not None:
            fill = _relleno_decision(datos[col_decision])
            if fill:
                for c in range(1, len(encabezados) + 1):
                    ws.cell(row=r, column=c).fill = fill
    for c, ancho in enumerate(anchos, 1):
        ws.column_dimensions[get_column_letter(c)].width = ancho
    ultima = fila + len(filas)
    if filas:
        ws.auto_filter.ref = f"A{fila}:{get_column_letter(len(encabezados))}{ultima}"
    ws.freeze_panes = ws.cell(row=fila + 1, column=1)
    return ultima


def _titulo(ws, texto, subtitulo=None):
    ws["A1"] = texto
    ws["A1"].font = Font(bold=True, size=14, color=AZUL)
    if subtitulo:
        ws["A2"] = subtitulo
        ws["A2"].font = Font(italic=True, color="595959")


def _bloque(ws, fila, etiqueta, pares, ancho_merge=6):
    ws.cell(row=fila, column=1, value=etiqueta).font = Font(bold=True, color=AZUL)
    fila += 1
    for k, texto in pares:
        ws.cell(row=fila, column=1, value=k).font = Font(bold=True)
        ws.cell(row=fila, column=2, value=texto).alignment = WRAP
        ws.merge_cells(start_row=fila, start_column=2, end_row=fila, end_column=ancho_merge)
        ws.row_dimensions[fila].height = max(18, min(90, 15 * (1 + len(str(texto)) // 110)))
        fila += 1
    return fila + 1


# --------------------------------------------------------------------------- hojas
def hoja_guia(wb, d):
    ws = wb.active
    ws.title = "Guia"
    _titulo(ws, f"Matrices de revisión sistemática – {d['actividad']}",
            f"Fecha: {d['fecha']} · Elaborado por: {d['autora']} · Método PRISMA 2020")
    filas = [
        ["M1 · Búsqueda y registro", "Registrar los resultados brutos de cada base de datos y controlar duplicados",
         "Al terminar de correr las ecuaciones de búsqueda", "Base, ecuación, filtros, fecha, conteos, registro de resultados"],
        ["M2 · Cribado (inclusión y exclusión)", "Decidir qué artículos merecen leerse completos y justificar cada descarte",
         "Al leer títulos y resúmenes, y luego el texto completo", "ID, título, decisión, criterio aplicado, puntaje por pregunta"],
        ["M3 · Extracción y síntesis", "Desglosar cada artículo aprobado para compararlos entre sí",
         "Con los PDF definitivos, en la lectura crítica", "Autor y año, objetivo, muestra, método, hallazgos, limitaciones, conclusiones"],
        ["M4 · Temática o cruzada", "Agrupar hallazgos por variable o categoría y preparar la redacción",
         "Antes de escribir el marco teórico o la discusión", "Categoría, autores que coinciden, que discrepan, vacíos, síntesis"],
        ["PRISMA 2020", "Mostrar el paso de M1 a M3 en números", "Al cerrar la selección", "Diagrama oficial adaptado"],
    ]
    _tabla(ws, 4, ["Matriz", "Para qué sirve", "Cuándo se usa", "Columnas"], filas, [34, 60, 48, 60])
    ws.freeze_panes = None
    ws.auto_filter.ref = None


def hoja_m1(wb, d):
    ws = wb.create_sheet("M1_Busqueda_Registro")
    _titulo(ws, "Matriz 1 · Búsqueda y registro operacional",
            f"Base(s) de datos consultada(s) con acceso {d.get('institucion', 'institucional')}. Registro de transparencia del proceso.")
    fila = _bloque(ws, 4, "Preguntas que debe sustentar la literatura", list(d["preguntas"].items()))
    fila = _bloque(ws, fila, "Criterios de selección", d["criterios"])
    ws.cell(row=fila, column=1, value="Estrategia de búsqueda").font = Font(bold=True, color=AZUL)
    filas = [[b["id"], b.get("base", "Scopus"), b["ecuacion"], b["filtros"], b.get("fecha", d["fecha"]),
              b.get("metodo", "—"), b["sin_filtros"], b["con_filtros"], b.get("rol", "")] for b in d["busquedas"]]
    fila = _tabla(ws, fila + 1, ["Búsqueda", "Base de datos", "Ecuación", "Filtros aplicados", "Fecha de consulta",
                                 "Método (API / navegador)", "Resultados sin filtros", "Resultados con filtros", "Rol"],
                  filas, [12, 14, 70, 40, 14, 16, 13, 13, 36])
    fila += 2
    ws.cell(row=fila, column=1, value="Registro de resultados (registros únicos con filtros)").font = Font(bold=True, color=AZUL)
    _tabla(ws, fila + 1, ["ID", "Búsqueda", "Año", "Autores", "Título", "Revista", "DOI", "Acceso abierto"],
           [[r["id"], r["busqueda"], r["anio"], r["autores"], r["titulo"], r["revista"], r["doi"], r["oa"]]
            for r in d["cribado_titulo"]], [12, 14, 7, 30, 70, 30, 28, 10])


def hoja_m2(wb, d):
    ws = wb.create_sheet("M2a_Cribado_titulo")
    _titulo(ws, "Matriz 2a · Cribado por título", "Todos los registros únicos. Decisión y criterio de exclusión explícito.")
    _tabla(ws, 4, ["ID", "Año", "Título", "Decisión", "Criterio aplicado"],
           [[r["id"], r["anio"], r["titulo"], r["decision"], r["motivo"]] for r in d["cribado_titulo"]],
           [10, 7, 80, 18, 70], col_decision=3)

    ws = wb.create_sheet("M2b_Cribado_resumen")
    _titulo(ws, "Matriz 2b · Cribado por resumen (abstract)", "Candidatos que pasaron el cribado por título.")
    _tabla(ws, 4, ["ID", "Autores (año)", "Título", "Acceso abierto", "Preguntas a las que podría aportar", "Decisión", "Criterio aplicado"],
           [[r["id"], r["cita"], r["titulo"], r["oa"], r["preguntas"], r["decision"], r["motivo"]] for r in d["cribado_resumen"]],
           [10, 28, 60, 10, 18, 22, 60], col_decision=5)

    ws = wb.create_sheet("M2c_Elegibilidad")
    _titulo(ws, "Matriz 2c · Elegibilidad por lectura del texto completo",
            "Puntaje por pregunta: 0 = no aporta · 1 = aporte parcial · 2 = aporte directo y sustentado.")
    qs = list(d["preguntas"].keys())
    ultima = _tabla(ws, 4, ["ID", "Autores (año)", "Texto completo"] + qs + ["Total", "Decisión", "Justificación"],
                    [[r["id"], r["cita"], r["acceso"]] + [r["puntajes"].get(q, "") for q in qs] +
                     [sum(r["puntajes"].values()) if r["puntajes"] else "", r["decision"], r["motivo"]] for r in d["elegibilidad"]],
                    [10, 30, 30] + [6] * len(qs) + [7, 22, 60], col_decision=4 + len(qs))
    for fila in range(5, ultima + 1):
        for c in range(4, 4 + len(qs)):
            v = ws.cell(row=fila, column=c).value
            if v in FILL_PUNTAJE:
                ws.cell(row=fila, column=c).fill = FILL_PUNTAJE[v]
                ws.cell(row=fila, column=c).alignment = CENTRO


def hoja_m3(wb, d):
    ws = wb.create_sheet("M3_Extraccion")
    _titulo(ws, "Matriz 3 · Extracción y síntesis de contenido",
            "Artículos leídos en texto completo. Evidencia textual en el idioma original con su página; aportes parafraseados en español.")
    filas = []
    for a in d["analisis"]:
        aporte = "\n".join(f"{q}: {t}" for q, t in a.get("aportes", {}).items())
        filas.append([a["cita"], a["titulo"], a["revista"], a.get("contexto", ""), a.get("objetivo", ""),
                      a.get("muestra", ""), a.get("metodo", ""), a.get("hallazgos", ""), a.get("limitaciones", ""),
                      a.get("conclusiones", ""), aporte, a.get("evidencia", ""), a.get("decision", "")])
    _tabla(ws, 4, ["Autor(es) y año", "Título", "Revista", "País / contexto", "Objetivo", "Muestra / población", "Metodología",
                   "Hallazgos clave", "Limitaciones", "Conclusiones", "Aporte a las preguntas (paráfrasis)",
                   "Evidencia textual (página)", "Decisión"],
           filas, [24, 40, 24, 18, 38, 26, 32, 48, 34, 38, 60, 60, 18], col_decision=12)


def _tematica_automatica(d):
    """Si no hay d["tematica"], arma M4 por pregunta con los aportes de M3 (para completar a mano)."""
    filas = []
    for q, texto in d["preguntas"].items():
        aportes = [f"{a['cita']}: {a['aportes'][q]}" for a in d["analisis"]
                   if q in a.get("aportes", {}) and str(a.get("decision", "")).startswith("Incluido")]
        filas.append({"categoria": f"{q}. {texto}", "coinciden": "\n".join(aportes),
                      "discrepan": "", "vacios": "", "sintesis": "Completar: idea que integra a los autores."})
    return filas


def hoja_m4(wb, d):
    ws = wb.create_sheet("M4_Tematica")
    _titulo(ws, "Matriz 4 · Temática o cruzada de redacción",
            "Hallazgos agrupados por variable o categoría (no por autor). Base para el marco teórico y la discusión.")
    tem = d.get("tematica") or _tematica_automatica(d)
    _tabla(ws, 4, ["Variable o categoría temática", "Autores que coinciden y qué sostienen", "Autores que discrepan o matizan",
                   "Vacíos de conocimiento (gaps)", "Síntesis para redactar"],
           [[t["categoria"], t.get("coinciden", ""), t.get("discrepan", ""), t.get("vacios", ""), t.get("sintesis", "")] for t in tem],
           [34, 80, 50, 40, 60])

    ws = wb.create_sheet("M4b_Cruce")
    _titulo(ws, "Matriz 4b · Cruce autores × preguntas", "Puntaje 0–2 de la lectura completa. Muestra qué pregunta queda cubierta y por quién.")
    qs = list(d["preguntas"].keys())
    elegidos = [r for r in d["elegibilidad"] if r.get("puntajes")]
    ultima = _tabla(ws, 4, ["Autor(es) y año", "Decisión"] + qs,
                    [[r["cita"], r["decision"]] + [r["puntajes"].get(q, "") for q in qs] for r in elegidos],
                    [32, 24] + [8] * len(qs))
    for fila in range(5, ultima + 1):
        for c in range(3, 3 + len(qs)):
            v = ws.cell(row=fila, column=c).value
            if v in FILL_PUNTAJE:
                ws.cell(row=fila, column=c).fill = FILL_PUNTAJE[v]
                ws.cell(row=fila, column=c).alignment = CENTRO
    fila = ultima + 2
    ws.cell(row=fila, column=1, value="Cobertura (máximo puntaje por pregunta)").font = Font(bold=True, color=AZUL)
    for c, q in enumerate(qs, 3):
        maximo = max([r["puntajes"].get(q, 0) for r in elegidos if str(r["decision"]).startswith("Incluido")] or [0])
        celda = ws.cell(row=fila, column=c, value=maximo)
        celda.fill = FILL_PUNTAJE.get(maximo, FILL_PUNTAJE[0])
        celda.alignment = CENTRO


def hoja_prisma(wb, d, ruta_png):
    ws = wb.create_sheet("PRISMA_2020")
    _titulo(ws, "Diagrama de flujo PRISMA 2020", "Números calculados de M1 a M3. El diagrama también se guarda como PNG para el documento.")
    fila = 4
    for fase, concepto, n in d.get("prisma", []):
        c1 = ws.cell(row=fila, column=1, value=fase)
        c2 = ws.cell(row=fila, column=2, value=concepto)
        c3 = ws.cell(row=fila, column=4, value=n)
        ws.merge_cells(start_row=fila, start_column=2, end_row=fila, end_column=3)
        c1.font = Font(bold=True, color="FFFFFF")
        c1.fill = PatternFill("solid", fgColor=NARANJA if fase == "Inclusión" else AZUL)
        c1.alignment = CENTRO
        c2.alignment = WRAP
        c3.font = Font(bold=True)
        c3.alignment = CENTRO
        for c in (1, 2, 3, 4):
            ws.cell(row=fila, column=c).border = BORDE
        ws.row_dimensions[fila].height = 30
        fila += 1
    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 50
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 10
    if ruta_png and os.path.exists(ruta_png):
        try:
            from openpyxl.drawing.image import Image as ImagenXL
            img = ImagenXL(ruta_png)
            img.width, img.height = img.width * 0.55, img.height * 0.55
            ws.add_image(img, "F4")
        except ImportError:
            ws.cell(row=fila + 1, column=1, value=f"Diagrama: {os.path.basename(ruta_png)}")


def hoja_referencias(wb, d):
    ws = wb.create_sheet("Referencias_APA")
    _titulo(ws, "Artículos incluidos", "Referencias en formato APA 7.ª edición y uso dentro del trabajo.")
    _tabla(ws, 4, ["N.º", "Cita en el texto", "Referencia APA 7", "Preguntas donde se usa", "Archivo PDF"],
           [[i, r["cita"], r["apa"], r["preguntas"], r["pdf"]] for i, r in enumerate(d["incluidos"], 1)],
           [5, 30, 95, 20, 45])


def construir(d, salida, png=True):
    """Crea el Excel de las 4 matrices y, si png=True, el diagrama PRISMA 2020 junto a él."""
    ruta_png = None
    if png:
        ruta_png = os.path.splitext(salida)[0] + "_PRISMA_2020.png"
        dibujar(conteos_desde_datos(d), ruta_png, f"Diagrama de flujo PRISMA 2020 – {d['actividad']}")
    wb = Workbook()
    hoja_guia(wb, d)
    hoja_m1(wb, d)
    hoja_m2(wb, d)
    hoja_m3(wb, d)
    hoja_m4(wb, d)
    hoja_prisma(wb, d, ruta_png)
    hoja_referencias(wb, d)
    for hoja in wb.worksheets:
        hoja.sheet_view.zoomScale = 90
    wb.save(salida)
    return salida
