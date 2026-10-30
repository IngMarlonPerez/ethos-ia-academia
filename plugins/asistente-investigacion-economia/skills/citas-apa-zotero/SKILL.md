---
name: citas-apa-zotero
description: 'Citas y referencias APA 7 de Economía: verifica cada DOI, arma la lista y el .ris para Zotero, y revisa cita↔referencia. Usar al pedir citar, normas APA, el .ris, Zotero o revisar las citas.'
---

# Citas, referencias APA 7 y RIS para Zotero

Normas: `${CLAUDE_PLUGIN_ROOT}/referencias/citas.md`, `lista-referencias.md`, `adaptacion-espanol.md`, `formato-documento.md`, `perfil-unemi.md`.

## Pasos
1. **Verificar cada fuente por DOI** (Scopus: búsqueda `DOI(a) OR DOI(b)…`; OpenAlex/Crossref para autores completos, volumen y páginas). Las fuentes que no estén en Scopus no se citan (se documentan en «Descartadas»). **Nunca citar una referencia que no se haya verificado**: los compañeros pueden aportar referencias inexistentes.
2. **Lista APA 7** en `referencias_apa.py` (una lista única para documento, matriz y RIS). Año = año del volumen; autores hasta 20; título del artículo en minúscula tipo oración, revista y volumen en cursiva, DOI como `https://doi.org/…`; título original + título traducido entre corchetes si el artículo está en otro idioma; obras originales (libros) con año de la edición citada.
3. **Citas en el texto**: paréntesis con «&» (Autor & Autor, año) y narrativa con «y» (Autor y Autor, año); «et al.» desde 3 autores. Citas textuales ≤ 40 palabras entre comillas con página; paráfrasis sin comillas. Cada afirmación teórica con una cita que el artículo realmente respalda (resumen o PDF leído; declarar el nivel de lectura).
4. **RIS para Zotero**: `python -I "${CLAUDE_PLUGIN_ROOT}/scripts/ris_zotero.py" <config_trabajo.py>` → `referencias_incluidas_zotero.ris` (artículos + libros) y `referencias_elegibles_no_seleccionadas.ris`. Antes, `enriquecer_openalex.py` para resúmenes y autores completos. La usuaria importa el RIS (Archivo → Importar) y **reemplaza las citas del texto a mano, una por una**, con el complemento de Word de Zotero (estilo APA 7).
5. **Verificar**: `scripts/verificar_citas.py <docx>` (cita↔referencia: cero referencias sin cita), `scripts/verificar_apa.py` (formato) y `scripts/similitud.py` (originalidad / Turnitin < 10 %).
6. Siguiente: `paquete-evidencias-economia`.
