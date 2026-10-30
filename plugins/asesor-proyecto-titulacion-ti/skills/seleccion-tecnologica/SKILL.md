---
name: seleccion-tecnologica
description: 'Elige tecnologías de la tesis de TI comparando 3 opciones por decisión con matriz ponderada, evidencia y ADR. Usar al preguntar qué lenguaje, framework, base de datos o stack usar, o al justificarlos.'
---

# Selección tecnológica (etapa 4)

Cada decisión técnica se toma con **al menos 3 candidatas** (según el perfil), **criterios con origen** y **evidencia por celda**. El resultado es defendible ante el tutor y queda escrito en un ADR que el código debe respetar.

## 1. Lista de decisiones
Usa `referencias/catalogo-decisiones.md` para ver qué decisiones aplican según `titulacion.json` → `tipo_proyecto`. Como mínimo en un proyecto de software: lenguaje del backend, framework de backend, framework de frontend y base de datos. En ML o IA se suman la biblioteca de modelos y, si aplica, el proveedor de LLM.

## 2. Criterios ponderados (suman 100)
Salen de los **RNF y las restricciones reales**, no de gustos (`referencias/criterios-iso25010.md`). Cada criterio lleva su `origen`: «RNF-04», «OE2», «Restricción: equipo de 2, 6 meses, costo cero». Criterios típicos:
- ecosistema para el problema;
- **evidencia en trabajos previos** (cuántos lo usan: `tabla_trabajos_previos.py --conteos`);
- dominio del equipo;
- rendimiento;
- seguridad;
- licencia y soporte;
- compatibilidad con la infraestructura de la institución.

Explica los pesos en una oración cada uno.

## 3. Evidencia por candidata
- Lanza un agente `evaluador-tecnologia` por candidata, **en paralelo**. Pásale la decisión, los criterios con su origen y la ruta de `literatura/trabajos_previos.json`.
- Cada puntaje de 1 a 5 tiene justificación y **fuente** (`referencias/fuentes-validas.md`):
  - trabajos previos de la tabla;
  - artículos con DOI;
  - **documentación oficial** o repositorio oficial, con la fecha de consulta (versión LTS, licencia, soporte);
  - una prueba propia reproducible (por ejemplo, una medición de latencia en el repositorio).
- **Nunca** blogs, Medium, tutoriales, foros ni prensa.

## 4. Matriz, sensibilidad y ADR
1. Copia `${CLAUDE_PLUGIN_ROOT}/skills/seleccion-tecnologica/plantillas/decision.json` como `decisiones/DT-NN_<tema>.json` y llénalo.
2. Ejecuta:
   `python "${CLAUDE_PLUGIN_ROOT}/skills/seleccion-tecnologica/scripts/matriz_decision.py" decisiones/ --todas --adr --xlsx decisiones/Matriz_decisiones.xlsx`

El script:
- valida los pesos, el número de candidatas y que cada celda tenga fuente;
- calcula el puntaje ponderado sobre 5;
- varía cada peso ±20 % y dice si la ganadora es **estable**; si no lo es, aplica el criterio de `desempate` y lo deja escrito;
- escribe el ADR en `decisiones/adr/ADR-NNN-<tema>.md`.

Completa en el JSON la `eleccion` (razón y consecuencias: qué se gana, qué se sacrifica, qué riesgo queda) y vuelve a correr para actualizar el ADR. Si el código ya existe y la decisión no coincide con él, dilo con claridad: o se cambia el código o se justifica.

## 5. Verificación en el código
En cada DT, `verificacion_codigo` indica en qué archivo del repo (`requirements.txt`, `package.json`, `pom.xml`…) debe estar la tecnología y en qué versión. `verificar-coherencia` falla si no coinciden.

## 6. Para el documento (3.3 a)
- **Tabla de tecnologías:** «Capa | Tecnología y versión | Uso», con las versiones reales fijadas en el repositorio.
- **Por cada decisión:** un párrafo de contexto, la tabla ponderada (`matriz_decision.py DT-NN.json --tabla t.json` → `Insertor.tabla()`), la frase de sensibilidad y la razón de la elección con sus citas.
- Las decisiones de arquitectura van en 3.2 (skill `decision-arquitectura`).

**Control:**
- `matriz_decision.py --todas` termina sin errores: al menos 3 candidatas por decisión, pesos que suman 100, fuente válida en cada celda;
- cada ganadora es estable o tiene el desempate explicado;
- hay un ADR por decisión;
- las versiones del ADR coinciden con el repositorio (etapa 10).
