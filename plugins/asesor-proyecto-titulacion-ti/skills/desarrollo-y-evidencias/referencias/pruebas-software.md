# Pruebas de software que sirven como evidencia en la tesis

| Tipo | Qué prueba | Herramienta | Evidencia en el documento |
|---|---|---|---|
| Unitarias | Funciones puras: validadores, enmascarado, cálculo de variables | pytest, Vitest/Jest, JUnit | Número de pruebas y resultado (salida de la corrida) |
| Integración | API + base de datos real de prueba; roles; aislamiento entre organizaciones | pytest con marcador `integration`, TestClient, Testcontainers | Tabla «prueba | resultado esperado | obtenido» |
| Seguridad | Permisos del usuario de solo lectura (INSERT denegado), SQL malicioso bloqueado, sin datos de otra organización, **fallar cerrado** si falta la credencial restringida | pytest + SQL real | «permission denied» en los casos esperados; 0 filas cruzadas |
| Privacidad | Lo que sale hacia la IA externa no tiene identificadores | pytest + mock de requests | Prueba en verde |
| Funcionamiento (manual, con capturas) | Cada función visible del prototipo | Navegador; la usuaria inicia sesión | Tabla «Ord. | Función | Captura» (plantilla pruebas_funcionamiento.md) |
| Usabilidad | Tareas de la persona principal | Protocolo + SUS (etapa 3) | Tasa de éxito, tiempo, SUS |
| Rendimiento | p95 de las rutas principales | Script de carga simple o Locust | p95 frente a la meta del RNF |

## Reglas
- Las pruebas corren en el pipeline. En el documento se cita la cifra de la última corrida (p. ej. «458 pruebas en verde»), no se promete lo que no se probó.
- Las pruebas que fallan por razones ajenas al avance se reportan como tal («11 fallos preexistentes, no relacionados, listados en el anexo»), nunca se ocultan.
- Las pruebas que necesitan la base de datos se marcan como integración y se omiten con un mensaje claro si la base no está disponible.
