# De los RNF a los criterios de decisión (ISO/IEC 25010)

Cada criterio de una matriz de decisión sale de un **RNF**, de un **objetivo** o de una **restricción** del proyecto, y se escribe en `origen`. Así la decisión se puede trazar hasta el análisis del caso.

| Característica ISO/IEC 25010 | Criterio de decisión derivado | Cómo se puntúa (1–5) |
|---|---|---|
| Adecuación funcional | Ecosistema para el problema | 5 si hay bibliotecas maduras y mantenidas que cubren el requerimiento sin desarrollo propio |
| Eficiencia de desempeño | Rendimiento para la carga esperada | Con benchmark oficial o medición propia reproducible; no con opiniones |
| Compatibilidad | Integración con la infraestructura existente | 5 si hay conector oficial al motor o servicio institucional |
| Usabilidad / capacidad de interacción | Calidad de la interfaz que permite construir | Solo para decisiones de frontend |
| Fiabilidad | Madurez y estabilidad | Años en producción, versión LTS, ritmo de publicación de correcciones |
| Seguridad | Soporte de seguridad | Consultas parametrizadas, gestión de secretos, avisos de seguridad atendidos |
| Mantenibilidad | Mantenibilidad y dominio del equipo | Tipado, pruebas, curva de aprendizaje real del equipo |
| Portabilidad / flexibilidad | Despliegue y portabilidad | Contenedores, multiplataforma |

## Restricciones típicas de una tesis
- **Equipo** de 1 a 3 personas, **plazo** de 4 a 8 meses: pesa más el dominio del equipo que la escalabilidad extrema.
- **Costo cero** o licencias académicas.
- **Datos personales**: la opción debe permitir cumplir la ley de protección de datos (etapa 3).
- **Infraestructura institucional**: si la universidad usa SQL Server, conectarse a él es un criterio fuerte.

## Pesos
- Suman 100; ningún criterio pasa de 35 ni baja de 5.
- Cada peso se justifica en una oración.
- Si dos criterios miden lo mismo (p. ej. «popularidad» y «comunidad»), fusiónalos.
