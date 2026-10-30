# Registro de cambios

## 1.11.0 – 30 de octubre de 2026
- **Skill nueva `manual-arquitectura-tribunal`:** protocolo de entendimiento en 12 pasos (inventario, arquitectura declarada, capas, presentación, API, datos, núcleo de dominio, seguridad, lotes, despliegue, calidad y recorrido). Cada afirmación lleva archivo y línea, y las cifras se leen de los artefactos. Genera un manual para estudiar el sistema y preparar la demostración ante el tribunal, con recuadros «Para la demostración» y preguntas probables. `gen_manual_arquitectura.py` arma el Word desde un JSON y `docx_a_pdf.ps1` lo convierte con Word. El ejemplo real es VicMar: 13 páginas y 5 figuras.
- **Agente nuevo `cartografo-arquitectura`:** aplica la skill a un proyecto de punta a punta y devuelve el manual verificado sin tocar el código.

## 1.10.0 – 29 de octubre de 2026
- **Menos tokens por sesión:** las descripciones de las skills y los agentes se acortaron a unos 200 caracteres, conservando las frases que las activan. Así se cargan completas en cada sesión y no se recortan por falta de espacio. La skill `guion-video-tecnico` se fusionó en `video-tecnico` (sección 6b, con `gen_guion_docx.py` y `guion-ejemplo.json`), porque las dos se activaban con las mismas frases.

## 1.9.0 – 29 de octubre de 2026
- **Skill nueva `arranque-un-comando`:** el sistema arranca con `npm run dev` (`package.json` sin dependencias y `scripts/dev.mjs` con solo Node nativo). Abre Docker Desktop, construye y levanta los contenedores, espera a que estén sanos, carga los datos de prueba si la base está vacía, muestra el usuario y abre el navegador. Incluye `npm test`, `npm run codigo` y tareas de VS Code. Cubre también README y manuales, verificación en un proyecto aislado, commit con la autoría de la autora, push y zip limpio con `git archive` para Drive. Plantillas probadas en FlotaControl.
- **Agente nuevo `preparador-entrega-codigo`:** aplica esa skill de punta a punta y devuelve la evidencia de cada verificación.

## 1.8.0 – 29 de octubre de 2026
- **Skill nueva `guion-video-tecnico`:** convierte el guion de un avance en el guion del video técnico (15 a 20 min), centrado en el código abierto en VS Code: por segmento, qué archivo abrir, qué función señalar y qué decir, en prosa técnica con conectores y el porqué de cada decisión. Incluye `gen_guion_docx.py`, que arma el Word desde un JSON y calcula los tiempos por palabras, y el ejemplo real del sistema de pronóstico de demanda (13 segmentos). No inventa puntajes de comparación que el documento no tenga.

## 1.7.0 – 29 de octubre de 2026
- **Skill nueva `resumen-audio-notebooklm`:** escribe el prompt del «Resumen de audio» de NotebookLM para estudiar la tesis antes del video técnico. El audio recorre arquitectura y componentes, los 10 o más trabajos previos por eje, las tecnologías comparadas, lo distintivo del sistema, la evidencia, las ideas clave y las preguntas del tribunal. Incluye versión corta, fuentes y configuración, y el ejemplo real del Avance 3.

## 1.6.0 – 28 de octubre de 2026
- **Agente nuevo `guionista-video-tecnico`:** escribe la guía del video técnico (10 a 15 min) como guion en primera persona y prosa técnica continua, con conectores («ahora abro…», «a continuación levanto…»), siglas desarrolladas la primera vez y glosario al final. Verifica cada ruta, comando y cifra en el repositorio. El video es la carta de graduación ante el tribunal.
- **Agente nuevo `verificador-cumplimiento`:** contrasta el avance o trabajo final con todas las consignas y rúbricas de cada tutora, criterio por criterio y con página. Corre los controles de marcadores, citas↔referencias, rastros de IA y metadatos, y separa lo que queda «A cargo de la autora».
- **Agente nuevo `redactor-continuacion-avance`:** redacta una sección nueva que continúa lo aprobado (desarrollo, resultados, conclusiones finales) sin tocar las secciones aprobadas, con cifras leídas de los artefactos.
- **Regla del avance final:** lo aprobado en los avances anteriores no se reescribe sin autorización de la tutora. Se completan los datos que faltan y se agregan las secciones nuevas.

## 1.5.0 – 25 de octubre de 2026
- **Skill nueva `video-tecnico`:** prepara el video de la explicación práctica ante el tribunal (15 a 20 min). Cubre ocho pasos:
  - respaldo;
  - auditoría de calidad (rastros de IA, ruff, vulture, knip, tsc, residuos, comentarios con historia y archivos sin referencia), con informe;
  - comentarios de estilo documentación, con la autoría en git y en `AUTHORS`;
  - navegación para presentar: espacio de trabajo y CodeTour;
  - verificación con evidencia por avance, sin sobrescribir la del avance anterior;
  - guía en primera persona con anexos: preparación (que empieza por actualizar desde GitHub), plan B, preguntas del tribunal, versión de 5 minutos y origen de cada cifra;
  - manuales como documentos aparte;
  - paquete.
- **`scripts/gen_codetour.py`:** genera `.tours/` desde un JSON. Ubica cada paso por patrón y valida que el patrón sin «^» siga apuntando a la misma línea.
- **Plantillas:** guía real de ejemplo (`guia-video-tecnico-ejemplo.md`), recorridos de ejemplo (`recorridos-ejemplo.json`) y espacio de trabajo de VS Code.

## 1.4.1 – 24 de octubre de 2026
- **`verificar-coherencia`:** nuevo control `sin_pendientes`, activo por defecto. Falla si el documento conserva marcadores de dato pendiente (⟦…⟧, «COMPLETAR», «BORRADOR», «[pendiente…]») o texto de relleno de la plantilla («XXXX», «……»). Revisa párrafos, tablas, encabezados y pies. Nace de un caso real: un Avance 2 se entregó con 25 marcadores y la declaración de autoría sin llenar.
- **Perfil `unemi.json`:** el avance 3 (trabajo final) incluye:
  - `entregables_carpeta`: documento, presentación por estudiante, video de unos 15 min, trabajo práctico, declaración de autoría, anexos de IA y de interacción con las docentes, cédula y fotografía;
  - `primera_pagina`: integrantes y enlace del Drive;
  - `sin_marcadores_pendientes`.

## 1.4.0 – 24 de octubre de 2026
- **Skill nueva `respaldo-fuentes-oficiales`:** respalda cada cifra (tesis, entrevista, programa, presentación) con la fuente original y no con notas de prensa.
  - Jerarquía de fuentes, procedimiento por cifra (documento descargado, página, valor literal, recálculo, nivel de confianza) y trampas frecuentes (proforma, codificado y devengado; registros y personas únicas; tipos de deserción).
  - `referencias/portales-oficiales-ecuador.md`: 12 portales verificados en el navegador, con los cambios de 2025-2026 (Senescyt integrada al MINEDEC; finanzas.gob.ec redirige al MDEP).

## 1.3.0 – 11 de octubre de 2026
- **Skill nueva `presentacion-avance`:** presentación de cada avance sobre la presentación entregada en el avance anterior, con el mismo diseño.
  - Conserva la portada, con el título vigente y el número de avance, el fondo con el logo y el cierre; quita las diapositivas propias del avance anterior; nunca modifica el archivo anterior.
  - `presentacion_avance.py` arma el contenido desde un JSON con 10 tipos de diapositiva: agenda, lista con panel, objetivos, tarjetas con cifras, tabla con barras, fases, imagen lateral, galería, cifras con imagen y conclusiones.
  - Las notas de cada diapositiva son el guion del orador, en primera persona y para leer en voz alta; también se exporta a Word y a Markdown con la duración estimada (140 palabras por minuto). `--solo-guion` regenera solo el guion.
  - Ejemplo en `plantillas/presentacion-avance-ejemplo.json`; pruebas en `tests/test_presentacion_avance.py`.

## 1.2.1 – 10 de octubre de 2026
- **Menos tokens por sesión (informe de `/skill-doctor` y `claude plugin details`):** las descripciones de las 20 skills y los 4 agentes bajan un 60 % (de ~24.000 a ~9.400 caracteres, sumando los dos plugins), con los mismos disparadores. El costo siempre activo del Asesor pasa de ~5.200 a ~2.200 tokens. El informe mostraba varias skills (planteamiento-y-objetivos, proteccion-datos, publicacion-github, seleccion-tecnologica, trabajos-previos, verificar-coherencia) con menos de 20 tokens de listado, es decir, sin su descripción; con descripciones cortas deberían volver a listarse completas (a confirmar en el próximo informe).

## 1.2.0 – 10 de octubre de 2026
Se integró lo mejor del plugin «proyectos-academicos» de Victor Manuel Lluilema Pisco (créditos en los archivos adaptados), reescrito para proyectos de TI y adaptado a Windows con Office.
- **`documento-titulacion` protege el Word de la usuaria:**
  - `copia_trabajo.py`: copia versionada `_v02` desde los bytes del original, con su huella; nunca sobrescribe;
  - `huella.py`: huella de portada, fondo, encabezados, pies (XML e imágenes), secciones y estilos; `verificar`, `plantilla` y `restaurar` (recupera encabezados y pies perdidos desde la plantilla oficial);
  - `diff_versiones.py`: qué cambió la usuaria entre dos versiones y verificación «solo inserciones»;
  - `aserciones.py`: registra las correcciones y avisa si un guardado desde un Word viejo las revirtió;
  - el generador archiva cada salida anterior en `documento/versiones/` y, al terminar, comprueba que la zona protegida siga igual que en el origen;
  - `copiar_biblioteca.py` incluye `versionado_docx.py`.
- **`entrega-y-sustentacion`:**
  - `diapositivas.py`: presentación completa desde JSON, con letra adaptativa y 12 tipos de diapositiva;
  - `poster.py`: póster académico A0 de tres columnas (PPTX editable + PDF de imprenta + vista previa);
  - `iconos.py` y banco de 85 íconos propios (licencia ISC de Lucide en `assets/iconos/`);
  - `qa_pptx.py`: control de calidad del PPTX (texto que no cabe, marcadores de plantilla, fuentes, miniaturas);
  - ejemplos de TI en `plantillas/` y banco de preguntas del tribunal (`preguntas_tribunal.md`).
- **Agente nuevo `revisor-tribunal`:** revisión independiente con ojos de tribunal; contrasta el documento con el repositorio y devuelve hallazgos, fortalezas y las preguntas probables con su respuesta sugerida.
- **`asistente-titulacion-ti`:** `referencias/lecciones-aprendidas.md` (incidentes reales y la regla que evita cada uno) y regla transversal 5 ampliada.
- **Adaptación a Windows:** la exportación a PDF usa PowerPoint o LibreOffice y PyMuPDF (no exige poppler); el texto se mide con las fuentes Arial y Calibri de Windows.
- **Menos tokens por sesión (informe de `/skill-doctor` y `claude plugin details`):** las descripciones de las 20 skills y los 4 agentes bajan un 60 % (de ~24.000 a ~9.400 caracteres), con los mismos disparadores. El costo siempre activo pasa de ~5.200 a ~2.200 tokens. El informe de `/skill-doctor` mostraba varias skills (planteamiento-y-objetivos, proteccion-datos, publicacion-github, seleccion-tecnologica, trabajos-previos, verificar-coherencia) con menos de 20 tokens de listado, es decir, sin su descripción; con descripciones cortas deberían volver a listarse completas (a confirmar en el próximo informe).
- Pruebas nuevas: `tests/test_versionado_y_presentaciones.py`.

## 1.1.0 – 3 de octubre de 2026
Lo aprendido al auditar, reorganizar y publicar la tesis VicMar Data AI.
- **Skills nuevas:**
  - `organizacion-repositorio`: respaldo, inventario (`inventario.py`), código sin uso a revisión sin borrar (`mover_a_revision.py`), estructura por capas con ADR-000 respaldado por artículos y repositorios de referencia, y cómo recuperar archivos de un stash.
  - `uso-etico-ia`: la IA no es autora; escáner de rastros y de autoría de Office con corrección (`rastros_ia.py`) y anexo de uso ético en una carpeta local (`anexo_uso_ia.py`).
  - `publicacion-github`: controles previos (`preparar_publicacion.py`), bundle de respaldo, commit único con los autores reales y sin coautoría de asistentes, y push confirmado.
- `trabajos-previos`:
  - la tabla comparativa explícita frente al caso es obligatoria y cierra con la fila «Presente trabajo»;
  - nueva columna «Qué aporta el presente caso».
- `verificar-coherencia`: falla si «Referencias» o «Anexos» llevan número.
- `documento-titulacion`:
  - el generador es autocontenido (`copiar_biblioteca.py` copia la biblioteca a `_automatizacion/lib/`, sin rutas de la herramienta);
  - fija como autores del Word a los de `titulacion.json`.
- Reglas transversales 8 (la IA no es autora) y 9 (mover, no borrar; respaldar antes de reorganizar).

## 1.0.0 – 29 de septiembre de 2026
Primera versión, construida a partir de los Avances 1 y 2 de la tesis VicMar Data AI (UNEMI, 2026).
- Pipeline de 13 etapas con controles de calidad y tablero (`asistente-titulacion-ti`, `tablero.py`).
- Perfil institucional UNEMI y extracción de perfiles desde la plantilla de otra universidad.
- 17 skills: inicio, planteamiento y objetivos, trabajos previos, requerimientos, selección tecnológica, arquitectura, protección de datos, metodología, UML y datos, desarrollo y evidencias, conclusiones, documento, verificación de coherencia, matrices, retroalimentación del tutor y entrega.
- Matriz de decisión multicriterio con sensibilidad y ADR, para tecnologías y arquitectura (al menos 3 opciones).
- Detección de la arquitectura real del repositorio y verificación de reglas declaradas.
- Generación del Word desde la plantilla oficial (`docx_titulacion.py`), PDF con Word y verificador de coherencia configurable.
- Agentes `auditor-arquitectura`, `evaluador-tecnologia` y `revisor-tutor`.
- Reutiliza el Asistente de Investigación Científica para Scopus, PRISMA, lectura crítica y APA 7.
