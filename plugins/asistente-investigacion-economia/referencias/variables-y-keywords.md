# De la pregunta a las palabras clave

## 1. Estructurar la pregunta

Elige el esquema que se ajuste al tipo de estudio:

| Esquema | Para qué | Elementos |
|---|---|---|
| **PICO** | Efecto de una intervención | Población · Intervención · Comparación · Resultado (outcome) |
| **PEO** | Relaciones y exposiciones, típico en Economía y gestión | Población · Exposición o variable independiente · Resultado o variable dependiente |
| **SPIDER** | Estudios cualitativos | Muestra · Fenómeno de interés · Diseño · Evaluación · Tipo de investigación |
| **Conceptos del objetivo** | Trabajos teóricos o deberes | Un concepto por idea central del objetivo |

**Ejemplo (Economía):** «¿Cómo influye el sistema de costeo en la rentabilidad de las pymes manufactureras?»
- P = pymes manufactureras
- E = sistema de costeo (ABC, costeo directo, CVU)
- O = rentabilidad

## 2. Variables y dimensiones

| Variable | Tipo | Dimensiones (lo que se mide u observa) |
|---|---|---|
| Sistema de costeo | Independiente | método (ABC, estándar, directo), precisión de la asignación, uso gerencial |
| Rentabilidad | Dependiente | margen operativo, ROA, margen de contribución |
| Pymes manufactureras | Contexto / población | tamaño, sector, país |

Cada variable, y a veces cada dimensión importante, se convierte en un **concepto de búsqueda**.

## 3. Del concepto a los términos en inglés

Por cada concepto, reúne:
- **El término principal**, en inglés científico: «cost accounting».
- **Sinónimos y variantes:**
  - «management accounting», «costing system*», «cost management»;
  - variantes ortográficas: labor/labour, modeling/modelling;
  - siglas: CVP, ABC, SME*.
- **Términos más amplios o más específicos**, solo si ayudan: «activity-based costing», «time-driven activity-based costing».
- **Fuentes para descubrirlos:**
  - **JEL** (American Economic Association) para Economía: M41 Accounting, D24 Production/Costs, L25 Firm Performance;
  - **Tesauro de la UNESCO** para ciencias sociales;
  - las *Index Keywords* y *Author Keywords* de 2 o 3 artículos clave ya conocidos («pearl growing»): abre el registro en Scopus o usa `scopus_resumen` y copia sus palabras clave;
  - ERIC (educación), MeSH (salud) y APA Thesaurus (psicología), si el tema cruza esas áreas.

## 4. Tabla de conceptos (va en el protocolo)

| Concepto | Bloque OR | Fuente |
|---|---|---|
| Sistema de costeo | `"cost accounting" OR "costing system*" OR "activity-based costing" OR "management accounting"` | JEL M41 + keywords de artículos clave |
| Rentabilidad | `profitab* OR "financial performance" OR "operating margin"` | JEL L25 |
| Pymes | `SME* OR "small and medium*" OR "small business*"` | Author keywords |

La ecuación es `TITLE-ABS-KEY((bloque 1) AND (bloque 2) AND (bloque 3))` más los filtros.

## 5. Ajustar según los resultados

| Con filtros hay… | Qué hacer |
|---|---|
| Menos de 8 resultados | Ampliar: más sinónimos, quitar el concepto menos esencial, usar truncamiento `*` |
| Entre 8 y 300 resultados | Bien: cribar todo |
| Más de 300 resultados | Precisar: poner en `TITLE()` el concepto clave, `SUBJAREA(BUSI OR ECON)`, frases exactas en lugar de palabras sueltas, o `W/3` entre términos |
| Mucho ruido de otros sectores | Añadir `AND NOT` con prudencia (p. ej. `AND NOT TITLE(patient*)`) y justificarlo en la matriz |

Registra **todas** las ecuaciones que corras, también las que se descartan. Son parte de la transparencia de PRISMA.
