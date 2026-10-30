# Ejemplo: prompt de NotebookLM para el video técnico del Avance 3

Proyecto: sistema web con microservicios para el control de costos y mantenimiento de una flota de carga pesada.

**Fuentes:** `Ramos_Daniela_Trabajo_Final.pdf` y `Guia_video_tecnico_v2.pdf`. Opcional: `Manual_prueba_QR.pdf`.

**Configuración:** español, «Análisis en profundidad», duración larga.

```
Crea un resumen de audio en español, en tono de dos ingenieros de software que preparan a una estudiante para defender su sistema ante un tribunal de titulación. El objetivo es que ella entienda a fondo la arquitectura y pueda explicarla con seguridad y con sus propias palabras en un video técnico de 10 a 15 minutos. Basa todo solo en las fuentes; no inventes cifras, autores ni tecnologías. Cada vez que aparezca una sigla, di primero su nombre completo.

Recorre los temas en este orden y explica siempre el porqué de cada decisión, no solo el qué:

1. El problema y el caso: la pequeña empresa de transporte de carga pesada, las cinco causas del problema y qué confirmaron las tres entrevistas.

2. Los trabajos previos: los al menos 10 estudios de la tabla de comparación crítica, agrupados por eje (costos, mantenimiento y AHP, sistemas web y móviles, arquitectura). Para cada uno: qué investigó, con qué método, qué resultado obtuvo y qué toma o deja este proyecto. Cierra con el vacío de investigación: qué no resolvía ninguno y dónde se ubica este trabajo.

3. La selección de la arquitectura: los tres estilos comparados (monolito en capas, monolito modular y microservicios), los criterios ponderados, el puntaje de cada uno y por qué ganaron los microservicios de grano grueso, incluso reconociendo en qué criterios gana el monolito.

4. Los componentes arquitectónicos, uno por uno, y cómo se comunican: el frontend en React con TypeScript; el gateway nginx como única puerta de entrada (enrutamiento, límite de intentos, HTTPS); los tres microservicios en Python con FastAPI (auth-service, fleet-core-service, reporting-service) y la responsabilidad de cada uno; PostgreSQL con un esquema y un rol por servicio; y Docker Compose para levantar todo. Explica el recorrido de una petición desde el navegador hasta la base de datos.

5. Las comparaciones tecnológicas: el framework del back end (FastAPI frente a Django REST framework y Express) y por qué se eligió FastAPI; también el gestor de base de datos, el front end y los contenedores, con sus puntajes. Menciona por qué no se usaron Spring Boot, NestJS, Kong, Traefik ni Superset.

6. Lo distintivo del sistema: el modelo de costos (costo total igual a costo variable más costo fijo, costo por vehículo y por kilómetro); la priorización del mantenimiento con AHP (comparación pareada, pesos, razón de consistencia menor que 0,10, juicios de los tres expertos, por qué se apartó a E1 y la robustez del ranking); y el despacho por código QR con su diseño de seguridad.

7. La evidencia: las pruebas automatizadas y la cobertura, la prueba de carga, la validación de costos con un mes real de la empresa y las limitaciones declaradas.

Al final, haz un repaso rápido con las 8 o 10 ideas clave que la estudiante debe decir sí o sí en el video, y plantea 5 preguntas probables del tribunal con una respuesta breve basada en el documento.
```

**Versión corta:**

```
En español, como dos ingenieros que preparan a una estudiante para su video técnico ante el tribunal. Solo con las fuentes, sin inventar nada, siglas con nombre completo. Orden: problema y entrevistas; los 10 trabajos previos por eje (método, resultado, relación) y el vacío; los 3 estilos de arquitectura comparados y por qué ganaron los microservicios; cada componente (React, gateway nginx, 3 servicios FastAPI, PostgreSQL por esquema, Docker Compose) y el recorrido de una petición; FastAPI frente a Django REST y Express, y las demás comparaciones; costos, AHP con expertos y QR; pruebas y validación con el mes real. Cierra con las ideas clave y 5 preguntas probables del tribunal.
```
