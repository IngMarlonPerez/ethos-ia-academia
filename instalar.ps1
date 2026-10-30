# Instalador de Ethos IA Academia para Windows.
# Uso (PowerShell, en la carpeta del repositorio):  powershell -ExecutionPolicy Bypass -File instalar.ps1
# Registra las metodologías y herramientas en el cliente de IA que elijas. No envía datos a ningún servidor:
# las claves quedan solo en este equipo, como variables de entorno del usuario.
param([ValidateSet('', 'claude-code', 'claude-desktop', 'otro')][string]$Cliente = '')

$ErrorActionPreference = 'Stop'
$raiz = $PSScriptRoot
$servidor = Join-Path $raiz 'servidor\ethos_academia_mcp.py'
$plugins = 'asistente-investigacion-cientifica', 'asistente-investigacion-economia', 'asesor-proyecto-titulacion-ti',
           'practicas-ti-unemi', 'creacion-de-empresa'

function Paso($t) { Write-Host "`n== $t" -ForegroundColor Cyan }

# 1. Python 3.10 o superior (el servidor solo usa la biblioteca estándar).
Paso 'Python'
$py = Get-Command python -ErrorAction SilentlyContinue
$version = if ($py) { & python -c 'import sys;print(sys.version_info>=(3,10))' 2>$null }
if ($version -ne 'True') {
    Write-Host 'Instalando Python 3.12 con winget...'
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')
}
& python --version
& python -m pip install --user --quiet python-docx openpyxl pypdf
Write-Host 'Bibliotecas de Word, Excel y PDF listas.'

# 2. Claves opcionales: Scopus (Elsevier) y correo de contacto para OpenAlex y Unpaywall.
Paso 'Claves (opcional, Enter para omitir)'
$clave = Read-Host 'Clave de la API de Elsevier/Scopus'
if ($clave) { [Environment]::SetEnvironmentVariable('SCOPUS_API_KEY', $clave, 'User') }
$correo = Read-Host 'Correo de contacto para OpenAlex/Unpaywall'
if ($correo) { [Environment]::SetEnvironmentVariable('CORREO_CONTACTO_INVESTIGACION', $correo, 'User') }

# 3. Cliente de IA.
if (-not $Cliente) {
    Paso 'Cliente de IA'
    Write-Host '1) Claude Code   2) Claude Desktop   3) Otro cliente MCP (Goose, Cline, Continue, OpenCode... con cualquier modelo)'
    $Cliente = @{ '1' = 'claude-code'; '2' = 'claude-desktop'; '3' = 'otro' }[(Read-Host 'Elige 1, 2 o 3')]
}

switch ($Cliente) {
    'claude-code' {
        Paso 'Claude Code: catálogo y plugins'
        claude plugin marketplace add $raiz
        foreach ($p in $plugins) { claude plugin install "$p@ethos-ia-academia" --scope user }
    }
    'claude-desktop' {
        Paso 'Claude Desktop: servidor MCP'
        $cfg = Join-Path $env:APPDATA 'Claude\claude_desktop_config.json'
        New-Item -ItemType Directory -Force (Split-Path $cfg) | Out-Null
        $datos = if (Test-Path $cfg) { Get-Content $cfg -Raw | ConvertFrom-Json -AsHashtable } else { @{} }
        if (-not $datos.mcpServers) { $datos.mcpServers = @{} }
        $datos.mcpServers['ethos-academia'] = @{ command = 'python'; args = @($servidor) }
        if (Test-Path $cfg) { Copy-Item $cfg "$cfg.respaldo" }
        $datos | ConvertTo-Json -Depth 10 | Set-Content $cfg -Encoding utf8
        Write-Host "Registrado en $cfg (respaldo en .respaldo). Reinicia Claude Desktop."
    }
    default {
        Paso 'Otro cliente MCP'
        Write-Host 'Agrega este servidor MCP (stdio) en la configuración de tu cliente:'
        @{ 'ethos-academia' = @{ command = 'python'; args = @($servidor) } } | ConvertTo-Json -Depth 5
        Write-Host 'Funciona con el modelo que tu cliente use: Claude, GPT, Gemini o uno local con Ollama.'
    }
}

Paso 'Listo'
Write-Host 'Prueba: pide a tu asistente «lista las metodologías de Ethos IA Academia».'
