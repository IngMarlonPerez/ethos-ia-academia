<#
simular_redes.ps1 — SIMULA conexiones de red con Docker (iperf3 + tc/netem) y las mide.

IMPORTANTE: esto es una SIMULACIÓN DE LABORATORIO, no una medición de una red real. Los
perfiles (velocidad, latencia, jitter, pérdida) son parámetros de referencia definidos por
quien hace la práctica. En el informe se rotula siempre como «simulación» y se declaran los
parámetros. Sirve para comparar tipos de conexión que no se pueden probar en la realidad
(datos móviles sin plan, red institucional estando en línea desde casa).

Cómo funciona: un contenedor servidor (iperf3 -s) y un contenedor cliente en una red
puente de Docker. Antes de cada perfil se aplica `tc qdisc ... netem` (retardo, jitter,
pérdida y límite de velocidad) en la salida de AMBOS contenedores: la del cliente da la
subida y la del servidor la bajada. El retardo de ida y vuelta (RTT) se reparte a la mitad
por sentido.

Uso:
  pwsh -File simular_redes.ps1 -Salida "C:\ruta\laboratorio" [-Repeticiones 3] [-Segundos 6]
Salida: simulacion_redes.csv (conexion,prueba,bajada_mbps,subida_mbps,ping_ms,perdida_pct)
        y simulacion_redes_log.txt con los comandos y su salida.
Requisitos: Docker Desktop en marcha. Construye la imagen practicas-ti/lab:1.0 si no existe.
#>
param(
  [Parameter(Mandatory)][string]$Salida,
  [int]$Repeticiones = 3,
  [int]$Segundos = 6
)
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force $Salida | Out-Null
$raiz = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$img = "practicas-ti/lab:1.0"
if (-not (docker images -q $img)) { docker build -t $img "$PSScriptRoot\..\docker" | Out-Null }

# Perfiles de referencia: bajada/subida en Mbit/s, RTT y jitter en ms, pérdida en %
$perfiles = [ordered]@{
  "Referencia (sin emulacion)"        = @{ down = 0;   up = 0;  rtt = 0;  jit = 0;  loss = 0 }
  "Datos moviles 4G (simulado)"       = @{ down = 40;  up = 15; rtt = 50; jit = 10; loss = 0.1 }
  "Red institucional (simulada)"      = @{ down = 100; up = 100; rtt = 8;  jit = 1;  loss = 0 }
}

$log = Join-Path $Salida "simulacion_redes_log.txt"
"Simulacion de redes con Docker - $(Get-Date -Format 'yyyy-MM-dd HH:mm')" | Set-Content $log -Encoding utf8
function Reg($t) { $t | Add-Content $log -Encoding utf8; $t }

docker rm -f lab-srv lab-cli 2>$null | Out-Null
docker network rm lab-net 2>$null | Out-Null
docker network create lab-net | Out-Null
docker run -d --name lab-srv --network lab-net --cap-add NET_ADMIN $img sh -c "iperf3 -s" | Out-Null
docker run -d --name lab-cli --network lab-net --cap-add NET_ADMIN $img | Out-Null
Start-Sleep 3

function Netem($cont, $rate, $delay, $jit, $loss) {
  docker exec $cont sh -c "tc qdisc del dev eth0 root 2>/dev/null; true" | Out-Null
  if ($rate -gt 0 -or $delay -gt 0 -or $loss -gt 0) {
    $cmd = "tc qdisc add dev eth0 root netem delay ${delay}ms ${jit}ms loss ${loss}%"
    if ($rate -gt 0) { $cmd += " rate ${rate}mbit" }
    docker exec $cont sh -c $cmd | Out-Null
    Reg "  [$cont] $cmd"
  }
}

$csv = Join-Path $Salida "simulacion_redes.csv"
"conexion,prueba,bajada_mbps,subida_mbps,ping_ms,perdida_pct" | Set-Content $csv -Encoding utf8
foreach ($nombre in $perfiles.Keys) {
  $p = $perfiles[$nombre]
  Reg ""; Reg "=== $nombre ==="
  Reg "  Parametros: bajada $($p.down) Mbit/s | subida $($p.up) Mbit/s | RTT $($p.rtt) ms | jitter $($p.jit) ms | perdida $($p.loss) %"
  Netem "lab-cli" $p.up ($p.rtt / 2) ($p.jit / 2) $p.loss    # sale del cliente: subida
  Netem "lab-srv" $p.down ($p.rtt / 2) ($p.jit / 2) $p.loss  # sale del servidor: bajada
  Start-Sleep 2
  for ($i = 1; $i -le $Repeticiones; $i++) {
    $up = (docker exec lab-cli iperf3 -c lab-srv -t $Segundos -J | ConvertFrom-Json).end.sum_received.bits_per_second / 1e6
    $dn = (docker exec lab-cli iperf3 -c lab-srv -t $Segundos -R -J | ConvertFrom-Json).end.sum_received.bits_per_second / 1e6
    $pg = docker exec lab-cli ping -c 30 -i 0.2 lab-srv
    $m = ($pg | Select-String "rtt min/avg/max").ToString()
    $avg = [double](($m -split "=")[1].Trim().Split("/")[1])
    $pl = [double](([regex]::Match(($pg | Out-String), "(\d+(\.\d+)?)% packet loss")).Groups[1].Value)
    $fila = "{0},{1},{2},{3},{4},{5}" -f $nombre, $i, [math]::Round($dn, 1), [math]::Round($up, 1), [math]::Round($avg, 1), $pl
    $fila | Add-Content $csv -Encoding utf8
    Reg ("  prueba {0}: bajada {1} Mbps | subida {2} Mbps | ping medio {3} ms | perdida ping {4} %" -f $i, [math]::Round($dn, 1), [math]::Round($up, 1), [math]::Round($avg, 1), $pl)
  }
}
docker rm -f lab-srv lab-cli | Out-Null
docker network rm lab-net | Out-Null
Reg ""; Reg "Listo: $csv"
