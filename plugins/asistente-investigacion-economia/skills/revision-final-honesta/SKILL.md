---
name: revision-final-honesta
description: 'Control final de un trabajo de Economía: consigna y rúbrica, páginas, cifras, citas, figuras y restos de plantilla, con informe honesto. Usar ante «¿está listo?» o «revísalo como el docente».'
---

# Revisión final honesta

La usuaria exige **verificación real**: nada se da por hecho sin comprobarlo (releer el archivo guardado, recalcular con un método independiente, renderizar el docx), y se dice abiertamente cuando algo falló.

## Lista de control
1. **Consigna**: cada literal del checklist (etapa 0) tiene su sección y evidencia; extensión mínima/exacta medida en el PDF (portada, índice y referencias no cuentan).
2. **Rúbrica**: mapa criterio→evidencia completo (`referencias/rubricas-tipicas.md`); la visualización incluye variedad pedida (barras, dispersión, cajas, diagramas).
3. **Citas**: `verificar_citas.py` sin referencias huérfanas; `verificar_apa.py`; solo fuentes verificadas por DOI; citas textuales ≤ 40 palabras con página.
4. **Cifras**: recalculadas; fuentes oficiales con fecha de consulta; «estimación propia» rotulada. Delegar en `verificador-cifras-economia` si hay muchas.
5. **Figuras y tablas**: PNG revisados a ojo; nada superpuesto ni cortado; rótulos APA y numeración consecutiva con referencias cruzadas correctas.
6. **Documento**: sin restos de plantilla, comentarios ni cambios; ecuaciones nativas (`OMaths.Count`); ortografía; nombres de la carátula contra el plan; metadatos de autoría.
7. **Tono**: `referencias/tono-analitico.md` (resultados solo lo que muestran los datos, pasado, recomendaciones con mecanismo). Delegar en `revisor-rubrica-economia` (no modifica; devuelve correcciones priorizadas).
8. **IA**: anexo de uso responsable presente (`uso-responsable-ia`) y recordatorio de que cada integrante revise y asuma su sección.

## Informe final (siempre estas líneas, en español, sin adornos)
- **Qué se entregó** y dónde (rutas).
- **Qué se verificó** (páginas del cuerpo, ecuaciones nativas, citas, figuras).
- **Qué se leyó realmente**: PDF leídos / solo resumen / solo título y palabras clave; cribado asistido por reglas.
- **Qué se descartó** y por qué (fuentes de compañeros fuera de Scopus, no recuperados).
- **Borradores de otros integrantes** (secciones o conclusiones personales redactadas por el asistente) que deben reescribir.
- **Qué debe confirmar ella**: nombres de la carátula, enlace de Drive, indexación Scopus, declaración de IA, Turnitin.
- **Qué no se hizo** (subida a Drive, envío a la plataforma).
