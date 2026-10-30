---
name: revision-sistematica
description: 'Revisión sistemática PRISMA 2020: palabras clave, ecuaciones Scopus, cribado, PDF de acceso abierto y lectura con puntaje. Usar al buscar literatura, hacer estado del arte o trabajar con Scopus.'
---

# Revisión sistemática (pipeline PRISMA con controles de calidad)

La usuaria es investigadora. Lo esencial para ella:
- que cada artículo citado se haya **leído de verdad**;
- que la selección quede **documentada y defendible**.

El trabajo avanza como un pipeline: cada etapa tiene un **control de calidad**. No pases a la siguiente sin cumplirlo, y anota el avance en `00_Control_Proyecto.md` del proyecto.

## Herramientas

Las herramientas del **servidor MCP `literatura`** (de este plugin):

| Herramienta | Uso |
|---|---|
| `scopus_estado` | Primer paso: indica si hay clave de Elsevier, si la vista con resúmenes está disponible y si hay correo de contacto |
| `scopus_contar` | Conteos sin y con filtros (fase de identificación) |
| `scopus_exportar` | Guarda en disco el CSV de una ecuación, con resúmenes si la suscripción lo permite |
| `scopus_resumen` | Resumen de un artículo por EID o DOI |
| `openalex_doi`, `unpaywall_pdf` | Metadatos abiertos y enlace legal al PDF de acceso abierto |
| `descargar_pdf` | Guarda un PDF solo si el archivo empieza con `%PDF` |

Los scripts de esta skill están en `${CLAUDE_PLUGIN_ROOT}/skills/revision-sistematica/scripts/`. Más abajo, «`scripts/`» significa esa carpeta; escribe la ruta completa entre comillas al ejecutar.

| Script | Uso |
|---|---|
| `scopus_api.js` | Método del navegador (respaldo): `scopusBuscar(query, n)` y `scopusExportar(query, n, 'RIS'\|'CSV')` |
| `guardar_desde_navegador.py` | Decodifica CSV, RIS o PDF obtenidos en el Browser pane (`--b64`, `--json-key`) |
| `pdf_tools.py` | `oa` (PDF abiertos en OpenAlex) · `bajar` (descarga y verifica) · `texto` (texto con marcas `[[PAG n]]` y `_lectura.txt`) · `pagina` (ubica la página de una cita) |
| `inventario_pdf.py` | Cruza los DOI del corpus con los PDF de la carpeta (lee el DOI impreso en cada PDF, aunque el archivo tenga otro nombre) y detecta PDF dañados: `python inventario_pdf.py incluidos.csv --carpeta ARTICULOS_PDF` |

Skills hermanas del plugin:
- `nuevo-proyecto`: estructura del proyecto;
- `matrices-revision`: las 4 matrices y el diagrama PRISMA 2020;
- `redaccion-apa7`: redacción, citas y verificación;
- `paquete-evidencias`: carpeta para Drive y RIS para Zotero.

Agente: `lector-critico`, para leer PDF en paralelo cuando son muchos.

Consulta según haga falta:
- `referencias/variables-y-keywords.md`
- `referencias/ecuaciones-scopus.md`
- `referencias/criterios.md`
- `referencias/errores-conocidos.md`

## Criterios por defecto de la usuaria

Pregunta solo si el trabajo no los fija.
- Solo artículos (`DOCTYPE(ar)`), versión final (`PUBSTAGE(final)`), últimos 5 años en sentido estricto: en 2026, `PUBYEAR > 2021 AND PUBYEAR < 2027`.
- Inglés preferente, no rígido. Si el texto completo está en portugués o español y el artículo es pertinente, se usa. Queda registrado como excepción de idioma y la referencia lleva el título traducido entre corchetes.
- Acceso abierto: no se filtra de entrada, pero se prioriza al seleccionar. **Modo estricto (opcional, si el trabajo exige que todo lo citado sea verificable por cualquiera):** todo DOI del corpus debe ser de acceso abierto y tener su PDF descargado. Un DOI cerrado, o abierto cuyo PDF no se pudo obtener, no se cita: se excluye con el código **E-OA** («sin acceso abierto verificado») y se busca un reemplazo abierto. Para el filtro en Scopus añade `AND OPENACCESS(1)` a la cadena.
- Excluidos: revisiones de literatura, bibliométricos, casos docentes, congresos, libros y capítulos.
- Prioridad temática según la carrera: en Economía, contabilidad, economía y empresas antes que salud o agro.
- Nunca resuelvas CAPTCHAS ni pidas a la usuaria que insista: el artículo se registra como «No recuperado».

## Etapa 0 · Protocolo

Si el proyecto no tiene estructura, usa la skill `nuevo-proyecto`. Escribe en `protocolo.md`:
- el tema;
- la pregunta;
- los objetivos;
- las **preguntas Q1…Qn** que la literatura debe sustentar. Todo se puntúa contra ellas.

**Control:** las preguntas están escritas y la usuaria las aprobó.

## Etapa 1 · Variables y palabras clave

Sigue `referencias/variables-y-keywords.md`:
1. Identifica variables y dimensiones.
2. Tradúcelas a **conceptos en inglés** con sus sinónimos. Usa tesauros: JEL para Economía, UNESCO y los términos de indización de Scopus.
3. Arma bloques `OR` por concepto y únelos con `AND`, con `TITLE-ABS-KEY` y los filtros (`referencias/ecuaciones-scopus.md`).
4. Si la guía del trabajo trae una ecuación asignada, córrela **tal cual** primero, aunque dé 0 resultados.

**Control:** cada variable tiene su bloque `OR`; los bloques están unidos con `AND`; hay una tabla de conceptos en el protocolo.

## Etapa 2 · Búsqueda en Scopus → Matriz 1

1. Llama a `scopus_estado`.
   - **Si hay clave (vía preferida, autorizada):**
     - `scopus_contar` sin filtros y con filtros para cada ecuación;
     - luego `scopus_exportar` a `literatura/B<n>_<tema>/scopus_B<n>.csv`, con `etiqueta_busqueda` = B<n>.
     - **Resúmenes.** Sin la red de la UNEMI ni un token institucional, la API solo entrega la vista STANDARD, sin resúmenes, y `scopus_resumen` también devuelve 401. Es la situación más común. Completa los resúmenes en este orden:
       1. `openalex_doi` para cada registro con DOI: devuelve el resumen de la mayoría de los artículos. Guárdalo en la columna `Abstract` del CSV.
       2. Los que sigan sin resumen: `scopusBuscar` en el navegador con la sesión de la usuaria (método de respaldo, más abajo), usando una ecuación `EID(…) OR EID(…)`.
       3. Si la API sí entrega resúmenes (en la red UNEMI o con token), no hace falta nada de lo anterior.
   - **Si no hay clave o la API falla:** usa el método del navegador.
     - Abre `https://www.scopus.com/pages/home#basic` en el Browser pane y pide a la usuaria que inicie sesión ella misma. Nunca escribas credenciales.
     - Confirma que ya no dice «Scopus Preview».
     - Pega `scripts/scopus_api.js` con `javascript_tool`.
     - Ejecuta `scopusBuscar(q, 1).total` para los conteos y `scopusBuscar(q, 200)` para los registros.
     - Guarda con `guardar_desde_navegador.py`.
     - Recuérdale una vez que la API oficial es la vía recomendada: se configura en el plugin con su clave de dev.elsevier.com.
2. Registra en la matriz, para cada ecuación: base, ecuación, filtros, **fecha**, **método (API o navegador)** y conteos.
3. Elimina duplicados entre ecuaciones por EID. Marca en la columna `Previo` los registros ya cribados en búsquedas anteriores del mismo proyecto.
4. Si la usuaria se asusta por miles de resultados, explícale que esa es solo la cifra sin filtros de la fase de identificación.

**Control:** conteos con fecha y método registrados; CSV guardado; duplicados contados.

## Etapa 3 · Cribado por título y resumen → Matriz 2a y 2b

- Criba **todos** los títulos. Cada exclusión lleva un **código y motivo** (`referencias/criterios.md`: E1 fuera de tema… E8).
- Las reglas automáticas con expresiones regulares:
  - se aplican **solo al título**;
  - usan límites de palabra;
  - el criterio de caso docente (E5) se aplica al **nombre de la revista**;
  - revisa siempre una muestra.
- Lee los resúmenes de los que pasan. Excluye con motivo. Pasan a texto completo los que anticipan un aporte directo a alguna Q; normalmente son de 8 a 13 por búsqueda.

**Control:** el número de registros cribados es igual al de registros únicos; ninguna exclusión queda sin motivo.

## Etapa 4 · Texto completo

1. Busca el PDF en este orden:
   - `openalex_doi` (o `unpaywall_pdf` si hay correo) → `descargar_pdf`;
   - si no, `python scripts/pdf_tools.py oa DOI…` y `bajar`.
2. Si el sitio bloquea la descarga directa (Cloudflare en MDPI, EconStor o Springer), usa el Browser pane:
   - `navigate` a la página del artículo;
   - lee `meta[name="citation_pdf_url"]`;
   - haz `fetch` desde el mismo origen y pásalo a base64;
   - guárdalo con `guardar_desde_navegador.py --b64`.
3. Revistas OJS sin DOI: usa el buscador de la revista o el índice del número.
4. Si aparece un CAPTCHA o el acceso es restringido, registra el artículo como **«No recuperado»**. Añádelo a `literatura/por_descargar.json` con prioridad, referencia, enlace y nota.
5. Nombra los archivos `Autor_Año_Tema_corto.pdf`.

**Control:** cada PDF empieza con `%PDF`; los no recuperados quedan anotados. Antes de cerrar la etapa, corre `python "${CLAUDE_PLUGIN_ROOT}/skills/revision-sistematica/scripts/inventario_pdf.py" <dois.txt o incluidos.csv> --carpeta <carpeta_pdf>`: debe terminar en 0 (todos los DOI incluidos tienen su PDF legible). En modo estricto, los que falten se excluyen con E-OA.

## Etapa 5 · Lectura a fondo, puntaje y síntesis → Matrices 2c, 3, 4 y PRISMA

- Lee **antes de seleccionar**:
  - ejecuta `pdf_tools.py texto <carpeta_pdfs> <carpeta_temporal>`;
  - lee cada `_lectura.txt` completo;
  - si falta el marco teórico o el método, busca por palabra clave en el `.txt` completo.
- Con 6 o más PDF, delega en el agente `lector-critico`: un PDF por tarea, en paralelo. Revisa lo que devuelve antes de pasarlo a la matriz.
- Para cada artículo registra en M3:
  - objetivo, **muestra o población**, método;
  - hallazgos con cifras;
  - **limitaciones** y **conclusiones**;
  - aporte a cada Q, parafraseado en español;
  - evidencia textual en el idioma original **con la página de la revista**, no la del PDF: usa `pdf_tools.py pagina` y el encabezado impreso.
- Distingue la idea propia del autor de lo que solo cita de otros.
- Puntúa de 0 a 2 por Q:
  - selecciona el conjunto de mayor puntaje que cubra **todas** las Q con al menos un 2, sin redundancias (suelen ser de 4 a 6 artículos);
  - decisiones posibles: Incluido, Elegible – no seleccionado (con motivo) o No recuperado;
  - un artículo ya incluido en otra parte del proyecto se puede reutilizar.
- Mueve los PDF leídos y no seleccionados a `_leidos_no_seleccionados/`.
- Arma las matrices con la skill `matrices-revision`. Genera M1–M4, el cruce autores × preguntas y el diagrama PRISMA 2020 en PNG. Envía el Excel a la usuaria antes de redactar.

**Control:** cada Q tiene al menos un artículo incluido con puntaje 2; las cifras PRISMA cuadran de etapa a etapa (el script falla si no cuadran).

## Etapas 6–8 · Redacción, verificación y entrega

- **6 · Redacción:** skill `redaccion-apa7`. Cada afirmación teórica lleva una cita que el artículo realmente respalda.
- **7 · Verificación:** `verificar_apa.py` sobre el documento. El control es 0 errores.
- **8 · Entrega:**
  - RIS de los incluidos: `scopusExportar('EID(…) OR EID(…)', n, 'RIS')` en el navegador, o arma el RIS desde los metadatos;
  - skill `paquete-evidencias`.
  - **Control:** el número de registros `ER  -` es igual al número de referencias del documento.

Al cerrar cada etapa, actualiza `00_Control_Proyecto.md`. Si la usuaria edita a mano un documento generado por script, compara su hash antes de regenerarlo e integra sus cambios.
