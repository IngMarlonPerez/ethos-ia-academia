---
name: datos-macro-ecuador
description: 'Investigaciones de Macroeconomía de Ecuador con datos oficiales (BCE, INEC, Banco Mundial): PIB, ciclos, VAB, inflación y balanza, con gráficos y Word. Usar con variables macro de Ecuador o graficar el PIB.'
---

# Investigación macro de Ecuador con datos oficiales

Ejemplo completo del S6 (Grupo 5, Macroeconomía Básica): un ejemplo interno (no incluido en la versión pública). Fuentes y trampas: `referencias/fuentes-datos-ecuador.md`.

## Flujo
1. **Consigna y guía** (`leer-consigna-rubrica`): sacar los N puntos exactos, formato (A4, Times New Roman 12, interlineado 1,5), rúbrica por apartado, Turnitin < 10 % y reparto por integrante.
2. **Detectar huecos** antes de escribir: cruzar los N puntos contra lo entregado. Si falta uno (en S6: VAB y previsión del BCE), redactarlo desde el informe del BCE, **marcarlo como redactado por el asistente** y avisar.
3. **Verificar cada cifra** contra la fuente primaria: serie PIB real (Banco Mundial `NY.GDP.MKTP.KD.ZG` con `scripts/obtener_datos_wb.py`), Informe de evolución de la economía del BCE (PDF), IPC del INEC. No usar datos mensuales como anuales; comprobar las sumas internas de cada tabla; distinguir nominal vs real; las series encadenadas no suman (participaciones a precios corrientes + variaciones reales).
4. **Literatura Scopus de los últimos 5 años** (`PUBYEAR > 2020` en 2026), verificada por DOI con OpenAlex/Crossref; datos oficiales y el libro exigido (p. ej. Blanchard) no cuentan para esa regla. No hace falta el pipeline PRISMA completo salvo que la consigna lo pida.
5. **Gráfico del crecimiento** con `scripts/grafico_ciclo.py`: línea con marcadores, cero, tendencia, promedio y bandas por fase con leyenda y etiquetas sin encimar. Definir una **regla explícita** de clasificación y avisar que no es datación econométrica; incluir 2020 cuando el análisis cubra 2020–2025; responder «mayor variación / mayor retroceso» con salvedades (efecto rebote, nivel vs tasa, ventana, 1999).
6. **Redactar**: introducción (Blanchard cap. 5 IS-LM ↔ dolarización: sin LM propia, ajuste vía fiscal/externo), desarrollo por punto de la consigna, conclusiones (una por punto con cifra) y recomendaciones (fiscal, comercial, competitividad; cada una atada a un hallazgo y a literatura reciente). Cifras con coma decimal y punto de miles; tablas APA sin líneas verticales con «Nota. Elaboración propia con… (fecha de consulta)»; todo cálculo propio rotulado «estimación propia».
7. **Ensamblar** con `armar-documento-unemi` (carátula intacta, `_FINAL.docx`) y verificar el PDF página por página.
8. Entregar Word + PDF sin archivos sueltos y un resumen honesto (qué estaba mal, qué se cambió, qué verificar: Turnitin, número de página si el pie es gráfico, edición de Blanchard).
