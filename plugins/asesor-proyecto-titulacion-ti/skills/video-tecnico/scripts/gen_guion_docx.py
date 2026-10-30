"""Genera el guion del video técnico en Word a partir de un JSON.

Uso: python gen_guion_docx.py guion.json salida.docx

Los tiempos de cada segmento se calculan con las palabras del texto hablado y el ritmo
de lectura del JSON (140 palabras por minuto si no se indica), de modo que el resumen de
tiempos siempre coincide con lo que se va a decir. La autoría del archivo son los autores
del JSON; el PDF se obtiene después con Microsoft Word.
"""
import json
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt


def mmss(segundos: float) -> str:
    return f"{int(segundos // 60)}:{int(segundos % 60):02d}"


def calcular_tiempos(segmentos: list[dict], ppm: int) -> str:
    acumulado = 0.0
    for seg in segmentos:
        duracion = len(" ".join(seg["decir"]).split()) / ppm * 60
        seg["tiempo"] = f"{mmss(acumulado)} – {mmss(acumulado + duracion)}"
        acumulado += duracion
    return mmss(acumulado)


def construir(datos: dict, salida: str) -> str:
    ppm = datos.get("palabras_por_minuto", 140)
    total = calcular_tiempos(datos["segmentos"], ppm)
    autores = datos["autores"]

    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)
    for seccion in doc.sections:
        seccion.left_margin = seccion.right_margin = Cm(2.2)
        seccion.top_margin = seccion.bottom_margin = Cm(2)
    propiedades = doc.core_properties
    propiedades.author = propiedades.last_modified_by = "; ".join(autores)
    propiedades.title = datos["titulo"]
    propiedades.comments = ""

    doc.add_heading(datos["titulo"], 0)
    doc.add_paragraph(datos["proyecto"]).runs[0].bold = True
    doc.add_paragraph(f"Autores: {' y '.join(autores)}. Duración: {total} minutos a {ppm} palabras por minuto.")
    doc.add_paragraph("Cómo usar este guion. " + datos["como_usar"])

    doc.add_heading("Resumen de tiempos", 1)
    tabla = doc.add_table(rows=1, cols=3)
    tabla.style = "Light Grid Accent 1"
    for celda, texto in zip(tabla.rows[0].cells, ("Segmento", "Quién", "Tiempo")):
        celda.text = texto
    for seg in datos["segmentos"]:
        fila = tabla.add_row().cells
        fila[0].text, fila[1].text, fila[2].text = seg["titulo"], seg["quien"], seg["tiempo"]

    for seg in datos["segmentos"]:
        doc.add_heading(f"{seg['titulo']} ({seg['quien']}, {seg['tiempo']})", 1)
        for etiqueta, clave in (("Abrir: ", "abrir"), ("Señalar: ", "senalar")):
            p = doc.add_paragraph()
            p.add_run(etiqueta).bold = True
            p.add_run(seg[clave])
        doc.add_paragraph().add_run("Decir:").bold = True
        for parrafo in seg["decir"]:
            p = doc.add_paragraph(parrafo)
            p.paragraph_format.left_indent = Cm(0.8)
            p.paragraph_format.space_after = Pt(6)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_heading("Glosario para no trabarse", 1)
    for item in datos.get("glosario", []):
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(item["termino"] + ": ").bold = True
        p.add_run(item["definicion"])

    doc.add_heading("Preguntas probables del tribunal y respuesta breve", 1)
    for item in datos.get("preguntas", []):
        p = doc.add_paragraph(style="List Number")
        p.add_run(item["pregunta"] + " ").bold = True
        p.add_run(item["respuesta"])

    doc.add_heading("Lista de comprobación antes de grabar", 1)
    for item in datos.get("antes_de_grabar", []):
        doc.add_paragraph(item, style="List Bullet")

    doc.save(salida)
    return total


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as archivo:
        datos = json.load(archivo)
    total = construir(datos, sys.argv[2])
    palabras = sum(len(" ".join(s["decir"]).split()) for s in datos["segmentos"])
    print(f"{len(datos['segmentos'])} segmentos, {palabras} palabras, duracion {total}")
