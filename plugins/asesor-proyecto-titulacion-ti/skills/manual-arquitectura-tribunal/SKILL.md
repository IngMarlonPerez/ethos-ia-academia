---
name: manual-arquitectura-tribunal
description: 'Manual de arquitectura de la tesis de TI para el tribunal: componentes, archivos con línea, cifras reales y recorrido de la demo, en Word y PDF. Usar con «entender mi proyecto» o «manual de arquitectura».'
---

# Manual de arquitectura para la demostración técnica

Sirve para que la autora **entienda a fondo su propio sistema** antes del video técnico y de la sustentación: qué componentes tiene, dónde está cada archivo, qué hace cada parte importante del código y qué conviene mostrar al tribunal. Se aplica a **un proyecto a la vez**, con el protocolo de abajo, sin importar el stack.

El agente `cartografo-arquitectura` ejecuta esta skill de punta a punta. Invocarlo con la ruta del repositorio.

**No es** la guía del video (`video-tecnico`), ni los manuales del sistema, ni el documento de tesis. Es material de estudio y de apoyo para la demostración. No se pega en la tesis.

## Reglas
- **Nada se inventa.** Cada afirmación sale del repositorio con `archivo:línea`. Lo que no se encuentra se escribe «Por confirmar».
- **Las cifras se leen de los artefactos:** métricas JSON, reportes, salida real de las pruebas. Nunca se copian del documento ni de memoria.
- **Los números de línea se recalculan** con `grep -n` justo antes de generar el documento.
- **Las figuras salen de los diagramas del propio proyecto**, como `documentacion/diagramas/`. No se dibujan diagramas nuevos aquí.
- **Autoría:** van los autores en el JSON y en los metadatos de Office, sin nombrar ninguna herramienta de IA. Al final se pasa `uso-etico-ia/scripts/rastros_ia.py`, que debe dar 0.
- **Solo lectura sobre el código:** no se edita, no se hace commit y no se publica nada del proyecto.

## 1. Protocolo de entendimiento (solo lectura)

Cada paso deja notas con la evidencia. El orden importa: de lo general a lo particular.

| # | Paso | Cómo se verifica | Qué se anota |
|---|---|---|---|
| 1 | **Inventario** | Manifiestos: `package.json`, `requirements*.txt`, `pom.xml`, `*.csproj`, `docker-compose.yml`, `Dockerfile` | Stack y versiones, puntos de entrada (`main.py`, `app.module.ts`, `Program.cs`…), servicios del compose y puertos |
| 2 | **Arquitectura declarada** | ADR y matriz de decisión (`documentacion/decisiones/`), `ARQUITECTURA.md`, README | Estilo elegido y por qué. Si hay ADR, contrastarlo con el agente `auditor-arquitectura` y anotar las diferencias |
| 3 | **Capas y dependencias** | Árbol de carpetas (`git ls-files`), imports entre módulos | Tabla capa → tecnología → carpeta → responsabilidad, y las reglas de dependencia que se cumplen |
| 4 | **Presentación** | Router del frontend (rutas, guardas por rol), cliente HTTP | Ruta → pantalla → permiso, y cómo se envían el token y el contexto |
| 5 | **API o gateway** | `grep -rn` de los decoradores o anotaciones de ruta (`@router.get`, `@GetMapping`, `[HttpGet]`, `app.get(`) | Lista **contada** de endpoints por módulo y la autenticación y autorización con archivo:línea |
| 6 | **Datos** | Scripts SQL o migraciones, ORM, vistas, cuentas, seeds | Esquema (tablas, vistas, procedimientos), cuentas y privilegios, aislamiento entre clientes o instituciones |
| 7 | **Núcleo de dominio** | El módulo que resuelve el problema de la tesis: modelo de ML, cálculo de costos, AHP, reglas | Algoritmos o reglas con su función y línea. **Cifras desde los artefactos**: métricas, comparación de modelos, umbrales |
| 8 | **Seguridad y privacidad** | Hash de claves, JWT u OAuth, enmascarado, auditoría, LOPDP | Cada control con archivo:línea |
| 9 | **Procesos por lotes y ETL** | Orquestador, tareas programadas, scripts de carga | Pasos en orden y qué produce cada uno |
| 10 | **Despliegue** | `npm run dev` o el arranque que tenga, compose, puertos | Contenedores, imágenes, puertos y cómo se levanta |
| 11 | **Calidad** | Ejecutar las pruebas y contar el resultado real; CI | Número de pruebas que pasan (unitarias e integración) y los jobs de la CI |
| 12 | **Recorrido y preguntas** | Lo anterior | Unos 10 pasos de demostración (qué mostrar, archivo o pantalla, idea que demuestra) y de 5 a 8 preguntas probables del tribunal con su respuesta corta y su ubicación |

**Adaptar al stack.** Los pasos 4 a 9 cambian de nombre según el proyecto: microservicios con gateway, monolito MVC, Angular más Spring, etc. Lo que no cambia es la evidencia con archivo:línea.

## 2. Estructura del manual

1. La arquitectura en una frase, con la figura de arquitectura, las capas y las reglas.
2. Mapa de carpetas y archivos clave (árbol comentado).
3. Una sección por capa o componente (pasos 4 a 10), cada una con un recuadro **«Para la demostración»**: qué abrir y qué señalar.
4. Calidad y repositorio.
5. Recorrido sugerido para la demostración y preguntas probables del tribunal.

Lenguaje: español claro, explicando el porqué de cada decisión. Siglas desarrolladas la primera vez.

## 3. Generación

1. Escribir el contenido en un JSON con la forma de `plantillas/manual-ejemplo.json` (caso real de VicMar):
   - `raiz` (repositorio del proyecto), `salida`, `autores`, colores de la marca del proyecto y `portada`;
   - una lista de `bloques`: `h1`, `h2`, `h3`, `p`, `vineta`, `codigo`, `tabla`, `demo`, `imagen` y `salto`.
2. Generar el Word: `python scripts/gen_manual_arquitectura.py manual.json`.
3. Convertir a PDF con Word: `powershell -ExecutionPolicy Bypass -File scripts/docx_a_pdf.ps1 -Docx <salida.docx>`.
4. **Verificar el PDF:**
   - número de páginas y de figuras;
   - presencia de las cifras clave, buscándolas en el texto del PDF;
   - `rastros_ia.py` sobre el `.docx`, que debe dar 0;
   - revisar visualmente al menos la portada y una página con tabla.

**Salida:** `Guia_Arquitectura_<SIGLA>.docx` y `.pdf` en la carpeta del proyecto, fuera del repositorio si este se publica. Se usa un nombre corto, porque Word no abre rutas de más de 259 caracteres. Se guarda también el JSON, para regenerar el manual cuando cambie el código.

## Ejemplo real
VicMar (dos autores, octubre de 2026). Salió un manual de 13 páginas con 5 figuras que cubre:
- las 4 capas, el mapa de carpetas y los 26 servicios contados por grep;
- el aislamiento con SESSION_CONTEXT;
- los 4 modelos candidatos con la línea donde se elige el ganador y las cifras de `metricas.json`;
- la consulta conversacional en 5 pasos;
- el despliegue con `npm run dev`;
- un recorrido de 10 pasos y 7 preguntas del tribunal.
