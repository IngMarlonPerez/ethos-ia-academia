---
name: matrices-revision
description: 'Genera en Excel las 4 matrices de una revisión sistemática (búsqueda, cribado, extracción y síntesis, temática) y el diagrama PRISMA 2020. Usar al pedir una matriz de revisión, selección, literatura, extracción o PRISMA.'
---

# Las 4 matrices de revisión + PRISMA 2020

Todo sale de un solo archivo de datos por búsqueda, y un script genera el Excel y el diagrama. Así se puede regenerar sin perder nada cuando cambia una decisión.

| Hoja del Excel | Matriz | Para qué | Cuándo |
|---|---|---|---|
| `M1_Busqueda_Registro` | **1. Búsqueda y registro operacional** | Resultados brutos, ecuaciones, filtros, fecha, método, conteos y duplicados | Al terminar de correr las ecuaciones |
| `M2a_Cribado_titulo` · `M2b_Cribado_resumen` · `M2c_Elegibilidad` | **2. Cribado (inclusión y exclusión)** | Decisión y criterio por registro; puntaje 0–2 por pregunta en el texto completo | Al leer títulos y resúmenes, y luego los PDF |
| `M3_Extraccion` | **3. Extracción y síntesis** | Autor y año, objetivo, muestra, método, hallazgos, limitaciones, conclusiones, aporte y evidencia con página | En la lectura crítica de los PDF definitivos |
| `M4_Tematica` · `M4b_Cruce` | **4. Temática o cruzada** | Filas = variables o categorías; autores que coinciden o discrepan; vacíos; síntesis para redactar. Cruce autores × preguntas | Justo antes de escribir el marco teórico o la discusión |
| `PRISMA_2020` | Diagrama de flujo | Paso de M1 a M3 en números, con imagen | Al cerrar la selección |
| `Referencias_APA` | Selección final | Referencia APA 7 de cada incluido y dónde se usa | Antes de redactar |

Scripts en `${CLAUDE_PLUGIN_ROOT}/skills/matrices-revision/scripts/` (en el archivo de datos, `SCRIPTS` apunta a esta carpeta):
- `matrices.py`: la función `construir(d, salida)` genera el Excel y `<salida>_PRISMA_2020.png`.
- `diagrama_prisma.py`: `conteos_desde_datos(d)` y `dibujar(conteos, png)`. Es la plantilla oficial de PRISMA 2020 para bases de datos.
- `plantilla_datos.py`: la plantilla del archivo de datos. `nuevo-proyecto` la copia ya enlazada como `_automatizacion/matrices/datos_B1.py`.

## Cómo se usa

1. Copia `plantilla_datos.py` al proyecto como `datos_B<n>.py`, si `nuevo-proyecto` no lo hizo, y ajusta `SCRIPTS` a la carpeta `scripts/` de esta skill.
2. Completa las secciones marcadas con TODO, en el orden del pipeline:
   - `BUSQUEDAS` (con fecha y método) y `CSVS` → M1;
   - `PASAN_TITULO`, `REGLAS` y `MOTIVOS_RESUMEN` → M2a y M2b;
   - `ELEGIBILIDAD`, con puntajes `P(…)` por pregunta, decisión y `motivo_corto` → M2c, M4b y PRISMA;
   - `ANALISIS`, con muestra, limitaciones y conclusiones → M3;
   - `TEMATICA` → M4. Es opcional: si queda vacía, M4 se arma sola por pregunta con los aportes de M3 y queda por completar la síntesis;
   - `INCLUIDOS`, con la referencia APA 7 → Referencias.
3. Ejecuta `python datos_B<n>.py`. El script imprime el flujo PRISMA y **falla si los textos completos no cuadran** con las filas de elegibilidad.
4. Revisa el PNG del diagrama con Read antes de enviarlo. Envía el Excel a la usuaria (SendUserFile) antes de redactar.

## Cómo llenar bien M4 (la que prepara la redacción)

- Las filas son **ideas o variables**, no autores. Buenas categorías: las dimensiones del protocolo, las preguntas Q, o temas que salieron de la lectura.
- **Coinciden:** «Autor (año): lo que sostiene o encontró». Solo lo que el artículo realmente dice.
- **Discrepan o matizan:** contradicciones, contextos distintos o resultados opuestos. Es lo que da profundidad a la discusión.
- **Vacíos:** lo que ningún artículo resuelve (país, sector, método). Sirve para justificar la investigación.
- **Síntesis para redactar:** una o dos oraciones propias que integran a los autores. De aquí sale el párrafo del marco teórico.

## Controles de calidad
- Cada número del diagrama cuadra con la fase anterior: identificados − filtros − duplicados = cribados; cribados − excluidos = buscados; buscados − no recuperados = evaluados; evaluados − excluidos = incluidos.
- En `M4b_Cruce`, la fila de «Cobertura» muestra 2 en todas las preguntas. Si alguna tiene 1 o 0, hace falta buscar o leer más.
- Toda evidencia textual de M3 lleva la página de la revista.

## Compatibilidad
Los archivos de datos hechos con la versión anterior (`matriz_revision.py`, 6 hojas) funcionan con `matrices.py` sin cambios: los campos nuevos (`muestra`, `limitaciones`, `conclusiones`, `tematica`, `metodo`, `fecha`, `base`) son opcionales.
