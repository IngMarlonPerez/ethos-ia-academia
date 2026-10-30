---
name: diapositivas-tema-economico
description: 'Diapositivas grupales sobre un tema económico con la plantilla y colores UNEMI, datos oficiales y referencias con DOI, exportadas a PDF. Usar al pedir «diapositivas sobre un tema económico».'
---

# Diapositivas sobre un tema económico (plantilla UNEMI)

Probado en «S8-TARE_2 Metodología de Investigación Básica, Grupo 5» (2026-10-23): 9 láminas, tema inflación y canasta básica, 7 artículos Scopus + INEC. Script completo: un ejemplo interno (no incluido en la versión pública). Carga también la skill `pptx` (pptxgenjs).

## Flujo
1. **Consigna, rúbrica y plan del grupo** (`leer-consigna-rubrica`). Contrastar la estructura del plan con la de la consigna: en el S8 el plan tenía 4 láminas de desarrollo y la consigna exigía 5. Manda la consigna; avisar a la usuaria.
2. **Elegir el tema con Scopus antes de redactar**: `scopus_contar` para 3–4 temas candidatos (p. ej. inflación/canasta, dolarización, informalidad, remesas) y mantener el del plan si tiene literatura suficiente. Exportar con `scopus_exportar` (ventana 2020–2026, `DOCTYPE(ar)`).
3. **Resúmenes**: fuera de la red UNEMI `scopus_resumen` da HTTP 401 → leer el resumen en OpenAlex (`abstract_inverted_index`) y completar volumen, número y páginas en Crossref. **No citar un artículo cuyo resumen no se pudo leer** (se descartó así uno sobre salario mínimo).
4. **Datos oficiales**: confirmar cada cifra en la página del organismo con el navegador (p. ej. CFBC del INEC en `ecuadorencifras.gob.ec/canasta-familiar-basica-de-consumo-cfbc/`). Cifras derivadas (ingreso familiar = 1,6 perceptores × SBU) se rotulan como estimación. La fuente de datos (INEC) entra como referencia adicional: la rúbrica pide un **mínimo** de 7.
5. **Plantilla**: descomprimir el .pptx de la docente; `ppt/media` trae el fondo de portada y el de contenido (en UNEMI: azul `203145` y naranja `EC8532`, logo UNEMI arriba a la derecha). Usarlos como `background` en pptxgenjs `LAYOUT_WIDE`; el logo de la carrera va en el layout de contenido (arriba a la izquierda) y se agrega a mano en la portada.
6. **Diseño por lámina** (variar el formato): pregunta problema + cifra grande; 3 tarjetas con ícono para causas; cifras clave sobre fondo de color; gráfico de barras nativo; línea de tiempo; proceso numerado; conclusión sobre fondo oscuro; referencias con hipervínculo. Cuerpo ≥ 16 pt; cada lámina con «Fuente: Autor (año)».
7. **Exportar y revisar con PowerPoint real** (LibreOffice no está en Windows): COM `Presentations.Open` → `SaveAs(pdf, 32)` y `Slide.Export(png)` para mirar cada lámina.
8. **Errores típicos vistos**: el texto de la portada se monta sobre el logo UNEMI del fondo (el logo baja hasta ~2,3" de 7,5"); los rótulos de los gráficos salen con punto decimal según el idioma del sistema → poner el valor con coma en la categoría.
9. Entregar PDF + .pptx en la carpeta de la tarea y cerrar con `revision-final-honesta` (qué datos son estimaciones, qué referencia quedó sin volumen, que la usuaria pruebe los enlaces).
