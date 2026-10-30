# Asesor de Proyecto de Titulación de TI

Plugin de Claude (Claude Code, app de escritorio) que acompaña un **proyecto de titulación de Tecnologías de la Información** de principio a fin. Funciona como un **pipeline con controles de calidad**, igual que el Asistente de Investigación Científica: cada etapa tiene una skill y un control, y ninguna se cierra con el control pendiente.

Nació de los Avances 1 y 2 de la tesis *VicMar Data AI* (UNEMI, 2026). Todo lo que funcionó ahí es ahora una skill reutilizable:
- la búsqueda en Scopus;
- la lectura a fondo antes de seleccionar;
- los 10 o más trabajos previos con posición crítica;
- los requerimientos por componente;
- CRISP-DM, UML y el diccionario de datos;
- el código con resultados reales;
- el Word generado desde la plantilla oficial;
- la verificación de coherencia.

Además agrega tres cosas que en esa tesis faltaron:
- comparar **al menos 3 opciones por cada decisión tecnológica** (lenguaje, framework, base de datos…);
- comparar **al menos 3 estilos de arquitectura** (capas, desacoplada, microservicios…);
- **verificar en el código** que la arquitectura implementada es la declarada.

Autoría: Ethos IA (ETHOSLAB S.A.S.). Versión 1.5.0.

## Requisito: el Asistente de Investigación Científica
El Asesor **reutiliza** ese plugin, del mismo catálogo `ethos-ia-academia`, para:
- Scopus (API oficial o navegador), PRISMA y las 4 matrices de revisión;
- la lectura crítica de PDF (agente `lector-critico`);
- la redacción y verificación APA 7 (`redaccion-apa7`, `verificar_apa.py`, agente `revisor-apa`);
- el paquete de evidencias para Drive y Zotero.

No duplica nada: si falta, el Asesor lo avisa.

## El pipeline
| Etapa | Skill | Sección (UNEMI) | Control |
|---|---|---|---|
| 0 Inicio | `iniciar-titulacion` | — | Perfil confirmado; plantilla oficial copiada intacta |
| 1 Planteamiento | `planteamiento-y-objetivos` | Resumen, 1.1, 1.2 | Objetivos con Bloom y qué/cómo/para qué |
| 2 Literatura | `revision-sistematica` (investigación) → `trabajos-previos` | 1.3 | ≥ 10 trabajos leídos completos, con página, Arquitectura y Tecnologías |
| 3 Requerimientos | `analisis-requerimientos` + `proteccion-datos` | 2.1 | Trazabilidad objetivo → HU → RF → prueba |
| 4 Tecnologías | `seleccion-tecnologica` | 3.3 (a) | ≥ 3 candidatas por decisión; sensibilidad; ADR |
| 5 Arquitectura | `decision-arquitectura` | 3.2 (a) | ≥ 3 estilos; ADR; código = arquitectura declarada |
| 6 Metodología | `metodologia-desarrollo` | 3.1 | Cada fase con su entregable en el repositorio |
| 7 Diseño | `diseno-uml-datos` | 3.2 (b), (c) | UML exigidos; diccionario desde el esquema real |
| 8 Desarrollo | `desarrollo-y-evidencias` | 3.3 (b), (c) | Cifras solo de artefactos; pruebas en verde |
| 9 Conclusiones | `conclusiones-recomendaciones` | 4 | Una conclusión medida por objetivo |
| 10 Documento | `documento-titulacion`, `matrices-titulacion`, `verificar-coherencia` | todas | Verificador en 0; páginas mínimas |
| 11 Retroalimentación | `retroalimentacion-tutor` | — | Cada observación atendida y registrada |
| 11b Presentación del avance | `presentacion-avance` | — | Una diapositiva por apartado exigido; guion en primera persona dentro del tiempo |
| 11c Video técnico | `video-tecnico` | `gen_codetour.py` | Código auditado y comentado, recorridos CodeTour que abren la línea exacta, guía de 15 a 20 min en primera persona con cifras trazables, pasos de actualización desde GitHub, ensayo cronometrado |
| 11c-2 Guion técnico del video | `video-tecnico` (sección 6b) | `gen_guion_docx.py` | Guion centrado en el código por segmento, con tiempos por palabras (15 a 20 min), glosario y preguntas del tribunal, en Word y PDF |
| 11e Manual de arquitectura | `manual-arquitectura-tribunal` (agente `cartografo-arquitectura`) | `gen_manual_arquitectura.py`, `docx_a_pdf.ps1` | Componentes, archivos clave con línea, cifras desde los artefactos, recorrido de la demostración y preguntas del tribunal, en Word y PDF |
| 11d Estudio con audio | `resumen-audio-notebooklm` | — | Prompt de NotebookLM (versión larga y corta) que recorre arquitectura, trabajos previos, tecnologías comparadas y preguntas del tribunal, solo con lo que dice el documento |
| 11e Arranque y entrega del código | `arranque-un-comando` (+ agente `preparador-entrega-codigo`) | `plantillas/dev.mjs` | `npm run dev` levanta todo con Docker y carga los datos de prueba; `npm test`; VS Code ordenado; commit con la autoría de la autora y zip limpio para Drive |
| 12 Entrega | `entrega-y-sustentacion` (+ `paquete-evidencias`) | Anexos | Demo reproducible; carpeta completa |

La skill `asistente-titulacion-ti` (el **Asistente de proyecto de titulación de TI**) es la puerta de entrada: ubica el proyecto en el pipeline y deriva el trabajo a la skill que corresponde.

## Componentes
- **25 skills** (22 del pipeline y 3 transversales: `organizacion-repositorio`, `uso-etico-ia` y `publicacion-github`). Se activan solas según lo que pidas, o con `/asesor-proyecto-titulacion-ti:<nombre>`.
- **8 agentes:**
  - `auditor-arquitectura`: verifica la arquitectura en el código;
  - `evaluador-tecnologia`: puntúa una candidata con fuentes, uno por candidata en paralelo;
  - `revisor-tutor`: revisa el avance con la rúbrica de la universidad;
  - `revisor-tribunal`: simula al tribunal de sustentación, contrasta el documento con el repositorio y prepara las preguntas.
  - `cartografo-arquitectura`: manual de arquitectura del proyecto para el tribunal (componentes, archivos con línea, cifras reales y recorrido de la demostración), en Word y PDF.
  - `guionista-video-tecnico`: guion fluido del video técnico (10 a 15 min) con siglas y glosario, verificado en el repositorio.
  - `verificador-cumplimiento`: matriz Cumple / Parcial / Falta contra las consignas y rúbricas de cada tutora, con página.
  - `preparador-entrega-codigo`: deja el código listo para el tribunal con `npm run dev`, verificado en un proyecto aislado, y arma el zip limpio.
  - `redactor-continuacion-avance`: redacta una sección nueva del avance final sin tocar lo aprobado.
- **Perfil institucional** `perfiles/unemi.json`: secciones, mínimos de páginas, requisitos (10 trabajos previos, 20 referencias de los últimos 5 años, Resumen de 150 palabras), UML exigidos, carpeta de entrega y matrices oficiales. Para otra universidad, `perfil_desde_plantilla.py` propone un perfil leyendo su plantilla.
- **Scripts** (Python estándar + python-docx, openpyxl, pymupdf):

| Script | Qué hace |
|---|---|
| `iniciar_titulacion.py` | Estructura del proyecto |
| `tablero.py` | Estado del pipeline |
| `tabla_trabajos_previos.py` | Validación y conteos de los trabajos previos |
| `trazabilidad.py` | Validación de requerimientos y tablas de 2.1 |
| `matriz_decision.py` | Matriz ponderada, sensibilidad y ADR |
| `detectar_arquitectura.py`, `verificar_reglas.py` | Arquitectura real frente a la declarada |
| `anonimizar.py`, `buscar_secretos.py` | Privacidad |
| `renderizar_diagramas.py` | Mermaid → PNG con Edge o Chrome |
| `diccionario_datos.py` | Diccionario desde el esquema real |
| `docx_titulacion.py`, `generador_avance.py`, `docx_a_pdf.ps1` | El Word desde la plantilla oficial |
| `copia_trabajo.py`, `huella.py`, `diff_versiones.py`, `aserciones.py` | Copias versionadas, huella de portada y encabezados, restauración, comparación y correcciones que no se revierten |
| `copiar_biblioteca.py` | Copia la biblioteca del generador al proyecto (repositorio autocontenido) |
| `inventario.py`, `mover_a_revision.py` | Auditoría de la carpeta y código sin uso a revisión, sin borrar |
| `rastros_ia.py`, `anexo_uso_ia.py` | Sin rastros de herramientas de IA, autoría de Office y anexo de uso ético |
| `preparar_publicacion.py` | Controles antes de publicar en GitHub |
| `verificar_coherencia.py` | Control de calidad del avance |
| `matrices_titulacion.py` | Matrices metodológicas |
| `armar_entrega.py` | Carpeta de entrega |
| `presentacion_avance.py` | Presentación de un avance sobre la del avance anterior (mismo diseño) y guion en Word y Markdown |
| `diapositivas.py`, `poster.py`, `iconos.py`, `qa_pptx.py` | Diapositivas y póster A0 desde JSON, banco de íconos y control de calidad del PPTX |

## Instalación (local)
Requiere Python 3.10 o superior con `python-docx`, `python-pptx`, `openpyxl`, `pymupdf` y `Pillow`. Para los diagramas, Node.js con `@mermaid-js/mermaid-cli` en el proyecto. Para exportar el Word a PDF, Microsoft Word (o LibreOffice); para el PDF del póster y la revisión visual de las diapositivas, Microsoft PowerPoint o LibreOffice. Las fuentes Arial y Calibri (incluidas en Windows) se usan para medir el texto.
```
claude plugin marketplace add https://github.com/IngMarlonPerez/ethos-ia-academia
claude plugin install asistente-investigacion-cientifica@ethos-ia-academia --scope user
claude plugin install asesor-proyecto-titulacion-ti@ethos-ia-academia --scope user
```
Abre una sesión nueva. Los cambios del código del plugin se aplican al reinstalar o actualizar (`claude plugin update asesor-proyecto-titulacion-ti@ethos-ia-academia`).

## Uso
- «Quiero empezar mi proyecto de titulación de TI sobre …» → `asistente-titulacion-ti` e `iniciar-titulacion`.
- «¿Qué sigue en mi tesis?» → tablero y siguiente skill.
- «Busca y compara al menos 10 trabajos previos en Scopus» → `trabajos-previos` (con `revision-sistematica`).
- «¿Python, Java o Node para el backend?» → `seleccion-tecnologica`.
- «¿Microservicios o monolito? Verifica que el código lo cumpla» → `decision-arquitectura`.
- «Mis tutoras dicen: …» → `retroalimentacion-tutor`.
- «Genera el Word del Avance 2 y verifica la coherencia» → `documento-titulacion` y `verificar-coherencia`.

## Reglas que el Asesor respeta siempre
- Solo fuentes académicas (Scopus o DOI), verificadas en el texto completo. Nunca prensa.
- Leer antes de seleccionar.
- La arquitectura se evalúa en la literatura, en el diseño y en el código.
- Una sola fuente de verdad: ninguna cifra se escribe a mano.
- La plantilla oficial no se edita; el Word se trabaja en copias versionadas y la portada, los encabezados y los pies se verifican con una huella.
- Claude no escribe contraseñas ni envía datos personales a una IA externa.
- Commits y push solo con autorización; un solo commit limpio con los autores reales al publicar.
- La IA no es autora: no se nombra en el proyecto ni en los commits; se declara solo en un anexo local.
- Mover, no borrar: lo que sobra va a una carpeta de revisión con su índice.

## Privacidad
Ver [PRIVACY.md](PRIVACY.md).

## Créditos
Las piezas de versionado del Word, diapositivas, póster, íconos y control de similitud están adaptadas del plugin «proyectos-academicos» de Victor Manuel Lluilema Pisco. Los íconos son de [Lucide](https://lucide.dev) (licencia ISC, en `assets/iconos/LICENCIA_LUCIDE_ISC.txt`).
