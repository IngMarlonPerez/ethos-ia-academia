# Abre el .docx con Word, cuenta páginas/ecuaciones y exporta a PDF
param([string]$Docx, [string]$Pdf)
$w = New-Object -ComObject Word.Application
$w.Visible = $false
try {
  $doc = $w.Documents.Open($Docx, $false, $true)
  $doc.Repaginate()
  "Paginas totales: " + $doc.ComputeStatistics(2)
  "Ecuaciones OMath: " + $doc.OMaths.Count
  "Imagenes inline: " + $doc.InlineShapes.Count
  $doc.ExportAsFixedFormat($Pdf, 17)
  $doc.Close($false)
} finally { $w.Quit() }
