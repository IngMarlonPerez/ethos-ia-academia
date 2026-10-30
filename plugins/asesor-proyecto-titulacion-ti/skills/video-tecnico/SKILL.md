---
name: video-tecnico
description: 'Video técnico de la tesis de TI (15 a 20 min): código limpio y comentado, recorridos CodeTour y guion por segmento (qué abrir, qué señalar, qué decir) en Word y PDF. Usar ante «el video técnico», «la guía o el guion para grabar».'
---

# Video técnico de la explicación práctica

Es la pieza en la que el tribunal mide el **dominio técnico**: arquitectura, backend, frontend, gateway, pruebas, decisiones tecnológicas y validación. Si se presenta con claridad, la sustentación final (5 diapositivas en 5 minutos y 5 minutos de demostración) casi no deja preguntas técnicas.

El tribunal revisa cientos de proyectos, así que el video debe ser claro, preciso y conciso: **de 15 a 20 minutos, 30 como máximo**.

**Tres documentos distintos.** La guía del video, los manuales y el documento de tesis no se mezclan:
- la guía se usa para exponer y trae sus propios pasos de preparación, incluida la actualización desde GitHub;
- los manuales son documentación del sistema;
- el documento de tesis es la entrega académica.

Antes de escribir el guion conviene que la autora estudie su sistema con el manual de la skill `manual-arquitectura-tribunal`: componentes, archivos con línea y recorrido de la demostración.

## 1. Respaldo
- Crear una etiqueta local `respaldo-antes-limpieza-<avance>` y una rama de trabajo.
- Nada se borra: lo que sobre se mueve fuera del repositorio, a `_no_utilizado/<fecha>/`, con un LEEME que diga por qué. Nada se publica sin aprobación.

## 2. Auditoría de calidad (primero solo lectura, después el informe)

| Control | Herramienta | Criterio |
|---|---|---|
| Rastros de IA y autores ajenos | `uso-etico-ia/scripts/rastros_ia.py` | Cero; la IA va solo en el anexo |
| Python: imports y variables sin uso, errores | `ruff check --isolated --select F,E9,B904,B007,B905` | Cero. `B008` (`Depends` de FastAPI) es el patrón del framework, no un defecto |
| Python: código muerto | `vulture --min-confidence 80` | Confirmar cada caso con `git grep`; al 60 % salen falsos positivos de endpoints y validadores |
| TypeScript: archivos, dependencias y exportaciones sin uso | `npx knip` | Revisar si la exportación se usa dentro de su propio archivo |
| Tipos y compilación | `tsc -b --noEmit`, `npm run build` | Cero errores |
| Residuos | `git grep` de `console.log`, `debugger`, `print(`, código comentado, `.bak` | Cero, salvo salidas legítimas de una CLI |
| Comentarios con historia | `git grep` de «Fase N», «antes…», «ahora», «ya no», «TODO» y etiquetas internas | Reescribir en presente, explicando el porqué |
| Archivos sin referencia | `git grep` del nombre del archivo, también **fuera** del repositorio (documento, generadores) | Lo que usa la tesis se documenta, no se borra |

Informe: `auditoria_calidad_<avance>.md`, una tabla con control, herramienta, hallazgo, acción y estado.

## 3. Comentarios de estilo documentación
- **Python:** docstring de módulo (responsabilidad y RF/RNF que implementa) y docstring de una línea en cada `__init__.py`, fusionado con el comentario `#` que ya hubiera.
- **TypeScript:** cabecera JSDoc en cada página, componente y servicio, con la ruta, el rol que la ve, los endpoints que consume a través del gateway y los RF.
- **Trazabilidad:** se conservan los RF, los RNF y las citas a autores.
- **Autoría:** la autora va en git, en `AUTHORS` y en la sección «Autora» del README. Sin firma por archivo y sin nombrar ninguna herramienta de IA.
- **Restricción:** solo se tocan comentarios. Las pruebas deben dar los mismos resultados antes y después.

## 4. Navegación para presentar
- **Espacio de trabajo:** `<proyecto>.code-workspace` (plantilla en `plantillas/proyecto.code-workspace`), con fuente grande, sin minimapa y sin carpetas de caché.
- **Extensiones recomendadas:** `.vscode/extensions.json` con `vsls-contrib.codetour`. En `.gitignore` va `.vscode/*` con la excepción `!.vscode/extensions.json`.
- **Recorridos guiados:** `.tours/`, uno por segmento del video (arquitectura, cada microservicio, AHP o el módulo clave, frontend y pruebas).
  - Se generan con `scripts/gen_codetour.py desde un JSON`.
  - Cada paso se ubica por **patrón**, no por número de línea, y sin `^` porque CodeTour puede no usar el modo multilínea.
  - El script comprueba que cada patrón exista y que su primera coincidencia sea la línea correcta.
- **README:** un «Mapa del repositorio» con una tabla de recorrido, qué muestra y dónde.
- **Demostración sin celular:** si el sistema tiene un flujo móvil (QR o enlace), un script que emita el enlace de demostración para abrirlo en el navegador con la vista de celular.

## 5. Verificación (antes de escribir la guía)
- **Pruebas unitarias y de integración** de todos los servicios, contra una pila aislada.
  - Generar el JUnit y la cobertura en una carpeta **por avance**, sin sobrescribir la evidencia del avance anterior.
  - Si un generador escribe un archivo fijo, agregarle `--salida`.
- **Recorrido en el navegador** de las pantallas que se van a mostrar. Si después de reconstruir aparece un 502 o un 404, reiniciar el gateway.
- **Comprobar lo que se va a decir:** por ejemplo, que la documentación interactiva de la API carga a través del gateway. Lo que falle no entra en el guion.
- **Fusionar en `main`** y crear la etiqueta del avance (`vX.Y-avanceN`).
- **Push solo con aprobación**, con la cuenta de la autora; después, la integración continua debe quedar en verde.

## 6. Guía del video (Word y PDF)

**Plantilla:** `plantillas/guia-video-tecnico-ejemplo.md`, un caso real con microservicios y AHP. Se convierte con `md_a_docx.py` y `docx_a_pdf.ps1`.

**Estructura:**

| # | Segmento | Min | Qué se muestra |
|---|---|---|---|
| 0 | Apertura | 1 | Problema con datos de campo, objetivo general y título |
| 1 | Arquitectura | 3 | Contenedores en Docker, diagrama, compose, gateway y sus rutas, base de datos con un rol por servicio, por qué ese estilo (matriz) |
| 2 | Backend | 4 | Estructura de cada servicio, seguridad (hash, JWT y roles) y **un flujo de punta a punta en vivo** |
| 3 | Módulo clave (AHP u otro) | 3 | Configuración con procedencia, cálculo, consistencia, verificación independiente y resultado en pantalla |
| 4 | Frontend | 3 | Rutas, cliente hacia el gateway, token y recorrido en vivo por rol |
| 5 | Pruebas y validación | 3 | Conteo, cobertura, integración continua, carga y validación con datos reales |
| 6 | Decisiones y tendencias | 1,5 | Puntaje de cada matriz y respuesta a las herramientas que sugirió la tutora |
| 7 | Cierre | 0,5 | Resultado por objetivo específico y enlace al repositorio |

**Contenido de cada segmento:** ventana, qué abro, qué muestro y **qué digo**. El texto para decir va en primera persona y en lenguaje natural, como cita (`> `), para que el conversor lo sangre.

**Anexos obligatorios:**
- **Antes de grabar.** Empieza por **actualizar el código desde GitHub**: `git status`, `git stash` si hace falta, `git fetch origin --tags`, `git checkout main`, `git pull origin main`, `git describe --tags`, `docker compose down` (nunca `-v`), `docker compose up --build -d` y reiniciar el gateway. Sigue con los contenedores, el usuario de prueba local, el espacio de trabajo y CodeTour, las pestañas del navegador, el ensayo del flujo en vivo y las notificaciones apagadas.
- **Si algo falla durante la grabación:** tabla de síntoma y acción, con un plan B de capturas o video.
- **Diez preguntas probables del tribunal**, con su respuesta breve y verificable.
- **Versión de 5 minutos** para la demostración de la sustentación.
- **Dónde está cada cifra:** cifra, valor y archivo del proyecto.

**Reglas:**
- **Toda cifra sale de un artefacto.** Si se atribuye una frase o una regla a una entrevista, se nombra al informante (E-P2), no a «los entrevistados», salvo que lo hayan dicho todos.
- **Si un valor es una agregación**, por ejemplo la mediana, se dice así; no «los expertos calificaron».
- **Honestidad técnica:** se dice dónde gana la alternativa descartada.
- **Sin marcadores:** el PDF sale sin ⟦…⟧, «COMPLETAR» ni «BORRADOR» (control `sin_pendientes`).

## 6b. Guion centrado en el código (versión para leer al grabar)

Si la guía se lee entrecortada o solo recorre pantallas, se reescribe como guion: por segmento, **qué abrir, qué archivo o función señalar y qué decir**, siguiendo el camino de los datos. El orden es literatura y decisiones, arranque, arquitectura, una operación de punta a punta, datos, seguridad, núcleo distintivo, frontend, pruebas y resultados, y cierre.
- **Prosa continua** con conectores, en primera persona. Cada componente lleva su porqué y dónde gana la alternativa descartada.
- **Siglas en español primero**, y entre paréntesis el inglés y la sigla.
- **Cifras solo del documento o de los artefactos.** No se inventan puntajes que el documento no tenga.
- Cada archivo y función citados se verifican con `grep` antes de entregar.
- El guion se escribe como JSON (`plantillas/guion-ejemplo.json`: `segmentos` con `titulo`, `quien`, `abrir`, `senalar` y `decir`, más `glosario`, `preguntas` y `antes_de_grabar`) y se convierte con `python scripts/gen_guion_docx.py guion.json salida.docx`. El script calcula los tiempos por palabras; la meta es de 15 a 20 minutos y, si se pasa, se recorta texto. El PDF se saca con Word por COM.
- Nunca se sobrescribe una versión anterior: `_v2`, `_v3`.
- El agente `guionista-video-tecnico` sirve para pulir la fluidez de una guía que ya existe.

## 7. Manuales y README (documentos aparte)
- **Manual de usuario:** pantalla por pantalla y por rol, más preguntas frecuentes.
- **Manual técnico:** arquitectura, requisitos, instalación, **descarga y actualización desde GitHub entre avances** (`git clone`, o `fetch`/`pull` y reconstrucción, y volver a una etiqueta), variables, desarrollo, pruebas, operación, seguridad y solución de problemas.
- **Comprobar cada comando** contra el Dockerfile y el compose. Por ejemplo, las pruebas no van dentro de las imágenes, así que no se corren con `compose exec`.
- **Ubicación:** los PDF se copian al repositorio (`docs/manuales/`) y se enlazan desde el README.

## 8. Paquete
- **Código:** `git archive` de `main` en un zip, sin `.env` reales ni datos de campo, más el enlace al repositorio.
- **Carpeta de entrega:** una por cada elemento que pida la consigna, con un LEEME. Lo que aporta la autora (video, cédula, fotos) se indica y no se inventa.

**Control:**
- auditoría con todo en «atendido» o «justificado»;
- pruebas en verde;
- los recorridos abren la línea correcta;
- ensayo cronometrado entre 15 y 20 minutos;
- guía y manuales sin marcadores;
- integración continua en verde después del push.
