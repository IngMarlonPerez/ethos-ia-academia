---
name: diseno-uml-datos
description: 'Diseño de la tesis de TI: diagramas UML en Mermaid a PNG, modelo ER y diccionario de datos del esquema real. Usar al pedir UML, secuencia, casos de uso, despliegue, ER o diccionario de datos.'
---

# Diseño: UML y datos (etapa 7)

**Principio:** los diagramas y el diccionario se derivan del **sistema real**:
- una secuencia sigue las rutas, servicios y validaciones que existen en el código;
- el diccionario se lee del esquema de la base.

Así el documento no puede describir algo que el sistema no hace.

## 1. Qué diagramas
Los del perfil (`requisitos.uml_exigidos`; UNEMI: secuencia, colaboración, estados, actividades, flujo de trabajo y entidad-relación). También se recomiendan casos de uso, arquitectura (etapa 5) y despliegue.

Si hay varios flujos importantes, haz una secuencia para cada uno. En la tesis VicMar hubo dos:
- la consulta en lenguaje natural;
- la calificación por lotes.

## 2. Dibujarlos en Mermaid
- Copia la plantilla del tipo desde `${CLAUDE_PLUGIN_ROOT}/skills/diseno-uml-datos/plantillas/` a `diagramas/uml_<tipo>_<tema>.mmd`.
- El nombre `uml_<tipo>_…` le permite al script comprobar que no falte ninguno.
- Reemplaza el contenido con el flujo real: lee los archivos de rutas, servicios y modelos, y usa sus nombres reales.
- Lecciones aprendidas en `referencias/uml-mermaid.md`:
  - Mermaid no tiene casos de uso ni colaboración: se dibujan como flowchart, con actores `(( ))` y mensajes numerados;
  - las actividades con carriles van como subgrafos `direction TB` dentro de un `flowchart LR`;
  - un diagrama largo se parte en dos.

## 3. Renderizar y revisar
`python "${CLAUDE_PLUGIN_ROOT}/skills/diseno-uml-datos/scripts/renderizar_diagramas.py" diagramas/ --perfil <perfil>`

El script:
- usa Edge o Chrome ya instalados, con `puppeteer.json` escrito sin escapes rotos, y la escala `-s 2`;
- avisa si un PNG queda **muy alto o muy plano** para una página;
- falla si falta un tipo UML exigido.

Si mermaid-cli está en otra carpeta, pásalo con `--mmdc <ruta de mmdc.cmd>`. Si no está instalado, **pide autorización** antes de instalarlo en el proyecto:
`npm install --save-dev @mermaid-js/mermaid-cli`, con `PUPPETEER_SKIP_DOWNLOAD=1`.

Mira cada PNG con la herramienta Read antes de darlo por bueno.

## 4. Descripción de cada diagrama
Un párrafo por figura, que la plantilla exige («cada gráfica deberá ser detallada junto a su descripción»):
- qué muestra;
- el recorrido paso a paso, con los números del diagrama;
- qué decisión de diseño evidencia (p. ej. «el filtro por institución ocurre en el motor, paso 7»).

## 5. Modelo de datos y diccionario
- **Modelo:** entidad-relación normalizado (3FN) para sistemas transaccionales, o esquema estrella para BI y analítica (ver `referencias/modelo-datos.md`). Se dibuja en `uml_entidad_relacion_<tema>.mmd` y **debe coincidir** con el esquema real.
- **Diccionario desde el esquema real.** La cadena de conexión va en una variable de entorno; nunca en el comando ni en el repositorio.
  `python "${CLAUDE_PLUGIN_ROOT}/skills/diseno-uml-datos/scripts/diccionario_datos.py" --motor sqlserver --desc diagramas/descripciones.json --json documento/diccionario_datos.json --md documento/DICCIONARIO_DE_DATOS.md --vistas "VIS[_]%"`
  - Las descripciones de negocio van en `descripciones.json`, con claves `tablas` y `columnas`.
  - El script sale con código 1 mientras quede alguna columna «sin descripción».
  - En el Word, una tabla APA por tabla del modelo: `diccionario_datos.filas_word(d, tabla)` → `Insertor.tabla()`.
- **Redes, IA o seguridad sin base de datos:** en su lugar va la estructura o infraestructura (topología, capas del modelo, flujo de datos del pipeline), como dice la plantilla.

## 6. Recursos
Tabla «Tipo | Recurso | Especificación | Uso»:
- hardware: equipo de desarrollo y servidor;
- software, con las versiones reales fijadas en el repositorio;
- datos: fuente, licencia, anonimización;
- servicios externos: proveedores de IA y su plan.

**Control:**
- `renderizar_diagramas.py --perfil` termina sin errores ni diagramas ilegibles;
- cada diagrama tiene su descripción;
- `diccionario_datos.py` termina en 0;
- el modelo ER coincide con el esquema real.
