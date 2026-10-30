---
name: nuevo-proyecto
description: 'Inicia un proyecto de investigación con el pipeline del Asistente: carpetas, protocolo, tablero de control y datos de las 4 matrices. Usar cuando empiece un trabajo, tesis, artículo o revisión nueva, o pida preparar la estructura.'
---

# Nuevo proyecto de investigación

1. **Pregunta lo mínimo** que no se deduzca de los archivos: tema, dónde crear el proyecto, qué guía o tarea lo rige y el rango de años (por defecto, los últimos 5 años estrictos). Si hay un PDF de la tarea o una guía de grupo, **léelo primero**: fija criterios, estructura, fechas y reparto de partes.
2. **Crea la estructura:**
   `python "${CLAUDE_PLUGIN_ROOT}/skills/nuevo-proyecto/scripts/iniciar_proyecto.py" "<carpeta>" --tema "<tema>" --autora "<nombre>" --institucion "<institución>" [--desde AAAA --hasta AAAA]`
   No sobrescribe nada que ya exista. Crea:
   - `00_Control_Proyecto.md`: el tablero del pipeline, de la etapa 0 a la 8, con sus controles;
   - `protocolo.md`: pregunta, objetivos, Q1…Qn, variables, conceptos, ecuaciones y criterios;
   - `literatura/B1_<tema>/` con `_leidos_no_seleccionados/`;
   - `_automatizacion/matrices/datos_B1.py`: los datos de las matrices, ya enlazados con el plugin;
   - `documento/figuras/`.
3. **Completa el protocolo** con la usuaria: las preguntas Q1…Qn y las variables. Luego sigue con la skill `revision-sistematica`, desde la etapa 1.
4. Si el trabajo se escribe en una **plantilla de Word** del curso, cópiala intacta a `_automatizacion/Plantilla_ORIGINAL.docx` y arma el documento con `word_apa.py` (skill `redaccion-apa7`, `referencias/perfil-unemi.md`).
5. Si el proyecto tiene varias búsquedas (una por capítulo o actividad), crea `literatura/B2_…`, `B3_…` y copia `datos_B1.py` como `datos_B2.py`, cambiando `CARPETA`, `CSVS` y `BUSQUEDAS`.
