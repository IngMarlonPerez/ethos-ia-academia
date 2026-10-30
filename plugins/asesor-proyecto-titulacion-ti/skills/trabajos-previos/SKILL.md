---
name: trabajos-previos
description: 'Base conceptual y estado del arte de la tesis de TI (1.3): 10 o más trabajos previos leídos, tabla comparativa y vacío. Usar al pedir trabajos previos, antecedentes, estado del arte o marco teórico.'
---

# Trabajos previos y base conceptual (etapa 2)

**Qué se busca:** que cada trabajo previo citado se haya **leído completo**, que su selección sea **defendible** y que la literatura informe decisiones reales del proyecto: técnicas, tecnologías y arquitectura.

## 1. Preguntas de lectura (Q1…Qn)
Derívalas de los objetivos específicos (`requerimientos.json` → `objetivos`) y escríbelas en `protocolo.md` y en `literatura/trabajos_previos.json` → `preguntas`. Siempre incluyen estas cuatro:
- **Q técnica:** ¿qué problema resolvió y con qué técnica o modelo?
- **Q tecnologías y arquitectura:** ¿qué lenguaje, framework y base de datos usó, y con qué arquitectura (monolito, capas, cliente-servidor, microservicios, eventos, serverless)?
- **Q validación:** ¿cómo validó los resultados y con qué métricas?
- **Q limitación:** ¿qué limitación declara o se le puede señalar?

La usuaria aprueba las preguntas antes de buscar.

## 2. Ecuaciones de búsqueda para TI
Sigue `referencias/ecuaciones-ti.md`:
- **Una búsqueda por pilar técnico del proyecto.** En la tesis VicMar hubo tres: predicción de abandono, BI/NL2SQL y clustering.
- **Siempre una búsqueda de arquitectura y tecnología del dominio.** Por ejemplo: «learning analytics» AND («architecture» OR «microservices» OR «framework»). Esta búsqueda alimenta las etapas 4 y 5.
- Cada ecuación combina bloques `OR` unidos con `AND`:
  - problema o dominio;
  - técnica o tecnología;
  - contexto.

## 3. Búsqueda, cribado y descarga
Todo esto lo hace el plugin de investigación: usa la skill `asistente-investigacion-cientifica:revision-sistematica`, etapas 1 a 4. Cubre:
- Scopus por la API oficial, o por el navegador con la sesión de la usuaria: **ella inicia sesión; tú nunca escribes credenciales**;
- el cribado con códigos de exclusión;
- los PDF de acceso abierto verificados (`%PDF`);
- el registro de los «No recuperado».

Criterios por defecto, salvo que el perfil o el tutor digan otra cosa:
- artículos en versión final;
- últimos 5 años;
- se prioriza el acceso abierto;
- sin revisiones ni congresos, salvo que el tutor los acepte.

## 4. Leer ANTES de seleccionar
- Lanza un agente `asistente-investigacion-cientifica:lector-critico` por PDF, **en paralelo**, pasándole la ruta del PDF, las preguntas y el tema.
- Revisa lo que devuelve cada agente y guarda la ficha en `literatura/B<n>_<tema>/fichas/<Autor>_<año>.md`.
- Separa la idea propia del autor de lo que el autor solo cita de otros.
- Selecciona el conjunto que cubra **todas** las preguntas con puntaje 2, sin redundancias. Debe llegar al mínimo del perfil (UNEMI: 10); lo habitual es de 12 a 15.

## 5. Tabla de trabajos previos
Llena `literatura/trabajos_previos.json`, un objeto por trabajo. La plantilla trae un `_ejemplo`: bórralo. Los campos obligatorios son:
- `texto_completo_leido: true`;
- `evidencia` con **página de la revista**;
- `arquitectura`;
- `tecnologias` (lenguaje, frameworks, base de datos). Si el artículo no los describe, escribe «no reporta»: eso también es un hallazgo.

Valida:
`python "${CLAUDE_PLUGIN_ROOT}/skills/trabajos-previos/scripts/tabla_trabajos_previos.py" literatura/trabajos_previos.json --perfil <perfil> --md literatura/trabajos_previos.md --conteos`

`--conteos` dice cuántos trabajos usan cada lenguaje, framework, base de datos y arquitectura. Esa es la evidencia de «Evidencia en trabajos previos» en `seleccion-tecnologica` y `decision-arquitectura`.

## 6. Redacción de 1.3
Redacta con `asistente-investigacion-cientifica:redaccion-apa7`, en este orden (`referencias/estructura-base-conceptual.md`):
1. **Supuestos epistemológicos:** postura (p. ej. pragmático-tecnológica) contrastada con la positivista y la interpretativa, **unidad de análisis** definida operativamente y trabajo práctico.
2. **De lo general a lo particular:** teoría general → teorías sustantivas → resultados empíricos precedentes.
3. **Propuestas tecnológicas respaldadas:** «Respaldado por X (año), quienes…» y «Esta elección se refuerza con…».
4. **Comparación crítica de trabajos previos** (subtítulo en negrita):
   - consenso de los trabajos;
   - «sin embargo, desde una posición crítica…», con crítica específica a trabajos concretos;
   - **vacío** («vacío de integración», «de validación», «de contexto»);
   - «A diferencia de estos enfoques, el presente trabajo…».

   **La tabla comparativa explícita frente al caso es obligatoria** en el documento (en la UNEMI, una tutora la exigió como corrección del Avance 1). Se genera con `tabla_trabajos_previos.py --tabla` y cierra con la fila «Presente trabajo» (clave `presente_trabajo` del JSON). Columnas: Autor (año), Problema y técnica, Tecnologías, Arquitectura, Validación y resultado, Limitación y **Qué aporta el presente caso**. Si no cabe en una página vertical, se parte en dos tablas con las mismas filas. Después de la tabla, un párrafo con lo que muestra (por ejemplo, cuántos dejan el modelo aislado) y también en qué es más débil el caso propio. Los artículos sin texto completo se marcan con un asterisco y una nota.
5. **Las preguntas de «Está relacionado»** del perfil, respondidas **en prosa**; la tabla de la plantilla se elimina.
6. **Aporte y trabajo futuro.**

**Cada afirmación teórica lleva una cita que el artículo realmente respalda**, con la página verificada si es cita textual. Nunca prensa (ver las reglas transversales).

## 7. Referencias y evidencias
- Referencias en APA 7 con DOI, en orden alfabético; se cuentan las de los últimos N años del perfil.
- Consolida el RIS del avance: `Avance<N>_<k>_referencias_completas.ris`.
- Los PDF leídos y no seleccionados van a `_leidos_no_seleccionados/`.

**Control:**
- `tabla_trabajos_previos.py` termina sin errores: al menos el mínimo de incluidos, todos leídos completos, con página, Arquitectura y Tecnologías;
- cada pregunta tiene al menos un trabajo con puntaje 2;
- el vacío está redactado;
- hay al menos 20 referencias de los últimos 5 años (lo comprueba `verificar-coherencia`).
