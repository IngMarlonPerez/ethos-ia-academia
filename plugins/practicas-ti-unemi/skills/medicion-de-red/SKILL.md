---
name: medicion-de-red
description: 'Mide y compara conexiones propias (Wi-Fi 5/2,4 GHz, Ethernet, datos móviles) con ping y Speedtest, y arma tabla y gráfico. Usar para «mide mi red», «test de velocidad» o IoT.'
---

# Medición de red e IoT

## Principios
- Se mide **la conexión propia**; no se escanean otros equipos ni puertos. Si la usuaria pregunta por una «herramienta de escaneo» (Nmap, Wireshark, Fing): explica que miden otra cosa (descubrimiento de dispositivos o tráfico), que la práctica pide velocidad y estabilidad, y que solo se usan en su propia red si ella lo pide.
- La velocidad de enlace de `netsh` (p. ej. 173 Mbps) **no es** la velocidad de Internet: es lo negociado con el router. La de Internet la da Speedtest.
- Datos privados (SSID, MAC, IP) **no van** al informe.

## Pasos
1. **Instalar Speedtest** (una vez): `winget install Ookla.Speedtest.CLI`. Reinicia la consola si `speedtest` no se reconoce. Acepta la licencia con `--accept-license --accept-gdpr` (uso personal no comercial).
2. **Dejar una sola vía activa por medición.** Si hay dos adaptadores Wi-Fi conectados al mismo tiempo, Windows puede enviar el tráfico por cualquiera: desconecta uno (`netsh wlan disconnect interface="Wi-Fi 2"`; desactivar el adaptador exige administrador). Para medir Ethernet, desconecta el Wi-Fi durante la prueba y **reconéctalo al terminar** (`netsh wlan connect name="<perfil>" interface="<adaptador>"`).
3. **Medir cada conexión** (3 pruebas de Speedtest + 50 pings; unos 4 minutos):
   `pwsh -File "${CLAUDE_PLUGIN_ROOT}/skills/medicion-de-red/scripts/medir_red.ps1" -Conexion "Wi-Fi 5 GHz" -Salida "<carpeta>\medicion"`
   Repite con `-Conexion "Wi-Fi 2.4 GHz"`, `"Ethernet"`, etc. Usa un servidor fijo con `-Servidor <id>` (lista con `speedtest -L`) para que las conexiones sean comparables. Si un servidor da `Latency test failed` o `Unknown error`, prueba otro de la lista.
   - Lanza la medición **en segundo plano** y espera el aviso de fin; no uses Internet en el equipo mientras corre.
   - Una prueba de Speedtest cortada (ventana reiniciada) no vale: se repite.
4. **Conexiones que dependen de la usuaria:** Wi-Fi de otra banda (conectarse con contraseña), datos móviles (compartir Internet desde un celular con datos) o red institucional (solo en el campus o por VPN). Si no puede (estudia en línea desde casa, el celular no tiene datos), **sustituye** por una conexión que sí pueda probar (otra banda del mismo router, cable Ethernet) y deja la justificación en el texto del informe. No inventes datos de la conexión que falta.
5. **Gráfico y promedios:** `python -I "${CLAUDE_PLUGIN_ROOT}/skills/medicion-de-red/scripts/graficos_red.py" "<carpeta>\medicion"` → `figura1_velocidad.png` y los promedios para la tabla.
6. **Redactar:** tabla (bajada, subida, latencia, estabilidad observada con pérdida de paquetes, rango de latencia y jitter) y análisis: banda de 5 GHz frente a 2,4 GHz (más capacidad frente a más alcance y más interferencia), Ethernet como referencia estable, latencia con carga (bufferbloat) cuando suba mucho. Señala valores atípicos (una primera prueba con latencia alta) en lugar de esconderlos.
7. **IoT desde la literatura** (no se mide): busca con `asistente-investigacion-cientifica:revision-sistematica` artículos comparativos de LPWAN (LoRaWAN, Sigfox, NB-IoT). Conclusión típica: la elección depende de la aplicación y de los compromisos entre desempeño, seguridad, escala, consumo y costo. Cita solo lo que respalda el resumen o el texto leído.

## Salida para el informe
Tabla (promedios), `figura1_velocidad.png`, los archivos `ping_*.txt` y `speedtest_*.json` como evidencia de los anexos, y el Anexo con la captura del resultado de speedtest.net (la que tome la usuaria o la que se genere de la web).

## Condiciones, repeticiones y figuras de análisis
- **Declara las condiciones de cada medición**: qué adaptadores estaban activos (si hay dos Wi-Fi conectados a la vez, dilo como limitación), servidor, fecha y hora. No escribas «una sola vía activa» si no fue cierto para todas las conexiones.
- Si la usuaria corre `ping -n 50 8.8.8.8 | Select-Object -Last 4` varias veces, esas corridas son datos reales: léelas con `mcp__terminal__read_terminal` y úsalas para mostrar la variabilidad (media y máximo por corrida). Confirma con ella en qué conexión se hicieron.
- **Figuras para «Resultados y análisis»:** `python -I "${CLAUDE_PLUGIN_ROOT}/skills/medicion-de-red/scripts/graficos_latencia_simulacion.py" --reales resultados.csv --simulados simulacion_redes.csv --ping "Etiqueta=archivo.txt" --salida "<carpeta>"` genera `figura2_latencia_paquetes.png` y `figura3_real_vs_simulado.png` (los perfiles simulados van rayados y rotulados).
- La latencia bajo carga (la que muestran speedtest.net o la CLI al bajar y subir) refleja el encolamiento del enlace; descríbela como «sugiere», no como causa comprobada.
- Para conexiones que no se pueden medir, usa `laboratorio-docker` (simulación rotulada).
