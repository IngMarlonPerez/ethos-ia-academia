# Exporta un .docx a PDF con Word (COM) y muestra el número de páginas.
# Uso (PowerShell, rutas absolutas y cortas):  .\docx_a_pdf.ps1 -In C:\w\out.docx -Out C:\w\out.pdf
# Desde bash, las barras invertidas se pierden: llamar con la herramienta PowerShell.
param([string]$In, [string]$Out)
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$d = $w.Documents.Open($In, $false, $true)
$d.Repaginate()
$n = $d.ComputeStatistics(2)
$d.ExportAsFixedFormat($Out, 17)
$d.Close($false); $w.Quit()
"páginas: $n"
