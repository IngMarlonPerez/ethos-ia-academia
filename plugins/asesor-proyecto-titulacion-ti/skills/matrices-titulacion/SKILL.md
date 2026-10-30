---
name: matrices-titulacion
description: 'Matrices de la tesis de TI en Excel sin cifras a mano: consistencia, trabajos previos, decisiones, trazabilidad y coherencia literatura-código. Usar al pedir matriz de consistencia o matrices del avance.'
---

# Matrices metodológicas del proyecto (etapa 10)

Las 4 matrices de la **revisión sistemática** (búsqueda, cribado, extracción y síntesis, temática) y el diagrama PRISMA los hace `asistente-investigacion-cientifica:matrices-revision`. Esta skill arma las matrices **del proyecto de titulación**, que cruzan la literatura con el código.

## Fuentes (una sola verdad)
| Hoja | Se llena desde |
|---|---|
| 1. Matriz de consistencia | `_automatizacion/datos_matrices.json` → `consistencia` (etapa 1) |
| 2. Extracción bibliográfica | `literatura/trabajos_previos.json` (etapa 2) |
| 3. PRISMA | `datos_matrices.json` → `prisma`, o la ruta al Excel de `matrices-revision` |
| 4. Decisiones | `decisiones/DT-*.json`, resueltas con `matriz_decision.py` (etapas 4 y 5) |
| 5. Trazabilidad | `requerimientos/requerimientos.json` (etapa 3) |
| 6. Coherencia literatura-código | `datos_matrices.json` → `coherencia_literatura_codigo`; `{cifra}` se reemplaza por el valor del artefacto |
| Matrices oficiales del perfil | `datos_matrices.json` → `oficiales`; «Estado del Arte» se llena sola desde los trabajos previos |

## Coherencia literatura-código
Esta hoja responde a la pregunta del tutor «¿dónde está en el código lo que dice la literatura?». Una fila por cada antecedente que sostiene una decisión:
- **Antecedente:** «Villar y Andrade (2024)».
- **Qué afirma el documento:** «SMOTE mejora el recall bajo desbalance».
- **Decisión en el código:** «Se comparó RF + SMOTE contra RF + class_weight dentro de la validación cruzada».
- **Dónde está implementada:** `backend/ml/entrenar_abandono.py`.
- **Evidencia medida:** «recall temporal = {cifra}», con `cifra` → artefacto y ruta.

Cubre los trabajos previos de la comparación crítica y todos los que justifican técnicas, tecnologías o la arquitectura. En la tesis VicMar fueron 25 filas.

## Generar
Desde la raíz del proyecto:
`python "${CLAUDE_PLUGIN_ROOT}/skills/matrices-titulacion/scripts/matrices_titulacion.py" [--salida documento/Matrices_Metodologicas.xlsx]`

Abre el Excel (skill `xlsx` si hace falta ajustar formato) y envíaselo a la usuaria. Para el informe oficial de la carrera, copia las hojas oficiales al formato que entregue el tutor, si trae el suyo.

**Control:**
- todas las cifras vienen de artefactos;
- ninguna fila de coherencia queda sin archivo ni evidencia (lo revisa `verificar-coherencia` si `comprobar.matriz_literatura_codigo` apunta al Excel);
- la extracción tiene al menos el mínimo de trabajos previos del perfil.
