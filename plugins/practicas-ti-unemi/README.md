# Prácticas de TI (UNEMI)

Plugin de Claude Code para hacer de punta a punta las **prácticas de laboratorio de la carrera de Tecnologías de la Información** de la UNEMI. Nace de la Práctica 3 de *Fundamentos de Tecnologías de Información* (Internet, comercio electrónico, seguridad, ciclo de vida de sistemas e inteligencia artificial) y sirve para cualquier práctica con guía de la SGA.

## Skills

| Skill | Qué hace |
|---|---|
| `asistente-practica-ti` | Puerta de entrada: etapas, controles y reglas |
| `leer-guia-practica` | Lee la guía PDF, también las páginas en imagen (visión), y resume objetivos y rúbrica |
| `medicion-de-red` | Ping + Speedtest por conexión (Wi-Fi 5/2,4 GHz, Ethernet, datos móviles), CSV, gráfico, tabla e IoT |
| `comparar-plataformas-comercio` | Amazon, Mercado Libre, Shopify: seguridad, usabilidad y modelo de negocio sin comprar |
| `laboratorio-docker` | Simula con Docker lo que no se puede medir: datos móviles y red institucional (iperf3 y tc/netem) y cifrado de disco completo con LUKS (equivalente de BitLocker) en una VM Linux, siempre rotulado como simulación |
| `seguridad-cifrado-antivirus` | VeraCrypt, 7-Zip (AES-256), Defender, EICAR; BitLocker solo en Windows Pro |
| `ciclo-vida-ia-sistemas-expertos` | SDLC frente a MLOps; sistema experto de reglas frente a modelo generativo |
| `evidencias-capturas` | Capturas seguras (HTML→PNG, ventana concreta) y revisión de cada imagen |
| `informe-practica-unemi` | Word sobre la plantilla oficial, APA 7, anexos con imágenes y verificación |
| `tarea-grupal-gestion-ti` | Tareas grupales de Gestión de TI (ITIL 4, COBIT, ISO 20000): Word sobre la plantilla de portada, KPI, APA 7 y anexo de IA aparte |

## Requisitos
- Windows con PowerShell; Python con `pymupdf`, `python-docx`, `matplotlib`, `Pillow`.
- Plugin `asistente-investigacion-cientifica` (Scopus, `word_apa.py`, verificador APA):
  `claude plugin install asistente-investigacion-cientifica@ethos-ia-academia --scope user`
- Opcional: Docker Desktop (laboratorio), Speedtest CLI (`winget install Ookla.Speedtest.CLI`), VeraCrypt (`winget install IDRIX.VeraCrypt`), 7-Zip.

## Principios
No se inventan resultados; no se cambia la seguridad de la computadora; no se escanean redes ajenas; no se compra ni se crean cuentas; lo que solo la estudiante puede hacer se le pide con pasos exactos; los datos privados (SSID, MAC, rutas, contraseñas) no van al informe.

Los resultados de las skills son material de estudio: el informe final es de la estudiante y debe declarar el uso de IA según la normativa de su curso.

Licencia MIT. Autoría: Ethos IA (ETHOSLAB S.A.S.).
