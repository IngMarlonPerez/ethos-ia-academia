# Ecuaciones de búsqueda para proyectos de TI (Scopus)

La sintaxis y los filtros son los del plugin de investigación (`asistente-investigacion-cientifica`, `referencias/ecuaciones-scopus.md`). Aquí va solo lo propio de TI.

## Tres bloques por pilar técnico
```
TITLE-ABS-KEY( <problema o dominio: 2-4 sinónimos en inglés> )
AND TITLE-ABS-KEY( <técnica o tecnología: 2-5 sinónimos> )
AND TITLE-ABS-KEY( <contexto: 2-3 sinónimos> )
AND DOCTYPE(ar) AND PUBSTAGE(final) AND PUBYEAR > <año-5> AND PUBYEAR < <año+1>
```
- Un pilar = un componente del sistema que la tesis debe justificar: modelo predictivo, segmentación, NL2SQL, dashboard, IoT, seguridad…
- Pon los sinónimos entre comillas: `"student dropout" OR "student attrition"`.
- Si una ecuación devuelve demasiado, agrega el bloque de contexto. Si devuelve muy poco, quita un sinónimo restrictivo del bloque técnico.

## Búsqueda obligatoria de arquitectura y tecnologías del dominio
Alimenta las etapas 4 (tecnologías) y 5 (arquitectura):
```
TITLE-ABS-KEY( <dominio> )
AND TITLE-ABS-KEY( "software architecture" OR "system architecture" OR microservice* OR "layered architecture"
                   OR "client-server" OR "event-driven" OR serverless OR framework )
AND TITLE-ABS-KEY( <tipo de sistema: "information system" OR platform OR "web application" OR dashboard> )
```

## Ejemplo real (tesis VicMar Data AI, UNEMI 2026)
| Búsqueda | Ecuación (resumida) | Identificación → incluidos |
|---|---|---|
| B1 Predicción de abandono | `("student dropout" OR "student attrition") AND ("machine learning" OR "random forest" OR "predictive model") AND ("higher education" OR university)` | 459 → 134 tras filtros |
| B2 BI y NL2SQL | `("business intelligence" OR "text-to-SQL" OR NL2SQL) AND (university OR "higher education")` | 79 |
| B3 Clustering institucional | `(clustering OR "k-means") AND (dropout OR "at-risk") AND (institution* OR program*)` | 28 |

Lección: en esa tesis **no hubo** una búsqueda de arquitectura. Por eso la comparación de estilos se tuvo que justificar después. El Asesor la exige desde el inicio.

## Del español al inglés
- abandono / deserción → dropout, attrition, withdrawal
- inteligencia de negocios → "business intelligence", dashboard, "data warehouse"
- lenguaje natural a SQL → "text-to-SQL", NL2SQL, "natural language interface" AND database
- sistema web → "web application", "information system", platform
- microservicios → microservice*, "service-oriented"
- educación superior → "higher education", university, college
