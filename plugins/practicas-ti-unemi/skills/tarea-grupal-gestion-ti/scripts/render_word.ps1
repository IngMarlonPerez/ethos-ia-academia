# Uso: powershell -NoProfile -File render_word.ps1 "C:\ruta\documento.docx"
# Exporta a PDF con Word (COM) junto al .docx e imprime nº de páginas y la página donde empieza «Bibliografía».
param([Parameter(Mandatory=$true)][string]$Docx)
$Docx = (Resolve-Path $Docx).Path
$Pdf  = [System.IO.Path]::ChangeExtension($Docx, ".pdf")
$w = New-Object -ComObject Word.Application; $w.Visible = $false
try {
  $d = $w.Documents.Open($Docx, $false, $true)
  $d.ExportAsFixedFormat($Pdf, 17)
  "pages: " + $d.ComputeStatistics(2)
  foreach ($p in $d.Paragraphs) { if ($p.Range.Text -like "Bibliograf*") { "bib page: " + $p.Range.Information(3); break } }
  $d.Close($false)
} catch { $_.Exception.Message } finally { $w.Quit() }
