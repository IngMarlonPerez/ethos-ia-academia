---
name: analisis-requerimientos
description: 'Análisis del caso de la tesis de TI (2.1): alternativas, historias de usuario, RF, RNF ISO 25010, métricas y trazabilidad. Usar para requerimientos, RF/RNF, casos de uso o trazabilidad.'
---

# Análisis del caso y requerimientos (etapa 3)

La fuente única es `requerimientos/requerimientos.json`: de ahí salen las tablas del Word, la trazabilidad, las matrices y los controles. Se trabaja **por componente** o «pieza» del sistema. En la tesis VicMar las piezas fueron Modelo, Clustering, NL2SQL y Dashboard, más una Transversal.

## 1. Alternativas de solución (al menos las del perfil; UNEMI: 3)
- Cada alternativa tiene descripción, ventajas (viñetas), desventajas y limitaciones, y un veredicto.
- Arma la **matriz comparativa** de 8 a 10 criterios: costo, escalabilidad, personalización, análisis de datos, tiempo de implementación, mantenimiento, control de acceso, protección de datos… Valores Bajo/Medio/Alto o Sí/No, en `criterios_alternativas` y `matriz_alternativas`.
- Casi siempre las opciones son: proceso manual o hojas de cálculo, una herramienta comercial (p. ej. Power BI o un ERP), y el prototipo propio (la «seleccionada», con la razón).
- Esto es distinto de la selección de **tecnologías** (etapa 4) y de **arquitectura** (etapa 5), que tienen su propia skill.

## 2. Actores y persona principal
Tabla: actor, perfil, necesidad principal y conocimiento técnico. Marca la **persona principal** (`persona_principal: true`), normalmente la autoridad o el usuario de negocio **sin perfil técnico**. Las historias y la prueba con usuarios se diseñan para ella.

## 3. Historias de usuario
- Formato: «Como <actor>, quiero <capacidad> para <beneficio>».
- Criterios de aceptación **Dado / Cuando / Entonces**, verificables.
- Cada historia lleva: los objetivos que atiende, la pieza y la prioridad.
- Entre 8 y 12 historias suelen cubrir un prototipo. Plantilla en `plantillas/hu.md`.

## 4. Requerimientos funcionales por pieza
«El sistema debe…», uno por fila, con: `pieza`, `historias`, `objetivo`, `implementacion` (el archivo del repositorio que lo implementa, cuando ya exista) y `pruebas`.

## 5. Requerimientos no funcionales (ISO/IEC 25010)
Plantilla en `plantillas/rf_rnf.md`. Un RNF sin «cómo se verifica» no sirve. Cubre al menos:
- seguridad (confidencialidad, integridad, control de acceso);
- **privacidad y protección de datos personales**: es obligatoria; usa la skill `proteccion-datos`;
- rendimiento o eficiencia;
- usabilidad para la persona principal;
- mantenibilidad;
- portabilidad y reproducibilidad;
- fiabilidad.

## 6. Métricas de calidad con meta
Una por objetivo específico como mínimo, en `metricas`: métrica, pieza, meta, objetivo, y `artefacto` + `ruta_json` donde el código dejará el valor real. Ejemplos según el tipo de proyecto:
- **ML:** ROC-AUC ≥ 0,90, recall de la clase positiva ≥ 0,80, PR-AUC.
- **IA/LLM:** exactitud en el conjunto dorado ≥ 80 %, 100 % de preguntas maliciosas bloqueadas.
- **Software:** tiempo de respuesta p95 < 2 s, 0 violaciones de aislamiento, SUS ≥ 68.
- **Clustering:** silhouette, prueba de diferencias entre grupos.

## 7. Trazabilidad y tablas
`python "${CLAUDE_PLUGIN_ROOT}/skills/analisis-requerimientos/scripts/trazabilidad.py" requerimientos/requerimientos.json --perfil <perfil> --repo <repo> --tablas documento/tablas_2_1.json`

Valida la cadena objetivo → HU → RF → componente → prueba. Genera las tablas (alternativas, actores, historias, RF, RNF, métricas y trazabilidad) que el generador del Word inserta con `Insertor.tabla()`.

## 8. Prueba con usuarios
Protocolo en `plantillas/protocolo_usuarios.md`:
- de 5 a 6 tareas mapeadas a las historias;
- de 3 a 5 personas sin perfil técnico;
- medición de éxito, tiempo y SUS (`plantillas/sus.md`).

**Las sesiones las hacen los autores.** El documento no afirma resultados de usabilidad hasta tener esos datos.

**Control:**
- `trazabilidad.py` termina sin errores: alternativas suficientes con una seleccionada, cada objetivo con historia, RF y métrica, cada RF y RNF con su prueba, y un RNF de privacidad;
- el texto de 2.1 cumple el mínimo de páginas del perfil (lo mide `verificar-coherencia`).
