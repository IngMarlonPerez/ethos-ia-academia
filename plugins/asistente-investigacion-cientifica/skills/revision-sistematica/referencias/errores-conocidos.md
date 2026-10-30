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
