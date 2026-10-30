<#
probar_cifrado.ps1 — prueba de cifrado con VeraCrypt (contenedor) y 7-Zip (AES-256) y
estado de Microsoft Defender. Todo con ARCHIVOS DE PRUEBA, nunca con datos reales.

No cambia ninguna configuración de seguridad de Windows (no toca BitLocker, ni
Cifrado de dispositivo, ni Defender): solo crea archivos en -Salida, mide tiempos y
lee el estado de Defender.

La contraseña de prueba se genera al azar y se guarda en LEEME_prueba.txt dentro de
-Salida. NO la imprime en pantalla ni la repitas en el chat.

Uso:
  pwsh -File probar_cifrado.ps1 -Salida "C:\ruta\anexoC" [-TamanoContenedorMB 100] [-TamanoArchivoMB 50]
Salida: resultados_cifrado.json con tiempos y estados.
#>
param(
  [Parameter(Mandatory)][string]$Salida,
  [int]$TamanoContenedorMB = 100,
  [int]$TamanoArchivoMB = 50
)
New-Item -ItemType Directory -Force $Salida | Out-Null
$res = [ordered]@{ fecha = (Get-Date -Format "yyyy-MM-dd HH:mm") }

# --- edición de Windows (BitLocker solo en Pro/Enterprise/Education)
$os = Get-CimInstance Win32_OperatingSystem
$res.windows = $os.Caption
$res.bitlocker_disponible = ($os.Caption -notmatch "Home")
"Windows: $($os.Caption) | BitLocker disponible: $($res.bitlocker_disponible)"

# --- contraseña de prueba
$pw = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object { [char]$_ })
Set-Content "$Salida\LEEME_prueba.txt" "Contenedor de prueba (sin datos reales). Contrasena: $pw"

# --- VeraCrypt
$vc = "C:\Program Files\VeraCrypt"
if (Test-Path "$vc\VeraCrypt Format.exe") {
  $cont = "$Salida\prueba_veracrypt.hc"
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $p = Start-Process "$vc\VeraCrypt Format.exe" -PassThru -ArgumentList "/create `"$cont`" /password $pw /hash sha512 /encryption AES /filesystem NTFS /size ${TamanoContenedorMB}M /force /silent"
  $p.WaitForExit(300000) | Out-Null
  $sw.Stop()
  $res.veracrypt = [ordered]@{
    version = (Get-Item "$vc\VeraCrypt.exe").VersionInfo.ProductVersion
    cifrado = "AES"; hash = "SHA-512"; sistema = "NTFS"; tamano_mb = $TamanoContenedorMB
    tiempo_creacion_s = [math]::Round($sw.Elapsed.TotalSeconds, 1)
    archivo_creado = (Test-Path $cont)
  }
  # Montaje de verificación (puede pedir permisos; si falla, se anota)
  $m = Start-Process "$vc\VeraCrypt.exe" -ArgumentList "/q /s /v `"$cont`" /l Y /p $pw" -PassThru -Wait
  Start-Sleep 3
  $res.veracrypt.montaje_ok = ($m.ExitCode -eq 0 -and (Test-Path "Y:\"))
  Start-Process "$vc\VeraCrypt.exe" -ArgumentList "/q /s /d Y" -Wait
  "VeraCrypt: $($res.veracrypt.tiempo_creacion_s) s, montaje ok: $($res.veracrypt.montaje_ok)"
} else { $res.veracrypt = "No instalado (winget install IDRIX.VeraCrypt)"; "VeraCrypt no está instalado." }

# --- 7-Zip (AES-256 con nombres cifrados)
$z = @("C:\Program Files\7-Zip\7z.exe", "C:\Program Files (x86)\7-Zip\7z.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($z) {
  $src = "$Salida\datos_prueba"; New-Item -ItemType Directory -Force $src | Out-Null
  $buf = New-Object byte[] ($TamanoArchivoMB * 1MB); (New-Object Random 42).NextBytes($buf)
  [IO.File]::WriteAllBytes("$src\archivo_prueba.bin", $buf)
  $dest = "$Salida\prueba_7zip.7z"
  $sw = [Diagnostics.Stopwatch]::StartNew()
  & $z a -t7z -p"$pw" -mhe=on -mx=1 $dest "$src\archivo_prueba.bin" | Out-Null
  $sw.Stop()
  $mala = (& $z t $dest -p"incorrecta" 2>&1 | Out-String) -match "Wrong password"
  $buena = (& $z t $dest -p"$pw" 2>&1 | Out-String) -match "Everything is Ok"
  $res.sevenzip = [ordered]@{
    metodo = "7zAES (AES-256)"; tamano_mb = $TamanoArchivoMB
    tiempo_cifrado_s = [math]::Round($sw.Elapsed.TotalSeconds, 1)
    rechaza_clave_incorrecta = $mala; abre_con_clave_correcta = $buena
  }
  "7-Zip: $($res.sevenzip.tiempo_cifrado_s) s | rechaza incorrecta: $mala | abre con correcta: $buena"
} else { $res.sevenzip = "No instalado"; "7-Zip no está instalado." }

# --- Defender (solo lectura)
try {
  $s = Get-MpComputerStatus
  $res.defender = [ordered]@{
    version_producto = $s.AMProductVersion; firmas = $s.AntivirusSignatureVersion
    firmas_actualizadas = "$($s.AntivirusSignatureLastUpdated)"
    proteccion_tiempo_real = $s.RealTimeProtectionEnabled
    ultimo_examen_rapido_inicio = "$($s.QuickScanStartTime)"; ultimo_examen_rapido_fin = "$($s.QuickScanEndTime)"
    detecciones_en_historial = @(Get-MpThreatDetection).Count
  }
  "Defender: tiempo real $($s.RealTimeProtectionEnabled) | detecciones $($res.defender.detecciones_en_historial)"
} catch { $res.defender = "No se pudo leer: $($_.Exception.Message)" }

$res | ConvertTo-Json -Depth 5 | Set-Content "$Salida\resultados_cifrado.json" -Encoding utf8
"Resultados: $Salida\resultados_cifrado.json"
