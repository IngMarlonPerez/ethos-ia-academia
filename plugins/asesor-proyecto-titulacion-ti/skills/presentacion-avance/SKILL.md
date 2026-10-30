---
name: presentacion-avance
description: 'Presentación de un avance de la tesis de TI sobre la del avance anterior (mismo diseño), con guion en primera persona. Usar al pedir «la presentación del avance», «las diapositivas» o «el guion para presentar».'
---

# Presentación y guion de un avance

Para la defensa final usa `entrega-y-sustentacion`. Esta skill hace la presentación **de cada avance**. Conserva el diseño de la presentación que ya se entregó en el avance anterior y escribe el guion que la autora lee mientras presenta.

## 1. Antes de escribir
- **Lee lo que pide la tarea del avance** (aula virtual, perfil institucional, rúbrica). Una diapositiva por apartado exigido. En la UNEMI, el Avance 2 tiene:
  - portada;
  - contenido;
  - 1.1 Descripción;
  - 1.2 Propósito;
  - 1.3 Base conceptual;
  - 2.1 Requerimientos, con alternativas;
  - el modelo de decisión, si existe (por ejemplo, el AHP);
  - 3.1 Metodología;
  - 3.2 Diseño: arquitectura, despliegue, UML, y modelo entidad-relación con los recursos;
  - la evidencia del prototipo;
  - las conclusiones preliminares con el análisis de innovación;
  - el cierre.
- **Base:** la presentación del avance anterior (`.pptx`). Nunca se modifica: el script la abre y guarda el resultado en otro archivo. Si no hay una anterior, usa `entrega-y-sustentacion` → `diapositivas.py`.
- **Cifras, títulos y nombres** salen del documento del avance y de sus artefactos (`cifras_*.json`, matrices, `titulacion.json`), nunca de memoria. El título es el **vigente**: el corregido, si la tutora lo cambió.
- **Figuras:** se usan las del proyecto, como diagramas y capturas. Antes de usar una captura, revisa que no muestre datos personales reales ni credenciales.

## 2. El JSON
Copia `plantillas/presentacion-avance-ejemplo.json` a la carpeta de la presentación del avance; por ejemplo, `01_ANTEPROYECTO_Y_AVANCES/presentacion_avance2/presentacion_avance2.json`. Las rutas del JSON son relativas a esa carpeta.

- **`base`, `portada_base`, `layout_contenido`, `cierre.diapositiva_base`**
  - Abre la base para ver qué diapositiva es la portada, cuál es el cierre y qué diseño (*layout*) trae el fondo y el logo de las diapositivas de contenido: `python -c "from pptx import Presentation; ..."`, o mira las miniaturas.
  - Las demás diapositivas del avance anterior **se quitan**, porque eran de ese avance.
- **`portada.reemplazos`:** `{"texto con el que empieza el cuadro": "texto nuevo"}`. Así se cambia el título y el número de avance sin tocar el formato. Si un texto no aparece, el script se detiene.
- **`colores`:** `primario` y `acento`, tomados de la base. Por ejemplo, en la UNEMI son `203145` y `E87D1E`.
- **`diapositivas`:** cada una lleva `tipo`, `titulo`, `seccion` (el apartado del formato, como «1.1 Descripción») y `notas`, que es el guion.

| Tipo | Para qué | Campos |
|---|---|---|
| `agenda` | Contenido | `partes` [[n, título, detalle]] (4) |
| `lista_panel` | Problema y causas; ejes del estado del arte | `intro`?, `puntos` [[etiqueta, texto]] o [[etiqueta, título, detalle]], `panel` {`titulo`, `cifras`, `texto`, `nota`}, `pie`? |
| `objetivos` | Propósito | `general`, `especificos` [[OE, verbo, detalle]], `que_como_para_que` |
| `tarjetas_cifras` | Alternativas y requerimientos | `tarjetas` [[etiqueta, título, detalle, destacada]], `cifras`, `recuadro` {`titulo`, `puntos`}, `pie` |
| `tabla_barras` | Matriz y pesos (AHP, decisión) | `tabla` (fila 1 = encabezado), `nota_tabla`, `barras` [[etiqueta, valor 0–1, texto]], `panel` {`titulo`, `texto`}, `pie`, `nota` |
| `fases` | Metodología | `fases` [[etiqueta, título, detalle]], `destacada`, `subtitulo`, `pasos` [[n, texto]], `pie` |
| `imagen_lateral` | Arquitectura; modelo ER y recursos | `imagen`, `recuadro` {`cifra`, `etiqueta_cifra`, `titulo`, `filas` [[texto, valor, destacada]], `subtitulo`, `puntos`} |
| `galeria` | Despliegue; UML (2 a 4 figuras) | `imagenes` [[ruta, pie]] |
| `cifras_imagen` | Evidencia del prototipo | `cifras` (hasta 3), `imagen` |
| `conclusiones` | Conclusiones e innovación | `puntos`, `panel` {`titulo`, `puntos`}, `pie` |

**Que quepa.** Títulos de una línea, de unas 45 letras como máximo. Puntos de una o dos líneas. Si algo no cabe, se divide en dos diapositivas; no se achica la letra.

## 3. El guion (las `notas`)
Se escribe para **leerlo en voz alta**:
- en primera persona;
- con frases completas y un lenguaje natural;
- con conectores («Para lograrlo…», «Quiero aclarar que…»);
- sin viñetas ni siglas sin explicar.

Cada bloque dice lo que muestra su diapositiva y por qué importa.

- **Ritmo:** unas 140 palabras por minuto. El script informa la duración total. Si la tarea fija un tiempo, por ejemplo un video de 2 a 5 minutos, recorta el guion antes de entregarlo.
- **Las mismas cifras** que el documento y las diapositivas.
- **Honestidad igual a la del documento:** lo provisional se dice provisional (hipótesis, matriz de un desarrollador, despliegue propuesto); lo que gana otra opción se reconoce.
- **Portada y cierre:** sus notas van en `portada.notas` y `cierre.notas`. El cierre agradece y abre las preguntas.
- **Sin rastros de herramientas de IA** en las diapositivas, las notas ni los metadatos (skill `uso-etico-ia`). El autor de los archivos es la autora (`autor`).

## 4. Generar y revisar
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/presentacion-avance/scripts/presentacion_avance.py" presentacion_avance2.json
python "${CLAUDE_PLUGIN_ROOT}/skills/entrega-y-sustentacion/scripts/qa_pptx.py" PRESENTACION_AVANCE_II.pptx --salida qa
```
- **Salida:** el `.pptx`, con el guion también en las notas del orador, y el guion en `<guion>.docx` y `<guion>.md`.
- **Si solo cambió el guion:** usa `--solo-guion`, que regenera solo el `.docx` y el `.md`.
- **Exportar a PDF:** con PowerPoint (COM) o con `qa_pptx.py`. **Mira todas las diapositivas** en una hoja de miniaturas. Busca:
  - texto cortado o que se sale;
  - texto claro sobre fondo claro, u oscuro sobre fondo oscuro;
  - figuras demasiado pequeñas para leerse;
  - restos del avance anterior.

  Corrige en el JSON, nunca a mano en el PPTX, y vuelve a generar.
- **Dónde guardar:** junto a la presentación del avance y, con una copia, en la carpeta de entrega del avance.

## 5. Control
- Hay una diapositiva por cada apartado que pide la tarea, en el orden del formato.
- La portada tiene el título vigente y el número de avance correcto.
- Las cifras son iguales a las del documento.
- El guion está en primera persona, sale con una duración dentro del límite de la tarea y cubre todas las diapositivas.
- La presentación del avance anterior no cambió.
