---
name: informe-practica-unemi
description: 'Arma el informe de la práctica en Word sobre la plantilla UNEMI con APA 7, anexos y verificación. Usar para «hazme el informe en el formato UNEMI».'
---

# Informe de la práctica (Word, plantilla UNEMI)

## Antes de armar
1. Estructura = la de la guía (`leer-guia-practica`). Cada sección debe poder defenderse con la **rúbrica**: desarrollo (acciones ejecutadas), redacción y ortografía, resultados (herramientas y técnicas usadas), conclusiones y/o recomendaciones **ligadas al contenido**, y **todos** los anexos.
2. Formato (perfil UNEMI): Times New Roman 12, interlineado 1,5, justificado, sangría de 1,27 cm; referencias con sangría francesa y alineadas a la izquierda; márgenes de la plantilla. La portada se **llena sin reescribirla**: solo TEMA, AUTORES, ASIGNATURA, DOCENTE, FECHA DE ENTREGA y PERIODO. Si la carrera de la plantilla no coincide (p. ej. «Ingeniería de Software» frente a «Tecnologías de la Información»), se avisa a quien arma la portada; no se corrige por cuenta propia.
3. Redacción con la skill `asistente-investigacion-cientifica:redaccion-apa7`: una idea por párrafo, citas que el artículo respalda, «y» entre dos autores en español, «et al.» desde 3 autores, partículas (da Costa, de Ruosi). Tono natural. No uses «demuestra» sin datos.

## Armar
1. Escribe `contenido.json` (formato en la cabecera de `scripts/armar_informe.py`): portada, bloques (títulos, párrafos, tablas, figuras, imágenes), referencias y anexos con imágenes.
2. `python -I "${CLAUDE_PLUGIN_ROOT}/skills/informe-practica-unemi/scripts/armar_informe.py" contenido.json`
   - Usa `word_apa.py` del plugin `asistente-investigacion-cientifica` (lo localiza solo).
   - Si el Word de salida está abierto, guarda `_v2`, `_v3`… y lo avisa: dile cuál es la vigente.
3. **Pendientes resaltados:** lo que solo la usuaria puede aportar (nombres, fecha, periodo, mediciones de una red que no es la suya, capturas de programas con permisos) se escribe `==así==` y se enumera al final. Nunca se rellena con datos supuestos.
4. Las celdas «a verificar» (p. ej. el modelo de negocio de una plataforma sin fuente) también se resaltan hasta que haya fuente.

## Controles de calidad
- `python -I "<redaccion-apa7>/scripts/verificar_apa.py" informe.docx --desde 2022 --hasta 2026` → **0 errores** (cita↔referencia, años, DOI, orden alfabético, «et al.»).
- Exporta a PDF con Word (COM: `ExportAsFixedFormat`) y mira las páginas con tablas, figuras y anexos con Read: tablas partidas, imágenes cortadas, títulos huérfanos.
- Cada cifra del texto sale de un archivo de medición o de un resumen/artículo leído; si solo se leyó el resumen, el informe lo dice y no cita páginas.
- Al editar un informe ya generado, parte de la última versión y conserva lo que la usuaria cambió a mano: compara antes de regenerar.

## Entrega
Dile a la usuaria: el archivo vigente, qué quedó resaltado, qué anexos tienen evidencia y cuáles no, y los archivos de prueba que puede borrar. Recuerda quitar el resaltado amarillo (Inicio → Color de resaltado → Sin color) y actualizar campos (Ctrl+A, F9) antes de subir al aula virtual.

## Lista de verificación y estructura profesional
- Usa `referencias/lista_verificacion_guia.md` como control final «al pie de la letra» de la guía y de la rúbrica.
- **Estructura que funcionó** (guía G003-S10): I Introducción (impacto en la vida diaria y la empresa, enfoque comparativo, objetivos literales), II Marco teórico con un apartado por concepto de la guía, III Metodología con los rótulos de la guía y un entorno experimental (tabla de equipo, herramientas y versiones), IV Desarrollo experimental que abre con la tabla de la guía (subtema, actividad, instrumento) y un «cómo se cubrió» por subtema, V Resultados y análisis con figuras y una síntesis de hallazgos, VI Conclusiones y recomendaciones con datos.
- **Anexos** con bloques (`"anexos": [{"bloques": [...]}]`): un anexo por instrumento de la guía, con párrafo descriptivo y figuras numeradas (A1, A2…), cada una con el comando o la herramienta en el pie.
- **Portada:** `portada.compactar` (por ejemplo 3) quita párrafos vacíos antes de «MILAGRO-ECUADOR» cuando varios autores desbordan la hoja; `portada.carrera` corrige la carrera de la plantilla si la usuaria lo pide; `portada.fecha = ""` deja el campo en blanco sin resaltarlo.
- **Ejecuta las pruebas antes de redactar** y redacta con las cifras leídas de los archivos de medición (el generador del informe puede leer los CSV y JSON directamente).
- Antes de entregar, lee todo el texto una vez (el corrector automático en español no es fiable) buscando afirmaciones que no se probaron, referencias de anexos mal numeradas y condiciones de medición sin declarar.
- Exporta también el PDF con Word (`ExportAsFixedFormat`) y revisa todas las páginas.
