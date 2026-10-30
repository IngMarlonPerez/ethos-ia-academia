# Asistente de Investigación Científica en la Economía

Plugin de Claude Code para **trabajos académicos de Economía** (UNEMI y similares), nacido de los proyectos reales de Historia del Pensamiento Económico, Macroeconomía, Microeconomía, Sistema de Costeo y Metodología de la Investigación.

> Es **independiente** del plugin `asesor-proyecto-titulacion-ti` (proyectos de titulación de TI) y del genérico `asistente-investigacion-cientifica`. No necesita ninguno de los dos.

## Qué hace
De la consigna al Word entregado y la carpeta para Drive:

| Etapa | Skill |
|---|---|
| Entrada y ruta del trabajo | `asistente-economia` |
| Estructura, respaldo de plantilla y tablero | `iniciar-trabajo` |
| Consigna, rúbrica, plan y borradores de compañeros | `leer-consigna-rubrica` |
| Scopus por áreas de la economía, OpenAlex, PDF abiertos | `buscar-literatura-economia` |
| Selección con puntaje 0–2, M1–M4 y PRISMA | `matriz-consistencia` |
| Introducción CARS, metodología, secciones, conclusiones | `redactar-trabajo-teorico` |
| Ejercicios con ecuaciones nativas de Word | `ejercicios-con-ecuaciones` |
| Álgebra Lineal: vectores y espacios vectoriales con ecuaciones nativas | `algebra-lineal-vectores` |
| Datos de Ecuador (BCE, INEC, Banco Mundial) y ciclo del PIB | `datos-macro-ecuador` |
| Figuras sin textos superpuestos | `graficos-economia` |
| Word sobre la plantilla y PDF con Word real | `armar-documento-unemi` |
| APA 7, verificación por DOI, RIS para Zotero | `citas-apa-zotero` |
| Carpeta de evidencias para Drive | `paquete-evidencias-economia` |
| Control de calidad e informe honesto | `revision-final-honesta` |
| Anexo de uso responsable de la IA | `uso-responsable-ia` |

Agentes: `lector-critico-economia`, `revisor-rubrica-economia`, `verificador-cifras-economia`.
Servidor MCP `literatura`: Scopus (API de Elsevier), OpenAlex y Unpaywall; solo biblioteca estándar de Python.

## Instalación
```
/plugin marketplace add https://github.com/IngMarlonPerez/ethos-ia-academia     (si aún no está agregado)
/plugin install asistente-investigacion-economia@ethos-ia-academia
/plugin configure asistente-investigacion-economia
```
La clave de Elsevier la escribe la usuaria en `/plugin configure` (o en la variable de entorno `SCOPUS_API_KEY`); el asistente nunca escribe ni pide contraseñas. Requisitos: Python 3.10+ con `python-docx`, `lxml`, `openpyxl`, `matplotlib`, `numpy`, `pymupdf`, `pillow`; Microsoft Word para exportar PDF por COM.

## Reglas incorporadas (de las correcciones reales de la usuaria)
Scopus de los últimos 5 años estrictos (con excepciones documentadas), leer antes de juzgar pertinencia, verificar antes de dar por hecho, solo fuentes académicas con DOI, plantilla y carátula intactas, fórmulas en el Editor de Ecuaciones, gráficos sin texto superpuesto, informe final honesto y anexo de uso responsable de la IA. Detalle en `referencias/reglas-de-la-usuaria.md`; tono para resultados y conclusiones en `referencias/tono-analitico.md`.

## Ejemplos completos
- `ejemplos/hpe_grupo11/`: Historia del pensamiento económico (15 puntos): 16 páginas, 43 referencias, 6 figuras, matriz PRISMA, RIS.
- `ejemplos/macro_s6/`: Macroeconomía Básica de Ecuador (PIB, VAB, BCE, ciclo).
- `ejemplos/micro_elasticidad/`: ejercicios de elasticidad con ecuaciones OMML.

## Flujo mínimo (línea de comandos, lo que hacen las skills)
```
python -I scripts/iniciar_trabajo.py "<carpeta>" --tema "…" --autora "Grupo N" --plantilla "<plantilla.docx>"
# … búsqueda en Scopus (herramientas MCP) → editar config_trabajo.py …
python -I scripts/enriquecer_openalex.py <openalex.json> <csv…> --correo <correo>
python -I scripts/matriz_consistencia.py <config_trabajo.py>
python -I scripts/ris_zotero.py <config_trabajo.py>
python -I scripts/graficos_busqueda.py <config_trabajo.py>
python -I scripts/exportar_pdf_word.py "<documento.docx>" --miniaturas
python -I scripts/verificar_citas.py "<documento.docx>"
```

Licencia MIT. Autoría: Ethos IA (ETHOSLAB S.A.S.).
