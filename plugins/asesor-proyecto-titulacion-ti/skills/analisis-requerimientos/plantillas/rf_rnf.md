# Plantilla de requerimientos funcionales y no funcionales

## Requerimientos funcionales (por pieza o componente)
| ID | Pieza | Requerimiento funcional | HU | Obj. | Implementación |
|---|---|---|---|---|---|
| RF-01 | Modelo | El sistema debe estimar para cada alumno activo la probabilidad de abandono del próximo periodo. | HU-01 | OE2 | backend/ml/predecir.py |

Redacción: «El sistema debe + verbo + objeto + condición». Uno por fila. Si todavía no existe el archivo, deja la columna vacía y complétala en la etapa 8.

## Requerimientos no funcionales (ISO/IEC 25010)
| ID | Característica › subcaracterística | Requerimiento (medible) | Cómo se verifica |
|---|---|---|---|
| RNF-01 | Seguridad › Confidencialidad | Cada institución ve solo sus datos, filtrados en el motor de base de datos. | Prueba de integración con dos instituciones: 0 filas cruzadas |
| RNF-02 | Seguridad › Confidencialidad (privacidad) | Ningún dato personal se envía a servicios externos de IA; minimización y seudonimización según la ley del país. | Prueba que intercepta el envío y busca identificadores |
| RNF-03 | Seguridad › Integridad | El usuario de consulta solo puede ejecutar SELECT sobre vistas autorizadas. | 8 preguntas maliciosas bloqueadas; la base no cambia |
| RNF-04 | Eficiencia › Comportamiento temporal | Respuesta p95 < N s para consultas del panel. | Medición de latencia en la evaluación |
| RNF-05 | Usabilidad › Facilidad de aprendizaje | Una persona sin perfil técnico completa las tareas clave sin ayuda. | Prueba con usuarios: éxito ≥ 80 %, SUS ≥ 68 |
| RNF-06 | Mantenibilidad › Modificabilidad | Agregar una institución requiere solo un perfil de mapeo, sin cambiar el código. | Segunda institución cargada con el mismo código |
| RNF-07 | Portabilidad › Instalabilidad | El prototipo se reconstruye con un solo comando. | pipeline.ps1 termina sin errores |
| RNF-08 | Fiabilidad › Tolerancia a fallos | Si un proveedor externo falla, el sistema usa otro o informa sin inventar datos. | Prueba con proveedor simulado caído |

## Características de ISO/IEC 25010 (para no olvidar ninguna)
Adecuación funcional · Eficiencia de desempeño · Compatibilidad · Usabilidad (capacidad de interacción) · Fiabilidad · Seguridad · Mantenibilidad · Portabilidad (flexibilidad) · Protección (safety, en la versión 2023).
