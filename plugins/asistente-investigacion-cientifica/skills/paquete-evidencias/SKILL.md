---
name: paquete-evidencias
description: 'Arma la carpeta de evidencias para Drive: PDF citados, RIS consolidado sin duplicados para Zotero, matrices PRISMA, CSV de Scopus, LEEME y lista de artículos por descargar. Usar al pedir preparar evidencias, subir a Drive o el .ris para Zotero.'
---

# Paquete de evidencias (Drive + Zotero)

Script: `${CLAUDE_PLUGIN_ROOT}/skills/paquete-evidencias/scripts/armar_paquete.py` (en los pasos, `scripts/` es esa carpeta). Copia los archivos y no los mueve. Si se vuelve a ejecutar, reemplaza la carpeta que él mismo generó; una carpeta ajena no la toca.

## Pasos
1. **Revisa la carpeta de literatura** del proyecto. Cada búsqueda o parte debe tener su subcarpeta con:
   - los PDF incluidos;
   - `_leidos_no_seleccionados/`;
   - `*_seleccionados.ris`;
   - la matriz `Matri*.xlsx`, el `*_PRISMA_2020.png` y `scopus_*.csv`.
   Antes de armar el paquete:
   - PDF sueltos con nombres del editor (p. ej. `jrfm-17-00366.pdf`): suelen ser duplicados. Compáralos por texto con los organizados y muévelos a `_duplicados/`, sin borrarlos.
   - Verifica que cada PDF empiece con `%PDF`.
   - **Artículos no recuperados:** créalos o actualízalos en `literatura/por_descargar.json`, con `prioridad` («Recomendado (Parte X)» u «Opcional»), `referencia` (APA), `enlace` (DOI o URL probada) y `nota` (motivo y utilidad).
2. **Ejecuta:**
   `python scripts/armar_paquete.py <literatura> <proyecto>/<Nombre_Carpeta_Evidencias> --titulo "…" --extra <anexo1> <anexo2>`
   Si la guía fija un nombre de carpeta, úsalo; por ejemplo, `Sistemas_Costeo_Grupo_J_Evidencias`. Si pide una subcarpeta con un nombre exacto (p. ej. `Metadatos_RIS`), respétalo.
3. **Controles de calidad** (el script los imprime):
   - por cada parte, número de PDF = número de registros RIS; si no coinciden, falta un PDF o un RIS;
   - `Referencias_consolidadas.ris` tiene tantos registros `ER  -` como referencias tiene el documento;
   - `LEEME.txt` explica cada carpeta y cómo compartir.
4. **Enlace de Drive:**
   - lo sube y lo copia la usuaria;
   - en el documento deja un marcador `==[PEGAR AQUÍ EL ENLACE PÚBLICO DE LA CARPETA DE GOOGLE DRIVE]==` (resaltado en amarillo con `word_apa`) en cada lugar que pida la guía, normalmente al final de las referencias y en los anexos;
   - dile cuántos marcadores hay y cómo encontrarlos (Ctrl+B, «PEGAR AQUÍ»).
5. Envía a la usuaria `LEEME.txt` y `Articulos_por_descargar_manualmente.txt`, y abre la carpeta en el Explorador si la herramienta está disponible.

## Zotero
- Importar: en Zotero, Archivo → Importar → `Metadatos_RIS/Referencias_consolidadas.ris` → «Colocar en una nueva colección».
- Para adjuntar los PDF, arrástralos sobre cada registro, o usa «Buscar PDF disponible».
- La conexión directa con Zotero (API local) llega en la versión 1.1 del plugin.
