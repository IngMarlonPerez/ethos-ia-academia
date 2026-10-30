---
title: "Guía del video técnico: FlotaControl"
subtitle: "Daniela Sofía Ramos Paredes · Ingeniería en Tecnologías de la Información · UNEMI · 2026"
---

# Cómo usar esta guía

Esta guía acompaña la grabación del video de la explicación práctica del trabajo de titulación. La duración prevista es de unos 19 minutos.

**Formato de cada segmento:**
- el tiempo y la ventana que se usa: Docker Desktop, VS Code o el navegador;
- qué se abre y qué se muestra;
- un texto para decir con naturalidad, que no hace falta leer al pie de la letra.

**Recorridos en VS Code.** Cada segmento de código tiene su recorrido guiado. VS Code abre el archivo en la línea exacta y basta con pulsar «siguiente».

**Regla de oro.** Toda cifra que se dice en el video está en un archivo del proyecto. La tabla del final indica dónde está cada una.

| # | Segmento | Tiempo | Ventana | Recorrido de VS Code |
|---|---|---|---|---|
| 0 | Apertura: problema y objetivo | 1 min | Navegador (README en GitHub) | No |
| 1 | Arquitectura y gateway | 3 min | Docker Desktop y VS Code | 1 · Arquitectura |
| 2 | Backend: los tres microservicios | 4 min | VS Code y navegador | 2 · auth-service y 3 · fleet-core-service |
| 3 | Priorización con AHP | 3 min | VS Code y navegador | 4 · reporting-service |
| 4 | Frontend y recorrido del sistema | 3 min | VS Code y navegador | 5 · Frontend |
| 5 | Pruebas y validación | 3 min | VS Code y navegador (GitHub Actions) | 6 · Pruebas |
| 6 | Decisiones tecnológicas y tendencias | 1,5 min | VS Code | No |
| 7 | Cierre: resultados por objetivo | 0,5 min | Navegador | No |

# Antes de grabar (lista de preparación)

**Primero: tener la última versión del código (la del Avance 3)**

Si la computadora tenía la versión del Avance 2, en una terminal:

```
cd control_flota
git status
git fetch origin --tags
git checkout main
git pull origin main
git describe --tags
docker compose down
docker compose up --build -d
docker compose restart gateway
```

- **Cambios locales:** si `git status` muestra archivos modificados, ejecutar antes `git stash`.
- **Versión correcta:** `git describe --tags` debe mostrar `v2.0-avance3`.
- **Datos:** la base de datos se conserva; no usar `docker compose down -v`.
- **Computadora sin el proyecto:** clonarlo con `git clone https://github.com/usuario/control_flota.git`, luego `cd control_flota` y `docker compose up --build -d`.

**Sistema**
- Docker Desktop abierto. En una terminal, en la carpeta `sistema-control-flota`, ejecutar `docker compose up -d`.
- En Docker Desktop, el grupo `sistema-control-flota` debe tener los 6 contenedores en verde: postgres, auth-service, fleet-core-service, reporting-service, gateway y frontend.
- Si el navegador muestra un error 502 o 404 después de reconstruir: `docker compose restart gateway`.
- Abrir http://localhost:5173 e iniciar sesión con el usuario de prueba local `admin` / `Admin1234`.

**VS Code**
- Abrir el archivo `flotacontrol.code-workspace`, en la raíz del repositorio.
- Instalar la extensión recomendada **CodeTour**; VS Code la sugiere al abrir el espacio de trabajo.
- Comprobar que en el panel Explorador aparece la sección **CODETOUR** con los 6 recorridos.
- Para iniciar un recorrido: clic en su nombre y luego en ▶. Para avanzar: el botón «Next» o la flecha →.
- Dejar abierta una terminal integrada en la carpeta `sistema-control-flota`.

**Navegador: pestañas abiertas en este orden**
- El repositorio en GitHub: https://github.com/usuario/control_flota (README).
- El sistema: http://localhost:5173 (tablero, con la sesión iniciada).
- Las ejecuciones de GitHub Actions del repositorio (pestaña «Actions»).

**Ensayo del flujo de cierre de viaje (segmento 2)**
- En **Mantenimiento**, en la tabla «Qué reparar primero», elegir un vehículo con un mantenimiento a más de 1000 km, por ejemplo LTA-1555, aceite.
- Anotar sus **km restantes**.
- En **Vehículos**, anotar el odómetro actual de ese vehículo.
- En **Viajes**, crear un viaje para ese vehículo con el km inicial igual al odómetro, y dejarlo **iniciado**.
- En el video se cerrará con km final = odómetro + km restantes − 500, para que salte la alerta «próximo».

**Grabación**
- Notificaciones del sistema apagadas; cerrar el correo y los mensajes.
- Compartir la pantalla completa en Google Meet; probar el micrófono.
- Tener a mano el texto de esta guía en una segunda pantalla o impreso.

# Segmento 0 · Apertura (1 min)

**Ventana:** navegador, README del repositorio en GitHub. Mostrar el título y el banner, y bajar hasta la sección «Qué hace».

**Qué digo:**

> Buenas, soy Daniela Sofía Ramos Paredes, de Ingeniería en Tecnologías de la Información de la UNEMI. Mi trabajo es un sistema web con arquitectura de microservicios para el control de costos operativos y el mantenimiento de una flota de transporte de carga pesada, con priorización del mantenimiento mediante AHP.

> El problema es concreto: en las pequeñas empresas de transporte de Arenillas, los gastos se anotan en libretas o en WhatsApp, nadie sabe cuánto cuesta realmente cada camión y, como lo confirmaron las tres personas entrevistadas, todo depende de una sola persona.

> El objetivo general es desarrollar un sistema web con arquitectura de microservicios que apoye la toma de decisiones administrativas de una pequeña empresa de transporte de carga pesada.

> En este video les muestro la arquitectura, el backend, la priorización con AHP, el frontend y cómo validé que el sistema funciona.

# Segmento 1 · Arquitectura y gateway (3 min)

**Ventanas:** Docker Desktop, luego VS Code con el recorrido **1 · Arquitectura**.

**Qué muestro:**
- **Docker Desktop:** el grupo `sistema-control-flota` con sus 6 contenedores en ejecución.
- **VS Code:** abrir `docs/diagramas/arquitectura_contenedores.png` y explicar el diagrama.
- **Recorrido 1, sus 7 pasos:**
  - `docker-compose.yml`: postgres, los tres servicios, el gateway y el frontend;
  - `infra/postgres/roles.sql`: un rol por servicio;
  - `infra/nginx/nginx.conf`: las rutas `/api/auth`, `/api/fleet` y `/api/reports`, y el límite de intentos del login.

**Qué digo:**

> El sistema está formado por seis contenedores que levanto con Docker Compose: tres microservicios hechos con FastAPI, una base de datos PostgreSQL, un API gateway con Nginx y el frontend en React.

> El navegador nunca habla directamente con un microservicio: todo entra por el gateway, en el puerto 8080. El gateway reparte cada petición según su ruta: lo que empieza con `/api/auth` va a auth-service, `/api/fleet` va a fleet-core-service y `/api/reports` va a reporting-service. Además limita los intentos de inicio de sesión a diez por minuto.

> En la base de datos hay una sola instancia de PostgreSQL con dos esquemas, `auth` y `fleet`, y cada servicio tiene su propio rol de base de datos, dueño solo de su esquema. Así, aunque comparten la instancia, un servicio no puede leer los datos del otro. reporting-service no tiene base de datos: pide los datos a fleet-core por HTTP.

> Elegí microservicios de grano grueso con una matriz de decisión ponderada: obtuvieron 3,95, frente a 3,60 del monolito modular y 3,35 del monolito en capas. Ganaron por el aislamiento de los datos personales y por el despliegue independiente de cada servicio. Soy transparente en esto: en rendimiento y en costo de operación gana el monolito, y lo dejé documentado.

# Segmento 2 · Backend: los tres microservicios (4 min)

**Ventana:** VS Code, recorridos **2 · auth-service** y **3 · fleet-core-service**; luego el navegador para el flujo de cierre de viaje.

**Qué muestro en el recorrido 2 (auth-service, 5 pasos):**
- `main.py`: la aplicación FastAPI, con sus routers y `/health`;
- `core/security.py`: bcrypt y emisión del JWT, con el id del usuario, el rol y la expiración;
- `routers/auth.py`: el endpoint de login;
- `core/lockout.py`: el bloqueo por intentos fallidos.

**Qué muestro en el recorrido 3 (fleet-core-service, 9 pasos):**
- `main.py`: los módulos del dominio;
- `core/database.py`: el esquema propio;
- `core/deps.py`: la autorización por rol;
- `models/trip.py` y `migrations/versions`;
- `trips/router.py`, la función `close_trip`;
- `maintenance/policy.py`;
- `despacho/router.py`;
- `analytics/router.py`;
- `costs/proration.py`.

**Flujo de punta a punta en el navegador:**
- **Viajes:** abrir el viaje iniciado durante la preparación y cerrarlo con el km final calculado, más el ingreso del viaje.
- **Resultado:** el sistema muestra la alerta de mantenimiento «próximo».
- **Mantenimiento:** la alerta aparece en la lista de vencidos o próximos.

**Qué digo:**

> Cada microservicio tiene la misma estructura: un archivo `main.py` que arma la aplicación FastAPI, una carpeta `core` con la configuración y la seguridad, los modelos de SQLAlchemy, los esquemas de Pydantic que validan cada dato que entra, y los routers con los endpoints.

> auth-service se encarga de los usuarios y los roles. Las contraseñas se guardan con hash bcrypt, nunca en texto plano. Al iniciar sesión se emite un token JWT que lleva el usuario, su rol y la expiración. Los otros dos servicios validan ese token por su cuenta, sin consultar la base de usuarios. Si alguien falla varias veces la contraseña, la cuenta se bloquea un tiempo.

> fleet-core-service es el núcleo del dominio: vehículos, conductores, viajes, gastos, mantenimiento, costos fijos y el despacho por código QR. Cada endpoint declara qué rol puede usarlo: sin token responde 401 y con un rol no permitido, 403. Los cambios del esquema de la base se versionan con migraciones de Alembic.

> Les muestro un flujo completo. Cierro este viaje con su kilometraje final. Al cerrarlo, fleet-core guarda el kilometraje y el ingreso, actualiza el odómetro del vehículo y revisa sus mantenimientos pendientes. Como a este le faltan menos de 1000 km, que es el umbral que fijaron los expertos, devuelve una alerta de «próximo».

> El conductor no tiene usuario ni contraseña: registra la salida desde el celular con una credencial QR personal, guardada como hash y con vigencia. Lo muestro en el frontend.

# Segmento 3 · Priorización con AHP (3 min)

**Ventanas:** VS Code con el recorrido **4 · reporting-service** (8 pasos); luego el navegador en **Mantenimiento**, tabla «Qué reparar primero».

**Qué muestro:**
- **Recorrido 4:**
  - `core/fleet_client.py`: sin base de datos propia;
  - `dashboards/cost_model.py`;
  - `dashboards/ahp_config.json`, con los juicios de los expertos y su procedencia;
  - `dashboards/ahp.py`: pesos, CR y la regla de no arrancar si CR ≥ 0,10;
  - `dashboards/service.py`: el ranking con desempate.
- **Opcional:** `12_RESULTADOS_OBTENIDOS/ahp_expertos.md`, tablas 1 y 2.
- **Navegador:** la frase «seguridad (53 %), urgencia (42 %) y costo (5 %)», y dos mantenimientos con el mismo puntaje (0,974) en los que aparece primero el más vencido.

**Qué digo:**

> La priorización usa el método AHP de Saaty con tres criterios: seguridad, urgencia por kilometraje y costo. Los juicios no están escritos en el código: viven en este archivo de configuración, que declara de dónde salió cada valor.

> Apliqué el cuestionario a tres expertos externos del transporte de carga. El cálculo normaliza la matriz por columnas y obtiene los pesos y la razón de consistencia. Dos expertos fueron consistentes, con CR menor que 0,10. El tercero tuvo un CR de 0,54 porque marcó el máximo, 9, en las tres comparaciones. Según el protocolo aprobado, su matriz se le devolvió para revisión y el sistema usa la media geométrica de los dos expertos consistentes. El resultado es seguridad 53 %, urgencia 42 % y costo 5 %, con CR de 0,0115.

> Verifiqué los pesos con una librería independiente, ahpy, y coinciden. Además, si un día alguien carga una matriz inconsistente, el servicio no arranca.

> Un hallazgo: con la mediana de las calificaciones de los expertos, frenos, llantas, bocines, aceite y filtros quedan igual de críticos. Por eso, cuando dos mantenimientos empatan, el sistema atiende primero el más vencido en kilómetros. Es la regla que me dio una de las propietarias entrevistadas: seguridad primero y luego el kilómetro. Aquí se ve: los dos tienen 0,974, y primero aparece el vencido hace 481 km.

> El ranking es estable: con cambios de hasta 30 % en los pesos, el primer lugar y los tres primeros no cambian, y la tau de Kendall no baja de 0,935.

*Si en la pantalla los números de km son otros, por los ensayos o por un viaje cerrado, decir los que se ven.*

# Segmento 4 · Frontend y recorrido del sistema (3 min)

**Ventanas:** VS Code con el recorrido **5 · Frontend** (8 pasos), luego el navegador.

**Qué muestro en el código:**
- `App.tsx`: las rutas;
- `services/apiClient.ts`: todo va al gateway, `:8080/api`, con el token en la cabecera `Authorization`;
- `context/AuthContext.tsx`;
- las páginas del tablero, de mantenimiento, de conductores (el QR) y de despacho.

**Qué muestro en el navegador, en este orden:**
- **Tablero:**
  - indicadores del período y gráfica de costos;
  - cambiar el modo de IVA entre montos pagados y sin IVA;
  - la estructura del costo en categorías.
- **Costos:** costos fijos y de personal; solo los ve el administrador.
- **Reportes:** exportar a Excel o PDF.
- **Conductores:** en un conductor, «Generar código»; se muestra la tarjeta con el QR para la cabina.
- **Terminal de VS Code:** `python scripts/enlace_despacho_demo.py`. Copiar el enlace que imprime.
- **Navegador:**
  - abrir el enlace en una pestaña nueva;
  - F12 y Ctrl+Shift+M para la vista de celular;
  - mostrar el formulario del conductor con su vehículo asignado.

**Qué digo:**

> El frontend está hecho en React con TypeScript y Vite. Cada pantalla es una ruta. El inicio de sesión y el portal del conductor son públicas; las demás exigen sesión, y algunas, el rol de administrador.

> Todas las llamadas pasan por este cliente, que apunta al gateway y agrega el token JWT en cada petición. Así el frontend no sabe cuántos microservicios hay detrás: solo conoce el gateway.

> El tablero muestra el costo de cada camión y de la flota en el período: el costo variable, el costo fijo, el costo total, el costo por kilómetro y la utilidad. Puedo ver los montos tal como se pagaron o sin IVA. Los costos fijos y los sueldos solo los ve el administrador; el operador no.

> Para el despacho, el administrador genera el código QR del conductor y lo imprime para la cabina. El conductor lo escanea y se abre este formulario en su celular, ya con su nombre y su vehículo. Registra el origen, el destino y el kilometraje de salida, y el viaje queda iniciado. Para el video genero el enlace del QR con un script y lo abro con la vista de celular del navegador. Fíjense que el token desaparece de la barra de direcciones al cargar, para que no quede a la vista.

# Segmento 5 · Pruebas y validación (3 min)

**Ventanas:** VS Code con el recorrido **6 · Pruebas** (4 pasos); luego el navegador en GitHub Actions.

**Qué muestro:**
- **Recorrido 6:**
  - una prueba unitaria del AHP;
  - la prueba del desempate;
  - una prueba de integración por el gateway;
  - `.github/workflows/ci.yml`.
- **Navegador:** la pestaña «Actions» de GitHub con la última ejecución en verde.
- **Opcional, en VS Code:**
  - `12_RESULTADOS_OBTENIDOS/pruebas_avance3.md` y `cobertura_pruebas.md`;
  - la tabla de `validacion_costos_mes_real.md`.

**Qué digo:**

> Hay dos tipos de pruebas. Las unitarias verifican cada cálculo contra un cálculo hecho a mano: los pesos del AHP, el costo por kilómetro, el prorrateo de los costos fijos. Las de integración envían peticiones HTTP reales a través del gateway, con autenticación y roles, contra una copia aislada del sistema.

> En total son 910 pruebas: 909 aprobadas y una omitida a propósito, la que agota el límite de peticiones del gateway, porque lo bloquea un minuto. La cobertura de las pruebas unitarias es del 80 %, por encima del 60 % que pedía el requerimiento. Cada cambio que subo a GitHub dispara la integración continua: corre las pruebas, construye las imágenes y levanta el sistema completo.

> Medí el rendimiento: con 10 usuarios a la vez abriendo el tablero, el 95 % de las cargas completas tarda menos de 1,19 segundos, dentro de los 2 segundos del requerimiento. Con un millón de viajes, las consultas por vehículo y por viaje son de 6 a 10 veces más rápidas gracias a los índices.

> Y la validación más importante: cargué en el sistema un mes real de la empresa caso, septiembre de 2026, con sus comprobantes del SRI anonimizados. El ingreso, el combustible, los peajes y los filtros coinciden al centavo con el cálculo manual de la propietaria. El costo total difiere en −0,48 % y la utilidad en +0,64 %. La única diferencia es el pago al chofer, porque el sistema prorratea los montos mensuales por días.

# Segmento 6 · Decisiones tecnológicas y tendencias (1,5 min)

**Ventana:** VS Code; si se desea, el README en la sección «Arquitectura».

**Qué digo:**

> Cada tecnología salió de una matriz de decisión con criterios ponderados:

> - **Backend:** FastAPI obtuvo 4,80, frente a 4,00 de Django REST y 2,95 de Express, que es la base de NestJS. Ganó por la validación de datos con Pydantic y porque un solo lenguaje, Python, sirve para los servicios y para el análisis de costos y del AHP. Spring Boot implicaría un segundo lenguaje para ese análisis.
> - **Base de datos:** PostgreSQL obtuvo 4,80, por los esquemas y roles con dueño por servicio.
> - **Empaquetado:** Docker Compose obtuvo 4,20 frente a 3,90 de Kubernetes, porque una pequeña empresa no necesita la complejidad de operar un clúster.
> - **Frontend:** React y Vue quedaron prácticamente empatados (4,65 y 4,75). Mantuve React porque el prototipo ya estaba construido y probado con él.

> Sobre las herramientas que se recomendaron:

> - **Gateway:** Nginx cubre hoy el enrutamiento, el límite de peticiones y HTTPS. Kong o Traefik serían el siguiente paso si se necesita autenticación en el borde o el descubrimiento automático de servicios.
> - **Tablero:** está dentro de la aplicación porque depende de los roles, ya que los sueldos no los ve el operador, y del ranking AHP. Superset quedaría para análisis libres sobre PostgreSQL.
> - **ahpy:** ya la usé para verificar los pesos.

> Las tendencias que sigue el proyecto son los contenedores, los microservicios con API gateway, la integración continua y el despliegue en la nube, que dejé propuesto en Cloud Run.

# Segmento 7 · Cierre (0,5 min)

**Ventana:** navegador, README en GitHub, sección «Pruebas y calidad».

**Qué digo:**

> En resumen:

> - **Diagnóstico:** las entrevistas y el mes real confirmaron el problema.
> - **Diseño:** una arquitectura de microservicios con su modelo de datos y su modelo AHP.
> - **Desarrollo:** los módulos de registro, costos, alertas, priorización y despacho móvil.
> - **Evaluación:** 909 de 910 pruebas aprobadas, la validación de costos con datos reales y los pesos de los expertos con CR de 0,0115.

> El código completo está en el repositorio de GitHub. Gracias.

# Si algo falla durante la grabación

| Problema | Qué hacer |
|---|---|
| El navegador muestra 502, 404 o «No se pudo conectar» | En la terminal: `docker compose restart gateway`, esperar 5 segundos y recargar |
| Un contenedor no está en verde | `docker compose up -d` y esperar a que todos estén «healthy» |
| El enlace del despacho dice que el código ya no es válido | Volver a ejecutar `python scripts/enlace_despacho_demo.py`: cada vez emite un código nuevo |
| CodeTour no aparece | Abrir el archivo indicado con Ctrl+P y el nombre del archivo; la guía trae la ruta |
| Algo de la demostración no carga a tiempo | Mostrar la captura equivalente de `docs/capturas/` o el video `docs/video/demo_panel.mp4` y seguir |

# Preguntas probables del tribunal

| Pregunta | Respuesta breve |
|---|---|
| ¿Por qué microservicios y no un monolito, si es una empresa pequeña? | Lo decidí con una matriz ponderada (3,95 frente a 3,60 y 3,35). Ganó por aislar los datos personales y desplegar cada servicio por separado. El monolito gana en rendimiento y en costo de operación, y lo declaro; por eso son microservicios de grano grueso: solo tres servicios. |
| ¿Cómo se comunican los servicios? | El navegador solo habla con el gateway. reporting-service consulta a fleet-core por HTTP, reenviando el token del usuario para que se respeten los mismos permisos. |
| ¿Cómo se protege la información? | Contraseñas con bcrypt, JWT con rol y expiración, autorización por rol en cada endpoint, un rol de base de datos por servicio, límite de intentos en el gateway, bloqueo de cuentas y credencial QR guardada como hash, con vigencia y revocable. |
| ¿Qué pasa si los expertos no son consistentes? | Si el CR es de 0,10 o más, la matriz se devuelve al experto. El sistema usa solo las matrices consistentes y no arranca con una configuración inconsistente. |
| ¿Por qué solo dos expertos en los pesos? | Consulté a tres; uno fue inconsistente (CR 0,54) y quedó pendiente de revisar sus juicios. Con el método del vector propio, el agregado de los tres da CR = 0,1000, que no pasa el umbral, así que incluirlo sin revisar no era correcto. El ranking con y sin él mantiene el primer lugar. |
| ¿Cómo sabe que el costo que calcula es correcto? | Por las pruebas unitarias contra cálculos hechos a mano y por la validación con un mes real de la empresa caso: −0,48 % en el costo total, por la convención de prorrateo. |
| ¿Por qué no calcula el costo por kilómetro de la empresa caso? | Porque la propietaria no registra el kilometraje. El sistema deja ese indicador vacío en lugar de inventarlo. Registrar el km al cerrar cada viaje es una de las recomendaciones. |
| ¿El sistema soporta carga? | Con 10 usuarios concurrentes, el p95 de la carga completa del tablero es de 1,19 s, menor que los 2 s de RNF-01. |
| ¿Qué falta para producción? | El despliegue en la nube (Cloud Run, propuesto), las pruebas con usuarios (SUS), el rubro de comisión del conductor por viaje y la revisión del tercer experto. |
| ¿Cómo se verifica que el código funciona en cada cambio? | La integración continua de GitHub Actions corre las pruebas, construye las imágenes y levanta el sistema completo. |

# Versión de 5 minutos para la sustentación

| Min | Qué se muestra |
|---|---|
| 0:00–0:45 | Docker Desktop con los 6 contenedores y el diagrama de arquitectura: tres microservicios, el gateway, la base de datos y el frontend |
| 0:45–1:45 | Iniciar sesión → tablero: costo por vehículo, costo por km y utilidad; cambio de IVA |
| 1:45–2:45 | Mantenimiento: alertas por kilometraje y ranking AHP con los pesos de los expertos (53 %, 42 %, 5 %; CR 0,0115) |
| 2:45–3:45 | Conductores → generar QR → abrir el enlace del despacho en vista de celular |
| 3:45–4:30 | Reportes: exportar a Excel o PDF |
| 4:30–5:00 | GitHub Actions en verde: 909 de 910 pruebas y validación con el mes real (−0,48 %) |

# Dónde está cada cifra que se dice

| Cifra | Valor | Archivo |
|---|---|---|
| Pruebas | 910 en total, 909 aprobadas, 1 omitida | `12_RESULTADOS_OBTENIDOS/pruebas_avance3.md` |
| Cobertura de las pruebas unitarias | 80 % (77 %, 69 % y 94 % por servicio) | `12_RESULTADOS_OBTENIDOS/cobertura_pruebas.md` |
| Pesos AHP y CR | 0,528 / 0,420 / 0,053; CR 0,0115 | `12_RESULTADOS_OBTENIDOS/ahp_expertos.md` |
| CR del experto inconsistente | 0,5407 | `12_RESULTADOS_OBTENIDOS/ahp_expertos.md` |
| Agregado de los 3 expertos con ahpy | CR 0,1000 | `12_RESULTADOS_OBTENIDOS/ahp_expertos.md` |
| Estabilidad del ranking | τ ≥ 0,935 con ±30 % | `12_RESULTADOS_OBTENIDOS/ahp_expertos.md` |
| Umbral «próximo» | 1000 km | `services/fleet-core-service/app/maintenance/maintenance_policy.json` |
| Validación con el mes real | Costo −0,48 %; utilidad +0,64 % | `12_RESULTADOS_OBTENIDOS/validacion_costos_mes_real.md` |
| Prueba de carga | p95 de 1,19 s con 10 usuarios | `12_RESULTADOS_OBTENIDOS/prueba_de_carga_tablero.md` |
| Benchmark con índices | 6 a 10 veces más rápido con un millón de viajes | `12_RESULTADOS_OBTENIDOS/benchmark_consultas.md` |
| Matrices de decisión | Microservicios 3,95; FastAPI 4,80; PostgreSQL 4,80; Docker Compose 4,20; React 4,65 | `14_DOCUMENTACION_TECNICA_ADICIONAL/decisiones/resultados_decisiones.json` |
