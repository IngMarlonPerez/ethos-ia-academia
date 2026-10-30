# Formato del documento (APA 7, trabajo de estudiante)

**La guía del curso o la plantilla institucional prevalece.** Esto es lo que dice APA cuando la guía no fija algo.

## Página y texto
- **Fuentes aceptadas por APA 7:** Times New Roman 12, Arial 11, Calibri 11, Georgia 11, Lucida Sans Unicode 10 o Computer Modern 10.
- **Interlineado:** doble en APA puro. Las guías universitarias suelen pedir 1,5, como la UNEMI.
- **Márgenes:** 2,54 cm por lado.
- **Alineación:** a la izquierda en APA puro. Muchas guías piden justificado.
- **Sangría:** 1,27 cm en la primera línea de cada párrafo, excepto en títulos, resúmenes y referencias (que llevan sangría francesa).
- **Número de página:** arriba a la derecha.

## Portada de estudiante (APA 7)
Título del trabajo en negrita, centrado y en la mitad superior; autores; afiliación (facultad o carrera y universidad); código y nombre de la asignatura; docente; fecha de entrega. Si la institución tiene portada oficial, como la UNEMI, **usa la plantilla sin modificarla**. Si notas un error en ella, comunícalo en lugar de corregirlo por tu cuenta.

## Títulos (5 niveles)
| Nivel | Formato | En `word_apa.Cursor.titulo()` |
|---|---|---|
| 1 | Centrado, negrita | `titulo(texto, 1)` |
| 2 | Alineado a la izquierda, negrita | `titulo(texto, 2)` |
| 3 | Alineado a la izquierda, negrita cursiva | `titulo("*texto*", 3)` |
| 4 | Con sangría, negrita, termina en punto, y el texto sigue en la misma línea | `titulo(texto, 4)` |
| 5 | Con sangría, negrita cursiva, termina en punto, y el texto sigue | `titulo(texto, 5)` |
- En español, los títulos llevan mayúscula solo en la primera palabra y en los nombres propios (RAE). APA en inglés usa mayúscula en cada palabra importante (*title case*).
- La introducción no lleva el título «Introducción» en APA puro, pero las plantillas universitarias sí lo incluyen. Sigue la plantilla.

## Tablas
- Encima: **Tabla N** en negrita; debajo, el título en *cursiva*, en una línea aparte.
- Solo líneas horizontales: arriba, bajo el encabezado y al final. **Sin líneas verticales.**
- El encabezado se repite si la tabla continúa en otra página, y las filas no se parten (`word_apa` lo hace).
- **Nota** debajo, empezando con la palabra *Nota.* en cursiva: fuente («Elaboración propia con base en…»), abreviaturas y notas de probabilidad (* p < .05).
- Cada tabla se menciona en el texto antes de aparecer: «La Tabla 3 muestra…».
- Las tablas grandes pueden usar letra de 10 puntos e interlineado sencillo.

## Figuras
- **Figura N** en negrita, título en *cursiva* debajo, luego la imagen y luego la *Nota*.
- Números y texto legibles en la figura; los gráficos de Excel se exportan a PNG.
- Mencionala en el texto antes de que aparezca.

## Números y estadística
- En palabras: de cero a nueve («cinco empresas»). En cifras: de 10 en adelante.
- **Siempre en cifras:**
  - porcentajes, estadísticos, dinero y unidades de medida;
  - edades, tamaños de muestra, puntajes, fechas y horas;
  - números de tablas y figuras.
- Una oración no empieza con cifra: se reescribe o se escribe en palabras.
- Decimales:
  - con coherencia en todo el documento (2 decimales para dinero y porcentajes);
  - el separador que exija la guía (ver `adaptacion-espanol.md`).
- Estadísticos en *cursiva*: *M*, *DE* (desviación estándar), *n*, *N*, *p*, *t*, *F*, *r*, *R*², β.
- *p* exacta con 2 o 3 decimales (*p* = .032, o *p* = 0,032 en español). Si es muy pequeña: *p* < .001.
- Sin cero inicial en valores que no pueden superar 1: *p*, *r*.
- Ecuaciones:
  - las sencillas pueden ir en el texto;
  - las importantes, en línea aparte y centradas, con el **editor de ecuaciones de Word** (Alt+=; `word_apa.ecuacion()`);
  - no se usan imágenes de fórmulas ni números sueltos.

## Siglas y abreviaturas
- La primera vez se escribe el término completo con la sigla entre paréntesis («margen de contribución (MC)») y luego solo la sigla.
- Solo conviene abreviar un término que aparece 3 veces o más.
- No se define una sigla en un título.

## Seriación
- Dentro de una oración: (a), (b), (c).
- En lista, lista numerada si hay orden o jerarquía y viñetas si no la hay. Todos los elementos con la misma estructura gramatical.

## Orden del trabajo (APA de estudiante / plantilla UNEMI)
Portada → (Resumen, si se pide) → Introducción → Desarrollo → Conclusiones → Referencias → Anexos o apéndices (Anexo A, Anexo B… con título propio, cada uno en página nueva).
