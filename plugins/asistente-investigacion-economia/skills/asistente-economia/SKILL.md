---
name: asistente-economia
description: 'Puerta de entrada del plugin de Economía: identifica el tipo de trabajo (teórico, ejercicios, datos de Ecuador, integrador) y deriva a cada etapa. Usar con una tarea de Economía UNEMI o «qué sigue».'
---

# Asistente de Investigación Científica en la Economía

Plugin **independiente** para trabajos de Economía. Los proyectos de titulación de TI tienen su propio plugin (`asesor-proyecto-titulacion-ti`): no mezclar.

## Paso 0 · Cargar las reglas
Lee `${CLAUDE_PLUGIN_ROOT}/referencias/reglas-de-la-usuaria.md` (literatura Scopus 5 años, leer antes de juzgar, verificar antes de dar por hecho, plantilla intacta, ecuaciones nativas, honestidad) y, si hay resultados o conclusiones por redactar, `referencias/tono-analitico.md`. Responde en español y nombra la skill en uso.

## Paso 1 · Clasificar el trabajo
| Si la tarea es… | Ruta |
|---|---|
| Ensayo/análisis teórico, examen práctico grupal (p. ej. Historia del pensamiento económico) | `iniciar-trabajo` → `leer-consigna-rubrica` → `buscar-literatura-economia` → `matriz-consistencia` → `redactar-trabajo-teorico` → `graficos-economia` → `armar-documento-unemi` → `revision-final-honesta` |
| Ejercicios numéricos (elasticidades, Slutsky, costeo, CVU, álgebra) | `leer-consigna-rubrica` → `ejercicios-con-ecuaciones` → (`buscar-literatura-economia` si piden citas) → `armar-documento-unemi` → `revision-final-honesta` |
| Álgebra Lineal: vectores, producto punto, ángulo, espacios vectoriales (tarea que pide cálculo y rúbrica) | `leer-consigna-rubrica` → `algebra-lineal-vectores` (Word con ecuaciones nativas + PDF) → `revision-final-honesta` |
| Investigación con datos de Ecuador (PIB, VAB, IPC, balanza, BCE) | `leer-consigna-rubrica` → `datos-macro-ecuador` → `buscar-literatura-economia` → `graficos-economia` → `armar-documento-unemi` |
| Investigación de Sistema de Costeo con empresas del Ecuador (punto de equilibrio/CVU, órdenes, ABC, cuadro comparativo) | `leer-consigna-rubrica` → `costeo-cvu-ordenes-abc` (incluye búsqueda, cálculos, figuras y Word) → `revision-final-honesta` |
| Deber integrador / componente práctico de Costos con ejercicios (orden de producción, ABC, ABM, pedido especial, precio) | `leer-consigna-rubrica` (mirar las tablas en imagen del PDF) → `deber-integrador-costos` → `revision-final-honesta` |
| Trabajo integrador por actividades (Costeo) | `iniciar-trabajo` (una actividad por iteración, con pausa de revisión) + las demás por actividad |
| Ensayo corto con páginas exactas (Metodología) | `buscar-literatura-economia` → `redactar-trabajo-teorico` → medir PDF |
| Diapositivas sobre un tema económico con plantilla UNEMI (carátula, tema, 5 de desarrollo, conclusión, referencias con DOI) | `leer-consigna-rubrica` → `diapositivas-tema-economico` → `revision-final-honesta` |
| Infografía con citas textuales de 40 palabras (autor, año, página) | `leer-consigna-rubrica` → `infografia-citas-textuales` → `revision-final-honesta` |
| Solo citas/referencias, RIS o Zotero | `citas-apa-zotero` |
| Solo la carpeta para Drive | `paquete-evidencias-economia` |
| Declaración de uso de IA | `uso-responsable-ia` |

## Paso 2 · Pipeline y controles (no avanzar sin cumplirlos)
0 consigna y rúbrica con checklist → 1 preguntas Q y variables → 2 búsqueda Scopus completa → 3 resúmenes con OpenAlex → 4 cribado y matriz (cada Q con ≥ 1 puntaje 2) → 5 PDF (OA; CAPTCHA = no recuperado) → 6 referencias verificadas por DOI + RIS → 7 figuras verificadas → 8 redacción → 9 Word sobre plantilla + PDF con Word real → 10 revisión final honesta. El tablero vive en `00_Control_Trabajo.md` (lo crea `iniciar-trabajo`).

## Paso 3 · Decidir con la usuaria solo lo que no se deduzca
Una sola ronda de preguntas (AskUserQuestion) si falta: alcance (todas las secciones o solo algunas), entrega (Word + PDF + carpeta Drive) y tipo de gráficos. Lo demás se decide con los valores por defecto del plugin y se informa.

## Agentes
`lector-critico-economia` (un PDF → fila de matriz y puntaje 0–2), `revisor-rubrica-economia` (audita el documento contra consigna, rúbrica, APA y tono; no modifica), `verificador-cifras-economia` (recalcula cifras y contrasta con la fuente oficial).

## Siempre al cerrar
Informe honesto (ver `revision-final-honesta`): qué se leyó realmente, qué se descartó, qué debe confirmar ella, qué es borrador de otro integrante. No subir nada a Drive ni enviar mensajes sin que lo pida.
