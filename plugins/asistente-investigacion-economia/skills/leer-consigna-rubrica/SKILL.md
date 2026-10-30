---
name: leer-consigna-rubrica
description: 'Lee la consigna, la rúbrica, el plan y los borradores del grupo, y produce el checklist de literales y el mapa rúbrica→evidencia. Usar cuando pase la tarea o diga «léelo y ten claro qué hay que hacer».'
---

# Leer la consigna y la rúbrica (pensar como economista senior)

1. **Extraer el texto**: PDF con texto → leerlo con Read (por páginas). PDF escaneado → `python -I "${CLAUDE_PLUGIN_ROOT}/scripts/pdf_a_texto.py" <pdf> <txt> 110` y leer las imágenes. Word → `scripts/volcar_docx.py` (salida UTF-8 a archivo; usar carpeta corta).
2. **Listar cada literal** de la consigna como checklist (cada punto, sub-punto, restricción de extensión, formato, citas, entrega, fecha). Anotar fechas internas del grupo y la oficial.
3. **Mapear la rúbrica a evidencias** con `referencias/rubricas-tipicas.md`. Si la rúbrica parece copiada de otra tarea (pide «base de datos», «diagramas de dispersión/caja» en un ensayo de historia), cumplirla igual con datos reales de Scopus y avisar a la usuaria.
4. **Leer el plan del grupo**: reparto por integrante, extensión por sección, cadenas Scopus asignadas, elementos visuales exigidos, política anti-plagio/IA, cronograma, checklist de entrega.
5. **Diagnosticar los borradores** de compañeros: palabras y páginas, citas sin referencia, referencias que no existen o no están en Scopus (verificar por DOI), cifras sin fuente, falta de variables definidas/políticas/visual, partes que faltan por completo (p. ej. la de un integrante que no entregó). Anotar qué se conserva y qué se reescribe.
6. **Dejar escrito** en `00_Control_Trabajo.md`: checklist, mapa rúbrica→evidencia, diagnóstico, decisiones pendientes.
7. **Si falta una sección que la consigna exige**, se redacta marcándola como «redactada por el asistente» y se avisa para que el grupo confirme.
8. Verificar los **nombres de la carátula** contra el plan (nombre completo de cada integrante; ella va primero con su ORCID).
9. Hacer una sola ronda de preguntas con AskUserQuestion solo para lo que no se deduzca (alcance, entrega, gráficos). Siguiente: `buscar-literatura-economia`.
