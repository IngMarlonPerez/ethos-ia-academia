---
name: resumen-audio-notebooklm
description: 'Escribe el prompt del «Resumen de audio» de NotebookLM para estudiar la tesis de TI antes del video técnico o la sustentación. Usar al pedir «el prompt para NotebookLM» o «un podcast para estudiar mi tesis».'
---

# Prompt para el resumen de audio de NotebookLM

Sirve para que la autora **estudie escuchando** su propio trabajo antes de grabar el video técnico (skill `video-tecnico`) o de sustentar. NotebookLM genera el audio a partir de las fuentes que se suban; esta skill entrega el texto que se pega en **Resumen de audio → Personalizar** y la lista de fuentes.

## 1. Leer el proyecto antes de escribir (nunca de memoria)

Ubicar y leer, sin modificar nada:
- el **documento final** del avance (PDF o borradores), que será la fuente principal;
- la **guía del video técnico**, si existe, para que el audio siga el mismo orden de segmentos;
- la tabla de **comparación crítica de trabajos previos** (cuántos son y sus ejes);
- las **decisiones tecnológicas** (DT-xx o ADR): qué se comparó con qué y qué ganó;
- los componentes reales del sistema (servicios, gateway, base de datos, front end, contenedores);
- lo distintivo del sistema (por ejemplo, modelo de costos, AHP, QR) y la evidencia (pruebas, cobertura, carga, validación con datos reales, limitaciones).

En el prompt solo se nombra lo que aparece en esos archivos. Si algo no está, no se menciona; si un número no es seguro, se pide a NotebookLM que lo tome «de la fuente» en vez de escribirlo.

## 2. Estructura del prompt (en español)

1. **Rol y tono:** dos ingenieros de software que preparan a la estudiante para defender su sistema ante el tribunal; explican el porqué de cada decisión, no solo el qué.
2. **Reglas:** basarse solo en las fuentes, sin inventar cifras, autores ni tecnologías; desarrollar cada sigla la primera vez.
3. **Recorrido**, en el orden del video:
   - problema y caso (causas, entrevistas o diagnóstico);
   - trabajos previos por eje: qué investigó cada uno, con qué método, qué resultado y qué toma o deja el proyecto; cierre con el vacío de investigación;
   - selección de la arquitectura: estilos comparados, criterios ponderados, puntajes y en qué criterio gana la alternativa descartada;
   - componentes uno por uno y el recorrido de una petición desde el navegador hasta la base de datos;
   - comparaciones tecnológicas (lenguaje y framework, base de datos, front end, empaquetado) y por qué no se usaron las herramientas sugeridas por la tutora que se descartaron, si las hay;
   - lo distintivo del sistema;
   - evidencia y limitaciones.
4. **Cierre:** las 8 a 10 ideas clave que deben decirse en el video y 5 preguntas probables del tribunal con respuesta breve basada en el documento.

Entregar además una **versión corta** (un párrafo) por si NotebookLM rechaza el texto largo.

## 3. Indicaciones de uso que acompañan al prompt

- **Fuentes que hay que subir**, con su ruta: el documento final en PDF, la guía del video y, si sirven, los manuales.
- **Configuración:** idioma español, formato «Análisis en profundidad» y duración larga.
- **Forma de estudio:** escucharlo dos veces, la segunda con la guía del video abierta, siguiendo cada segmento.

## 4. Reglas

- La IA no es autora. El prompt es material de estudio personal y no va al documento, al repositorio ni a la entrega. Si se registra, va solo en el anexo de uso de IA (`uso-etico-ia`).
- No subir a NotebookLM consentimientos, cédulas, RUC, firmas ni datos de campo sin anonimizar (`proteccion-datos`). Solo se sube el documento ya anonimizado.
- El audio no reemplaza la lectura del documento. Toda cifra que se vaya a decir en el video se confirma en el documento o en los artefactos.

## 5. Entrega

Presentar el prompt en un bloque de texto listo para copiar, seguido de la versión corta y las indicaciones de uso. Si la usuaria lo pide, guardarlo también en `Avance N/Video_tecnico/Prompt_NotebookLM.md`.

## Ejemplo real

`templates/prompt-notebooklm-ejemplo.md` contiene el prompt del sistema de control de flota (microservicios con FastAPI, AHP y costos), que sirve de modelo de nivel y de orden.
