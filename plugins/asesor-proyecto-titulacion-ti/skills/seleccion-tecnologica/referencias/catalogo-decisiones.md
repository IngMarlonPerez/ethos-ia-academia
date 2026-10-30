# Catálogo de decisiones tecnológicas por tipo de proyecto

Candidatas habituales en tesis de TI (2026). **No son recomendaciones**: la matriz decide con la evidencia del proyecto. Agrega otras si el dominio lo pide.

| Decisión | Aplica a | Candidatas típicas (elige ≥ 3 pertinentes) |
|---|---|---|
| Lenguaje del backend | software, datos_ml, ia_llm | Python · Java · C# (.NET) · JavaScript/TypeScript (Node.js) · Go · PHP |
| Framework de backend | software | FastAPI · Django · Flask · Spring Boot · ASP.NET Core · Express/NestJS · Laravel |
| Framework de frontend | software | React · Angular · Vue · Svelte · Next.js · plantillas del servidor (sin SPA) |
| Base de datos | software, datos_ml | PostgreSQL · SQL Server · MySQL/MariaDB · MongoDB · SQLite (prototipo) |
| Almacén analítico / BI | datos_ml | Esquema estrella en SQL Server/PostgreSQL · DuckDB · Power BI · Metabase · panel propio |
| Acceso a datos | software | ORM (SQLAlchemy, Hibernate, Entity Framework, Prisma) · SQL parametrizado · procedimientos almacenados |
| Biblioteca de ML | datos_ml | scikit-learn · XGBoost/LightGBM · TensorFlow/Keras · PyTorch |
| Proveedor de LLM | ia_llm | API comercial (Claude, GPT, Gemini) · modelo abierto autoalojado (Llama, Qwen, Mistral) · cascada de proveedores |
| Orquestación de LLM | ia_llm | SDK directo · LangChain · LlamaIndex |
| Autenticación | software | JWT propio · OAuth2/OIDC (Keycloak, Auth0) · sesión del servidor |
| Despliegue | software | Contenedores (Docker Compose) · PaaS (Render, Railway, Vercel) · servidor institucional · nube (AWS, Azure, GCP) |
| Móvil | software | Flutter · React Native · Kotlin nativo · PWA |
| Redes o IoT | redes | MQTT (Mosquitto) · CoAP · HTTP; ESP32 · Raspberry Pi · Arduino |
| Seguridad | seguridad | Wazuh · Suricata · Snort · ELK · herramientas de escaneo (OWASP ZAP, Nmap) |

## Criterios que casi siempre aplican (ajusta los pesos a los RNF)
- **Ecosistema para el problema**: ¿hay bibliotecas maduras para lo que hay que hacer?
- **Evidencia en trabajos previos**: ¿cuántos de los trabajos previos lo usan? (`tabla_trabajos_previos.py --conteos`)
- **Dominio del equipo**: ¿lo conoce el equipo? Cita las asignaturas de la malla que lo enseñaron.
- **Rendimiento** para la carga esperada (no la de Netflix).
- **Seguridad**: soporte para parametrizar consultas, gestionar identidades y actualizaciones de seguridad.
- **Licencia y costo**: libre o sin costo para una institución pública.
- **Soporte a largo plazo**: versión LTS, fin de soporte, actividad del proyecto.
- **Compatibilidad**: con la infraestructura de la institución (motor de base de datos existente, servidores Windows o Linux).
