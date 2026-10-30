# Criterios de selección y códigos de exclusión

## Inclusión (por defecto)
- Artículo científico revisado por pares (`DOCTYPE(ar)`), versión final.
- Publicado en los últimos 5 años en sentido estricto (en 2026: 2022–2026), salvo que la guía diga otra cosa.
- En inglés. Se acepta portugués o español como **excepción de idioma** si el artículo es pertinente; la decisión es de la investigadora y queda registrada.
- Aborda al menos una de las preguntas Q1…Qn del protocolo.

## Códigos de exclusión (usar siempre código y motivo)

| Código | Motivo | Se aplica a |
|---|---|---|
| E1 | Fuera del tema o de otro sector sin aporte conceptual (salud, agro, energía, ingeniería, transporte…) | título o resumen |
| E2 | Revisión de literatura o estudio bibliométrico | título o tipo de documento |
| E3 | Otro tema contable o financiero que no responde a las preguntas (bursátil, bancario, tributario…) | título o resumen |
| E4 | Herramienta tecnológica (IA, *blockchain*, *big data*) sin aporte al tema | título o resumen |
| E5 | Caso docente | **nombre de la revista** (Case Studies, Issues in Accounting Education, Journal of Accounting Education…) |
| E6 | Modelo de teoría de juegos, investigación de operaciones o decisión grupal sin relación con el tema | título |
| E7 | Contabilidad ambiental o de ciclo de vida sin relación con el tema | título |
| E8 | Tema no pertinente a las preguntas del trabajo (residual) | título o resumen |
| E-OA | Sin acceso abierto verificado, o abierto pero sin PDF recuperable (solo en **modo estricto de acceso abierto**) | texto completo |

Motivos típicos del cribado por resumen:
- sin acceso abierto (cuando hay alternativas abiertas);
- sector ajeno;
- ensayo sin método verificable;
- aporte marginal;
- reservado para otra parte del trabajo.

## Elegibilidad por texto completo (puntaje por pregunta)

| Puntaje | Significa |
|---|---|
| 0 | No aporta a la pregunta |
| 1 | Aporte parcial o indirecto: lo menciona, lo cita de otros o no lo desarrolla |
| 2 | Aporte directo y sustentado: definición explícita, hallazgo empírico o desarrollo propio con datos |

Decisiones posibles:
- **Incluido.**
- **Elegible – no seleccionado.** Lleva un motivo: redundante con otro de mayor puntaje, menor puntaje, otro sector, marco conceptual con datos simulados… Para el diagrama PRISMA se agrupa con `motivo_corto`.
- **No recuperado.** CAPTCHA, acceso restringido o DOI inexistente. Se anota en `literatura/por_descargar.json`.

Regla de selección: el conjunto de mayor puntaje que cubra **todas** las preguntas con al menos un 2, sin redundancias. Desempates, en orden:
1. contexto afín al trabajo;
2. evidencia empírica;
3. acceso abierto;
4. calidad de la revista y citas.

## Reutilización dentro de un mismo proyecto
- Los registros ya cribados en una búsqueda anterior se marcan como `Previo` y conservan su decisión. En PRISMA se cuentan como «duplicados o ya cribados».
- Un artículo ya incluido en otra parte puede entrar como «Incluido (reutilizado)» sin volver a descargarse, pero sí se vuelve a leer por las nuevas preguntas.
