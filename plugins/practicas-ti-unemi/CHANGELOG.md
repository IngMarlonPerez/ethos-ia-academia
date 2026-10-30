# Cambios

## 1.2.1 – 29 de octubre de 2026
- **Menos tokens por sesión:** las descripciones de las skills y los agentes se acortaron a unos 200 caracteres, conservando las frases que las activan. Así se cargan completas en cada sesión y no se recortan por falta de espacio.

## 1.2.0
- Nueva skill `tarea-grupal-gestion-ti`: tareas grupales de Gestión de TI (ITIL 4, COBIT, ISO 20000) en Word sobre la plantilla de portada UNEMI, con coherencia por códigos de problema, responsable por subsección, KPI con línea base y plazo, medición de páginas con Word y anexo de IA aparte. Incluye `ooxml.py`, `ensamblar_plantilla.py`, `render_word.ps1`, un ejemplo completo y una guía de contenido ITIL 4.

## 1.1.0
- Nueva skill `laboratorio-docker`: simulación de redes (iperf3 y tc/netem) y cifrado de disco completo con LUKS en contenedores, con scripts probados.
- `evidencias-capturas`: `render_consola.py` (texto real de consola a imagen, con enmascarado de IP privadas) y uso de las terminales de la sesión como evidencia.
- `medicion-de-red`: figuras de latencia por paquete y de real frente a simulado; reglas sobre condiciones de medición.
- `informe-practica-unemi`: lista de verificación contra la guía y la rúbrica, anexos con bloques, compactación de portada, carrera y fecha en blanco.
- `asistente-practica-ti`: reglas de rigor y de cero pendientes en el documento final.

## 1.0.1
- Descripciones de las skills más cortas (menos contexto por turno).

## 1.0.0
- Primera versión: 8 skills (guía, red, comercio electrónico, seguridad, ciclo de vida e IA, evidencias, informe, puerta de entrada) y scripts probados para extraer la guía, medir la red, graficar, probar cifrado, ejecutar un sistema experto, generar transcripciones, capturar y armar el Word.
