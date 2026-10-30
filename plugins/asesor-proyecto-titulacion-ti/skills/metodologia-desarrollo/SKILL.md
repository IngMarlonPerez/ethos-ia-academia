---
name: metodologia-desarrollo
description: 'Documenta la metodología de la tesis de TI (3.1): marco justificado con literatura (CRISP-DM, Scrum, XP, RUP o híbrido), fases con entregable real, iteraciones y figura. Usar al pedir metodología, CRISP-DM, Scrum, fases, iteraciones o sprints.'
---

# Metodología de desarrollo (etapa 6)

La plantilla UNEMI pide «sistematizar los entregables». Por eso **cada fase apunta a un archivo que existe en el repositorio** y a un resultado que se puede verificar. Las tutoras de la tesis VicMar pidieron explícitamente «documentar cada fase CRISP-DM».

## 1. Elegir el marco
Ver `referencias/metodologias.md`.

| Tipo de proyecto (`titulacion.json` → `tipo_proyecto`) | Marco habitual |
|---|---|
| datos_ml (modelo predictivo, clustering, BI) | CRISP-DM, con iteraciones incrementales para el software que lo rodea |
| software (sistema web o móvil) | Scrum (o XP) con sprints; RUP o cascada si el tutor lo exige |
| ia_llm | CRISP-DM o ciclo de evaluación con conjunto dorado + Scrum |
| redes / seguridad | PPDIOO, NIST CSF, ciclo de pentesting (PTES), según el caso |

Justifica la elección con 1 o 2 trabajos previos que usaron el mismo marco (columna Técnica o Metodología de la tabla).

## 2. Cada fase, con evidencia
Para cada fase escribe:
- **Objetivo** de la fase en el proyecto (no la definición del libro).
- **Actividades** realizadas.
- **Entregable:** un archivo del repositorio (`backend/ml/entrenar.py`, `requerimientos/requerimientos.json`, `diagramas/uml_secuencia_*.png`…).
- **Resultado verificable**, con una cifra leída del artefacto: «ROC-AUC temporal = 0,997, `metrics.json`».

Arma la tabla «Fase | Entregable en el repositorio | Resultado verificable» y comprueba que cada archivo exista.

## 3. Iteraciones
Tabla «Iteración | Periodo | Incremento | Cierre (evidencia)». Para Scrum, además, el backlog con las historias por sprint. Si hubo rondas de evaluación que corrigieron defectos, van aquí. En la tesis VicMar, las cuatro rondas del NL2SQL pasaron la exactitud de 67,5 % a 92,5 %.

## 4. Control de calidad por fase
Tabla «Fase | Pregunta de control | Cómo se verifica». Por ejemplo: «Preparación | ¿Hay fuga de información entre entrenamiento y prueba? | Validación agrupada por alumno + corte temporal».

## 5. Figura
Parte de `${CLAUDE_PLUGIN_ROOT}/skills/metodologia-desarrollo/plantillas/metodologia_crisp_dm.mmd`, `metodologia_scrum.mmd` o `metodologia_hibrida.mmd`. Cópiala a `diagramas/metodologia_<marco>.mmd`, reemplaza el texto por los entregables reales y renderízala con la skill `diseno-uml-datos`.

**Control:**
- cada fase tiene un entregable que existe en el repositorio y un resultado verificable;
- el marco está justificado con literatura;
- 3.1 cumple el mínimo de páginas del perfil (UNEMI: 3).
