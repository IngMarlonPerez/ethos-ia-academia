---
name: evidencias-capturas
description: 'Genera y revisa capturas para los anexos (HTML a PNG, ventana concreta) sin filtrar datos privados. Usar para «saca capturas» o «necesito evidencias».'
---

# Evidencias y capturas

## Qué método usar
| Necesito… | Método |
|---|---|
| Una página web pública | `scripts/html_a_png.ps1 -Origen <url> -Png <archivo>` (Chrome/Edge sin ventana). Amazon y otros sitios lo bloquean: pide la captura a la usuaria |
| Una transcripción o salida de consola | Genera HTML (`pagina_transcripcion.py` u HTML propio) y conviértelo con `html_a_png.ps1` |
| Una ventana (VS Code, consola) | `scripts/capturar_ventana.ps1 -Titulo "<título>" -Png <archivo>` (PrintWindow) |
| Un programa con permisos (Seguridad de Windows, Configuración, instaladores) | La usuaria captura con **Win+Shift+S** (o Impr Pant) y te da el archivo o lo pega en el chat |

El navegador integrado de Claude **lee** páginas (`get_page_text`, `read_page`), pero no guarda PNG en disco.

## Reglas
1. **Revisa cada imagen con Read antes de usarla.** Debe mostrar solo lo que se evidencia. Descarta y borra lo que muestre: la conversación con Claude, rutas o carpetas de otros proyectos, correos, contraseñas, SSID o MAC.
2. **No uses `CopyFromScreen` del escritorio:** captura lo que esté al frente (en una ocasión salió la ventana de Claude con la conversación). `capturar_ventana.ps1` usa PrintWindow sobre la ventana elegida.
3. **VS Code en «modo restringido»:** abre una pantalla de «Confianza en el área de trabajo» con rutas de otros proyectos. No pulses «Confiar»: cierra esa pestaña con Ctrl+W (puede cerrar también el archivo) y reabre el archivo con `code -r <archivo>` antes de capturar.
4. **Rotula con honestidad.** Una imagen generada a partir de la salida real (no una foto de la ventana) lo dice en el pie: «imagen de consola generada con la salida real del programa».
5. **Las imágenes que envía la usuaria** en el chat quedan en la carpeta de imágenes de la sesión; conviértelas con Pillow a PNG si vienen en `.webp` antes de insertarlas en Word (`python-docx` no admite WebP).
6. Nombra los archivos por anexo (`AnexoA_…`, `D1_…`) y guárdalos en `anexos/`. Cada anexo de la guía debe tener su evidencia; si falta, la celda o el párrafo queda resaltado y se le dice a la usuaria qué captura falta.
7. Los archivos de prueba grandes (contenedores `.hc`) se avisan y se ofrecen para borrar.

## Evidencia desde las terminales de la app
Las pestañas de terminal de la sesión (donde la usuaria o Claude ejecutaron comandos) se leen con `mcp__terminal__read_terminal` (sin `tab_id` lista las pestañas; con `tab_id` lee una). Es salida original de los comandos. Para convertirla en imagen:
1. Copia el texto tal cual a un `.txt` (si es larguísimo, como la barra de progreso de Speedtest, deja un extracto con las líneas finales y rotula «extracto: se omiten las líneas de progreso»).
2. `python -I scripts/render_consola.py texto.txt imagen.png --titulo "Terminal de la sesión (PowerShell 7) · transcripción de la salida original" [--enmascarar-ip-privadas]`.
3. Pide a la usuaria las capturas con Win+Shift+S solo cuando haga falta una imagen real de una interfaz gráfica (Seguridad de Windows, menús, instaladores).
- **PrintWindow** sale en negro en algunas aplicaciones (p. ej. la interfaz de VeraCrypt) y **CopyFromScreen** captura lo que esté al frente (puede ser la conversación): en esos casos no insistas; usa una transcripción rotulada o pide la captura.
- Las capturas que la usuaria pega en el chat quedan en la carpeta de imágenes de la sesión: cópialas a `anexos/` con nombres por anexo.
