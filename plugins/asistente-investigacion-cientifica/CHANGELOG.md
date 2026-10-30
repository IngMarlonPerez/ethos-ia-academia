# Registro de cambios

## 1.2.2 – 29 de octubre de 2026
- **Menos tokens por sesión:** las descripciones de las skills y los agentes se acortaron a unos 200 caracteres, conservando las frases que las activan. Así se cargan completas en cada sesión y no se recortan por falta de espacio.

## 1.2.1 – 10 de octubre de 2026
- **Menos tokens por sesión:** las descripciones de las 5 skills y los 2 agentes se acortan (~1.160 a ~540 tokens siempre activos), con los mismos disparadores. `nuevo-proyecto` y `paquete-evidencias` salían con menos de 20 tokens de listado; deberían verse completas (a confirmar).

## 1.2.0 – 10 de octubre de 2026
Adaptado del plugin «proyectos-academicos» de Victor Manuel Lluilema Pisco.
- `revision-sistematica`:
  - `inventario_pdf.py`: cruza los DOI del corpus con los PDF de la carpeta (lee el DOI impreso en cada PDF, aunque el archivo tenga otro nombre) y detecta PDF dañados; la carpeta del usuario solo se lee;
  - **modo estricto de acceso abierto** (opcional): todo DOI del corpus debe ser abierto y tener su PDF; si no, se excluye con el nuevo código **E-OA** (`referencias/criterios.md`).
- `redaccion-apa7`: `similitud.py`, control preventivo de similitud antes de Turnitin o Compilatio (8 palabras idénticas = falla; 35 % de trigramas compartidos = advertencia).
- Pruebas nuevas en `tests/`.

## 1.1.0 – 29 de septiembre de 2026
- Servidor `literatura`: si el plugin no tiene la clave configurada, usa las variables de entorno `SCOPUS_API_KEY` y `SCOPUS_INSTTOKEN` (también desde el registro de Windows).
- Scopus: paginación con `start` (el `cursor` está restringido para claves estándar).
- Resúmenes: OpenAlex primero; el navegador queda como respaldo.
- `verificar_apa.py`: ya no se cae al imprimir nombres con caracteres fuera de cp1252 en consolas de Windows.
- Lo usa como dependencia el plugin «Asesor de Proyecto de Titulación de TI».

## 1.0.0 – 28 de septiembre de 2026
Primera versión, construida a partir del procedimiento usado en el trabajo integrador S7 (Sistemas de Costeo, UNEMI).
- Pipeline de revisión sistemática PRISMA 2020 en 9 etapas, cada una con su control de calidad (skill `revision-sistematica`).
- Identificación de variables y palabras clave: esquemas PICO/PEO/SPIDER, tesauros JEL y UNESCO, plantillas de ecuaciones de Scopus.
- Servidor MCP `literatura`: Scopus Search y Abstract Retrieval (API oficial de Elsevier), OpenAlex, Unpaywall y descarga verificada de PDF.
- Las 4 matrices de revisión en Excel (M1 búsqueda y registro, M2 cribado, M3 extracción y síntesis, M4 temática y cruce autores × preguntas), con el diagrama PRISMA 2020 en PNG.
- Skill `redaccion-apa7`: citas, referencias, formato, estilo y adaptación al español; biblioteca `word_apa.py` y verificador `verificar_apa.py`.
- Paquete de evidencias para Drive y RIS consolidado para Zotero.
- Agentes `lector-critico` y `revisor-apa`.
