---
name: laboratorio-docker
description: 'Simula con Docker lo que no se puede medir en el equipo: perfiles de red con iperf3 y netem, y cifrado LUKS. Usar si falta la conexión real o BitLocker, o se necesita evidencia reproducible.'
---

# Laboratorio con Docker (simulaciones rotuladas)

Docker Desktop corre una máquina virtual Linux (WSL2). Sirve para **simular** y **reproducir**. Una simulación NO es una medición real: en el informe se rotula siempre «simulación», se declaran los parámetros y no se mezcla con los datos medidos en la red de la usuaria.

## Cuándo usarla
- La guía pide un tipo de conexión que no se puede probar (datos móviles sin plan, red institucional estando en línea desde casa): se **simula el perfil** y se compara con las conexiones reales medidas.
- BitLocker no existe (Windows Home): se prueba **LUKS2** (dm-crypt, AES-XTS) en una VM Linux como el equivalente de cifrado de disco completo, y se aclara que no es BitLocker.
- Se necesita una evidencia reproducible (los scripts guardan el comando y su salida real).

## Pasos
1. Comprueba Docker: `docker version` (cliente y servidor). Si no responde, pide a la usuaria abrir Docker Desktop. **No toques las imágenes ni contenedores de otros proyectos**: esta skill usa solo `practicas-ti/lab:1.0`, `lab-srv`, `lab-cli` y `lab-net`.
2. **Redes:** `pwsh -File "${CLAUDE_PLUGIN_ROOT}/skills/laboratorio-docker/scripts/simular_redes.ps1" -Salida "<carpeta>\laboratorio\redes"` (unos 4 min; lánzalo en segundo plano y no lo mezcles con otras mediciones). Mide tres perfiles con iperf3 y ping: referencia sin emulación, datos móviles 4G y red institucional. Edita la tabla `$perfiles` del script para otros valores.
   - Los parámetros son **supuestos de referencia** de quien hace la práctica (velocidad, RTT, jitter, pérdida). Decláralos en el informe; no los presentes como datos de una operadora ni de la universidad.
   - La velocidad TCP depende del RTT y de la pérdida (efecto Mathis): una pérdida pequeña con RTT alto baja mucho el rendimiento aunque el enlace tenga capacidad. Es un resultado para el análisis.
3. **Cifrado de disco completo:** `pwsh -File "${CLAUDE_PLUGIN_ROOT}/skills/laboratorio-docker/scripts/probar_luks.ps1" -Salida "<carpeta>\laboratorio\luks"`. Crea una imagen de 100 MB dentro del contenedor, la cifra con LUKS2, la formatea, escribe un archivo, comprueba que una clave incorrecta se rechaza y que la correcta recupera el mismo hash. Usa `--privileged` solo dentro de la VM desechable; no toca los discos de Windows.
   - Si el kernel de WSL2 no trae dm-crypt y falla, dilo con el error real y no lo inventes.
4. **Evidencias:** convierte `simulacion_redes_log.txt`, `luks_log.txt` y los CSV en imágenes de consola con `evidencias-capturas` (rotuladas «salida real de Docker») y en gráficos con `medicion-de-red/scripts/graficos_red.py`.
5. Al terminar, `docker rm -f lab-srv lab-cli` y `docker network rm lab-net` (los scripts ya lo hacen).

## En el informe
- Tabla separada (o filas con la etiqueta «(simulado)») para los perfiles simulados, con los parámetros en la nota.
- Frase de límite: «Los perfiles son supuestos de laboratorio; no representan mediciones de una operadora ni de la red institucional».
- Para LUKS: «equivalente abierto de BitLocker; BitLocker no está disponible en Windows Home».
