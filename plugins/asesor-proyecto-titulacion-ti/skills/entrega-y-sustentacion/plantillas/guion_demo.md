# Guion de la demo (~5 minutos)

Preparación:
- el pipeline corrió sin errores (`scripts/pipeline.ps1`);
- el backend y el frontend están levantados (`.claude/launch.json`);
- **la usuaria inicia sesión ella misma**; Claude nunca escribe contraseñas.

| # | Qué se muestra | Historia / RF | Qué decir (una frase) | Captura |
|---|---|---|---|---|
| 1 | Inicio de sesión con el rol de la persona principal | HU-01 | «Entra una autoridad sin perfil técnico.» | figuras/demo_01_login.png |
| 2 | Vista principal con el resultado clave (p. ej. riesgo y sus factores) | HU-01, HU-02 | «Cada caso muestra sus 3 factores principales.» | figuras/demo_02_panel.png |
| 3 | Confiabilidad del modelo o componente (métricas reales) | HU-06 | «Las métricas salen de la validación temporal.» | figuras/demo_03_metricas.png |
| 4 | Segunda función (segmentación, comparación, reporte) | HU-04 | | figuras/demo_04_….png |
| 5 | Consulta en lenguaje natural (si aplica): 2 o 3 preguntas | HU-03 | | figuras/demo_05_chat.png |
| 6 | Un intento malicioso bloqueado | RNF-03 | «El sistema no ejecuta escrituras ni muestra otra institución.» | figuras/demo_06_bloqueo.png |
| 7 | Cambio de organización o rol: cada uno ve solo lo suyo | RNF-01 | | figuras/demo_07_aislamiento.png |
| 8 | Cierre: reconstrucción con un comando | RNF-07 | | — |

Las capturas se guardan en `figuras/demo_<nn>_<tema>.png`: el generador del Word las inserta en 3.3 y en «Pruebas de funcionamiento».
