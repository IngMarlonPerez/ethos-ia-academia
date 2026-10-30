# Trampas técnicas (Windows + Word + Python) ya sufridas

## Escribir código
- **Heredocs de bash corrompen `\n` y `\`**: escribir los `.py` con la herramienta **Write** y parchearlos con **Edit**. Un parche hecho con heredoc dejó cadenas partidas en varias líneas (error real en gráficos y documentos).
- Ejecutar con `PYTHONUTF8=1 python -I script.py`. `-I` quita el directorio actual del path: añadir `sys.path.insert(0, carpeta_de_scripts)` en los scripts que importan librerías hermanas.
- La consola de Windows rompe tildes: `sys.stdout.reconfigure(encoding="utf-8")`, volcar a archivos UTF-8 y leerlos con Read.
- Teclear claves de DOI con cuidado (error real `worlrevipolieco` vs `worlrevipoliecon`): comparar siempre en minúsculas contra el CSV y dejar un `assert` de que todas las claves existen.
- Con python-docx un reemplazo de texto puede «no hacer nada» porque el texto está partido en runs: releer el archivo guardado y buscar el texto para confirmar.

## Rutas y Word
- Las carpetas de tareas UNEMI miden ~220 caracteres: un nombre largo supera MAX_PATH (260) y Word «no abre» el archivo. Nombres cortos y **exportar en `%TEMP%\hpe`** (ruta corta): `scripts/exportar_pdf_word.py` lo hace solo.
- Word por COM: usar PowerShell con un `.ps1` en archivo (el PowerShell tool bloqueó rutas con espacios entre comillas). Trabajar sobre copia y copiar el PDF de vuelta.
- La plantilla UNEMI trae margen inferior de 280 twips en la última sección: `lib_docx.ensamblar()` lo lleva a 1300.
- PDF escaneado sin texto: rasterizar con `scripts/pdf_a_texto.py <pdf> <txt> 110` y leer las imágenes.
- Descargas del navegador integrado no llegan a disco: `fetch` + base64 + `scripts/guardar_desde_navegador.py`.
- `rm` con comodines tras `cd` puede ser bloqueado: borrar solo archivos propios con ruta completa.

## Scopus / OpenAlex
- API sin red UNEMI: vista STANDARD (sin resúmenes, primer autor). `scopus_resumen` devuelve 401. Usar OpenAlex (`abstract_inverted_index`) para resúmenes y autores completos.
- `scopus_exportar` con `max_registros` menor que el total deja la matriz con un PRISMA falso: exportar todo.
- OpenAlex a veces trae el título en otro idioma o autores en mayúsculas: normalizar antes del RIS.
- Sitios que devuelven HTTP 403 (Springer/Taylor & Francis/PhilPapers/OUP): se anotan en `por_descargar.md`; no resolver CAPTCHA.

## Gráficos
- Diseñar a **tamaño final** (6 in de ancho): una figura de 7,5 in reducida a 15 cm deja la letra ilegible.
- Leyendas fuera del área de datos; no poner texto sobre flechas ni etiquetas sobre cajas. `lib_figuras.guardar()` verifica textos superpuestos o fuera del lienzo y **siempre se abre el PNG** para mirarlo.
- Un verificador no detecta flechas que cruzan texto: revisar a ojo.
