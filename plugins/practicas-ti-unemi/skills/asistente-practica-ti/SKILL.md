---
name: asistente-practica-ti
description: 'Puerta de entrada para hacer una práctica de laboratorio de TI de la UNEMI de punta a punta (guía PDF, mediciones, evidencias, informe Word APA 7). Usar con «guía de práctica», «mi práctica de Fundamentos de TI» o «actividad de aprendizaje».'
---

# Asistente de prácticas de TI (UNEMI)

Pipeline con un control de calidad por etapa. No pases a la siguiente sin cumplirlo.

| # | Etapa | Skill | Control |
|---|---|---|---|
| 1 | Leer la guía (texto y páginas en imagen) | `leer-guia-practica` | Objetivos, estructura sugerida y rúbrica identificados |
| 2 | Literatura científica (Scopus, últimos 5 años) | `asistente-investigacion-cientifica:revision-sistematica` | 2 artículos por subtema, con DOI verificado |
| 3 | Medición de red | `medicion-de-red` | Tabla con 3 mediciones por conexión y condiciones declaradas |
| 3b | Lo que no se puede medir (datos móviles, red institucional, BitLocker en Home) | `laboratorio-docker` | Simulación rotulada y parámetros declarados |
| 4 | Comercio electrónico | `comparar-plataformas-comercio` | Cuadro comparativo con fuentes, sin comprar |
| 5 | Cifrado y antivirus | `seguridad-cifrado-antivirus` | Tiempos medidos y estado de Defender |
| 6 | Ciclo de vida, IA y sistemas expertos | `ciclo-vida-ia-sistemas-expertos` | Casos resueltos por el modelo y por el sistema de reglas |
| 7 | Evidencias (capturas) | `evidencias-capturas` | Cada anexo tiene su imagen revisada |
| 8 | Informe Word y verificación APA | `informe-practica-unemi` | 0 errores APA y lista de verificación de la guía completa |

## Reglas que valen para todas las etapas
1. **No inventes resultados.** Lo que no se midió o probó se deja resaltado (`==completar==`) y se dice a la usuaria qué falta y cómo hacerlo. Los datos medidos salen de archivos reales (CSV, JSON, texto de consola).
2. **No cambies la seguridad de la computadora.** No actives BitLocker ni «Cifrado de dispositivo», no pulses «Confiar» en VS Code, no desactives Defender. BitLocker no existe en Windows Home: se documenta como limitación, con evidencia.
3. **Nada de escaneo de redes ajenas.** Se mide la conexión propia (ping, Speedtest). Nmap u otro escáner solo sobre la red de la propia usuaria y si ella lo pide.
4. **Privacidad.** Fuera del documento: SSID, dirección MAC, IP, rutas de otros proyectos, conversaciones, contraseñas. Las contraseñas de prueba se generan al azar, se guardan en un archivo local y no se escriben en el chat.
5. **Cuentas y compras.** No crear cuentas, no iniciar sesión por la usuaria, no comprar. La simulación de compra llega hasta el listado y el carrito.
6. **Lo que solo ella puede hacer** (conectarse a otra red con contraseña, compartir datos móviles, escribir nombres y fechas de la portada, pulsar «Aceptar» en instaladores con permisos) se le dice con pasos numerados y exactos.
7. **Word abierto bloquea el guardado**: guarda copias `_v2`, `_v3`… y dile cuál es la vigente.
8. **Las citas salen de lo que se leyó.** Si solo se leyó el resumen, dilo y no cites páginas.
9. **Rigor:** no afirmes lo que no se probó (p. ej. «clave incorrecta rechazada» solo para las herramientas en que se probó); declara las condiciones de cada medición (adaptadores activos, servidor, fecha) y las limitaciones; lo simulado va rotulado como simulación.
10. **Cero pendientes en el documento final:** nada de notas «completar» ni texto resaltado. Lo que solo la usuaria puede aportar se le pide en el chat antes de armar el informe (AskUserQuestion) y un campo que ella prefiera llenar a mano queda en blanco.
11. La guía de la práctica prevalece sobre cualquier plantilla de este plugin (por ejemplo, si pide «red institucional» y la usuaria estudia en línea desde casa, se sustituye por otra conexión y se justifica en el texto).

**Otras tareas de TI:** si no es una práctica de laboratorio sino una tarea grupal de Gestión de TI (ITIL, COBIT, ISO 20000, plan con KPI), usa `tarea-grupal-gestion-ti`.

## Cómo empezar
1. Pide la ruta del PDF de la guía y de la plantilla Word (`formato_para_actividades_de_aprendizaje_UNEMI.docx`) y crea una carpeta de trabajo con `literatura/`, `medicion/`, `anexos/`.
2. Ejecuta `leer-guia-practica` y propón el reparto por subtemas que fija la guía.
3. Usa `informe-practica-unemi/referencias/lista_verificacion_guia.md` como lista de control «al pie de la letra».
4. Sigue la tabla de etapas en el orden que permita lo disponible: las pruebas que dependen de la usuaria (otra red, datos móviles) se piden pronto para no frenar el informe.
5. Al final, `informe-practica-unemi` y la verificación con `asistente-investigacion-cientifica:redaccion-apa7`.

Requisitos: plugin `asistente-investigacion-cientifica` (Scopus, APA); Python con `pymupdf`, `python-docx`, `matplotlib`, `Pillow`; Windows con PowerShell.
