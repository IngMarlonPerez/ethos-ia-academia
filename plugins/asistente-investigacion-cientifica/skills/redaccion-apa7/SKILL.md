---
name: redaccion-apa7
description: 'Redacción académica en APA 7 en español: citas, referencias con DOI, formato, cita↔referencia y similitud. Usar al redactar, citar, parafrasear, «normas APA» o corregir un documento académico.'
---

# Redacción en estilo APA 7.ª edición (en español)

Objetivo: textos que un docente o revisor lea como escritos por una investigadora cuidadosa. Tienen que cumplir cuatro condiciones:
- cada afirmación teórica tiene su cita;
- cada cita dice lo que el artículo realmente dice;
- el formato cumple APA 7;
- la prosa suena natural, no a IA.

Scripts: `${CLAUDE_PLUGIN_ROOT}/skills/redaccion-apa7/scripts/`. Para usar `word_apa.py` desde el script del proyecto, añade esa carpeta a `sys.path` antes de `from word_apa import …`.
Referencias: `${CLAUDE_PLUGIN_ROOT}/skills/redaccion-apa7/referencias/`.

## Antes de escribir
1. **Lee la guía del trabajo**: el PDF de la tarea, la guía del grupo o las normas de la revista. **Lo que pide la guía prevalece sobre APA**: fuente, interlineado, alineación, extensión, secciones, años de las fuentes. Si el trabajo es de la UNEMI y la guía no dice otra cosa, usa `referencias/perfil-unemi.md`.
2. **Ten a mano la evidencia**: la Matriz 3 (extracción, con la evidencia textual y su página) y la Matriz 4 (temática, con la síntesis por variable) de la skill `matrices-revision`. No escribas de memoria sobre lo que dice un artículo.
3. Define el perfil de números para todo el documento: separador decimal, «%» y comillas (`referencias/adaptacion-espanol.md`).

## Flujo
1. **Redactar:** `referencias/estilo-redaccion.md`.
   - Una idea por párrafo: afirmación, luego desarrollo con evidencia citada, luego cierre o transición.
   - Organiza el marco teórico por **variables o ideas** (filas de M4), no autor por autor.
   - Integra a los autores: «coinciden…», «a diferencia de…».
2. **Citar:** `referencias/citas.md`.
   - Texto en español: «y» entre dos autores; «et al.» desde la primera cita con 3 o más autores.
   - Página en las citas textuales. En la paráfrasis también se recomienda, y es obligatoria cuando se cita una cifra o una idea puntual.
   - Una cita textual de un artículo en inglés, traducida al español, es paráfrasis: sin comillas y con la página.
3. **Armar la lista de referencias:** `referencias/lista-referencias.md`.
   - Solo lo citado; todo lo citado.
   - Orden alfabético letra por letra.
   - Sangría francesa, DOI como `https://doi.org/…` y cursivas en la revista y el volumen.
4. **Formatear:** `referencias/formato-documento.md` (títulos, tablas, figuras, números, ecuaciones).
   - Para Word usa `scripts/word_apa.py`: `Cursor`, `tabla`, `figura`, `ecuacion` (editor de ecuaciones de Word), `referencias` ordenadas y `==marcador resaltado==` para lo que otra persona debe completar.
5. **Verificar:** `python "${CLAUDE_PLUGIN_ROOT}/skills/redaccion-apa7/scripts/verificar_apa.py" documento.docx --desde AAAA --hasta AAAA`. En trabajos largos, puedes delegar la auditoría completa en el agente `revisor-apa`. Revisa:
   - cita↔referencia, años distintos y duplicados;
   - orden alfabético y formato del DOI;
   - uso de «et al.» y de «&», y rango de años;
   - sangría francesa y cursivas.
6. **Similitud preventiva (antes de Turnitin o Compilatio):** `python "${CLAUDE_PLUGIN_ROOT}/skills/redaccion-apa7/scripts/similitud.py" documento.docx --fuentes incluidos.csv` (compara con los resúmenes) o `--carpeta textos/` (con los `.txt` que genera `pdf_tools.py texto`). Marca como FALLA las oraciones con 8 o más palabras idénticas a una fuente y como ADVERTENCIA las que comparten 35 % de trigramas. Reescribe desde la idea, no desde la frase. No sustituye a un detector oficial.
   - **Control: 0 errores.** Revisa también cada advertencia.
6. **Revisión visual:** exporta a PDF (COM de Word) y mira las páginas con tablas, figuras, ecuaciones y referencias. Revisa títulos huérfanos, «%» o números cortados y tablas partidas.

## Reglas que más se olvidan
| Situación | Correcto |
|---|---|
| 3 o más autores | (Pérez et al., 2024) desde la primera cita |
| 2 autores en el texto en español | Pérez y Gómez (2024) · (Pérez y Gómez, 2024) |
| Varias obras | (Gómez, 2023; Pérez et al., 2024), en orden alfabético y con punto y coma |
| Mismo autor, mismo año | (Pérez, 2024a, 2024b): las letras se asignan en la lista, por orden del título |
| Cita textual | "texto" (Pérez, 2024, p. 15) · sin página: (Pérez, 2024, párr. 3) |
| 40 palabras o más | en bloque con sangría de 1,27 cm, sin comillas, con la cita después del punto final |
| Fuente secundaria | (Allport, 1954, como se citó en Nuttin, 1985): en la lista va solo Nuttin |
| Artículo con número de artículo | *Revista*, *12*(1), Artículo 11. https://doi.org/… |
| Partícula al inicio de oración | «Da Silva et al. (2026)» y en la lista «da Silva, L. M.» |
| Título en otro idioma (no inglés) | Título original [Traducción al español entre corchetes] |

## Tono natural
- Frases de extensión variada, verbos concretos y sin muletillas: «cabe destacar», «juega un papel crucial», «en el mundo actual», tríadas de adjetivos, exceso de rayas.
- Afirma con la fuerza que da la evidencia: «sugiere» o «muestra», no «demuestra» sin datos.
- Si la skill **humanizer** está disponible y la usuaria lo pide, úsala en fragmentos sueltos sin alterar cifras ni citas.
- No inventes datos, páginas ni autores. Si falta una fuente para una afirmación, dilo y propón buscarla con `revision-sistematica`.
