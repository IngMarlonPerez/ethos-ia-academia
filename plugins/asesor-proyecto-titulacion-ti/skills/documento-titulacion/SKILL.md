---
name: documento-titulacion
description: 'Genera el Word de cada avance desde la plantilla oficial (APA 7, PDF con índice) y protege el Word de la usuaria con copias versionadas. Usar para armar o regenerar el documento, o si se perdió el encabezado.'
---

# Documento del avance (etapa 10)

## Principios
Aprendidos en los Avances 1 y 2 (detalle en `referencias/errores-docx.md`):
1. **La plantilla oficial y los avances entregados no se editan.** Se copian; el generador inserta.
2. **Anclas por prefijo de texto** (`buscar(doc, 'Referencias', 'Heading 1')`), nunca por índice de párrafo: los índices cambian con cualquier edición.
3. **Una sola fuente de verdad:** cifras y tablas desde JSON; código extraído en vivo.
4. **Si el Word se editó a mano** (cambió la huella de su texto), no se sobrescribe: se integran esos cambios en el generador. Se usa la huella del texto y no el md5, porque Word vuelve a guardar el archivo al actualizar el índice.
5. **Cada versión se conserva y la zona protegida no se toca** (portada, fondo, encabezados, pies, logo, secciones). Ver la sección «Versionado y protección».

## Versionado y protección del Word
Scripts de esta skill (`scripts/`), adaptados del plugin «proyectos-academicos». Todos salen con código 1 si algo falla.

| Cuándo | Comando | Qué garantiza |
|---|---|---|
| Antes de tocar el Word de la usuaria | `python copia_trabajo.py documento/Avance_2.docx` | Copia los bytes a `Avance_2_v02.docx` + `.huella.json`; el original no cambia |
| La usuaria dice que lo editó | `python diff_versiones.py anterior.docx actual.docx` | Muestra qué párrafos cambió, añadió o quitó, para integrarlo al generador |
| Después de CADA lote de cambios | `python huella.py verificar nuevo.docx --contra huella.json` | Portada, encabezados, pies, logo, fondo y secciones siguen igual |
| Si solo se añadió contenido | `python diff_versiones.py antes.docx despues.docx --solo-inserciones` | Ningún párrafo existente cambió |
| Se perdió el encabezado o el fondo | `python huella.py plantilla doc.docx --plantilla plantilla.docx` → `huella.py restaurar … -o salida.docx` | Copia los encabezados y pies que faltan desde la plantilla oficial, sin tocar el texto |
| Al registrar una corrección | `python aserciones.py registrar documento/aserciones.json "Descripción" --contiene "nuevo" --no-contiene "viejo"` | Queda anotada para detectar reversiones |
| Antes de editar o regenerar | `python aserciones.py verificar documento/Avance_2.docx documento/aserciones.json` | Si un guardado desde un Word viejo deshizo una corrección: **informa y pregunta** antes de reaplicarla |

Reglas:
- Nunca se sobrescribe una versión existente (`copia_trabajo.py` se niega).
- El generador ya archiva la salida anterior en `documento/versiones/` y, al terminar, comprueba la zona protegida contra el origen. Si falla, no se entrega: se restaura.
- Pide que cierre Word antes de cada lote (un archivo abierto no se puede guardar de vuelta).
- Los incidentes reales que originaron estas reglas están en `asistente-titulacion-ti/referencias/lecciones-aprendidas.md`.

## 1. Preparar el generador del avance
- **Primero copia la biblioteca al proyecto**, para que el repositorio sea autocontenido y no apunte a ninguna carpeta de la herramienta:
  `python "${CLAUDE_PLUGIN_ROOT}/skills/documento-titulacion/scripts/copiar_biblioteca.py" <raíz del proyecto>`
  Deja `_automatizacion/lib/` (docx_titulacion, formato_es, perfil, trazabilidad, tabla_trabajos_previos, matriz_decision) y `_automatizacion/perfiles/`. Vuelve a ejecutarlo después de actualizar el plugin.
- Copia `${CLAUDE_PLUGIN_ROOT}/skills/documento-titulacion/scripts/generador_avance.py` a `_automatizacion/build_avance<N>.py` y ajusta `AVANCE`.
- El origen es la plantilla original para el Avance 1, o `titulacion.json` → `documentos[N-1].entregado` para los siguientes.
- El esqueleto ya:
  - importa la biblioteca desde `_automatizacion/lib/` (nunca desde la carpeta del plugin);
  - fija como autores del Word a los de `titulacion.json` (`autores`), y a nadie más;
  - lee el proyecto y el perfil;
  - trae una función de sección de ejemplo (2. Análisis del caso con las tablas de `trazabilidad.py`).
- Agrega una función por sección, con el orden y los títulos del perfil.

## 2. Insertar con `Insertor`
`docx_titulacion.py` toma el formato del perfil (fuente, tamaño, interlineado, tamaños de título).

| Método | Uso |
|---|---|
| `titulo(ancla, texto, nivel, salto_pagina, antes)` | Estilos `Heading 1/2` de la plantilla; `antes=True` para abrir una sección antes de «Referencias» |
| `subtitulo`, `parrafo`, `bloque`, `vinetas` | Texto con `**negrita**` y `*cursiva*` |
| `tabla(ancla, filas, titulo, nota, anchos, tam)` | Tabla APA 7 numerada, encabezado sombreado y repetido en cada página |
| `figura(ancla, png, titulo, fuente, ancho)` | Figura APA 7 numerada, leyendas unidas a la imagen |
| `codigo(ancla, texto, titulo)` | Código monoespaciado con fondo gris |

Utilidades del mismo módulo:
- `reemplazar_texto`, `eliminar` y `quitar_numeracion` (Referencias y Anexos van sin número);
- `insertar_referencia(doc, antes_de, partes)` y `referencia_desde_markdown('Autor. (2025). Título. *Revista, 4*(2), 1–9.')`;
- `funcion_py` y `fragmento` para el código;
- números con `formato_es` (`n`, `pct`, `miles`, `media_de`).

Además:
- Borra los párrafos de instrucciones de la plantilla («Se refiere a…», «(La extensión de este apartado…)») y las tablas de preguntas que deben ir en prosa, según el perfil.
- **El texto lo redacta Claude** con la skill `asistente-investigacion-cientifica:redaccion-apa7` (tono académico, citas APA 7) y queda en el generador como constantes o en archivos `.md` que el generador lee.

## 3. Generar, exportar y revisar
1. Genera: `python _automatizacion/build_avance<N>.py`. Se detiene si la plantilla cambió o si el Word se editó a mano.
2. Exporta el PDF, que actualiza el índice y los campos:
   `powershell -ExecutionPolicy Bypass -File "${CLAUDE_PLUGIN_ROOT}/skills/documento-titulacion/scripts/docx_a_pdf.ps1" -Docx documento/Avance_<N>.docx`
   Sin Word, usa LibreOffice y avisa que el índice no se actualizó.
3. **Revisa visualmente** las páginas nuevas: rinde el PDF a imágenes con pymupdf o léelo con la skill `pdf`. Busca leyendas huérfanas, tablas cortadas, figuras ilegibles y texto de la plantilla que haya quedado.
4. Corre `verificar-coherencia`. Si falla, corrige el **generador** (nunca el Word) y regenera.

## 4. Registro de cambios
`documento/Registro_cambios_Avance<N>.md` (`referencias/registro-cambios.md`):
- **secciones nuevas**, y qué observación del tutor atiende cada una;
- **cambios en secciones ya entregadas** («Dónde | Antes | Ahora | Por qué»): cifras actualizadas, alcance, frases corregidas;
- **pendientes de los autores** (prueba con usuarios, anexo de actividades, enlaces de videos).

Envía a la usuaria el `.docx`, el `.pdf` y el registro. Ella revisa antes de entregar.

**Control:**
- el md5 de la plantilla es igual al registrado (la plantilla nunca se abre ni se guarda con Word);
- el `.docx` y el `.pdf` se generaron sin errores;
- `verificar_coherencia.py` termina en 0;
- el registro de cambios lista cada modificación a lo ya entregado.
