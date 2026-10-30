"""Crea la estructura de un proyecto de investigación nuevo (no sobrescribe nada que ya exista).

    <proyecto>/
      00_Control_Proyecto.md        tablero del pipeline con sus controles de calidad
      protocolo.md                  tema, pregunta, objetivos, variables, keywords, criterios y ecuaciones
      literatura/B1_<tema>/         PDF, CSV y RIS de la primera búsqueda (+ _leidos_no_seleccionados/)
      _automatizacion/matrices/datos_B1.py   datos de las 4 matrices (copia de la plantilla, ya enlazada)
      documento/                    el trabajo en Word y sus figuras

Uso:
    python iniciar_proyecto.py <carpeta_proyecto> --tema "Costos y rentabilidad" --autora "Nombre Apellido"
                               [--desde 2022] [--hasta 2026] [--institucion "UNEMI"]
"""
import argparse
import datetime
import os
import re
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.dirname(os.path.dirname(AQUI))
SCRIPTS_MATRICES = os.path.join(SKILLS, "matrices-revision", "scripts")


def _slug(texto):
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^A-Za-z0-9]+", "_", t).strip("_")[:40] or "Tema"


def _escribir(ruta, contenido, creados):
    if os.path.exists(ruta):
        return
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    creados.append(ruta)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto")
    ap.add_argument("--tema", required=True)
    ap.add_argument("--autora", required=True)
    ap.add_argument("--institucion", default="institucional")
    hoy = datetime.date.today()
    ap.add_argument("--desde", type=int, default=hoy.year - 4)
    ap.add_argument("--hasta", type=int, default=hoy.year)
    a = ap.parse_args()

    raiz = os.path.abspath(a.proyecto)
    slug = _slug(a.tema)
    carpeta_b1 = os.path.join(raiz, "literatura", f"B1_{slug}")
    creados = []
    for d in (carpeta_b1, os.path.join(carpeta_b1, "_leidos_no_seleccionados"), os.path.join(raiz, "documento", "figuras"),
              os.path.join(raiz, "_automatizacion", "matrices")):
        if not os.path.isdir(d):
            os.makedirs(d)
            creados.append(d + os.sep)

    filtros = (f"PUBYEAR > {a.desde - 1} AND PUBYEAR < {a.hasta + 1} AND DOCTYPE(ar) AND LANGUAGE(english) AND PUBSTAGE(final)")
    _escribir(os.path.join(raiz, "protocolo.md"), f"""# Protocolo de revisión – {a.tema}

Autora: {a.autora} · Institución: {a.institucion} · Inicio: {hoy.isoformat()}

## 1. Pregunta y objetivos
- Pregunta de investigación: …
- Objetivo general: …
- Objetivos específicos / preguntas que la literatura debe sustentar:
  - Q1: …
  - Q2: …

## 2. Variables y dimensiones
| Variable | Tipo (independiente / dependiente / contexto) | Dimensiones |
|---|---|---|
| … | … | … |

## 3. Conceptos y palabras clave (en inglés)
| Concepto | Sinónimos y términos relacionados (OR) | Tesauro consultado |
|---|---|---|
| … | "…" OR "…" OR "…*" | JEL / UNESCO / APA Thesaurus |

## 4. Ecuaciones de búsqueda
Filtros de todas las búsquedas: `{filtros}`
| ID | Ecuación TITLE-ABS-KEY | Rol |
|---|---|---|
| B1 | TITLE-ABS-KEY((…) AND (…)) | Principal |

## 5. Criterios de selección
- Inclusión: artículos científicos, inglés (portugués o español si el artículo es pertinente), versión final, {a.desde}–{a.hasta}, área temática afín.
- Exclusión: libros, capítulos, congresos, revisiones, casos docentes, prensa; fuera de años; fuera de tema; texto completo no accesible.
- Prioridad: acceso abierto; contexto afín; evidencia empírica; citas como desempate.
""", creados)

    _escribir(os.path.join(raiz, "00_Control_Proyecto.md"), f"""# Tablero del proyecto – {a.tema}

Autora: {a.autora} · Inicio: {hoy.isoformat()} · Rango de años: {a.desde}–{a.hasta}

## Pipeline de investigación (cada etapa pasa solo si cumple su control)
| # | Etapa | Control de calidad | Estado |
|---|---|---|---|
| 0 | Protocolo (`protocolo.md`) | Preguntas Q1…Qn escritas | ⬜ |
| 1 | Variables y keywords → ecuaciones | Cada variable con su bloque OR; bloques unidos con AND | ⬜ |
| 2 | Búsqueda en Scopus → CSV (Matriz 1) | Conteos sin y con filtros registrados con fecha y método | ⬜ |
| 3 | Cribado por título y resumen (Matriz 2a, 2b) | Toda exclusión con motivo; muestra de reglas revisada | ⬜ |
| 4 | Texto completo (PDF) | Cada PDF empieza con %PDF; no recuperados anotados | ⬜ |
| 5 | Lectura a fondo → Matrices 2c, 3, 4 + PRISMA 2020 | Cada Q con al menos un artículo de puntaje 2; cifras PRISMA cuadran | ⬜ |
| 6 | Redacción APA 7 (`documento/`) | Cada afirmación teórica con su cita verificada | ⬜ |
| 7 | Verificación (`verificar_apa.py`) | 0 errores | ⬜ |
| 8 | Entrega (paquete de evidencias + RIS) | N.º de registros RIS = N.º de referencias | ⬜ |

## Búsquedas
| ID | Ecuación | Sin filtros | Con filtros | Incluidos | Carpeta |
|---|---|---|---|---|---|
| B1 | … | … | … | … | literatura/B1_{slug} |

## Decisiones y pendientes
- …
""", creados)

    plantilla = open(os.path.join(SCRIPTS_MATRICES, "plantilla_datos.py"), encoding="utf-8").read()
    plantilla = (plantilla.replace('r"RUTA_SCRIPTS_MATRICES"', f"r\"{SCRIPTS_MATRICES}\"")
                 .replace('r"RUTA/A/literatura/TEMA"', f"r\"{carpeta_b1}\"")
                 .replace('"TODO: tema o capítulo"', repr(a.tema))
                 .replace('"TODO: nombre de quien elabora"', repr(a.autora))
                 .replace('"TODO: fecha de la búsqueda"', repr(hoy.strftime("%d/%m/%Y")))
                 .replace('"PUBYEAR …; Article; English; final"', repr(f"PUBYEAR {a.desde}–{a.hasta}; Article; English; final")))
    _escribir(os.path.join(raiz, "_automatizacion", "matrices", "datos_B1.py"), plantilla, creados)

    print(f"OK proyecto en {raiz}")
    for c in creados:
        print("   creado:", os.path.relpath(c, raiz))
    if not creados:
        print("   (ya existía todo; no se modificó nada)")


if __name__ == "__main__":
    main()
