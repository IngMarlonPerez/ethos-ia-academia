---
name: papeleria-membretada
description: 'Hoja membretada de la empresa en Word y PDF y documentos sobre ella (cartas, actas, contratos). Usar al pedir el membrete o un documento «con el membrete».'
---

# Papelería membretada

## Antes de empezar
- Necesitas `empresa.json` con razón social, **RUC de la compañía** (no el personal), ciudad y contactos, y el logotipo exportado por `logos-y-piezas` (`logo-color.png` e `isotipo-color.png`).
- Si falta el RUC porque la empresa aún no está inscrita, crea el membrete **sin RUC** (campo vacío) y márcalo «versión provisional». No inventes el número.

## 1. Crear el membrete
`python "${CLAUDE_PLUGIN_ROOT}/skills/papeleria-membretada/scripts/crear_membrete.py" --empresa empresa.json --logo "01_Nombre_y_Marca/logos/logo-color.png" --isotipo "01_Nombre_y_Marca/logos/isotipo-color.png" --salida "08_Papeleria_Membretada/Membrete_<CLAVE>.docx"`

Lleva: encabezado (logo a la izquierda; razón social, RUC y ciudad a la derecha), barra de acento en degradado con los colores de marca, marca de agua (el isotipo muy tenue), pie con dirección, teléfono, correo y web con íconos, isotipo a la derecha y «Nombre comercial · Página X de Y». El cuerpo trae una carta de ejemplo.
- Sin `--isotipo` se omiten la marca de agua y el isotipo del pie.
- Los datos de contacto vacíos se quitan del pie (con su ícono).
- Los colores salen de `empresa.json → marca`.
- Prueba rápida sin datos reales: `--ejemplo` (con cualquier PNG en `--logo`).

## 2. Pasar a PDF y revisar
`python "${CLAUDE_PLUGIN_ROOT}/skills/papeleria-membretada/scripts/pdf_word.py" "08_Papeleria_Membretada/Membrete_<CLAVE>.docx"`
`python "${CLAUDE_PLUGIN_ROOT}/skills/papeleria-membretada/scripts/render_paginas.py" "<pdf>" "<prefijo>" 80`  (genera PNG para mirar)

- La conversión usa **Word instalado** (Windows, por COM) con tiempo límite y reintento; copia el archivo a una ruta corta porque Word no abre rutas de más de 259 caracteres. LibreOffice no hace falta.
- Mira la página: logo nítido, RUC correcto, nada pegado al borde, marca de agua apenas visible.
- **Peso:** si el PDF se sube a un portal con límite por página (la SCVS lo tiene), redúcelo; el membrete ya reduce sus imágenes. Un PDF de una página debe quedar en ~130 KB.

## 3. Documentos sobre el membrete
**a) Desde una plantilla Markdown** (actas, contratos, cartas, certificados): ver las plantillas en `gobierno-societario/plantillas/` y `equipo-y-practicantes/plantillas/`.
`python "${CLAUDE_PLUGIN_ROOT}/skills/papeleria-membretada/scripts/plantilla_a_docx.py" --plantilla acta.md --empresa empresa.json --membrete "08_Papeleria_Membretada/Membrete_<CLAVE>.docx" --datos datos.json --salida acta.docx --pdf`
Lo que no tenga dato queda como `[campo]` resaltado en amarillo y el script lo lista: así se ve qué falta antes de firmar.

**b) Desde Python**, para informes largos con tablas, figuras y notas APA: `scripts/mdoc.py` (`MDoc`: título, secciones, párrafos con **negrita**/~~cursiva~~/`código`, viñetas, tablas, imágenes, cuadros de aviso, firmas). Indica el membrete con `MDoc(template=...)` o `MEMBRETE_DOCX`, y los colores con `set_marca(...)`.

**c) Documentos financieros del balance inicial:** los genera `balance-inicial-scvs`.

## 4. Firma electrónica
Deja siempre espacio sobre la línea de firma: el sello de la firma (FirmaEC u otra) se estampa ahí. Los PDF firmados se guardan con sufijo `-signed` junto al original; **no sobrescribas** el original sin firma.

## 5. Reglas
1. El RUC y la razón social del membrete salen de `empresa.json`. Después de crear o cambiar el membrete, corre `verificar-expediente`: encuentra los documentos que aún tienen el dato viejo.
2. Al reemplazar un membrete, conserva el anterior como `..._version_anterior.docx`.
3. Metadatos del archivo: creador = razón social (no el nombre de una herramienta ni de una persona).
4. Documentos largos: nombres de archivo cortos (≤ 40 caracteres) y rutas cortas.
5. Lo que firma un tercero (contador, abogado) lleva sus datos reales; si faltan, líneas en blanco para llenar a mano. Nunca inventes un número de registro.

## Control
El membrete en PDF muestra RUC y razón social = `empresa.json`; los documentos generados tienen 0 campos amarillos antes de firmar; `verificar-expediente` sin hallazgos. Marca la etapa 3.
