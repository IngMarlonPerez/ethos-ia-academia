# Vocabulario de búsqueda por área de la economía (Scopus, TITLE-ABS-KEY)

Estructura de toda ecuación: **bloques OR por concepto, unidos con AND**, en inglés. Filtros por defecto: `AND DOCTYPE(ar) AND LANGUAGE(english) AND PUBSTAGE(final)`; ventana `AND PUBYEAR > 2020 AND PUBYEAR < 2027` si la usuaria exige 5 años (en 2026). Para historia del pensamiento: sin ventana y con excepción documentada.
Siempre: (1) correr primero las cadenas del plan del grupo tal cual; (2) `scopus_contar` sin y con filtros; (3) exportar **todos** los registros (`max_registros` ≥ total) para que el flujo PRISMA cuadre; (4) añadir una ecuación por pregunta Q.
Tesauros para sinónimos: **JEL** (A1 historia del pensamiento, D micro, E macro, M41 contabilidad de costos, O desarrollo, C econometría), términos indexados de Scopus y UNESCO.

| Área | Conceptos y bloques OR sugeridos | Ejemplo de ecuación |
|---|---|---|
| **Historia del pensamiento económico** | "ancient economic thought", scholasticism, "just price", usury · mercantilism, physiocracy, "Tableau economique", "net product" · "Richard Cantillon", "William Petty", "David Hume", "price-specie flow" · "labour theory of value", "surplus value", alienation, "primitive accumulation" · "marginal revolution", marginalism, "neoclassical economics", "theory of value" | `TITLE-ABS-KEY("Mercantilism" OR "Physiocracy" OR "Physiocrats" OR "Tableau economique") AND DOCTYPE(ar) AND LANGUAGE(english)` |
| **Microeconomía** | "price elasticity" OR "cross-price elasticity" · demand, "consumer choice", "Slutsky", "substitution effect", "income effect" · "market structure", oligopoly, monopoly · sector concreto (streaming, bus transport, food demand) | `TITLE-ABS-KEY("price elasticity" AND ("bus" OR "transport")) AND PUBYEAR > 2020` |
| **Macroeconomía** | "economic growth", "business cycle", recession, "GDP growth" · "value added", inflation, CPI · "balance of trade", exports, imports · dollarization, "IS-LM", "fiscal policy" · Ecuador / "Latin America" | `TITLE-ABS-KEY(("economic growth" OR "business cycle") AND Ecuador) AND PUBYEAR > 2020` |
| **Costeo y contabilidad de costos** | "cost accounting", "activity-based costing", "cost-volume-profit", "job order costing", "process costing", "decision making" · pymes / SMEs | `TITLE-ABS-KEY(("cost volume profit") AND ("decision making"))` · probadas en S9: ver skill `costeo-cvu-ordenes-abc` (B1 133, B2 817, B3 143) |
| **Metodología de la investigación** | "systematic review", PRISMA, "literature search", "bibliographic databases", "academic search engines", "research reliability" | `TITLE-ABS-KEY("academic search engines" AND (reliability OR quality))` |
| **Econometría y datos de corte transversal** | "multinomial logit", probit, IIA, "internal migration", youth, "binary choice", "marginal effects" | `TITLE-ABS-KEY("multinomial logit" AND ("internal migration" OR mobility))` |
| **Desarrollo, trabajo, distribución** | inequality, "income distribution", "labour market", informality, poverty, "platform economy" | `TITLE-ABS-KEY(("platform work" OR "gig economy") AND (exploitation OR alienation))` |
| **Redacción científica (para la introducción)** | "research article introduction", "move structure", "CARS model", "scientific writing" | `TITLE("introduction" AND ("research article*" OR "scientific paper*") AND ("move*" OR "writing" OR "structure"))` |

## Buenas prácticas probadas
- Una cadena demasiado amplia da miles de resultados: eso es solo la cifra de identificación; el cribado la reduce. No asustarse ni recortar a mano.
- Si la cadena exacta del plan da 0 (p. ej. "Precursors of classical economics"), se registra el 0 y se sigue con variantes.
- Un autor o escuela que el plan menciona pero que Scopus no devuelve se busca por **DOI** (`DOI(a) OR DOI(b)`): sirve también para verificar las referencias que aportan los compañeros.
- Scopus sin red UNEMI ni token → solo vista STANDARD: sin resúmenes y con **solo el primer autor**. Completar con OpenAlex (`scripts/enriquecer_openalex.py`).
- Descargar los conteos por periodo (2000–2009, 2010–2019, 2020–2026) para el gráfico de barras de la metodología.
