---
name: tarea-grupal-gestion-ti
description: 'Tarea grupal de Gestión de TI en Word: ITIL 4, COBIT e ISO 20000 por integrante, con KPI y APA 7. Usar con «tarea de Gestión de TI» o «plan de implementación con KPI».'
---

# Tarea grupal de Gestión de TI (Word sobre plantilla UNEMI)

Aprendida con la Tarea 2 de Gestión de TI (ITIL 4 aplicada a CNT EP). Sirve para cualquier tarea de la asignatura que **continúe** trabajos anteriores del grupo (Tarea 1, Trabajo de investigación) y se entregue en Google Docs / PDF con límite de páginas.

## Flujo
1. **Leer todo lo previo del grupo**: la consigna, los trabajos anteriores, el reparto por integrantes, los compendios de la unidad y las referencias del grupo. PDF a texto con `pdftotext -enc UTF-8 -layout` o `pymupdf`; los enlaces, con `page.get_links()`. Si `Read` con `pages` falla por falta de `pdftoppm`, usa texto.
2. **Plantilla**: guarda primero una copia intacta (`S8-TAREA_x_plantilla_original.docx`). La portada se conserva; solo se cambian TEMA y, avisando, la carrera. El cuerpo se genera con `scripts/ooxml.py` (párrafos, títulos, tablas, viñetas; Arial 12, interlineado sencillo, tablas en 8,5–10 pt) y se inserta con `scripts/ensamblar_plantilla.py`. Los valores decimales de la plantilla exportada de Google Docs rompen `python-docx`; por eso se edita el XML.
3. **Coherencia vertical** (lo que más puntúa): codifica los problemas heredados (p. ej. `GE-1`, `GE-2`, `GTI-1`, `GTI-2`) en una tabla de la introducción y cita el código en cada brecha, práctica, acción y KPI. Mantén el criterio de las tareas previas: separar lo documentado de lo propuesto o inferido.
4. **Responsable por subsección**: línea `Responsable: Nombre` bajo cada título, tomada del PDF de reparto. El cierre reflexivo lleva un párrafo por integrante.
5. **KPI concretos**: cifra + plazo + línea base. Si la línea base no existe en los estudios, se escribe «línea base: mes N» y las metas se declaran propuestas. Patrones: «reducir 30 % el tiempo de resolución de incidentes P1/P2 en 6 meses»; «100 % de plataformas críticas con RPO/RTO al mes 3»; «éxito de restauración ≥ 95 % desde el tercer trimestre».
6. **Citas**: solo fuentes del corpus ya verificado del grupo, la fuente primaria de la guía y los compendios (como «s. f.-a/b» si no tienen año). Usa los apellidos completos de la lista de referencias del grupo, no los alias de tareas anteriores. `verificar_apa.py` puede dar falsos positivos con AXELOS y «s. f.».
7. **Mide páginas con Word, no con LibreOffice**: `powershell -NoProfile -File scripts/render_word.ps1 "ruta.docx"` imprime las páginas y la página de «Bibliografía». El límite de la consigna (p. ej. 12) excluye bibliografía y anexos. Convierte el PDF a PNG con `pymupdf` y míralo: portada en 1 hoja, tablas partidas, títulos huérfanos.
8. **Tablas de acción**: `table(..., keep=True)` las mantiene unidas en una página.
9. **Anexo de IA aparte** (si la consigna lo permite): un `.docx` con tabla sección / aporte / limitaciones / verificación, honesto sobre qué fue inferencia y qué se verificó. Los enlaces pendientes van resaltados `==[pegar enlace]==`.
10. **Entrega**: sobrescribe el `.docx` pedido solo después de guardar la plantilla original; deja un PDF `_vista_previa`. Avisa: enlaces por pegar, cambio de carrera en la portada, metas propuestas, fuentes fuera de rango y borradores del cierre reflexivo para que cada integrante los adapte.

## Archivos
- `scripts/ooxml.py`: `h1, h2, resp, para, bullet, caption, nota, table`.
- `scripts/ensamblar_plantilla.py`: inserta el cuerpo tras la portada, con márgenes de 2,5 cm y viñetas.
- `scripts/render_word.ps1`: PDF y páginas con Word.
- `ejemplos/tarea2_itil_cnt_ep.py`: documento completo de ejemplo (11 páginas con portada, 6 acciones con KPI, ciclo Observar–Orientar–Actuar–Reflejar). Las rutas son de ejemplo.
- `referencias/itil4_gestion_ti.md`: guía de contenido ITIL 4 y trampas de terminología.

## Reglas
No inventes datos de la organización: lo no evidenciado se declara «no evidenciado, por verificar». No presentes metas como resultados. No cambies la portada de la plantilla sin avisar.
