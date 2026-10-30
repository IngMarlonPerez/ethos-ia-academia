# Changelog

## 1.3.1 – 29 de octubre de 2026
- **Menos tokens por sesión:** las descripciones de las skills y los agentes se acortaron a unos 200 caracteres, conservando las frases que las activan. Así se cargan completas en cada sesión y no se recortan por falta de espacio.

## 1.3.0 — 2026-10-24
- Nueva skill `algebra-lineal-vectores`: tareas de Álgebra Lineal (combinaciones lineales, producto punto, norma, ángulo, 10 axiomas de espacio vectorial) con toda la notación en ecuaciones nativas de Word, análisis por ejercicio según la rúbrica, verificación con Python y entrega .docx + PDF.
- `scripts/mathlib.py` ampliado: `\vec`, `\sqrt`, `^`, `\left\|…\right\|`, `\mathbb{R}`, `\alpha \beta \theta`, `\oplus \odot \in`, `\cos \arccos`, signo menos real. Compatible con los ejemplos anteriores.
ight\|`, `\mathbb{R}`, `lpha eta 	heta`, `\oplus \odot \in`, `\cos rccos`, signo menos real. Compatible con los ejemplos anteriores.
- Ejemplo `ejemplos/algebra_lineal_s9/` (S9-Tarea 2) con su PDF de salida y `figuras.py` (ángulo entre vectores y vectores paralelos) incrustadas en el Word.
- Errores conocidos: flecha de vector tachada con `→`, ℝ sin doble trazo, PDF de texto plano sin notación matemática.

## 1.2.0 — 2026-10-24
- Nueva skill `deber-integrador-costos`: costo por orden y hoja de costos, tasas y asignación ABC, clasificación ABM, etapas de decisión, pedido especial con costos relevantes, precio con margen sobre el costo, informe a la gerencia y auditoría al 100 % contra consigna y rúbrica.
- Ejemplo `ejemplos/costeo_s15/` con `04_auditar_formato.py` (fuente, tamaño, interlineado y alineación del Word).
- Errores conocidos: tablas de datos como imagen en el PDF de la consigna, rúbricas con criterios copiados de otra materia, `*` en tablas.

## 1.2.0 — 2026-10-23
- Nueva skill `diapositivas-tema-economico`: tema elegido con conteos de Scopus, datos oficiales verificados en el sitio del INEC, fondos y colores tomados del .pptx de la docente, logo de la carrera en cada lámina, 9 láminas según la consigna y exportación con PowerPoint COM.
- Nueva skill `infografia-citas-textuales`: citas literales de ~40 palabras desde el PDF completo con página impresa, infografía HTML → PNG con Chrome headless y Word sobre la carátula con referencias clicables.
- Ejemplos `ejemplos/diapositivas_s8/` y `ejemplos/infografia_s9/` (Metodología de Investigación Básica, Grupo 5).
- Nuevos errores conocidos (ver «Aprendido en S8/S9 Metodología»).

## 1.1.0 — 2026-10-23
- Nueva skill `costeo-cvu-ordenes-abc`: punto de equilibrio y CVU (manufactura y servicios), planeación de utilidades con participación laboral e IR de Ecuador, sensibilidad, hoja de costos por orden, ABC frente a reparto tradicional, cuadro comparativo, mapa mental y valoración de la realidad ecuatoriana.
- Ejemplo completo `ejemplos/costeo_s9/` (S9-Tarea 2, Grupo J).
- Nuevos errores conocidos: saltos de línea reales al editar con sed, `-I` ignora `PYTHONIOENCODING`, guion dentro de ecuaciones OMML, figura en la introducción con salto de página de la plantilla.

## 1.0.0 — 2026-10-13
Primera versión, construida a partir de los proyectos de Economía de la usuaria.
- 14 skills (entrada, inicio, consigna y rúbrica, búsqueda Scopus por áreas, matriz de consistencia, redacción teórica con introducción CARS, ejercicios con ecuaciones OMML, datos macro de Ecuador, gráficos verificados, ensamblaje Word/PDF, citas y RIS, evidencias, revisión final honesta, uso responsable de IA).
- 3 agentes: lector crítico, revisor de rúbrica, verificador de cifras.
- Servidor MCP `literatura` (Scopus, OpenAlex, Unpaywall) propio, con respaldo de variables de entorno.
- Scripts reutilizables: `matriz_consistencia`, `ris_zotero`, `graficos_busqueda` (con verificador de superposición), `exportar_pdf_word` (rutas largas), `verificar_citas`, `enriquecer_openalex`, `iniciar_trabajo`, `lib_docx`, `lib_figuras`, `mathlib`.
- Ejemplos completos: HPE Grupo 11, Macro S6, Micro (elasticidad).
