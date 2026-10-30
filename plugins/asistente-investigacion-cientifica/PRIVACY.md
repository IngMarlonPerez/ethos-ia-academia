# Política de privacidad – Asistente de Investigación Científica

Última actualización: 28 de septiembre de 2026.

## Qué datos maneja
- **Claves que tú configuras** (API key y token institucional de Elsevier): se guardan en el almacén seguro de credenciales de tu sistema operativo mediante el `userConfig` de Claude. El plugin solo las envía a `api.elsevier.com`, en las cabeceras de cada consulta. No se escriben en disco ni aparecen en las respuestas.
- **Correo de contacto** (opcional): se envía solo a `api.unpaywall.org` (obligatorio para ese servicio) y a `api.openalex.org` (recomendado).
- **Consultas y archivos:** las ecuaciones de búsqueda, los DOI y los CSV, PDF y Excel que genera el plugin quedan en las carpetas de tu proyecto, en tu computadora.

## Servicios externos que consulta
| Servicio | Cuándo | Qué recibe |
|---|---|---|
| Elsevier Scopus APIs (`api.elsevier.com`) | Al buscar, contar, exportar o pedir un resumen | La ecuación o el identificador, tu API key y el token (si lo configuraste) |
| OpenAlex (`api.openalex.org`) | Al consultar un DOI | El DOI y, si lo configuraste, tu correo |
| Unpaywall (`api.unpaywall.org`) | Al buscar un PDF de acceso abierto | El DOI y tu correo |
| Sitios de editoriales y repositorios | Al descargar un PDF de acceso abierto | La URL del PDF |

Cada servicio aplica su propia política de privacidad. El uso de Scopus está sujeto a los términos de Elsevier y a la licencia de tu institución.

## Qué NO hace
- No envía datos a la autora del plugin ni a terceros distintos de los de la tabla.
- No recopila estadísticas de uso.
- No resuelve CAPTCHA ni evita controles de acceso de ningún sitio.

## Retención y eliminación
Los datos de tus proyectos son archivos locales: los conservas o borras tú. Para eliminar las claves, vacía los campos en la configuración del plugin o desinstálalo.

## Contacto
Ethos IA (ETHOSLAB S.A.S.). Para dudas sobre el plugin, abre un aviso en su repositorio cuando se publique.
