---
name: ciclo-vida-ia-sistemas-expertos
description: 'Compara el ciclo de vida tradicional y el de IA, y un modelo generativo con un sistema experto de reglas, con evidencias. Usar para «ciclo de vida de sistemas» o «IA vs sistemas expertos».'
---

# Ciclo de vida, IA y sistemas expertos

## A. Ciclo de vida: software tradicional frente a IA
1. Elige el par de la guía (p. ej., app bancaria frente a un asistente tipo ChatGPT).
2. Compara por fase: planificación y análisis, diseño e implementación, pruebas, despliegue y mantenimiento. En IA se añaden los **datos** y el **modelo** como artefactos que se versionan, validan y monitorean; las pruebas usan métricas (exactitud, precisión, sesgos, alucinaciones); el mantenimiento es reentrenamiento y monitoreo (MLOps).
3. Literatura (Scopus, 5 años): Subramanya et al. (2022), de DevOps a MLOps, https://doi.org/10.3390/app12199851; Faruqui et al. (2024), IA que apoya la gestión del propio SDLC, https://doi.org/10.1109/ACCESS.2024.3519423. Cita solo lo que respalda el texto leído.

## B. IA generativa frente a sistema experto
1. **Construir el sistema experto** con reglas «si hechos → conclusión» (ver `ejemplos/reglas.json` y `casos.json`). Ejecuta:
   `python -I "${CLAUDE_PLUGIN_ROOT}/skills/ciclo-vida-ia-sistemas-expertos/scripts/sistema_experto.py" reglas.json casos.json --salida salida.txt`
   Cada conclusión cita la regla que la produjo; con un caso fuera de las reglas responde «sin regla aplicable».
2. **El modelo generativo responde de verdad.** Claude (esta sesión) contesta cada caso en el chat con su respuesta real; luego esas mismas respuestas se copian al JSON de la transcripción. **No se resumen ni se inventan después.** Si la guía pide ChatGPT o Gemini, solo la usuaria puede hacerlo con su cuenta (no se inician sesiones por ella); la alternativa honesta es declarar que el modelo usado fue Claude.
3. **Casos simulados** (educativos, sin datos reales; incluye siempre «no es un diagnóstico»): p. ej. gripe (fiebre alta, dolor muscular intenso, inicio brusco), alergia estacional, resfriado común.
4. **Evidencias:**
   - Transcripción: `python -I scripts/pagina_transcripcion.py conversacion.json transcripcion.html` y luego `evidencias-capturas/scripts/html_a_png.ps1`.
   - Código: abre `sistema_experto.py` en VS Code y captura la ventana (`capturar_ventana.ps1`).
   - Ejecución: captura de la consola; si la ventana no queda visible, genera la imagen de consola a partir de la **salida real** y rotúlala así en el pie.
5. **Comparación** (cuadro): origen del conocimiento (datos frente a reglas de especialistas), explicabilidad (baja frente a alta), riesgo (alucinaciones frente a cobertura limitada), y el enfoque híbrido de la literatura: Garrido-Merchán y Puente (2026), un modelo de lenguaje genera la base de conocimiento en Prolog para que un experto la valide, https://doi.org/10.1016/j.knosys.2026.116657; Chen et al. (2026), recuperación refinada con 31,2 % menos de alucinaciones y 28 % más de latencia, https://doi.org/10.1016/j.rineng.2026.109461.
6. **Observación honesta:** que ambos coincidan en 3 casos fáciles no prueba equivalencia; la diferencia está en la trazabilidad y en qué pasa fuera de las reglas.
