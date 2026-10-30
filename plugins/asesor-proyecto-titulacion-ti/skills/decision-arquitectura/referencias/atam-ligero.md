# ATAM ligero para una tesis

El ATAM completo (Architecture Tradeoff Analysis Method, del SEI) exige talleres con muchas partes interesadas. Para una tesis se usa su núcleo: **escenarios de atributos de calidad**, evaluados contra cada estilo candidato.

## 1. Escribir escenarios (5–8)
Formato: **fuente → estímulo → entorno → respuesta → medida**, derivado de un RNF.

| ID | RNF | Escenario | Medida |
|---|---|---|---|
| E1 | RNF-06 modificabilidad | Un administrador de TI agrega una segunda institución en operación normal; el sistema la integra | Solo un perfil de mapeo nuevo; 0 líneas cambiadas en el ETL y el modelo |
| E2 | RNF-01 confidencialidad | Un usuario de la institución A consulta datos | 0 filas de la institución B, verificadas en el motor |
| E3 | RNF-04 rendimiento | 20 usuarios consultan el panel a la vez | p95 < 2 s |
| E4 | Restricción del equipo | Dos personas deben entregar un prototipo en 6 meses | Todo desplegable con un comando; ≤ 2 servicios que operar |
| E5 | RNF-07 reproducibilidad | Un evaluador reconstruye el sistema en otra máquina | pipeline.ps1 sin pasos manuales |

## 2. Evaluar cada estilo contra cada escenario (1–5)
Estos puntajes son las celdas de la matriz ponderada (`matriz_decision.py`, `tipo: arquitectura`). Los pesos salen de la prioridad de cada escenario. Cada celda se justifica con evidencia de literatura o con una prueba propia.

## 3. Puntos de sensibilidad y compromisos (trade-offs)
Anota en el ADR:
- **Punto de sensibilidad:** una decisión que afecta mucho a un atributo. Por ejemplo, el filtro por institución en el motor, y no en la aplicación, determina la confidencialidad.
- **Compromiso:** una decisión que mejora un atributo y empeora otro. Por ejemplo, SPA + API mejora la experiencia y la reutilización de la API, pero agrega un desplegable y la gestión de tokens.
- **Riesgo:** qué podría salir mal y cómo se mitiga.

## 4. Verificar
Los escenarios medibles se convierten en pruebas (etapa 8). Las reglas estructurales van a `arquitectura_reglas.json` (etapa 5, paso 5).
