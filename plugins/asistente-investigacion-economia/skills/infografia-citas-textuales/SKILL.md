---
name: infografia-citas-textuales
description: 'Infografía académica UNEMI con citas textuales de unos 40 palabras con página, de artículos abiertos con DOI, renderizada y armada en Word. Usar con «infografía con citas textuales» u «organizador visual».'
---

# Infografía con citas textuales verificadas

Probado en «S9-TALLER_2 Metodología de Investigación Básica, Grupo 5» (2026-10-23): carátula + infografía (6 bloques) + 3 referencias. Scripts: un ejemplo interno (no incluido en la versión pública) (`infografia.js`, `ensamblar_s9.py`).

## Regla central
**Una cita textual solo se escribe si se copió del PDF completo** y se ubicó su página impresa. Nunca desde un resumen ni de memoria. Si no hay PDF legible, se cambia de fuente.

## Flujo
1. **Consigna y plan**: anotar número de citas, extensión («de 40 palabras» = 38–41), subtemas del plan por integrante (p. ej. formulación, justificación, viabilidad) y la fecha que manda la consigna (si el plan dice otra, avisar).
2. **Fuentes**: la búsqueda general de OpenAlex trae ruido; filtrar por título:
   `https://api.openalex.org/works?filter=title.search:<frase>,is_oa:true,has_doi:true,publication_year:2015-2026&sort=cited_by_count:desc`
   Preferir revistas indexadas en español con `best_oa_location.pdf_url`. Una fuente por subtema.
3. **PDF**: descargar con `curl -A "Mozilla/5.0…"` a una carpeta propia (ScienceDirect devuelve HTML → descartar). Extraer por página con **PyMuPDF** (pypdf falla en PDF con AES sin `cryptography`). Mapear página del PDF → página impresa con el encabezado (en el S9: Uninorte p. = 918 + n; Plumilla p. = 56 + n).
4. **Citas**: elegir pasajes que cubran el subtema; unir guiones de fin de línea; contar palabras con Python; usar «[…]» si se recorta el inicio. Toda paráfrasis de la infografía también lleva su cita (rúbrica: «la información está citada en el texto»).
5. **DOI y APA**: comprobar que cada DOI redirige (`curl -o /dev/null -w '%{http_code}'` → 302) y completar autores, volumen, número y páginas en Crossref. Apellidos compuestos completos (Pineda Ballesteros et al.).
6. **Diseño HTML** (794 × 1123 px, A4): encabezado azul con logo de la carrera + logo UNEMI recortado del fondo de la plantilla + foto del banner de la carrera (enmascarada para que no asome el texto del banner); bloques numerados, flujo de pasos con íconos, tarjetas (p. ej. FINER), citas destacadas con su (Autor, año, p. X), errores frecuentes y pie. Íconos de `react-icons` en SVG en línea.
7. **Render**: `chrome.exe --headless=new --force-device-scale-factor=3 --window-size=794,1123 --screenshot=<png> file:///<html>` con rutas `cygpath -m` (barras normales).
8. **Word**: la carátula del grupo puede traer el trabajo anterior debajo: conservar solo la página 1 (hasta el `sectPr` de la carátula) y reemplazar tema y fecha en los `w:t` (el texto está duplicado en cuadros de texto `mc:AlternateContent`: reemplazar en todos). Insertar título + imagen (alto ≈ 8,5") y «Referencias» con salto de página, sangría francesa e hipervínculos reales.
9. **PDF con Word COM** (`ExportAsFixedFormat`, 17), renderizar las páginas con PyMuPDF y revisar; comprobar con `page.get_links()` que los DOI son clicables.
10. Entregar PDF + Word + PNG; informe honesto (campo de las fuentes, fecha elegida, revisión ortográfica pendiente de la coordinadora).
