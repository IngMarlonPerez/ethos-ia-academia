---
name: logos-y-piezas
description: 'Convierte el logo oficial en todas las piezas: variantes, isotipo, favicons, portadas de redes y paleta. Usar cuando haya logo y se necesite exportarlo para web, redes o papelería.'
---

# Logos y piezas

## 1. Identifica la fuente y el tablero
- **PDF o .ai compatible con PDF** (lo normal si el diseñador usó Illustrator): ábrelo con PyMuPDF indicando que es PDF. Cada tablero es una variante. Lista cuántos hay y mira cada uno antes de elegir:
  ```python
  import pymupdf; d = pymupdf.open("Logo.ai", filetype="pdf"); print(len(d), [p.rect for p in d])
  ```
- **Qué tablero usar:** el de **color sobre fondo blanco** para membrete, papelería, impresión y como fuente de todo lo demás. El monocromo negro es para sellos y estampado de una tinta. Los de fondo oscuro son solo para pantalla; el de texto blanco sobre blanco es invisible.
- **PNG/JPG:** sirve si el logo está sobre blanco o ya es transparente. Nunca partas de una foto de una pared, un letrero ni una imagen generada por IA con texto: tienen errores y reflejos.
- Si el diseñador entregó imágenes de «mesas de trabajo» en PNG y un vector, usa el vector.

## 2. Exporta el juego de piezas
`python "${CLAUDE_PLUGIN_ROOT}/skills/logos-y-piezas/scripts/exportar_logo.py" --fuente "Logo.ai" --mesa 3 --fondo blanco --empresa empresa.json --salida "01_Nombre_y_Marca/logos"`

Genera, con fondo transparente salvo donde se indica:
| Archivo | Uso |
|---|---|
| `logo-color / -negro / -blanco.png` | Documentos, web, sello y fondos oscuros |
| `isotipo-color / -negro / -blanco.png` | Símbolo solo (se separa automáticamente si hay un hueco entre símbolo y texto) |
| `favicon-16/32/48.png`, `favicon.ico`, `apple-touch-icon.png`, `icon-192.png`, `icon-512.png` | Sitio web y aplicación instalable |
| `foto-perfil-800.png` | WhatsApp, Facebook, Instagram, LinkedIn, YouTube, X |
| `portada-facebook-820x312.png`, `portada-linkedin-1584x396.png`, `portada-youtube-2560x1440.png` | Portadas (YouTube con el contenido en la zona segura central) |
| `og-1200x630.png` | Vista previa al compartir el enlace del sitio |
| `paleta-swatch.png` | Muestra de colores para la imprenta |

Opciones: `--fondo transparente` si ya hay un PNG con alfa; `--color-fondo RRGGBB` para el fondo de portadas y foto de perfil (por defecto, el primario de la marca). Sobre fondo oscuro el símbolo va en blanco automáticamente.

## 3. Revisa a ojo
Junta las piezas sobre fondo blanco, gris y oscuro, y mira:
- ¿el logo en negro conserva los detalles (si el original tiene degradados internos, el negro los aplana: es lo esperado en un sello)?;
- ¿el isotipo se separó bien (sin cortar letras del nombre)?;
- ¿el favicon se entiende a 16 px?

**Límite conocido:** «color a alfa» convierte el blanco en transparencia. Si el logo tiene **partes blancas internas** (letras blancas dentro de una forma), quedan transparentes. En ese caso pide al diseñador el PNG con transparencia real y usa `--fondo transparente`.

## 4. Otras piezas que se piden
- **Sello físico:** versión monocromo negro; entrega al taller el vector o un PNG de ≥ 2000 px. El sello legal lleva la razón social; el comercial, el nombre de marca.
- **Camisetas y gorras:** el monograma simple (bordado: trazo grueso). Una versión por color de prenda.
- **Señalética y fachada:** revisa la ortografía del arte antes de imprimir.
- **Foto de perfil circular:** el símbolo ocupa ~60 % del lienzo para que el recorte circular no lo corte.

## 5. Registra y avisa
- Guarda en `01_Nombre_y_Marca/logos/` la fuente original (.ai) y el juego exportado; anota en `LEEME.txt` qué tablero se usó y quién es el autor del diseño.
- Pide al diseñador la **cesión escrita de derechos** si no la tienes, y decide dónde va su crédito (el README del sitio, el pie de la página de marca).
- Si hay documentos o piezas que aún muestran un logo o un nombre anterior, haz la lista (`verificar_expediente.py` busca `nombres_anteriores`) y corrígelos en un solo lote.

## Control
Logo en color, negro y blanco con transparencia; favicon y foto de perfil legibles; portadas con el tamaño oficial; fuente original archivada. Marca la etapa 2 con la nota «tablero N del archivo X; autor …».
