# Errores conocidos y cómo evitarlos

## Scopus
- **API oficial:**
  - la vista COMPLETE (con resúmenes) depende de la suscripción de la institución y de la red; fuera del campus hace falta el token institucional;
  - si no está disponible, `scopus_exportar` usa STANDARD y hay que completar los resúmenes con `scopus_resumen`;
  - las cuotas son semanales: consúltalas en dev.elsevier.com;
  - la clave y el token los escribe la usuaria en la configuración del plugin; nunca los escribas tú.
- **Método del navegador:**
  - la usuaria inicia sesión ella misma; si la página dice «Scopus Preview», la sesión no está iniciada;
  - no aceptes términos ni toques «Sign out».
- **Diálogo de exportación del sitio:** es frágil. Recuerda el último rango o vuelve a 10, a veces desmarca «Abstract» y un clic por coordenadas puede caer en el menú del perfil. Usa `scopusExportar` (API interna del sitio) o la API oficial.
- **URL de resultados:** al recargar agregan `offset=10`, y «All documents on this page» exporta una página vacía.
- **Encuestas emergentes** (LeapSpace, feedback): ciérralas con la X.
- **Portapapeles:** algunos clics sintéticos disparan «Copy query». Avisa a la usuaria si pasa.
- **Términos de Elsevier:** prohíben robots que busquen o extraigan contenido del sitio de forma continua. La vía autorizada para automatizar es la API oficial. El método del navegador es solo un respaldo puntual, con la sesión de la usuaria.

## Descargas
- **Descargas nativas del Browser pane:** no son confiables. A veces no llegan a disco y a veces aparecen después, sueltas en la carpeta y con el nombre del editor (p. ej. `jrfm-17-00366.pdf`). Usa siempre fetch → base64 → `guardar_desde_navegador.py`. Antes de entregar, compara los sueltos con los organizados y muévelos a `_duplicados/`; no los borres.
- **Salida muy grande de `javascript_tool`:** se guarda en `tool-results/*.txt` como JSON doble. `guardar_desde_navegador.py` lo decodifica. Si la salida es chica, añade `pad: 'x'.repeat(200000)` para forzar que se guarde en archivo.
- **Sitios que devuelven 403 o HTML a curl** (Cloudflare en MDPI, EconStor, Springer): descarga desde el navegador con `citation_pdf_url` y fetch en el mismo origen.
- **CAPTCHA** (ScienceDirect, Wiley, Hrčak, Virtus Interpress): no lo resuelvas ni pidas a la usuaria que insista. El artículo queda como «No recuperado» y se ofrece una sola vez descargarlo desde su Chrome.
- **Ruta demasiado larga en Windows:** no ejecutes Python con el directorio actual dentro de carpetas temporales muy profundas.

## Metadatos y citas
- **DOI que no resuelve:** algunas revistas imprimen un DOI que nunca registraron. Verifícalo con `https://doi.org/api/handles/<doi>`; si da 404, la referencia usa la URL del PDF.
- **Revistas OJS sin DOI:** busca en el sitio de la revista (buscador o índice del número) y toma `citation_pdf_url`.
- **Idioma mal indexado:** Scopus marca como «English» artículos cuyo texto completo está en portugués o español. Revisa el PDF.
- **Página correcta:** la de la revista, no la del PDF. EconStor agrega una portada (página de la revista = página del PDF − 1); si el artículo empieza en la p. 219, página = 218 + página del PDF. Confírmalo con el encabezado impreso.
- **Reglas con expresiones regulares:** usa límites de palabra («relationship» coincidía con «ship»). El nombre de una revista («International *Review of*…») disparó la regla de revisiones; aplica las reglas solo al título.

## Windows
- Usa `PYTHONIOENCODING=utf-8` al imprimir títulos con tildes o comillas tipográficas.
- Para exportar Word a PDF y revisarlo a la vista: COM de Word (`ExportAsFixedFormat`) + PyMuPDF para renderizar las páginas.

## Aprendido en S9 Sistema de Costeo (2026-10-23)
- **`python -I` ignora `PYTHONIOENCODING`/`PYTHONUTF8`:** dentro del script usa `sys.stdout.reconfigure(encoding="utf-8")` y `encoding="utf-8-sig"` al leer los CSV de Scopus.
- **`sed` con `
` en el reemplazo mete un salto de línea real** y rompe las cadenas de Python: edita con Edit o con un `str.replace` en Python.
- **Guion dentro de una ecuación OMML** (`	ext{horas-máquina}`) se ve como signo menos: usar abreviatura (`hm`) o espacio.
- **Figura grande al final de la introducción** + salto de página de la plantilla = media página en blanco: mover la figura al inicio del desarrollo.
- **Scopus STANDARD** trae solo el primer autor: completar autores con OpenAlex; fuentes sin DOI cuyos autores no se pueden completar se descartan (APA exige todos).
- **PowerShell 5 lee .ps1 UTF-8 sin BOM como ANSI:** ejecutar los .ps1 con tildes con `pwsh`.

## Aprendido en S8/S9 Metodología (2026-10-23)
- **`scopus_resumen` da HTTP 401 fuera de la red UNEMI** (también por DOI): leer el resumen en OpenAlex y completar volumen/páginas en Crossref.
- **LibreOffice no está instalado en Windows** (el `soffice.py` de la skill pptx falla con `AF_UNIX`): exportar y mirar láminas con PowerPoint COM (`SaveAs(pdf, 32)`, `Slide.Export`).
- **`pptxgenjs` no está preinstalado**: `npm install pptxgenjs react-icons react react-dom sharp` en una carpeta del scratchpad.
- **pypdf falla en PDF con cifrado AES** («cryptography>=3.1 is required»): usar PyMuPDF.
- **La carátula del grupo puede traer el trabajo anterior** debajo de la portada y textos duplicados en cuadros de texto: cortar en el `sectPr` de la portada y reemplazar en todos los `w:t`.
- **Chrome headless con rutas de Windows**: pasar `cygpath -m` (barras normales) a `--screenshot` y a `file:///`.
- **El logo UNEMI del fondo de portada ocupa hasta ~30 % del alto**: el texto de la carátula empieza debajo.
- **Rótulos de datos en gráficos nativos usan el separador decimal del sistema**: escribir el valor con coma en la categoría.

## Aprendido en S15 Componente Práctico 2 (2026-10-24)
- **Datos en imagen dentro del PDF de la consigna:** el texto extraído no los trae. Renderizar la página con PyMuPDF y mirarla con Read antes de calcular.
- **Rúbrica con criterios de otra materia** (p. ej. «valuación y presupuesto de capital» en Costos): agregar un apartado breve que conecte el trabajo con ese criterio en vez de ignorarlo.
- **Porcentajes solo en el texto** restan en «Cálculos»: toda cifra calculada lleva ecuación OMML.
- **`*` dentro de celdas** se interpreta como cursiva en `rich()`: usar `∗`.
- **`python -c` con regex y comillas escapadas** en bash da conteos falsos: escribir el auditor como archivo .py.

## Aprendido en S9 Álgebra Lineal (2026-10-24)
- **PDF hecho con texto plano (reportlab) no sirve para matemática:** fracciones con «/», raíces sin barra, vectores sin flecha, ℝ/⊕/⊙ como cuadros. La usuaria exige Editor de ecuaciones: construir el .docx con OMML y exportar con Word.
- **Vector con flecha:** `<m:chr m:val="⃗"/>` (combinante); con `→` la flecha queda encima de la letra y parece tachada.
- **ℝ:** `<m:scr m:val="double-struck"/>` con `R`; el carácter ℝ se ve como R normal.
- **Parchear un script generado con `sed` por rangos de líneas** duplicó bloques: reescribir el script con Write.
- **Tareas «a mano»:** entregar la guía en Word/PDF para que la usuaria la copie a mano; recordarle escanear y subir el PDF a Moodle antes de la fecha.
