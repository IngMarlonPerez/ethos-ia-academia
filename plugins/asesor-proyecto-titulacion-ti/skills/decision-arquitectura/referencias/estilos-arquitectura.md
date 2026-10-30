# Estilos de arquitectura para proyectos de titulación de TI

Resumen de trabajo para elegir los candidatos. **No reemplaza la evidencia**: cada afirmación que vaya al documento se sostiene con un artículo con DOI o con los trabajos previos del proyecto.

| Estilo | Cuándo conviene | Costos y riesgos | Señales en el código (detectar_arquitectura.py) |
|---|---|---|---|
| **Monolito (una aplicación)** | Alcance acotado, un equipo pequeño, interfaz renderizada en el servidor | Crece acoplado si no hay capas; un solo punto de despliegue | 1 desplegable con backend; sin SPA separada |
| **Monolito en capas / modular** | Casi todas las tesis: presentación → dominio → datos, con módulos por funcionalidad | Disciplina para no saltarse capas; escala verticalmente | Carpetas api/routes, core/services/domain, db/repositories/data |
| **Cliente-servidor desacoplado (SPA + API REST)** | Interfaz rica (paneles, gráficos) que consume la misma API que otros clientes (móvil, chat) | Dos desplegables; CORS, autenticación con tokens, versionar la API | Frontend (React/Angular/Vue) y backend (FastAPI/Spring/Express) en aplicaciones separadas |
| **Microservicios** | Varios equipos, dominios independientes, necesidad de escalar o desplegar partes por separado | Complejidad operativa alta (red, observabilidad, datos distribuidos, orquestación); suele sobrar en una tesis de 1 a 3 personas | ≥ 3 servicios de aplicación en docker-compose o k8s, cada uno con su base de datos |
| **Orientada a eventos** | Procesos asíncronos, IoT, integración entre sistemas, alto volumen de mensajes | Consistencia eventual, depuración difícil, broker que operar | Kafka, RabbitMQ, MQTT, Celery o colas |
| **Serverless (FaaS)** | Carga esporádica, costo por uso, funciones pequeñas | Arranque en frío, dependencia del proveedor, límites de ejecución | serverless.yml, funciones de Vercel o Netlify, AWS Lambda |
| **Hexagonal / limpia** | Dominio con reglas de negocio ricas que deben probarse aislado de la infraestructura | Más capas y abstracciones; sobrecosto si el dominio es simple | Carpetas domain/application/infrastructure/adapters/ports |

## Combinaciones frecuentes (válidas)
- **Cliente-servidor desacoplado + backend en capas**: fue la de la tesis VicMar Data AI, con React/Vite, FastAPI (api → core/ml → etl/datos) y SQL Server.
- **Monolito modular + un proceso por lotes**: por ejemplo, entrenamiento nocturno de modelos.
- **Capas + un componente orientado a eventos**: por ejemplo, telemetría IoT por MQTT.

Declara la combinación completa y verifica cada parte.

## Criterios (escenarios) que casi siempre aplican
- Modificabilidad: ¿cuánto cuesta agregar un módulo o una institución?
- Despliegue y operación: servidores, contenedores, costo mensual.
- Seguridad: superficie de ataque, dónde se valida, aislamiento de datos.
- Rendimiento para la carga real.
- Capacidad del equipo en el plazo.
- Evidencia en los trabajos previos del dominio.

## Frase honesta sobre microservicios
Si no se eligen, dilo con escenarios: «el escenario de modificabilidad se cumple con módulos dentro de un solo backend; los microservicios agregarían operación distribuida sin beneficio medible para una institución y un equipo de dos personas», con cita. No los descartes «porque son complejos» sin evidencia.
