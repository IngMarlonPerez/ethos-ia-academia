---
name: entrega-y-sustentacion
description: 'Demo, sustentación y entrega de la tesis de TI: capturas, diapositivas y póster desde JSON, simulacro de tribunal y carpeta de entrega. Usar para la demo, la defensa o «dejar todo listo para entregar».'
---

# Sustentación y entrega (etapa 12)

## 1. Demo reproducible
- Corre el pipeline del repositorio (`scripts/pipeline.ps1`, skill `desarrollo-y-evidencias`) hasta que termine sin errores.
- Levanta el backend y el frontend con `.claude/launch.json` (herramienta `preview_start`). Si un puerto está ocupado por otro proyecto, usa otro puerto y ajusta la URL del backend en el frontend; no detengas procesos ajenos sin preguntar.
- **La usuaria inicia sesión ella misma** en el panel del navegador. Claude nunca escribe contraseñas, ni siquiera las de prueba de otros sistemas.

Para preparar la demostración, el manual de arquitectura (`manual-arquitectura-tribunal`) da el recorrido de pantallas y archivos y las preguntas probables del tribunal.

## 2. Capturas
- Sigue `plantillas/guion_demo.md`: una captura por paso, en `figuras/demo_<nn>_<tema>.png`.
- Incluye:
  - la función principal;
  - la explicación de un resultado;
  - las métricas de confiabilidad;
  - un intento malicioso bloqueado;
  - el aislamiento entre organizaciones o roles.
- Revisa que ninguna captura muestre datos personales reales ni credenciales.
- El generador del Word las inserta en 3.3 y en «Pruebas de funcionamiento» (`desarrollo-y-evidencias/plantillas/pruebas_funcionamiento.md`). Después, regenera el documento y el PDF, y vuelve a verificar.

## 3. Guiones
- **Presentación** (`plantillas/guion_presentacion.md`): cronometrada a unas 140 palabras por minuto, repartida por autor, con las diapositivas que acompañan cada bloque. Toda cifra que se diga es la del documento.
- **Demo** (unos 5 minutos): el orden de las capturas, con una frase por paso.

## 4. Diapositivas
Genera la presentación desde un JSON (parte de `plantillas/diapositivas-ejemplo.json`):
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/entrega-y-sustentacion/scripts/diapositivas.py" contenido.json -o documento/Sustentacion_Apellido1_Apellido2.pptx
python "${CLAUDE_PLUGIN_ROOT}/skills/entrega-y-sustentacion/scripts/qa_pptx.py" documento/Sustentacion_Apellido1_Apellido2.pptx --salida qa
```
- **Contenido:** título → problema y cifra → objetivos → trabajos previos y vacío → requerimientos → arquitectura (figura) → metodología → resultados (cifras de los artefactos) → demo → conclusiones → referencias clave.
- **Datos del JSON:** autores, tutor y carrera se toman de `titulacion.json` o de la portada del documento, nunca de memoria. Toda cifra es la del documento.
- **Plantilla institucional:** si la universidad entrega una `.pptx`, ponla en `"plantilla"`: el generador duplica la carátula, el contenido y el cierre con su fondo, logo y franjas. Sin plantilla usa un diseño básico 16:9.
- **Tipos:** `agenda`, `texto`, `tarjetas`, `cifras`, `diagrama` (embudo, comparativo, niveles, proceso, mapa, árbol, línea de tiempo, cuadrantes, FODA, ciclo), `imagen`, `tabla` (nativa y editable), `comparativa`, `conclusiones`, `referencias`, `cita`. Cada una acepta `notas` (guion del orador).
- **Tamaño de letra adaptativo:** el cuerpo usa el mayor tamaño que cabe; si no cabe ni con el mínimo, avisa: divide la diapositiva, no encojas la letra.
- **Íconos propios** (85, licencia ISC de Lucide): `python scripts/iconos.py --buscar servidor` y en el JSON `"icono": "servidor"`. No uses íconos o imágenes de terceros sin licencia.
- **Control de calidad:** `qa_pptx.py` mide si el texto cabe, busca marcadores de plantilla y fuentes ajenas, y genera el PDF y una hoja de miniaturas. Míralas antes de entregar.
- **Exportar a PDF** necesita PowerPoint (Windows) o LibreOffice. Las diapositivas se generan igual sin ellos y `qa_pptx.py` avisa que omite el PDF; el póster sí los necesita, porque su PDF es el de imprenta.

## 4b. Póster académico
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/entrega-y-sustentacion/scripts/poster.py" contenido.json -o documento/Poster_Apellido1_Apellido2 --logo logo_blanco.png
```
A0 de tres columnas: PPTX editable, PDF de imprenta y vista previa PNG. Parte de `plantillas/poster-ejemplo.json` (bloques `seccion`, `parrafo`, `lista`, `numerados`, `cifras`, `tarjeta`, `destacado`, `figura`, `grafico`, `diagrama`). Sigue el orden problema → objetivos → diseño → metodología → resultados → conclusión → referencias.

## 4c. Simulacro de tribunal
Antes de la defensa, lanza el agente `revisor-tribunal` (después de `verificar_coherencia.py` y del `revisor-tutor`). Contrasta el documento con el repositorio y devuelve hallazgos, fortalezas y las preguntas probables, cada una con la debilidad que la motiva y dónde está la respuesta. El banco base está en `plantillas/preguntas_tribunal.md`. Ensaya las respuestas en voz alta y repártelas entre los autores.

## 5. Anexos
`plantillas/anexo_actividades.md`: al menos 5 actividades, con al menos 4 interacciones con los tutores y enlaces a las evidencias, más la tabla de videos (presentación, avance, explicación técnica).

**Claude no inventa fechas, actividades ni enlaces:** los completan los autores. Claude prepara la tabla y la inserta.

## 6. Carpeta de entrega
- Copia lo que el proyecto ya tiene: avances, diagramas, matrices y PDF citados.
  `python "${CLAUDE_PLUGIN_ROOT}/skills/entrega-y-sustentacion/scripts/armar_entrega.py" --copiar`
- Revisa qué falta o está vacío:
  `python "${CLAUDE_PLUGIN_ROOT}/skills/entrega-y-sustentacion/scripts/armar_entrega.py" --revisar`
- **Código fuente:** `git archive` desde el repositorio, que no incluye `.env` ni archivos ignorados. Antes, corre `proteccion-datos/scripts/buscar_secretos.py`.
- **PDF y metadatos RIS para Zotero y Drive:** skill `asistente-investigacion-cientifica:paquete-evidencias`. El número de registros RIS debe ser igual al número de referencias del documento.
- **Evidencias de tutorías:** una carpeta por tutor, con `Evidencias_<fecha>.pdf`, que aportan los autores.

## 7. Subir, publicar o enviar
Solo si la usuaria lo pide y lo confirma: subir a Drive, enviar un correo, publicar un video o hacer push de un repositorio son acciones hacia afuera.

**Control:**
- la demo se reconstruye desde cero con el pipeline;
- las capturas están en el documento;
- `armar_entrega.py --revisar` no reporta faltantes;
- el RIS tiene tantos registros como referencias;
- `buscar_secretos.py` termina en 0 sobre el código entregado;
- `qa_pptx.py` termina en 0 sobre las diapositivas y el póster, y se revisaron las miniaturas;
- el `revisor-tribunal` no deja hallazgos críticos y los autores ensayaron sus preguntas.
