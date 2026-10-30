# Modelo de datos: relacional normalizado o esquema estrella

| | Relacional normalizado (3FN) | Esquema estrella (dimensional) |
|---|---|---|
| Para qué | Operación diaria (OLTP): registrar, actualizar | Análisis y BI (OLAP): contar, agregar, comparar en el tiempo |
| Estructura | Entidades sin redundancia, con claves foráneas | Una tabla de hechos (grano definido) + dimensiones desnormalizadas |
| Ejemplo | cliente, pedido, detalle_pedido, producto | fact_matriculas (grano: alumno × periodo) + dim_alumno, dim_carrera, dim_tiempo… |
| En la tesis | Sistemas web de gestión | Tesis de BI, dashboards, modelos predictivos sobre historial |

## Buenas prácticas que se vuelven RNF
- **Declarar el grano** de cada tabla de hechos en una oración («una fila por alumno y periodo académico»).
- **Clave de negocio multiinstitución:** si el sistema atiende varias organizaciones, la clave única incluye la organización, p. ej. `(empresa_codigo, cedula)`, no la cédula sola.
- **Vistas de presentación** con el filtro de aislamiento (SESSION_CONTEXT, RLS de PostgreSQL) y un usuario de solo lectura que solo ve esas vistas.
- Las columnas personales se marcan en el diccionario, porque son las que enmascara `proteccion-datos`.

## Diccionario de datos (lo genera diccionario_datos.py)
Columnas: Columna | Tipo | Clave (PK, FK → tabla) | Nulo | Descripción de negocio. Ninguna columna queda sin descripción. Las vistas se listan aparte.
