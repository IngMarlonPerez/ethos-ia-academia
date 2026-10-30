---
name: seguridad-cifrado-antivirus
description: 'Prueba cifrado (VeraCrypt, 7-Zip), Defender y EICAR con archivos de prueba; BitLocker no existe en Windows Home. Usar para «virus, criptografía y respaldo».'
---

# Virus, criptografía y respaldo

## Límites
- **Archivos de prueba, nunca datos reales.** No uses la memoria USB de la usuaria para cifrar (puede ser un USB de arranque, p. ej. HBCD_PE).
- **No cambies la seguridad del equipo:** no actives BitLocker ni «Cifrado de dispositivo», no apagues Defender, no pulses «Confiar» en VS Code. Es decisión de la usuaria.
- **BitLocker:** solo en Windows Pro, Enterprise y Education. En **Home** no existe: no se «instala» por comando; habría que comprar la actualización a Pro. Se documenta como limitación con evidencia: (a) menú contextual de una unidad sin «Activar BitLocker», (b) la página de funciones Home/Pro de Microsoft Store donde BitLocker solo figura en Pro, (c) `Get-CimInstance Win32_OperatingSystem` con el nombre de la edición. `manage-bde -status` exige administrador.
- Las contraseñas de prueba se generan al azar y se guardan en `LEEME_prueba.txt`; no se escriben en el chat.

## Pasos
1. **Instalar** (el instalador pide permisos de administrador y los acepta la usuaria): `winget install IDRIX.VeraCrypt`. 7-Zip suele estar instalado.
2. **Correr la prueba:** `pwsh -File "${CLAUDE_PLUGIN_ROOT}/skills/seguridad-cifrado-antivirus/scripts/probar_cifrado.ps1" -Salida "<carpeta>\anexos\anexoC"`.
   Genera `resultados_cifrado.json`: edición de Windows, VeraCrypt (AES + SHA-512, NTFS, tiempo de creación y montaje de verificación), 7-Zip (método 7zAES/AES-256, tiempo, rechazo de contraseña incorrecta) y Defender (versión, firmas, protección en tiempo real, último examen rápido, detecciones).
   - Los tiempos de VeraCrypt (volumen) y 7-Zip (archivo) **no son directamente comparables** (distinto tamaño y tipo): dilo en el texto.
3. **Examen rápido de Defender** (opcional, tarda unos 30 minutos): `Start-MpScan -ScanType QuickScan` en segundo plano; el resultado se lee con `Get-MpComputerStatus` (inicio y fin) y `Get-MpThreatDetection` (detecciones). Si la usuaria quiere evidencia gráfica, que tome captura de «Seguridad de Windows» (Inicio y Protección contra virus y amenazas).
4. **Prueba EICAR** (opcional): archivo de texto estándar e inofensivo que todo antivirus detecta a propósito; demuestra que la protección responde. Se crea en el Escritorio, Defender avisa y lo pone en cuarentena; se documenta con el Historial de protección y se elimina de la cuarentena después.
5. **Respaldo:** si la guía lo pide, prueba una herramienta (Historial de archivos de Windows, copia con `robocopy`, 7-Zip) y anota método, tiempo y facilidad. Si no se probó, la celda queda resaltada.
6. **Literatura:** busca con `asistente-investigacion-cientifica:revision-sistematica` (p. ej. evaluación de antivirus con VirusTotal; fallo de cifrado en dispositivos portátiles). Marchetto (2026) y da Costa et al. (2026) sirvieron de contexto de riesgo: el antivirus puede no detectar todo y el cifrado solo protege si se aplica.

## Salida
Tabla comparativa (herramienta, hallazgo de la literatura, registro propio) con el tiempo, el método, la facilidad de uso (pasos, idioma de la interfaz) y la protección; evidencias del Anexo C. Borra o avisa de los archivos `.hc` de prueba (100 MB).

## Complementos
- **Cifrado de disco completo sin BitLocker:** `laboratorio-docker/scripts/probar_luks.ps1` (LUKS2 en una VM Linux). Se rotula como equivalente abierto, no como BitLocker.
- **Respaldo medible:** crea archivos de prueba, respalda con `robocopy`, compara SHA-256 de origen y respaldo, «pierde» un archivo moviéndolo a una carpeta de prueba (no lo borres) y restáuralo comparando hashes. Guarda la salida en un `.txt` y conviértela con `evidencias-capturas/scripts/render_consola.py`.
- **No generalices pruebas:** «una clave incorrecta se rechaza» solo para las herramientas en que se probó (7-Zip y LUKS2 sí; en VeraCrypt solo se montó con la contraseña correcta salvo que se pruebe).
- El examen rápido de Defender de la usuaria (captura de Seguridad de Windows) y el lanzado por PowerShell son dos datos distintos: cita cada uno con su fecha y duración.
- Una instalación con `winget` (VeraCrypt) también es evidencia: transcríbela desde la terminal de la sesión.
