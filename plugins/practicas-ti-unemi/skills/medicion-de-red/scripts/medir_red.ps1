<#
medir_red.ps1 — mide UNA conexión de la propia computadora y añade las filas a resultados.csv.

Hace: datos del adaptador (banda, señal, velocidad de vínculo), ping de N paquetes
(pérdida, mínimo, máximo, media) y K pruebas de Speedtest (bajada, subida, latencia,
jitter, pérdida). NO escanea otras computadoras ni puertos: solo mide la conexión de
quien ejecuta el script.

Uso:
  pwsh -File medir_red.ps1 -Conexion "Wi-Fi 5 GHz" -Salida "C:\ruta\medicion" [-Pruebas 3] [-Pings 50] [-Servidor 74242]

Requisitos: speedtest (winget install Ookla.Speedtest.CLI). Se acepta la licencia con
--accept-license --accept-gdpr (es del uso personal no comercial).
#>
param(
  [Parameter(Mandatory)][string]$Conexion,
  [Parameter(Mandatory)][string]$Salida,
  [int]$Pruebas = 3,
  [int]$Pings = 50,
  [string]$Destino = "8.8.8.8",
  [string]$Servidor = ""
)
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force $Salida | Out-Null
$etq = ($Conexion -replace '[^\w]+','_')

# --- speedtest.exe (en PATH o en el paquete de winget)
$exe = (Get-Command speedtest -ErrorAction SilentlyContinue).Source
if (-not $exe) {
  $exe = (Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter speedtest.exe -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
}
if (-not $exe) { throw "No está speedtest. Instala: winget install Ookla.Speedtest.CLI" }

# --- adaptador (sin MAC ni nombre de la red: son datos privados)
"--- Adaptadores Wi-Fi (sin SSID ni MAC) ---"
netsh wlan show interfaces | Select-String "Nombre|Estado|Banda|Canal|Tipo de radio|Señal|Rssi|recepción" |
  Where-Object { $_ -notmatch "BSSID" } | ForEach-Object { $_.ToString().Trim() } | Tee-Object "$Salida\adaptador_$etq.txt"
Get-NetAdapter | Select-Object Name, Status, LinkSpeed | Format-Table -AutoSize | Out-String

# --- ping
"--- Ping ($Pings paquetes a $Destino) ---"
ping -n $Pings $Destino | Out-File "$Salida\ping_$etq.txt" -Encoding utf8
Get-Content "$Salida\ping_$etq.txt" -Tail 4

# --- speedtest
$csv = Join-Path $Salida "resultados.csv"
if (-not (Test-Path $csv)) { "conexion,prueba,bajada_mbps,subida_mbps,ping_ms" | Out-File $csv -Encoding utf8 }
$args0 = @("--accept-license","--accept-gdpr","-f","json","-p","no")
if ($Servidor) { $args0 = @("-s",$Servidor) + $args0 }
for ($i = 1; $i -le $Pruebas; $i++) {
  & $exe @args0 | Out-File "$Salida\speedtest_${etq}_$i.json" -Encoding utf8
  $j = Get-Content "$Salida\speedtest_${etq}_$i.json" -Raw | ConvertFrom-Json
  $down = [math]::Round($j.download.bandwidth * 8 / 1e6, 1)
  $up   = [math]::Round($j.upload.bandwidth * 8 / 1e6, 1)
  $png  = [math]::Round($j.ping.latency, 1)
  "{0},{1},{2},{3},{4}" -f $Conexion, $i, $down, $up, $png | Add-Content $csv -Encoding utf8
  "Prueba {0}: bajada {1} Mbps | subida {2} Mbps | ping {3} ms | jitter {4} ms | pérdida {5} %" -f $i, $down, $up, $png, [math]::Round($j.ping.jitter,1), $j.packetLoss
  if ($i -lt $Pruebas) { Start-Sleep 5 }
}
"Listo. Filas añadidas a $csv"
