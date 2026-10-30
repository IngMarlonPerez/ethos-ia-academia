---
name: iniciar-trabajo
description: 'Prepara la estructura de un trabajo de Economía: carpeta de evidencias, respaldo de la plantilla, tablero y config_trabajo.py. Usar al empezar una tarea o con «prepara la carpeta».'
---

# Iniciar un trabajo de Economía

1. **Leer antes de crear**: PDF de la tarea, plan del grupo y plantilla (ver `leer-consigna-rubrica`). La plantilla que la usuaria indique es la fuente: **nunca se modifica**.
2. **Crear la estructura** (no sobrescribe nada existente):
   ```
   python -I "${CLAUDE_PLUGIN_ROOT}/scripts/iniciar_trabajo.py" "<carpeta del trabajo>" --tema "<tema>" --autora "<Grupo N>" --plantilla "<archivo.docx>"
   ```
   Crea `_respaldo/` (copia intacta + md5), `00_Control_Trabajo.md` (etapas 0–10), `Evidencias_Drive/` con `01_Busquedas_Scopus`, `02_PDF_articulos`, `03_Graficos`, `04_Scripts_Python` (librerías + `config_trabajo.py`), `05_Base_datos`, `06_Documento_final`.
3. **Completar `config_trabajo.py`** con la usuaria: tema, preguntas Q1…Qn (una por punto de la consigna), criterios, ecuaciones (`BUSQUEDAS`), reglas de exclusión. Los candidatos (`CAND`) se llenan después del cribado.
4. **Rutas largas**: las carpetas de tareas UNEMI miden ~220 caracteres. Nombres de archivo cortos; exportar siempre en una carpeta temporal corta (`exportar_pdf_word.py` lo hace). Ver `referencias/trampas-windows-office.md`.
5. **Trabajos por actividades** (p. ej. Costeo): una actividad por iteración, con pausa para su revisión; una búsqueda `B<n>` por actividad (copiar `CSVS`/`BUSQUEDAS`), y el avance en `00_Control_Trabajo.md`.
6. **Escribir los .py con la herramienta Write** (los heredocs de bash corrompen `\n` y `\`).
7. Continuar con `leer-consigna-rubrica` y luego `buscar-literatura-economia`.
