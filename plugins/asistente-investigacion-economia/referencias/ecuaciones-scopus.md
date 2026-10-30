# Ecuaciones de búsqueda en Scopus

Referencia oficial: https://dev.elsevier.com/sc_search_tips.html. La sintaxis de búsqueda avanzada es la misma en el sitio web y en la API.

## Campos más usados

| Código | Busca en |
|---|---|
| `TITLE-ABS-KEY( )` | título, resumen y palabras clave. Es el estándar para revisiones |
| `TITLE( )` | solo el título. Sirve para precisar |
| `AUTHKEY( )` / `KEY( )` | palabras clave del autor / todas las palabras clave |
| `SRCTITLE( )` | nombre de la revista |
| `AUTH( )` · `AU-ID( )` | autor por nombre o por identificador |
| `DOI( )` · `EID( )` | un documento concreto (útil para exportar el RIS de los incluidos) |

## Filtros (se agregan al final con AND)

| Filtro | Sintaxis para la API y la búsqueda avanzada |
|---|---|
| Años (5 años estrictos en 2026) | `PUBYEAR > 2021 AND PUBYEAR < 2027` |
| Solo artículos | `DOCTYPE(ar)` (revisión: `re`, congreso: `cp`, capítulo: `ch`, libro: `bk`) |
| Idioma | `LANGUAGE(english)` |
| Versión final (no «article in press») | `PUBSTAGE(final)` |
| Área temática | `SUBJAREA(BUSI OR ECON OR DECI)` (Business, Economics, Decision Sciences) |
| Acceso abierto (solo si se pide) | `OPENACCESS(1)` |

En la interfaz web, los filtros laterales aparecen como `LIMIT-TO(DOCTYPE,"ar")`. La API no acepta `LIMIT-TO`: usa las formas de la tabla. En la matriz se anotan los filtros en palabras («PUBYEAR 2022–2026; Article; English; final»).

## Operadores

- `OR` une sinónimos dentro de un bloque. `AND` une conceptos. `AND NOT` excluye; úsalo al final y con justificación.
- **Precedencia en Scopus:** OR se evalúa antes que AND, y AND antes que AND NOT. Aun así, usa **siempre paréntesis** para que la ecuación se lea sin ambigüedad.
- `"frase exacta"`: busca la frase, admite plurales y variantes menores. `{frase literal}`: coincidencia exacta, incluida la puntuación.
- `*` trunca (`costing*`, `profitab*`). `?` reemplaza una letra (`labo?r`).
- Proximidad:
  - `W/n`: a n palabras o menos, en cualquier orden, p. ej. `cost W/3 accounting`;
  - `PRE/n`: la primera palabra antes que la segunda.

## Plantilla

```
TITLE-ABS-KEY(("concepto 1" OR sinónimo* OR "variante") AND ("concepto 2" OR sinónimo*) AND ("concepto 3" OR sinónimo*))
AND PUBYEAR > 2021 AND PUBYEAR < 2027 AND DOCTYPE(ar) AND LANGUAGE(english) AND PUBSTAGE(final)
```

## Ejemplos que funcionaron (trabajo S7, Sistemas de Costeo)

- CVU y decisiones: `TITLE-ABS-KEY(("break-even analysis" OR "breakeven analysis" OR "cost-volume-profit" OR "CVP analysis") AND ("decision making" OR "pricing decision*" OR "profit planning"))` dio 327 registros sin filtros y 75 con filtros.
- Riesgo operativo: `TITLE-ABS-KEY(("margin of safety" OR "operating risk") AND ("break-even" OR "fixed cost*" OR "cost structure"))` dio 58 sin filtros y 16 con filtros.
- Elementos del costo: `TITLE-ABS-KEY(("direct material*" OR "direct labo*r" OR "manufacturing overhead" OR "indirect cost*") AND ("cost accounting" OR "product cost*" OR "costing"))`.

## Registro en la Matriz 1

Por cada ecuación se registra: identificador (B1, B2…), base de datos, ecuación completa, filtros, fecha de consulta, método (API oficial o navegador), resultados sin filtros, resultados con filtros y rol (principal, complementaria, asignada por la guía).
