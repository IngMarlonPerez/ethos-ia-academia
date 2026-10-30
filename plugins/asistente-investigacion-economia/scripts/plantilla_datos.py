"""PLANTILLA · Datos de las 4 matrices de revisión (PRISMA 2020) de una búsqueda.

Copiar este archivo al proyecto (p. ej. proyecto/_automatizacion/matrices/datos_TEMA.py), completar las
secciones marcadas con TODO y ejecutar:  python datos_TEMA.py

Qué alimenta cada sección:
  BUSQUEDAS + CSV exportados        → M1 Búsqueda y registro (y la fase de Identificación de PRISMA)
  PASAN_TITULO, REGLAS, MOTIVOS     → M2a/M2b Cribado por título y resumen
  ELEGIBILIDAD (puntaje 0–2)        → M2c Elegibilidad y M4b Cruce autores × preguntas
  ANALISIS                          → M3 Extracción y síntesis
  TEMATICA (opcional)               → M4 Temática; si se deja vacía, se arma sola por pregunta con los aportes de M3
  INCLUIDOS                         → Referencias APA 7
El diagrama PRISMA 2020 (PNG) se calcula solo; PRISMA2020 permite corregir cualquier número.
"""
import csv
import os
import re
import sys

# Carpeta de scripts de la skill matrices-revision (la escribe iniciar_proyecto.py; si no, ajustar a mano)
SCRIPTS = r"RUTA_SCRIPTS_MATRICES"
sys.path.insert(0, SCRIPTS)
from matrices import construir  # noqa: E402

# TODO: carpeta de la literatura de esta búsqueda y CSV exportados (scopus_exportar o scopusBuscar)
CARPETA = r"RUTA/A/literatura/TEMA"
CSVS = {"B1": "scopus_B1.csv"}          # prefijo de ID -> archivo CSV (una entrada por ecuación exportada)

TEMA = "TODO: tema o capítulo"
FECHA = "TODO: fecha de la búsqueda"
AUTORA = "TODO: nombre de quien elabora"

# TODO: preguntas u objetivos que la literatura debe sustentar (se puntúan 0–2 en la elegibilidad)
PREGUNTAS = {
    "Q1": "…",
    "Q2": "…",
}

CRITERIOS = [
    ("Inclusión", "Artículos científicos (Article), en inglés, versión final, últimos 5 años, área temática pertinente."),
    ("Exclusión", "Libros, capítulos, congresos, reviews, casos docentes, prensa; fuera de años o idioma; fuera de tema; "
                  "texto completo no accesible."),
    ("Prioridad", "Acceso abierto, contexto afín al trabajo y definiciones explícitas; citas como desempate."),
]

# TODO: una entrada por ecuación. metodo: "API oficial de Elsevier" o "Navegador (sesión institucional)"
BUSQUEDAS = [
    {"id": "B1", "base": "Scopus", "ecuacion": 'TITLE-ABS-KEY(...)', "filtros": "PUBYEAR …; Article; English; final",
     "fecha": FECHA, "metodo": "API oficial de Elsevier", "sin_filtros": 0, "con_filtros": 0, "rol": "Ecuación principal."},
]

# TODO: IDs (prefijo-fila del CSV) que pasan el cribado por título; el resto se excluye con REGLAS
PASAN_TITULO = set()
# IDs que ya se cribaron en otra búsqueda del proyecto (conservan esa decisión; se restan como «ya cribados»)
PREVIOS = set()

# Motivos de exclusión por título (primera regla que coincide con el TÍTULO; usar límites de palabra \b)
REGLAS = [
    (r"systematic literature review|literature review|bibliometric|\ba review\b", "E2 · Revisión de literatura o bibliométrico"),
    (r"\bpatient|\bhealth|\bclinic|hospital", "E1 · Fuera del tema: salud"),
    (r"supply chain|\btransport|logistic|construction|\benergy\b|electric", "E1 · Fuera del tema: otros sectores"),
]
REVISTAS_DOCENTES = r"case studies|issues in accounting education|journal of accounting education"

# TODO: IDs que pasan a texto completo -> preguntas a las que podrían aportar
TEXTO_COMPLETO = {}
# TODO: IDs excluidos por resumen -> (preguntas, motivo)
MOTIVOS_RESUMEN = {}


def P(*v):
    return dict(zip(PREGUNTAS.keys(), v))


# TODO: una entrada por texto completo buscado.
# decision: "Incluido" | "Elegible – no seleccionado" | "No recuperado"
# motivo_corto (opcional): razón agrupada para el diagrama PRISMA, p. ej. "Aporte menor o redundante", "Otro sector"
ELEGIBILIDAD = [
    # {"id": "B1-3", "cita": "Autor et al. (2024)", "acceso": "PDF editorial", "puntajes": P(2, 1),
    #  "decision": "Incluido", "motivo": "…"},
]

# TODO: una entrada por artículo LEÍDO. Evidencia en el idioma original con la página de la revista.
ANALISIS = [
    # {"cita": "Autor, Autor y Autor (2024)", "titulo": "…", "revista": "Revista, 10(2), 1–20", "contexto": "País · sector",
    #  "objetivo": "…", "muestra": "…", "metodo": "…", "hallazgos": "…", "limitaciones": "…", "conclusiones": "…",
    #  "aportes": {"Q1": "paráfrasis en español"}, "evidencia": '"cita textual" (p. 5).', "decision": "Incluido"},
]

# Opcional: matriz temática redactada a mano (si queda vacía se arma sola por pregunta)
TEMATICA = [
    # {"categoria": "Variable X", "coinciden": "Autor (2024): …", "discrepan": "Autor (2023): …",
    #  "vacios": "…", "sintesis": "Idea que integra a los autores para redactar."},
]

# TODO: artículos incluidos con su referencia APA 7
INCLUIDOS = [
    # {"cita": "(Autor et al., 2024)", "preguntas": "Q1, Q2", "pdf": "Autor_2024_Tema.pdf", "apa": "Autor, A. (2024). …"},
]

PRISMA2020 = {}   # opcional: corregir un número del diagrama, p. ej. {"duplicados": 7}


def _motivo(titulo, revista):
    if re.search(REVISTAS_DOCENTES, (revista or "").lower()):
        return "E5 · Caso docente"
    for patron, m in REGLAS:
        if re.search(patron, titulo.lower()):
            return m
    return "E8 · Tema no pertinente a las preguntas del trabajo"


def datos():
    filas = {}
    for pref, archivo in CSVS.items():
        for i, r in enumerate(csv.DictReader(open(os.path.join(CARPETA, archivo), encoding="utf-8-sig")), 1):
            eid = r.get("EID", "")
            if eid and any(eid == x[1].get("EID") for x in filas.values()):
                continue  # duplicado entre ecuaciones
            filas[f"{pref}-{i}"] = (pref, r)
    titulo, resumen = [], []
    for rid, (pref, r) in filas.items():
        if rid in PREVIOS:
            continue
        oa = "Sí" if r.get("Open Access", "").strip() else "No"
        pasa = rid in PASAN_TITULO
        titulo.append({"id": rid, "busqueda": pref, "anio": r["Year"], "autores": r["Authors"][:120], "titulo": r["Title"],
                       "revista": r["Source title"], "doi": r["DOI"], "oa": oa,
                       "decision": "Pasa a resumen" if pasa else "Excluido (título)",
                       "motivo": "Título pertinente a las preguntas." if pasa else _motivo(r["Title"], r["Source title"])})
        if pasa:
            cita = f"{r['Authors'].split(';')[0]}{' et al.' if ';' in r['Authors'] else ''} ({r['Year']})"
            if rid in TEXTO_COMPLETO:
                resumen.append({"id": rid, "cita": cita, "titulo": r["Title"], "oa": oa, "preguntas": TEXTO_COMPLETO[rid],
                                "decision": "Pasa a texto completo", "motivo": "El resumen anticipa aporte directo."})
            else:
                preg, mot = MOTIVOS_RESUMEN.get(rid, ("—", "Aporte insuficiente según el resumen."))
                resumen.append({"id": rid, "cita": cita, "titulo": r["Title"], "oa": oa, "preguntas": preg,
                                "decision": "Excluido (resumen)", "motivo": mot})
    n_tit, n_pasan = len(titulo), len(resumen)
    n_tc = sum(1 for r in resumen if r["decision"].startswith("Pasa"))
    n_norec = sum(1 for r in ELEGIBILIDAD if r["decision"] == "No recuperado")
    n_eval = len(ELEGIBILIDAD) - n_norec
    n_inc = sum(1 for r in ELEGIBILIDAD if r["decision"] == "Incluido")
    sin = sum(b["sin_filtros"] for b in BUSQUEDAS)
    con = sum(b["con_filtros"] for b in BUSQUEDAS)
    prisma = [
        ("Identificación", "Registros identificados sin filtros", sin),
        ("Identificación", "Eliminados por filtros automáticos (años, tipo, idioma, etapa, área)", sin - con),
        ("Identificación", "Registros con filtros", con),
        ("Identificación", "Duplicados o ya cribados en otra búsqueda", con - n_tit),
        ("Cribado", "Registros únicos cribados por título", n_tit),
        ("Cribado", "Excluidos por título", n_tit - n_pasan),
        ("Cribado", "Registros cribados por resumen", n_pasan),
        ("Cribado", "Excluidos por resumen", n_pasan - n_tc),
        ("Elegibilidad", "Textos completos buscados", n_tc),
        ("Elegibilidad", "Textos completos no recuperados", n_norec),
        ("Elegibilidad", "Textos completos leídos y evaluados", n_eval),
        ("Elegibilidad", "Elegibles no seleccionados", n_eval - n_inc),
        ("Inclusión", "Artículos incluidos", n_inc),
    ]
    assert n_tc == len(ELEGIBILIDAD), f"Textos completos ({n_tc}) ≠ filas de ELEGIBILIDAD ({len(ELEGIBILIDAD)})"
    return {"actividad": TEMA, "fecha": FECHA, "autora": AUTORA, "institucion": "institucional",
            "preguntas": PREGUNTAS, "criterios": CRITERIOS, "busquedas": BUSQUEDAS, "prisma": prisma,
            "cribado_titulo": titulo, "cribado_resumen": resumen, "elegibilidad": ELEGIBILIDAD,
            "analisis": ANALISIS, "tematica": TEMATICA, "incluidos": INCLUIDOS, "prisma2020": PRISMA2020}


if __name__ == "__main__":
    d = datos()
    for fase, concepto, n in d["prisma"]:
        print(f"{fase:15} {n:>6}  {concepto}")
    nombre = re.sub(r"[^A-Za-z0-9_-]+", "_", TEMA)[:40]
    print("OK", construir(d, os.path.join(CARPETA, f"Matrices_Revision_{nombre}.xlsx")))
