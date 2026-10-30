# Marcos metodológicos para tesis de TI

| Marco | Fases | Entregables típicos en el repositorio | Cuándo usarlo |
|---|---|---|---|
| **CRISP-DM** | 1 Comprensión del negocio · 2 Comprensión de los datos · 3 Preparación · 4 Modelado · 5 Evaluación · 6 Despliegue | 1: objetivos, HU y criterios de éxito · 2: perfil de datos, exploración · 3: ETL, anonimización, variables, atípicos · 4: script de entrenamiento y comparación de modelos · 5: metrics.json, figuras, pruebas · 6: API, panel, almacén | Modelos predictivos, clustering, BI analítica |
| **Scrum** | Product backlog → sprint planning → sprint (2 semanas) → review → retrospectiva | Backlog (HU), incremento por sprint con pruebas, acta de revisión con el tutor | Sistemas web o móviles con requisitos que cambian |
| **XP** | Planificación con historias · diseño simple · TDD · integración continua · entregas pequeñas | Pruebas automatizadas, integración continua | Equipo muy pequeño con énfasis en calidad del código |
| **RUP** | Inicio · Elaboración · Construcción · Transición | Visión, casos de uso, arquitectura, releases | Cuando el tutor pide artefactos UML formales por fase |
| **Cascada / en V** | Requisitos → diseño → implementación → pruebas → despliegue | Documento por fase | Requisitos fijos o normativos |
| **Híbrida** | CRISP-DM para el componente analítico dentro de iteraciones incrementales | Lo de ambos, sin duplicar | Tesis con modelo + sistema (el caso más común en la UNEMI) |
| **PPDIOO / NIST CSF / PTES** | Preparar-planificar-diseñar-implementar-operar-optimizar · identificar-proteger-detectar-responder-recuperar · fases de pentesting | Topología, configuraciones, informe de hallazgos | Redes, ciberseguridad |

## Cómo redactar cada fase (modelo de la tesis VicMar)
> **Fase 3 · Preparación de los datos.** Se seudonimizaron las columnas personales del dataset de prueba (…) y se construyó el panel alumno-periodo, en el que cada fila usa solo información disponible hasta el periodo t (…). *Entregables:* `backend/ml/features_abandono.py`, `docs/…/anonimizar_padron.py`. *Resultado verificable:* 83.678 filas, 14.508 alumnos, 0 cédulas reales (buscar_secretos.py).

Las cifras de «Resultado verificable» se leen de los artefactos con el generador. No se escriben a mano.
