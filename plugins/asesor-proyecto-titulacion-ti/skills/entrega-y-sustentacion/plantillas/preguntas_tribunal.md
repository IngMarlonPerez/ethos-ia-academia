# Banco de preguntas del tribunal (proyecto de titulación de TI)

Punto de partida del agente `revisor-tribunal`. Para cada pregunta, prepara una respuesta de 3 a 5 líneas **con datos del propio proyecto** (cifra, tabla o archivo). Tacha las que no apliquen y añade las que motive tu documento.
Adaptado del banco de «proyectos-academicos» (V. M. Lluilema Pisco) y ampliado para proyectos de software.

## Problema y alcance
- ¿Quién es la persona que toma la decisión con este sistema y qué decide hoy sin él?
- ¿Por qué este problema y no otro? ¿Qué cifra lo sostiene y de qué fuente?
- ¿Qué incluye y qué NO incluye el prototipo? ¿Qué quedó fuera por tiempo?

## Trabajos previos y vacío
- ¿Qué hace su solución que los trabajos previos no hacen? Muéstrelo en la tabla comparativa.
- ¿Por qué esos 10 trabajos y no otros? ¿Cómo los buscó y los seleccionó?
- ¿Alguno de ellos contradice su enfoque? ¿Cómo lo explica?

## Requerimientos
- ¿Cómo comprobó que los requerimientos son los que necesita el usuario y no los que usted supuso?
- ¿Cuántos requerimientos funcionales tienen prueba? ¿Cuál no se alcanzó?
- ¿Cómo midió la usabilidad (SUS u otro) y con cuántas personas?

## Tecnologías y arquitectura
- ¿Qué otras opciones evaluó para el lenguaje, el framework y la base de datos? ¿Con qué criterios y pesos?
- Si cambiaran los pesos, ¿ganaría la misma opción? (análisis de sensibilidad)
- ¿Por qué esa arquitectura y no microservicios, o un monolito? ¿Cómo comprobó que el código la respeta?
- ¿Qué pasaría con 10 veces más usuarios? ¿Qué componente falla primero?

## Datos, modelo y validación
- ¿De dónde salen los datos y quién autorizó su uso? ¿Qué hizo con los datos personales?
- ¿Cómo evitó la fuga de datos entre entrenamiento y prueba? ¿Validó por grupos o por tiempo?
- ¿Qué línea base comparó? ¿Cuánto mejora su modelo y es esa mejora significativa?
- ¿Qué meta no alcanzó y qué explica la diferencia?
- (Si usa IA generativa) ¿Cómo evalúa las respuestas incorrectas o las preguntas adversariales? ¿Qué conjunto de prueba usó?

## Seguridad y ética
- ¿Qué ocurre si un usuario intenta ver datos de otra organización o rol? Muéstrelo.
- ¿Dónde guarda las credenciales y las claves? ¿Hay alguna en el repositorio?
- ¿Cómo declara el uso de herramientas de IA en el proyecto y quién responde por lo que dice el documento?
- ¿Qué sesgos puede tener el modelo y cómo los revisó?

## Resultados y conclusiones
- ¿Cuál es el hallazgo más importante y con qué cifra lo sostiene?
- ¿Cómo responde cada conclusión a su objetivo específico?
- ¿Qué limitaciones tiene el estudio? ¿Qué recomienda hacer después?

## Aplicabilidad
- ¿Quién usaría esto mañana y qué le falta para producción?
- ¿Cuánto costaría mantenerlo y quién lo mantendría?
- ¿Se puede reproducir su resultado desde cero? Muéstrelo con el pipeline.
