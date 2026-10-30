---
name: paquete-evidencias-economia
description: 'Carpeta de evidencias para Drive de un trabajo de Economía: CSV, RIS, PDF, gráficos, scripts, matriz y documento final. Usar con «evidencias» o «dejar todo ordenado». No sube nada.'
---

# Paquete de evidencias para Drive

Estructura (la crea `iniciar-trabajo`):
| Carpeta | Contenido |
|---|---|
| `01_Busquedas_Scopus/` | CSV exportados completos, búsqueda por DOI, `referencias_incluidas_zotero.ris` y `referencias_elegibles_no_seleccionadas.ris` |
| `02_PDF_articulos/` | PDF de acceso abierto con `Autor_Año_Tema.pdf`; `por_descargar.md` con prioridad, DOI y motivo (403, cerrado, CAPTCHA) |
| `03_Graficos/` | PNG de todas las figuras |
| `04_Scripts_Python/` | librerías, `config_trabajo.py`, scripts de construcción (reproducibles) |
| `05_Base_datos/` | `Matriz_consistencia.xlsx`, base de datos Excel (hojas **Definiciones**, **Fuentes** con verificación y nivel de lectura, **Conteos_Scopus**, **Politicas** con país/año/impacto/fuente, **Matriz_evolutiva**, **Corpus**, **Resumen_estadistico**, **Descartadas**), `prisma_conteos.json`, `openalex_metadatos.json` |
| `06_Documento_final/` | Word y PDF entregados |
| raíz | `LEEME.md` (qué hay, cómo se reproduce, flujo de selección, cómo citar con Zotero, qué debe revisar el grupo) |

## Pasos
1. Regenerar todo desde los scripts (matriz, RIS, figuras, documento) para que carpeta y documento coincidan; correr `inventario_pdf.py` para cruzar los DOI incluidos con los PDF.
2. Redactar `por_descargar.md` y `LEEME.md` (modelo: un ejemplo interno (no incluido en la versión pública) y la carpeta del S7 de HPE). El LEEME declara con honestidad el nivel de lectura de los incluidos y que el cribado por título fue asistido por reglas.
3. **No subir a Drive ni compartir**: la usuaria sube la carpeta y pega el enlace en los marcadores «PEGAR AQUÍ» del documento. Si lo pide expresamente y hay conector de Drive, confirmar antes de publicar.
4. Si hay integrantes, recordar que la carpeta de Drive debe tener permiso de lectura para la docente.
