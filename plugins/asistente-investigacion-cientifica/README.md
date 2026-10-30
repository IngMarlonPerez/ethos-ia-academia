# Asistente de Investigación Científica

Plugin de Claude (Claude Code, app de escritorio y Cowork) que convierte una revisión de literatura en un **pipeline con controles de calidad**, como un CI/CD pero de investigación científica.

Recorre todo el camino, de la pregunta de investigación al documento terminado:
- identifica variables y palabras clave;
- busca en **Scopus**;
- aplica criterios de inclusión y exclusión;
- descarga los PDF de acceso abierto y los lee a fondo;
- arma las **4 matrices de revisión** con el **diagrama PRISMA 2020**;
- redacta en **estilo APA 7.ª edición** y verifica cada cita contra su referencia.

Autoría: Ethos IA (ETHOSLAB S.A.S.). Versión 1.2.1.

## El pipeline
| Etapa | Qué hace | Control de calidad |
|---|---|---|
| 0 Protocolo | Pregunta, objetivos, preguntas Q1…Qn | Preguntas aprobadas |
| 1 Variables y keywords | Conceptos en inglés, sinónimos, tesauros (JEL, UNESCO), ecuación booleana | Un bloque OR por variable, unidos con AND |
| 2 Búsqueda en Scopus | API oficial de Elsevier o navegador con la sesión institucional → Matriz 1 | Conteos con fecha y método |
| 3 Cribado | Título y resumen con códigos de exclusión → Matriz 2 | Toda exclusión con motivo |
| 4 Texto completo | PDF de acceso abierto (OpenAlex, Unpaywall, editor) | Cada PDF verificado |
| 5 Lectura y síntesis | Lectura a fondo, puntaje 0–2 por pregunta → Matrices 3 y 4 + PRISMA | Todas las preguntas cubiertas |
| 6 Redacción APA 7 | Párrafos, citas, referencias, tablas, figuras y ecuaciones en Word | — |
| 7 Verificación | `verificar_apa.py` | 0 errores |
| 8 Entrega | Carpeta para Drive + RIS consolidado para Zotero | RIS = referencias |

## Componentes
- **Skills.** Se activan solas cuando la tarea coincide con su descripción, o con `/asistente-investigacion-cientifica:<nombre>`:
  - `nuevo-proyecto`: carpetas, protocolo y tablero de un trabajo nuevo;
  - `revision-sistematica`: el pipeline completo (etapas 0–8);
  - `matrices-revision`: las 4 matrices (búsqueda y registro, cribado, extracción y síntesis, temática o cruzada) y el diagrama PRISMA 2020;
  - `redaccion-apa7`: redacción académica, citas, referencias, formato y verificación en APA 7 adaptada al español;
  - `paquete-evidencias`: carpeta de evidencias para Drive y `Referencias_consolidadas.ris` para Zotero.
- **Agentes:**
  - `lector-critico`: lee un PDF y devuelve su fila de extracción, con evidencia y página;
  - `revisor-apa`: audita un documento contra APA 7 y la guía del trabajo.
- **Servidor MCP `literatura`.** Está escrito en Python estándar y no requiere instalar nada:
  - `scopus_estado`, `scopus_contar`, `scopus_exportar`, `scopus_resumen` (API oficial de Elsevier);
  - `openalex_doi`, `unpaywall_pdf`, `descargar_pdf`.

## Instalación (local)
Requiere Python 3.10 o superior, con `python-docx`, `openpyxl`, `pypdf`, `pymupdf` y `Pillow`.
```
claude plugin marketplace add https://github.com/IngMarlonPerez/ethos-ia-academia
claude plugin install asistente-investigacion-cientifica@ethos-ia-academia --scope user
```
Abre una sesión nueva y comprueba que aparece con `/plugin`. Los cambios en el código se aplican al iniciar la siguiente sesión, o con `/reload-plugins`.

## Configurar la API de Scopus (recomendado)
1. Entra en https://dev.elsevier.com, inicia sesión con tu **correo institucional** y crea una API key («Create API Key»). Es gratuita para uso académico no comercial.
2. En Claude: `/plugin` → pestaña **Installed** → «Asistente de Investigación Científica» → **Configure**. Escribe:
   - la clave de Elsevier;
   - opcionalmente, el token institucional (lo da la biblioteca; solo hace falta fuera de la red de la universidad);
   - opcionalmente, tu correo de contacto (lo usan Unpaywall y OpenAlex).
   - **Alternativa** si esa ventana no aparece en tu app: crea las variables de entorno de Windows `SCOPUS_API_KEY` y, si hace falta, `SCOPUS_INSTTOKEN`. Ve a Inicio → «Editar las variables de entorno de su cuenta» → Nueva. Luego reinicia Claude.
3. Las claves se guardan cifradas en el almacén seguro del sistema (o en tus variables de usuario de Windows, si usas la alternativa); nunca en archivos del plugin ni del proyecto.
4. Prueba: pide «revisa el estado de la conexión con Scopus» (herramienta `scopus_estado`).

Sin clave, el asistente usa el método del navegador: abre Scopus en el navegador de la app, tú inicias sesión y la búsqueda sigue desde tu sesión. Los términos de Elsevier restringen la automatización del sitio web, por eso la API oficial es la vía recomendada.

## Uso
- «Quiero empezar una revisión sobre costos de producción y rentabilidad en pymes»: `nuevo-proyecto`, luego `revision-sistematica`.
- «Hazme las matrices de esta búsqueda»: `matrices-revision`.
- «Redacta el marco teórico en APA con los artículos incluidos» o «revisa las citas de este Word»: `redaccion-apa7` y el agente `revisor-apa`.
- «Deja todo listo para subir a Drive»: `paquete-evidencias`.

## Zotero
Importa `Metadatos_RIS/Referencias_consolidadas.ris` con Archivo → Importar. La conexión directa con Zotero llega en la versión 1.1.

## Privacidad
Ver [PRIVACY.md](PRIVACY.md). En resumen:
- el plugin corre en tu computadora;
- consulta Elsevier, OpenAlex y Unpaywall solo cuando se lo pides;
- no recopila ni envía datos a la autora ni a terceros.

## Próximas versiones
- 1.1: conexión directa con Zotero (API local) y más bases (Web of Science, SciELO, PubMed).
- 2.0: servidor remoto con inicio de sesión (OAuth) para el chat web, el celular y otras IA compatibles con MCP; publicación en el directorio de Anthropic.
