# Convierte UN .docx a PDF con Word (abrir, exportar, cerrar). Uso:
#   powershell -NoProfile -ExecutionPolicy Bypass -File docx_a_pdf.ps1 -in "a.docx" -out "a.pdf"
# Para rutas largas y para lotes usar pdf_word.py (copia a una ruta corta, aplica tiempo límite y mata Word si se cuelga).
param([string]$in, [string]$out)
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
  $d = $w.Documents.Open($in, $false, $true)
  if ($null -eq $d) { throw "Word no pudo abrir el documento" }
  $d.ExportAsFixedFormat($out, 17)
  $d.Close($false)
} finally { $w.Quit() }
