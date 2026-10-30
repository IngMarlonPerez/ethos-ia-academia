# Reglas de trabajo de la usuaria (aprendidas en sus proyectos de Economía)

Estas reglas salen de correcciones y aprobaciones reales en: Historia del Pensamiento Económico (S7 Grupo 11), Macroeconomía Básica (S6 Grupo 5), Microeconomía (S5 Slutsky, S7 elasticidades), Sistema de Costeo (S7 Grupo J), Metodología de la Investigación (S3, S5, S7). Aplicarlas por defecto; si la consigna dice otra cosa, manda la consigna y se avisa.

## Perfil
- Estudiante de Economía (perfil de ejemplo) (Milagro), periodo agosto–diciembre 2026. Escribe y espera respuestas **en español**. Se dedica a la investigación científica: quiere un método reutilizable (su «pipeline CI/CD de investigación»).
- Trabaja en **grupos de 5** con reparto de partes; con frecuencia le toca consolidar el archivo maestro. La carátula del grupo va con ella primero (con su ORCID debajo), luego los demás integrantes. Verificar siempre los nombres de la carátula contra el plan del grupo.
- Docentes exigentes con las citas. Citas textuales ≤ 40 palabras, entre comillas y con (Autor, año, p. X).

## Literatura
1. **Scopus** es la fuente de artículos: API oficial de Elsevier (clave guardada por ella; nunca se escribe ni se pide su contraseña); navegador con su sesión institucional solo como respaldo. Cadenas del plan del grupo: se corren **tal cual** primero, aunque den 0.
2. **Ventana temporal**: últimos 5 años estrictos (en 2026 → 2021–2026, `PUBYEAR > 2020`) cuando ella lo fija. Excepciones documentadas: datos oficiales (BCE, INEC, Banco Mundial), libros exigidos por el docente (p. ej. Blanchard) y, en historia del pensamiento, estudios fundacionales (se prefieren los recientes; se anota la excepción en la matriz).
3. **Idioma**: inglés preferente, no rígido. Si el artículo es pertinente y el texto completo está en español o portugués, se usa; se registra «excepción de idioma decidida por la investigadora» y la referencia lleva el título traducido entre corchetes cuando corresponde.
4. **Prioridad temática**: economía, contabilidad y empresas antes que salud o agro. Acceso abierto como desempate.
5. **Leer antes de juzgar**: la lista por título/resumen es «preselección, pertinencia no confirmada». Solo tras leer introducción, método, resultados y conclusiones se registra el veredicto con la página. Si no hay texto completo, la fuente no sostiene afirmaciones fuertes: se declara el nivel de lectura (PDF / resumen / solo título).
6. **Matriz de consistencia / PRISMA** antes de seleccionar: identificación → cribado por título → por resumen → elegibilidad con puntaje 0–2 por pregunta → inclusión, con decisión y motivo por registro.
7. **Solo fuentes académicas verificables** para cifras y antecedentes (Scopus/DOI). Nunca prensa ni sitios secundarios. Cada referencia se verifica por DOI (Scopus + OpenAlex/Crossref) antes de citarla; los compañeros a veces aportan referencias inexistentes.
8. **CAPTCHA** (ScienceDirect, Cloudflare): no se resuelve ni se insiste; el artículo se registra como «No recuperado».
9. Los PDF van a una carpeta de Drive; los metadatos a un **.ris** que ella importa en **Zotero** y con el que reemplaza las citas a mano una por una. El texto del documento lleva citas planas coherentes con el RIS.

## Documento
- **Nunca sobrescribir la plantilla ni la carátula**: copia `_respaldo_original.docx` antes de tocar, resultado en el nombre del archivo maestro (o `_FINAL`). Si ella indica un archivo como plantilla, ese es la fuente.
- Guardar el **hash md5** de la última versión generada; si el Word no coincide, ella lo editó a mano: integrar sus cambios antes de regenerar.
- Todas las fórmulas y cálculos en el **Editor de Ecuaciones de Word** (OMML nativo), no como texto plano.
- Tablas y figuras con rótulo APA (Tabla/Figura N en negrita, título en cursiva, «Nota. Elaboración propia…»), legibles, sin palabras partidas; **ningún texto superpuesto o cortado en gráficos**.
- Cuerpo mínimo/exacto según la consigna (portada, índice y referencias no cuentan). Verificar abriendo el Word real y exportando el PDF; mirar página por página.
- No recortar sin necesidad contenido que ella ya aprobó. Si la docente pide «dos hojas», medir en el PDF.
- Rutas largas: nombres cortos y exportar en una carpeta temporal corta (ver `trampas-windows-office.md`).

## Honestidad y verificación
- **No dar nada por terminado sin verificarlo**: releer el archivo guardado, recalcular con un método independiente, renderizar el docx/xlsx. Decir abiertamente lo que falló.
- Informe final siempre con: qué se leyó realmente (PDF vs resumen vs título), qué fuentes se descartaron y por qué, qué secciones o conclusiones son borrador de otro integrante, qué debe confirmar ella, y qué cifras son «estimación propia».
- Si falta una sección que la consigna exige (p. ej. VAB o previsión BCE; la parte de un integrante), redactarla **marcándola** y avisar para que el grupo confirme.
- Subir a Drive, enviar correos o publicar: solo si ella lo pide. Dejar marcadores «PEGAR AQUÍ» para el enlace.

## Uso de la inteligencia artificial
- La IA **no es autora**; la responsabilidad es de las personas. En trabajos grupales de Economía se incluye un **anexo de uso responsable de la IA** (tabla tarea / apoyo / control) y se pide a los integrantes confirmar que lo declarado es cierto. La política antiplagio del grupo prohíbe copiar y pegar IA sin revisión crítica: recordar que cada integrante revise y parafrasee su sección.
- Proyectos de titulación de **TI** se rigen por el otro plugin (`asesor-proyecto-titulacion-ti`); este plugin es solo para trabajos de Economía.
