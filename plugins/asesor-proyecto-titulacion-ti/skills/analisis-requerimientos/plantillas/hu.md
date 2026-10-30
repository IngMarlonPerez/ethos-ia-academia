# Plantilla de historias de usuario

| ID | Historia de usuario | Criterio de aceptación (Dado / Cuando / Entonces) | Pieza | Obj. | Prioridad |
|---|---|---|---|---|---|
| HU-01 | Como **<actor>**, quiero **<capacidad>** para **<beneficio>**. | *Dado* <contexto inicial>, *cuando* <acción del usuario>, *entonces* <resultado observable y medible>. | <pieza> | OE2 | Alta |

## Reglas
- Una historia = una necesidad del actor, **no** una tarea técnica («crear la tabla X» no es una historia).
- El beneficio («para…») debe ser del actor, no del sistema.
- El criterio de aceptación se verifica sin ambigüedad: cifras, estados o mensajes concretos.
- La persona principal (sin perfil técnico) protagoniza al menos la mitad de las historias.
- Numeración estable (HU-01…). Los RF, las pruebas y el protocolo de usuarios la citan.

## Ejemplo (tesis VicMar Data AI)
| HU-03 | Como autoridad académica, quiero preguntar en español «¿cuántos estudiantes de Enfermería están en riesgo alto?» para decidir sin depender del área de TI. | *Dado* que inicié sesión con el rol académico, *cuando* escribo la pregunta en el chat, *entonces* veo el número correcto y una explicación sin datos personales, en menos de 30 s. | NL2SQL | OE2 | Alta |
