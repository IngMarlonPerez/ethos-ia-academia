---
name: asistente-titulacion-ti
description: 'Puerta de entrada del Asesor de titulación de TI: ubica la etapa del proyecto, muestra los controles pendientes y deriva. Usar con «mi tesis», «avance 1/2/3», «qué sigue» o «en qué etapa voy».'
---

# Asistente de proyecto de titulación de TI (orquestador)

Este plugin trata la tesis como un **pipeline con controles de calidad**, igual que el Asistente de Investigación Científica. Cada etapa tiene una skill y un control, y ninguna se cierra con el control pendiente. El pipeline sale de los Avances 1 y 2 de la tesis VicMar Data AI (UNEMI, 2026) y sirve para cualquier universidad mediante un **perfil institucional**; la UNEMI es el perfil por defecto.

## Al empezar cada sesión
1. **Plugin de investigación.** Comprueba que estén las herramientas `mcp__plugin_asistente-investigacion-cientifica_literatura__*` y las skills `asistente-investigacion-cientifica:*`. Si faltan, dile a la usuaria:
   `claude plugin install asistente-investigacion-cientifica@ethos-ia-academia --scope user`
   Sin ese plugin no hay búsqueda en Scopus, PRISMA ni verificación APA.
2. **Proyecto.** Busca `titulacion.json` en la carpeta actual o en sus carpetas superiores. Si no existe, usa la skill `iniciar-titulacion`.
3. **Estado.** Ejecuta:
   `python "${CLAUDE_PLUGIN_ROOT}/skills/asistente-titulacion-ti/scripts/tablero.py" estado`
   Indica la etapa actual, lo que falta para cerrarla y qué skill sigue.
4. **Propuesta.** Muestra ese resumen en 3 o 4 líneas y propón el siguiente paso. Si la usuaria pide algo de otra etapa, ve directo a esa skill: el pipeline ordena el trabajo, no lo bloquea.

## Las etapas
Detalle en `referencias/pipeline.md`.

| Etapa | Skill | Sección (UNEMI) |
|---|---|---|
| 0 Inicio | `iniciar-titulacion` | — |
| 1 Planteamiento y objetivos | `planteamiento-y-objetivos` | Resumen, 1.1, 1.2 |
| 2 Literatura y trabajos previos | `asistente-investigacion-cientifica:revision-sistematica` → `trabajos-previos` | 1.3 |
| 3 Análisis y requerimientos | `analisis-requerimientos` + `proteccion-datos` | 2.1 |
| 4 Selección tecnológica | `seleccion-tecnologica` | 3.3 (a) |
| 5 Arquitectura | `decision-arquitectura` | 3.2 (a) |
| 6 Metodología | `metodologia-desarrollo` | 3.1 |
| 7 Diseño UML y datos | `diseno-uml-datos` | 3.2 (b), (c) |
| 8 Desarrollo y evidencias | `desarrollo-y-evidencias` + `proteccion-datos` | 3.3 (b), (c) |
| 9 Conclusiones | `conclusiones-recomendaciones` | 4 |
| 10 Documento y control | `documento-titulacion`, `matrices-titulacion`, `verificar-coherencia` | todas |
| 11 Retroalimentación | `retroalimentacion-tutor` | — |
| 11b Presentación de cada avance | `presentacion-avance` | — |
| 11c Estudio del sistema y demostración | `manual-arquitectura-tribunal` (agente `cartografo-arquitectura`) | — |
| 12 Sustentación y entrega | `entrega-y-sustentacion` + `asistente-investigacion-cientifica:paquete-evidencias` | Anexos |

**Skills transversales** (en cualquier etapa, sobre todo antes de cada entrega):
- `organizacion-repositorio`: auditoría, código en una sola carpeta por capas con ADR-000, lo que sobra a la carpeta de revisión;
- `uso-etico-ia`: sin rastros de herramientas de IA en el proyecto, autoría de los metadatos y anexo de uso ético en una carpeta local;
- `publicacion-github`: controles previos, commit único y limpio con los autores reales, y push confirmado.

Las etapas 4 y 5 suelen decidirse antes de programar, aunque se documentan en el Avance 2. Si el código ya existe, se documentan igual y `decision-arquitectura` verifica que el código cumpla lo declarado.

## Reglas transversales
Aplícalas siempre; están en `referencias/reglas-transversales.md`. Lee también `referencias/lecciones-aprendidas.md` al empezar el proyecto y antes de cada entrega: resume los incidentes reales (Word guardado desde una versión vieja, portada sin encabezado, correcciones revertidas) y la regla que evita cada uno.
1. **Solo fuentes académicas** (Scopus o DOI), verificadas en el texto completo. Nunca prensa ni blogs.
2. **Leer antes de seleccionar**: un trabajo previo cuenta solo si tiene su ficha de lectura con página.
3. **La arquitectura se evalúa siempre** en tres lugares:
   - en la literatura (columna «Arquitectura» de los trabajos previos);
   - en el diseño (al menos 3 estilos comparados);
   - en el código (`auditor-arquitectura`).
4. **Una sola fuente de verdad**: las cifras del documento se leen de los artefactos, no se escriben a mano.
5. **La plantilla y el documento oficial no se editan**: se generan copias por script.
6. **Seguridad**:
   - Claude no escribe contraseñas;
   - no se envían datos personales a una IA externa;
   - los commits y el push se hacen solo con autorización.
7. **La IA no es autora**: no se nombra en el proyecto ni en los commits; se declara solo en el anexo local (`uso-etico-ia`).
8. **Mover, no borrar**: lo que sobra va a la carpeta de revisión con su índice (`organizacion-repositorio`).

## Cerrar una etapa
Solo cuando su control se cumple, y citando la evidencia:
`python "${CLAUDE_PLUGIN_ROOT}/skills/asistente-titulacion-ti/scripts/tablero.py" marcar <n> cerrada --nota "<evidencia>"`

Para cambiar de avance: `tablero.py avance 2`. El tablero `00_Control_Titulacion.md` se regenera solo; no lo edites a mano.

**Control:** el tablero refleja el estado real. Una etapa cerrada tiene su evidencia en la nota.
