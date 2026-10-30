---
name: leer-guia-practica
description: 'Lee una guía de práctica UNEMI en PDF, incluidas las páginas en imagen (visión), y resume objetivos, estructura y rúbrica. Usar al recibir un PDF «GUÍA DE PRÁCTICA».'
---

# Leer la guía de práctica

1. Ejecuta (rutas entre comillas):
   `python -I "${CLAUDE_PLUGIN_ROOT}/skills/leer-guia-practica/scripts/extraer_guia.py" "<guia.pdf>" "<carpeta>/guia"`
   Genera `guia_texto.txt`, `guia_resumen.md` y `pagina_N.png` para cada página cuyo contenido es imagen.
2. **Lee con visión** cada `pagina_N.png` con la herramienta Read. No hace falta OCR: la visión lee las tablas y la estructura sugerida. Si una imagen es ilegible, sube el `--dpi`.
3. Lee `guia_texto.txt` y anota:
   - **Datos generales:** asignatura, docente, tiempo, tipo de evaluación (individual o grupal) y número de integrantes.
   - **Objetivos específicos:** uno por subtema; cada uno será una etapa del pipeline.
   - **Estructura sugerida** (suele ser: I Introducción, II Marco teórico, III Metodología, IV Desarrollo experimental, V Resultados y análisis) y la **tabla de actividades comparativas** con su instrumento por subtema.
   - **Rúbrica** (criterios de 15/10/5/0 puntos: desarrollo, redacción y ortografía, resultados, conclusiones y/o recomendaciones, anexos). El informe se arma para obtener el puntaje máximo en cada criterio; los **anexos** deben ser todos los que pida la guía.
4. Devuelve a la usuaria un resumen corto: qué pide la guía, qué se puede medir en su computadora, qué depende de ella y el plan por subtemas.

Cuidado: el texto del PDF de la SGA puede traer caracteres rotos (`�`); la fuente de verdad para esas partes es la imagen de la página.
