# Perfil de formato UNEMI (usado en los trabajos de la autora)

Se aplica cuando el trabajo es de la Universidad Estatal de Milagro y la guía no indica otra cosa. En `word_apa.py`: `usar_perfil("unemi")`, que es el perfil por defecto.

| Elemento | Criterio |
|---|---|
| Fuente | Times New Roman 12 (o Arial 11, si la guía lo permite) |
| Interlineado | 1,5 |
| Alineación | Justificado; las referencias van alineadas a la izquierda con sangría francesa |
| Sangría | 1,27 cm en la primera línea de cada párrafo |
| Márgenes | Los de la plantilla oficial; si no hay plantilla, 2,54 cm |
| Portada | Plantilla oficial UNEMI **sin modificar**. Los errores de la portada se comunican a quien la arma, no se corrigen por cuenta propia |
| Estructura | Portada → Introducción → Desarrollo (partes o capítulos) → Conclusiones → Referencias (o «Bibliografía», según la plantilla) → Anexos |
| Fuentes | Artículos científicos de los últimos 5 años (p. ej. Scopus con la cuenta institucional), en APA 7 |
| Ecuaciones | Editor de ecuaciones de Word (Alt+=). No se aceptan números sueltos ni imágenes de fórmulas |
| Gráficos | Elaborados en Excel con fórmulas vivas y exportados como figura APA |
| Evidencias | PDF y metadatos .ris en la carpeta de Drive del grupo, con el enlace en Referencias y en Anexos (skill `paquete-evidencias`) |
| Entrega | En Moodle; revisar la fecha interna del grupo y la oficial |

## Cómo trabajar dentro de una plantilla existente
- **Nunca reescribas la plantilla a mano.** Usa un script que parta de una copia intacta (`Plantilla_ORIGINAL.docx`) e inserte el contenido después de los títulos existentes, con `word_apa.buscar_parrafo(doc, "Introducción")` y `Cursor`.
- Guarda el hash (md5) de cada versión generada. Si el Word cambió, la usuaria lo editó: compara antes de regenerar e integra sus cambios en el contenido.
- Exporta a PDF (COM de Word) y revisa visualmente las páginas nuevas antes de entregar.
