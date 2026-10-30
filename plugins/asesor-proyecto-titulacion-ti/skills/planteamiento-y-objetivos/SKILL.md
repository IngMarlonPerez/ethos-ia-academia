---
name: planteamiento-y-objetivos
description: 'Planteamiento de la tesis de TI (1.1 y 1.2) y Resumen: título, problema, justificación, objetivos con Bloom, alcance y matriz de consistencia. Usar al pedir problema, objetivos, justificación o resumen.'
---

# Planteamiento y objetivos (etapa 1)

Antes de escribir, lee la guía de la sección en el perfil (`secciones` → `1.1`, `1.2` y `resumen`). En la UNEMI los mínimos son 1.1 = 2 páginas y 1.2 = 1 página, y el Resumen tiene 150 palabras como máximo.

## 1. Título
Sigue `referencias/formula-titulo.md`. Propón de 3 a 5 opciones de 12 a 20 palabras con la estructura:

> verbo nominalizado + variable/objeto + método o tecnología + contexto

Ejemplo: «Desarrollo de un modelo predictivo de abandono estudiantil mediante inteligencia de negocios y procesamiento de lenguaje natural en una universidad pública».

La usuaria elige. El título se guarda en `titulacion.json` → `titulo`.

## 2. Descripción (1.1)
En este orden:
1. contexto;
2. necesidad;
3. causas y efectos del problema;
4. antecedentes con cifras;
5. justificación: ¿qué tan conveniente es?, ¿para qué sirve?, ¿ayudará a resolver un problema real?, ¿quiénes se benefician?

- Cada cifra del problema lleva una cita de una fuente con DOI verificada en el PDF. Si hace falta, busca con `asistente-investigacion-cientifica:revision-sistematica`. **Nunca prensa.**
- Redacta con `asistente-investigacion-cientifica:redaccion-apa7`.

## 3. Propósito del caso (1.2)
- **Objetivo general:** un solo verbo de Bloom de nivel alto (Desarrollar, Diseñar, Implementar, Evaluar), con **¿Qué?** (verbo en infinitivo + objeto), **¿Cómo?** (método o tecnología) y **¿Para qué?** (finalidad).
- **Objetivos específicos:** de 3 a 4, en progresión de Bloom: analizar o diagnosticar, luego desarrollar o implementar, luego evaluar o validar (`referencias/bloom-verbos.md`). Cada uno debe poder medirse después, porque tendrá una métrica en la etapa 3 y una conclusión en la etapa 9.
- **Alcance y limitaciones:** qué entra y qué no (datos, instituciones, módulos, despliegue) y por qué.
- **Criterios de éxito verificables**, uno por objetivo específico, por ejemplo «ROC-AUC ≥ 0,90 en validación temporal» o «exactitud ≥ 80 % en el conjunto dorado». Se trasladan a `requerimientos.json` → `metricas`.

Guarda los objetivos en `requerimientos/requerimientos.json` → `objetivos` (id, texto, bloom). De ahí los leen la trazabilidad, las matrices y el generador.

## 4. Matriz de consistencia
Llena `_automatizacion/datos_matrices.json` → `consistencia`: problema, objetivo, nivel de Bloom, unidad de análisis, diseño o metodología, y resultado o instrumento. La genera `matrices-titulacion`.

## 5. Resumen y Abstract
Se escriben **al final de cada avance**, con los resultados reales:
- un solo párrafo en pasado, de 150 palabras como máximo, con objetivo, metodología y resultados;
- cada cifra se lee del artefacto (`documento-titulacion`);
- palabras clave: 5 como máximo;
- el Abstract es su traducción fiel.

Registra las cifras del Resumen en `_automatizacion/coherencia.json` → `cifras` para que el verificador las compare.

## Lista de cumplimiento
Antes de cerrar, usa `referencias/checklist-avance1.md` (tabla «Requisito | ¿Dónde está? | Estado»).

**Control:**
- los objetivos tienen un verbo de Bloom y qué/cómo/para qué;
- cada objetivo específico tiene un criterio de éxito medible;
- cada cifra del problema tiene una cita con DOI;
- la matriz de consistencia está llena.
