# -*- coding: utf-8 -*-
"""CONFIGURACIÓN ÚNICA DEL TRABAJO. Copiada por iniciar_trabajo.py a <proyecto>/Evidencias_Drive/04_Scripts_Python/.
La leen: matriz_consistencia.py, ris_zotero.py, graficos_busqueda.py. Completar los TODO con la usuaria.
Las rutas se derivan de la ubicación de este archivo (…/Evidencias_Drive/04_Scripts_Python/config_trabajo.py).
"""
TEMA = "TODO: tema del trabajo"
FECHA = "TODO: fecha de la búsqueda (dd-mmm-aaaa)"
AUTORA = "TODO: Grupo N (coordinación: nombre)"

# Preguntas que la literatura debe sustentar: una por punto de la consigna (+ una de redacción si se justifica la introducción)
PREGUNTAS = {
    "Q1": "TODO: pregunta derivada del punto 1 de la consigna",
    "Q2": "TODO",
}

CRITERIOS = [
    ("Inclusión", "Artículo de revista (DOCTYPE ar), versión final, preferentemente en inglés, pertinente de forma directa a alguna pregunta."),
    ("Exclusión", "Libros, capítulos, congresos, notas; aplicaciones sin aporte a la pregunta; otras disciplinas; aporte redundante o parcial frente a otro ya incluido."),
    ("Prioridad", "Acceso abierto y resumen disponible; últimos 5 años; cobertura de todas las preguntas con al menos un puntaje 2."),
]

# prefijo de búsqueda -> CSV exportado con scopus_exportar (carpeta 01_Busquedas_Scopus). El último puede ser la verificación por DOI.
CSVS = {"B1": "scopus_B1_tema.csv"}

BUSQUEDAS = [
    {"id": "B1", "base": "Scopus", "ecuacion": 'TITLE-ABS-KEY("TODO")', "filtros": "Article; English",
     "fecha": FECHA, "metodo": "API oficial de Elsevier", "sin_filtros": 0, "con_filtros": 0, "rol": "Ecuación principal (Q1)."},
]

# Reglas de exclusión por TÍTULO (primera que coincide). Códigos E1 otra disciplina/aplicación, E2 revisiones, E8 no pertinente (por defecto).
REGLAS = [
    (r"systematic literature review|literature review|bibliometric|\ba review\b", "E2 · Revisión de literatura o bibliométrico"),
    (r"health|medic|patient|clinic|hospital", "E1 · Otra disciplina: salud"),
]

# Candidatos evaluados. Clave = DOI en minúsculas.
#   sc: puntaje 0-2 por pregunta en el orden de PREGUNTAS | dec: "I" incluido, "N" elegible no seleccionado
#   acc: "PDF" (PDF leído) | "RES" (resumen OpenAlex/Scopus) | "MET" (solo título y palabras clave)
CAND = {
    # "10.xxxx/yyyy": dict(cita="Autor (2024)", sc=(2, 0), dec="I", acc="RES", mot="Por qué aporta.",
    #                       obj="Objetivo del estudio", hall="Hallazgo clave con cifra", aportes={"Q1": "Aporte parafraseado"}),
}

LIBROS = [  # obras originales / libros exigidos (TY BOOK en el RIS): (autor "Apellido, Nombre", año, título, editorial)
    # ("Marx, Karl", 1867, "Das Kapital (Vol. 1)", "Otto Meissner"),
]
TITULOS_APA = {}   # doi -> título tal como va en la referencia (si OpenAlex/Scopus lo trae distinto)
IDIOMA = {}        # doi -> "es" | "pt" (por defecto "en")
PDFS = {}          # doi -> archivo en 02_PDF_articulos (si se deja vacío, no se enlaza)

# Figura de evidencia bibliométrica: conteos por periodo (scopus_contar con PUBYEAR) y CSV de cada bloque
PERIODOS = ["2000–2009", "2010–2019", "2020–2026"]
CONTEOS_PERIODO = {}          # "Bloque": [n1, n2, n3]
CORPUS = {}                   # "Bloque": "scopus_B1_tema.csv"
