---
name: iniciar-titulacion
description: 'Crea la estructura de una tesis de TI: perfil institucional, plantilla Word intacta, titulacion.json, tablero y carpetas. Usar al empezar la tesis o configurar la plantilla de la universidad.'
---

# Iniciar un proyecto de titulación de TI

1. **Lee antes de preguntar.** Si hay reglamento, plantilla (.docx), guía del tutor o una carpeta de ejemplo de la carrera, léelos primero: fijan la estructura, los mínimos y las fechas. Luego pregunta solo lo que falte:
   - tema provisional, carrera, autores y tutores;
   - universidad (si no es la UNEMI, se necesita su plantilla);
   - ruta del repositorio de código, si ya existe;
   - tipo de proyecto: `software`, `datos_ml`, `ia_llm`, `redes` o `seguridad`. Puede ser más de uno.

2. **Perfil institucional.**
   - UNEMI: `unemi`. Ya trae secciones, mínimos de páginas, requisitos, UML exigidos, carpeta de entrega y matrices oficiales.
   - Otra universidad: propón un borrador desde su plantilla.
     `python "${CLAUDE_PLUGIN_ROOT}/skills/iniciar-titulacion/scripts/perfil_desde_plantilla.py" "<plantilla.docx>" --id <sigla> --institucion "<nombre>" --salida "<proyecto>/_automatizacion/perfil_<sigla>.json"`
     Muestra a la usuaria la lista «Por revisar» y completa lo que la plantilla no trae: avance de cada sección, UML exigidos y carpeta de entrega. Usa `${CLAUDE_PLUGIN_ROOT}/perfiles/unemi.json` como modelo.

3. **Crea la estructura.** No sobrescribe nada.
   `python "${CLAUDE_PLUGIN_ROOT}/skills/iniciar-titulacion/scripts/iniciar_titulacion.py" "<carpeta>" --tema "<tema>" --carrera "<carrera>" --autores "A; B" --tutores "T1; T2" --perfil unemi --plantilla "<plantilla oficial.docx>" --repo "<ruta del código>" --tipo software datos_ml`

   Crea:
   - `titulacion.json` (datos del proyecto y estado de las etapas) y `00_Control_Titulacion.md` (el tablero);
   - `_automatizacion/`: `Plantilla_ORIGINAL.docx` (copia intacta, con md5 registrado), `coherencia.json` y `datos_matrices.json`;
   - `literatura/trabajos_previos.json`, `requerimientos/requerimientos.json`, `decisiones/adr/`, `diagramas/`, `figuras/`, `documento/` y `retroalimentacion/`;
   - `entregables/`, con la estructura de entrega del perfil.

4. **Literatura.** Invoca la skill `asistente-investigacion-cientifica:nuevo-proyecto` sobre la **misma carpeta**. Crea `protocolo.md`, `literatura/B1_…/` y el archivo de datos de las 4 matrices PRISMA. Las preguntas Q1…Qn del protocolo se escriben en la etapa 2 (skill `trabajos-previos`).

5. **Cierra la etapa 0:**
   `python "${CLAUDE_PLUGIN_ROOT}/skills/asistente-titulacion-ti/scripts/tablero.py" marcar 0 cerrada --nota "perfil <id>; plantilla md5 <…>"`
   Luego sigue con `planteamiento-y-objetivos`.

## Si ya hay un proyecto avanzado sin el Asesor
Caso de la tesis VicMar Data AI: corre `iniciar_titulacion.py` sobre la carpeta existente, que no toca nada de lo que ya hay. Después:
- registra en `titulacion.json` → `documentos` los avances ya entregados;
- marca como cerradas las etapas cumplidas, citando su evidencia.

**Control:**
- el md5 de `_automatizacion/Plantilla_ORIGINAL.docx` es igual al del archivo oficial;
- la usuaria confirmó el perfil;
- el tablero existe.
