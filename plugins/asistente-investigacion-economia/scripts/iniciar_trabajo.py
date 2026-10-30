# -*- coding: utf-8 -*-
"""Crea la estructura de un trabajo de Economía y copia las plantillas.
    python -I iniciar_trabajo.py "<carpeta del trabajo>" --tema "..." --autora "Grupo N" [--plantilla "<archivo.docx>"]
Crea (sin sobrescribir nada existente):
  _respaldo/                        copia intacta de la plantilla Word indicada (+ md5)
  00_Control_Trabajo.md             tablero de etapas con controles
  Evidencias_Drive/{01_Busquedas_Scopus, 02_PDF_articulos, 03_Graficos, 04_Scripts_Python, 05_Base_datos, 06_Documento_final}
  Evidencias_Drive/04_Scripts_Python/  librerías + config_trabajo.py (para completar)
"""
import hashlib, os, shutil, sys
sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
LIBS = ["lib_docx.py", "lib_figuras.py", "mathlib.py", "matrices.py", "diagrama_prisma.py", "matriz_consistencia.py", "ris_zotero.py", "graficos_busqueda.py",
        "enriquecer_openalex.py", "exportar_pdf_word.py", "exportar_pdf_word.ps1", "verificar_citas.py", "verificar_apa.py", "similitud.py", "pdf_tools.py", "inventario_pdf.py"]

CONTROL = """# Control del trabajo · {tema}

Autoría: {autora} · Creado: {hoy}

| Etapa | Qué se hace | Control (no pasar sin cumplirlo) | Estado |
|---|---|---|---|
| 0 Consigna y rúbrica | Leer consigna, rúbrica, plan y borradores; checklist de literales; mapa rúbrica→evidencia | Cada literal de la consigna tiene sección y evidencia asignadas | ☐ |
| 1 Preguntas y variables | Q1…Qn, variables, conceptos en inglés, bloques OR/AND | Tabla de conceptos escrita y aprobada por la usuaria | ☐ |
| 2 Búsqueda Scopus | Cadenas del plan tal cual + ampliadas; conteos sin/con filtros; exportar TODO | CSV completos, conteos con fecha y método | ☐ |
| 3 Enriquecer | OpenAlex: resúmenes y autores completos | `openalex_metadatos.json` generado | ☐ |
| 4 Cribado y matriz | Reglas por título, puntaje 0–2 por pregunta, PRISMA | Cada Q con ≥ 1 artículo puntaje 2; cifras PRISMA cuadran | ☐ |
| 5 PDF | Descargar los de acceso abierto; anotar `por_descargar.md` | Cada PDF empieza con %PDF; nada de CAPTCHA | ☐ |
| 6 Referencias y RIS | Verificar por DOI; `ris_zotero.py`; `referencias_apa.py` | RIS importable; cita↔referencia sin errores | ☐ |
| 7 Figuras | Gráficos Python a tamaño final | Verificador OK y cada PNG mirado | ☐ |
| 8 Redacción | Introducción CARS, metodología, secciones, conclusiones, anexo de IA | Tono analítico; cada afirmación respaldada | ☐ |
| 9 Documento | Ensamblar Word sobre la plantilla; PDF con Word real | Páginas del cuerpo según consigna; ecuaciones nativas | ☐ |
| 10 Entrega | Carpeta de evidencias, LEEME, informe honesto | Revisión final con el agente revisor-rubrica-economia | ☐ |

Última versión generada (md5): _pendiente_
Marcadores para la usuaria: enlace de Drive, nombres de la carátula, conclusiones personales de otros integrantes.
"""


def main(a):
    carpeta = os.path.abspath(a[0])
    def val(flag, d=""):
        return a[a.index(flag) + 1] if flag in a else d
    tema, autora, plantilla = val("--tema", "TODO tema"), val("--autora", "TODO autoría"), val("--plantilla")
    ev = os.path.join(carpeta, "Evidencias_Drive")
    for sub in ("01_Busquedas_Scopus", "02_PDF_articulos", "03_Graficos", "04_Scripts_Python", "05_Base_datos", "06_Documento_final"):
        os.makedirs(os.path.join(ev, sub), exist_ok=True)
    os.makedirs(os.path.join(carpeta, "_respaldo"), exist_ok=True)
    scripts = os.path.join(ev, "04_Scripts_Python")
    for f in LIBS:
        dst = os.path.join(scripts, f)
        if not os.path.exists(dst):
            shutil.copyfile(os.path.join(AQUI, f), dst)
    cfg = os.path.join(scripts, "config_trabajo.py")
    if not os.path.exists(cfg):
        shutil.copyfile(os.path.join(RAIZ, "plantillas_proyecto", "config_trabajo.py"), cfg)
    if plantilla:
        dst = os.path.join(carpeta, "_respaldo", os.path.splitext(os.path.basename(plantilla))[0] + "_respaldo_original.docx")
        if not os.path.exists(dst):
            shutil.copyfile(plantilla, dst)
        print("Plantilla respaldada:", dst, "md5", hashlib.md5(open(dst, "rb").read()).hexdigest())
    ctl = os.path.join(carpeta, "00_Control_Trabajo.md")
    if not os.path.exists(ctl):
        import datetime
        open(ctl, "w", encoding="utf-8").write(CONTROL.format(tema=tema, autora=autora, hoy=datetime.date.today().isoformat()))
    print("Estructura lista en", carpeta, "\nSiguiente: completar", cfg, "y seguir la skill buscar-literatura-economia.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
