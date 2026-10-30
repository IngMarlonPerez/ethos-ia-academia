<#
pipeline.ps1 — reconstruye y valida el prototipo de punta a punta, en orden.
Cada paso se detiene si el anterior falló. Es la base de la demo y de las
cifras del documento: el generador del Word SOLO lee los artefactos que deja
este pipeline (metrics.json, resultados de evaluación, figuras).

Copia este archivo a scripts/pipeline.ps1 del repositorio y reemplaza los pasos.

Uso (desde la raíz del repositorio):
  powershell -ExecutionPolicy Bypass -File scripts\pipeline.ps1 [-ConEvaluacion] [-Levantar]

Credenciales: se leen de un .env que NO está en el repositorio. Este script no
contiene ni pide contraseñas.
#>
param(
    [switch]$ConEvaluacion,   # pasos lentos o que consumen cuota de servicios externos
    [switch]$Levantar         # abre backend y frontend para la demo en vivo
)
$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $PSScriptRoot
$py = Join-Path $raiz 'backend\venv\Scripts\python.exe'     # ← ajustar
$env:PYTHONIOENCODING = 'utf-8'
$inicio = Get-Date

function Paso([string]$titulo, [scriptblock]$accion) {
    Write-Host ''
    Write-Host "== $titulo" -ForegroundColor Cyan
    & $accion
    if ($LASTEXITCODE -ne 0) { throw "Falló el paso: $titulo (código $LASTEXITCODE)" }
}

if (-not (Test-Path $py)) { throw "No existe $py. Crea el entorno virtual e instala requirements.txt" }

Push-Location $raiz
try {
    Paso '1. Base de datos disponible'          { docker start mi-base | Out-Null }        # ← ajustar
    Paso '2. Datos de prueba (anonimizados)'    { & $py scripts\cargar_datos.py }          # ← ajustar
    Paso '3. Esquema y vistas'                  { & $py scripts\crear_esquema.py }
    Paso '4. ETL'                               { & $py scripts\etl.py }
    Paso '5. Entrenar y evaluar (escribe metrics.json)' { & $py ml\entrenar.py }
    Paso '6. Figuras de resultados'             { & $py ml\reporte_validacion.py }
    Paso '7. Diccionario de datos'              { & $py scripts\diccionario.py }
    if ($ConEvaluacion) {
        Paso '8. Evaluación con el conjunto dorado' { & $py eval\evaluar.py }
    }
    Paso '9. Pruebas automatizadas'             { & $py -m pytest -q }
}
finally { Pop-Location }

$min = [math]::Round(((Get-Date) - $inicio).TotalMinutes, 1)
Write-Host "`nPipeline completo en $min min. Siguiente: generar el documento y verificar la coherencia." -ForegroundColor Green
if ($Levantar) {
    Start-Process powershell -ArgumentList '-NoExit', '-Command', "cd '$raiz'; npm run dev:backend"   # ← ajustar
    Start-Process powershell -ArgumentList '-NoExit', '-Command', "cd '$raiz'; npm run dev"
}
