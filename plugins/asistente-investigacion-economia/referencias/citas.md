# Citas en el texto (APA 7, adaptación al español)

APA usa el sistema **autor-fecha**. Cada cita en el texto tiene su entrada en la lista de referencias, y cada entrada se cita al menos una vez. Las comunicaciones personales son la única excepción.

## Formas de citar

- **Parentética:** autor y año entre paréntesis, al final de la idea: «…el costo variable reduce el margen (Pérez, 2024).»
- **Narrativa:** el autor forma parte de la oración y el año va entre paréntesis: «Pérez (2024) encontró que…».

## Según el número de autores

| Autores | Parentética | Narrativa |
|---|---|---|
| 1 | (Pérez, 2024) | Pérez (2024) |
| 2 | (Pérez y Gómez, 2024) | Pérez y Gómez (2024) |
| 3 o más | (Pérez et al., 2024) | Pérez et al. (2024) |
| Autor corporativo con sigla | 1.ª vez: (Comisión Económica para América Latina y el Caribe [CEPAL], 2024) · luego: (CEPAL, 2024) | 1.ª vez: Comisión Económica para América Latina y el Caribe (CEPAL, 2024) · luego: CEPAL (2024) |
| Autor corporativo sin sigla | (Universidad Estatal de Milagro, 2025) | Universidad Estatal de Milagro (2025) |
| Sin autor | Título breve: («Costos ocultos», 2024) si es un artículo o capítulo; (*Manual de costos*, 2024) si es un libro o informe | Igual |
| Sin fecha | (Pérez, s.f.) | Pérez (s.f.) |
| En prensa | (Pérez, en prensa) | Pérez (en prensa) |

- «et al.» va desde la **primera** cita con 3 o más autores: APA 7 eliminó la regla de APA 6 de nombrar a todos la primera vez.
- **Ambigüedad:** si dos referencias se abrevian igual (Kapoor, Bloom, et al., 2017 y Kapoor, Zucker, et al., 2017), escribe los apellidos necesarios para distinguirlas.
- **«y» o «&»:** APA en inglés usa «&» en la cita parentética. En un texto en español se escribe «y», tanto en la cita narrativa como en la parentética. En la lista de referencias se mantiene «&», como en el trabajo S7. Si la guía pide otra cosa, sigue la guía en todo el documento.
- **Partículas:** «da Silva», «de Loecker» o «van der Berg» se escriben como en el artículo. Al inicio de oración llevan mayúscula: «Da Silva et al. (2026)».

## Varias obras y repeticiones
- Varias obras en un paréntesis: orden alfabético y punto y coma → (Gómez, 2023; Pérez et al., 2024; Zapata y Luna, 2022).
- Mismo autor, varios años: (Pérez, 2021, 2024).
- Mismo autor y mismo año: (Pérez, 2024a, 2024b). Las letras se asignan en la lista de referencias según el orden alfabético del título.
- Obras citadas como ejemplo: (véase Pérez, 2024; también Gómez, 2023).
- Una idea que se retoma más adelante se vuelve a citar. Evita citar la misma fuente en cada oración de un párrafo que se basa entero en ella: una cita al inicio y otra al retomarla basta, si queda claro que las ideas siguen siendo de esa fuente.

## Citas textuales
- **Menos de 40 palabras:** entre comillas y con página: «…los costos fijos no cambian con el volumen» (Pérez, 2024, p. 15).
  - Página: p. 15 · pp. 15–16 · sin páginas: párr. 3 · con sección: (Pérez, 2024, sección Discusión, párr. 2).
- **40 palabras o más, en bloque:**
  - párrafo aparte con sangría izquierda de 1,27 cm y sin comillas;
  - mismo interlineado del texto;
  - la cita va **después** del punto final: … del período. (Pérez, 2024, p. 15)
  - `word_apa.Cursor.cita_en_bloque(texto, cita)` lo arma.
- Omisiones: tres puntos entre corchetes […]. Aclaraciones propias: entre corchetes. Un error del original: [*sic*].
- **Traducción:** si traduces al español una cita de un artículo en inglés, APA la considera paráfrasis. Va sin comillas y con la página (Pérez, 2024, p. 15). Si quieres conservar el texto exacto, cita en inglés entre comillas y con página.
- Usa las citas textuales con moderación. En trabajos académicos, la paráfrasis bien hecha luce más.

## Paráfrasis
- Reescribe con tus palabras y tu estructura, sin cambiar el sentido, y cita la fuente.
- La página se recomienda en la paráfrasis. Inclúyela siempre que parafrasees una cifra, una definición o una idea puntual de un texto largo.
- Distingue lo que el autor **encontró o sostiene** de lo que **cita de otros**. Si el artículo solo resume a otro autor, redacta «Pérez et al. (2024), al revisar estudios previos, señalan…», o busca la fuente original.

## Fuentes secundarias (úsalas lo menos posible)
- Formato: (Allport, 1954, como se citó en Nuttin, 1985). En la lista de referencias va **solo** la fuente que leíste: Nuttin.
- Si la fuente original está fuera del rango de años exigido, prefiere redactar la idea atribuyéndola al autor que leíste.

## Comunicaciones personales
(J. Pérez, comunicación personal, 5 de mayo de 2026). Incluye entrevistas no grabadas, correos y conversaciones. **No** van en la lista de referencias.

## Errores frecuentes
- «Pérez, et al. (2024)», con coma antes de et al. cuando es un solo apellido: se escribe «Pérez et al. (2024)».
- «(Pérez 2024)»: falta la coma. Lo correcto es «(Pérez, 2024)».
- Un año en el texto distinto al de la lista, o un apellido mal escrito: `verificar_apa.py` lo detecta.
- Citar un artículo por algo que solo aparece en su resumen o que el artículo atribuye a otro autor.
