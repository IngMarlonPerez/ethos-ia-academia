---
name: buscar-literatura-economia
description: 'Busca y exporta literatura de Economía en Scopus por API: conceptos JEL, ecuaciones OR/AND, conteos con filtros, OpenAlex y PDF abiertos. Usar al pedir artículos, Scopus o ecuaciones de búsqueda.'
---

# Buscar literatura de Economía en Scopus

Herramientas MCP del servidor `literatura` de este plugin: `scopus_estado`, `scopus_contar`, `scopus_exportar`, `scopus_resumen`, `openalex_doi`, `unpaywall_pdf`, `descargar_pdf`. Reglas: `referencias/reglas-de-la-usuaria.md`. Vocabulario por área: `referencias/areas-economia-busqueda.md`. Más detalle: `referencias/ecuaciones-scopus.md`, `variables-y-keywords.md`, `criterios.md`, `errores-conocidos.md`.

## Pasos
1. **`scopus_estado`**. Si falla la clave: la usuaria la configura (`/plugin configure` o la variable `SCOPUS_API_KEY`); nunca se escribe ni se pide su contraseña. Respaldo: Scopus en el navegador con su sesión institucional (`scripts/scopus_api.js` + `guardar_desde_navegador.py`).
2. **Cadenas del plan del grupo**: ejecutarlas **tal cual** (`scopus_contar`), aunque den 0; registrar el resultado.
3. **Variables → conceptos en inglés** (con sinónimos): un bloque OR por concepto, bloques unidos con AND, `TITLE-ABS-KEY`. Una ecuación por pregunta Q (B1…Bn).
4. **Filtros**: `DOCTYPE(ar) AND LANGUAGE(english)`; ventana `PUBYEAR > 2020 AND PUBYEAR < 2027` si ella exige 5 años (excepciones documentadas: historia del pensamiento fundacional, datos oficiales, libros del docente; idioma flexible).
5. **Conteos**: sin filtros y con filtros por ecuación, y por periodo (2000–2009, 2010–2019, 2020–2026) para la figura de barras. Guardar fecha y método.
6. **`scopus_exportar` con `max_registros` ≥ total** al CSV `01_Busquedas_Scopus/scopus_B<n>_<tema>.csv`. Exportar todo: de lo contrario el PRISMA queda falso.
7. **Verificar las fuentes aportadas por compañeros** con una búsqueda por DOI (`DOI(a) OR DOI(b)…`) exportada como `scopus_REFS…csv`: las que no figuren en Scopus se descartan y se documentan (hoja «Descartadas»).
8. **Completar con OpenAlex** (la API sin red UNEMI solo da STANDARD: sin resúmenes y con un solo autor):
   `python -I "${CLAUDE_PLUGIN_ROOT}/scripts/enriquecer_openalex.py" "<proyecto>/Evidencias_Drive/05_Base_datos/openalex_metadatos.json" <csv1> <csv2> … --correo <correo>`
9. **PDF de acceso abierto**: `openalex_doi` → `descargar_pdf` a `02_PDF_articulos/Autor_Año_Tema.pdf`. HTTP 403 o CAPTCHA → «No recuperado» en `por_descargar.md`, sin insistir. Verificar con `scripts/inventario_pdf.py`.
10. **Pendiente de confirmar**: lo preseleccionado por título/resumen es «pertinencia no confirmada» hasta leer el texto (o declarar el nivel de lectura). Siguiente: `matriz-consistencia`.

## Para la introducción
Buscar literatura sobre cómo se escribe una introducción (ecuación B6 de `areas-economia-busqueda.md`) y aplicar el modelo CARS: ver `redactar-trabajo-teorico`.
