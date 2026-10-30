# Fuentes válidas para puntuar tecnologías y arquitecturas

| Nivel | Fuente | Sirve para | Cómo se cita en la celda |
|---|---|---|---|
| 1 | Trabajos previos de la tabla (leídos completos) | «Evidencia en la literatura», uso en el dominio | «8 de 12 trabajos previos (tabla_trabajos_previos.py --conteos)» |
| 1 | Artículo con DOI (Scopus) que compara o evalúa la tecnología o el estilo | rendimiento, mantenibilidad, adopción | «Autor et al. (año), p. N» |
| 2 | Documentación oficial o repositorio oficial | versión LTS, licencia, fin de soporte, capacidades | «docs.python.org/3.14, consultado 2026-09-29» |
| 2 | Medición propia reproducible en el repositorio | rendimiento en la carga real del proyecto | «scripts/bench_api.py → p95 = 120 ms» |
| 3 | Malla curricular o experiencia documentada del equipo | dominio del equipo | «Asignatura Programación Web (malla 2022)» |

**No válidas** (el script las rechaza en la columna de fuente):
- blogs, Medium y dev.to;
- tutoriales, GeeksforGeeks y W3Schools;
- foros como Stack Overflow y Reddit;
- YouTube, Wikipedia y prensa;
- rankings de popularidad sin metodología publicada.

Una encuesta de desarrolladores (Stack Overflow Developer Survey, JetBrains) solo cuenta como dato de adopción, citada como informe con su año y su metodología, y nunca como prueba de calidad técnica.

En el documento de tesis, las fuentes de nivel 2 se citan en APA 7 como software o como página web con la fecha de consulta. Las de nivel 1 son las únicas que sostienen afirmaciones comparativas («X es más mantenible que Y»).
