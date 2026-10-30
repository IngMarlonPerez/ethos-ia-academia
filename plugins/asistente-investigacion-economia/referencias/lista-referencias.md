# Lista de referencias (APA 7, adaptación al español)

## Reglas generales
- **Título de la sección:** «Referencias», centrado y en negrita. Si la plantilla del curso dice «Bibliografía», respeta la plantilla.
- **Formato:**
  - el mismo interlineado del documento;
  - **sangría francesa** de 1,27 cm;
  - alineación a la izquierda, aunque el texto esté justificado: evita espacios raros en los DOI.
- **Contenido:** solo las obras citadas, y todas ellas. Las comunicaciones personales no van.
- **Autores:**
  - Apellido, Iniciales con punto y espacio (Pérez, J. A.);
  - hasta **20 autores**, con «&» antes del último;
  - con 21 o más: los 19 primeros, puntos suspensivos (…) y el último.
  - Autor corporativo: el nombre completo, sin sigla (Comisión Económica para América Latina y el Caribe).
- **Fecha:** (2024). · (2024, 5 de mayo). · (s.f.). · (en prensa).
- **Títulos:**
  - artículos, capítulos y páginas web: en tipo oración, sin cursiva;
  - libros, informes, tesis, conjuntos de datos y software: en tipo oración y en *cursiva*;
  - revistas: con sus mayúsculas oficiales y en *cursiva*.
- **Fuente:** *Nombre de la Revista*, *volumen*(número), páginas. El volumen va en cursiva; el número entre paréntesis y sin cursiva; las páginas con guion medio (20–27).
- **Número de artículo:** si la revista no usa páginas, se escribe «Artículo 11» (APA en inglés: «Article 11»).
- **DOI:**
  - siempre como `https://doi.org/10.xxxx/…`, sin «doi:», sin «Recuperado de» y sin punto final;
  - si la revista imprimió un DOI que no resuelve (compruébalo con `https://doi.org/api/handles/<doi>`), usa la URL estable del artículo.
- **URL:**
  - solo si no hay DOI y el recurso es de acceso abierto o de un sitio web;
  - un artículo de base de datos sin DOI (p. ej. suscripción de la biblioteca) va sin URL, como un impreso.

## Orden alfabético (APA 7, 9.44–9.49)
1. Por el apellido del primer autor, **letra por letra** y sin contar espacios ni signos: «da Silva» se ordena como «dasilva», después de «Daowadueng».
2. «Nada precede a algo»: Loft, V. va antes que Loftus, E.
3. Mismo primer autor:
   - la obra de un solo autor va antes que la de varios;
   - las de varios autores se ordenan por el segundo apellido, y así sucesivamente.
4. Mismos autores: por año, de la más antigua a la más reciente.
5. Mismos autores y mismo año: por título, con la letra a, b… después del año (2024a).
6. Las partículas se ordenan según el uso del autor. Si la usa como parte del apellido (De Vries), se ordena por la partícula.

`word_apa.referencias()` y `verificar_apa.py` aplican estas reglas.

## Plantillas y ejemplos

**Artículo con DOI**
Pérez, J. A., Gómez, M., & Ruiz, L. (2024). Costos indirectos y rentabilidad en pymes manufactureras. *Revista de Contabilidad*, *27*(2), 195–211. https://doi.org/10.6018/rcsar.509111

**Artículo con número de artículo**
Lambert, S. L., Krieger, K., & Mauck, N. (2024). Predicting operating income via a generalized operating-leverage model. *International Journal of Financial Studies*, *12*(1), Artículo 11. https://doi.org/10.3390/ijfs12010011

**Artículo sin DOI, de acceso abierto**
Thasan, S., Rahman, A., Subramanian, P., & Williams, M. J. (2023). An intelligent decision support system to aid profit planning in manufacturing companies. *International Journal of Intelligent Systems and Applications in Engineering*, *11*(4s), 345–356. https://ijisae.org/index.php/IJISAE/article/view/2674

**Artículo en otro idioma (no inglés)**
Ortiz, M. F., & Silva, J. dos S. (2024). Gestão de custos em uma indústria de laticínios: Uma análise de custo, volume e lucro [Gestión de costos en una industria láctea: un análisis de costo, volumen y utilidad]. *Custos e @gronegócio On Line*, *20*(3), 155–176. URL

**Artículo en prensa (publicación anticipada)**
Pérez, J. (en prensa). Título. *Revista*. https://doi.org/…

**Libro**
Horngren, C. T., Datar, S. M., & Rajan, M. V. (2021). *Contabilidad de costos: Un enfoque gerencial* (16.ª ed.). Pearson.
(Si el libro tiene DOI, va al final. APA 7 ya no incluye la ciudad de la editorial.)

**Libro editado y capítulo**
Gómez, M. (Ed.). (2023). *Gestión estratégica de costos*. Editorial Universitaria.
Luna, P. (2023). Costeo basado en actividades. En M. Gómez (Ed.), *Gestión estratégica de costos* (pp. 45–78). Editorial Universitaria.

**Tesis de repositorio**
García, A. (2027). *Sistemas de costeo y rentabilidad en pymes de Milagro* [Tesis de licenciatura, Universidad Estatal de Milagro]. Repositorio Institucional UNEMI. URL

**Informe de un organismo** (si el autor y la editorial son el mismo, se omite la editorial)
Comisión Económica para América Latina y el Caribe. (2024). *Estudio económico de América Latina y el Caribe 2024* (LC/PUB.2024/10-P). https://…

**Norma legal** (adaptación usual en países hispanohablantes)
Asamblea Nacional del Ecuador. (2010). *Código Orgánico de la Producción, Comercio e Inversiones*. Registro Oficial Suplemento 351.

**Página web**
Banco Central del Ecuador. (2026, 10 de marzo). *Título de la página*. https://…
Si el contenido cambia y no está archivado: … Recuperado el 5 de mayo de 2026, de https://…

**Conjunto de datos**
Instituto Nacional de Estadística y Censos. (2025). *Encuesta estructural empresarial 2024* [Conjunto de datos]. https://…

**Software**
StataCorp. (2023). *Stata statistical software* (Versión 18) [Software]. https://www.stata.com
R Core Team. (2025). *R: A language and environment for statistical computing* (Versión 4.5) [Software]. R Foundation for Statistical Computing. https://www.R-project.org

**Herramienta de IA generativa** (guía de APA Style, 2023; declara su uso si la institución lo pide)
Anthropic. (2026). *Claude* (versión Opus 5) [Modelo de lenguaje grande]. https://claude.ai

**Artículo de periódico**
Apellido, N. (2026, 3 de abril). Título del artículo. *El Universo*. https://…

## Abreviaturas en español
ed. (edición: 2.ª ed.) · Ed./Eds. (editor/es) · trad. (traductor) · p./pp. · párr. · s.f. · Vol. · N.º (número de informe) · [Conjunto de datos] · [Software] · [Tesis de maestría, Universidad X] · [Tesis doctoral, Universidad X].

## Antes de entregar
- Todas las referencias tienen DOI o URL cuando existen, con el formato correcto.
- Los años coinciden con los de las citas y están dentro del rango exigido.
- `verificar_apa.py` da 0 errores.
- El RIS consolidado de Zotero tiene el mismo número de registros que la lista.
