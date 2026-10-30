<#
html_a_png.ps1 — convierte una página HTML (local o web) en PNG con Chrome o Edge sin ventana.
Sirve para evidencias reproducibles: transcripciones, salidas de consola, páginas públicas.

Uso:
  pwsh -File html_a_png.ps1 -Origen "C:\ruta\pagina.html" -Png "C:\ruta\captura.png" [-Ancho 1100] [-Alto 1000]
  pwsh -File html_a_png.ps1 -Origen "https://www.shopify.com/pricing" -Png "...\shopify.png"

Notas:
- Amazon y algunos sitios bloquean el navegador sin ventana: si no aparece el PNG, pide a la
  usuaria su captura (Win+Shift+S) o usa el navegador del panel de Claude solo para LEER la página.
- Para páginas web NO inicies sesión ni crees cuentas.
#>
param(
  [Parameter(Mandatory)][string]$Origen,
  [Parameter(Mandatory)][string]$Png,
  [int]$Ancho = 1100,
  [int]$Alto = 1000,
  [int]$TiempoMs = 15000
)
$nav = @("C:\Program Files\Google\Chrome\Application\chrome.exe",
         "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
         "C:\Program Files\Microsoft\Edge\Application\msedge.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $nav) { throw "No hay Chrome ni Edge instalados." }
if ($Origen -notmatch '^https?://' -and $Origen -notmatch '^file:') {
  $Origen = "file:///" + ((Resolve-Path $Origen).Path -replace '\\','/' -replace ' ','%20')
}
New-Item -ItemType Directory -Force (Split-Path $Png) | Out-Null
$perfil = Join-Path $env:TEMP ("cap_" + [guid]::NewGuid().ToString("N").Substring(0,8))
$p = Start-Process $nav -PassThru -ArgumentList "--headless=new","--disable-gpu","--hide-scrollbars","--user-data-dir=`"$perfil`"","--window-size=$Ancho,$Alto","--virtual-time-budget=$TiempoMs","--screenshot=`"$Png`"","`"$Origen`""
if (-not $p.WaitForExit(120000)) { $p.Kill() }
if (Test-Path $Png) { "Captura: $Png" } else { Write-Warning "No se generó la captura (el sitio puede bloquear el navegador sin ventana)." }
