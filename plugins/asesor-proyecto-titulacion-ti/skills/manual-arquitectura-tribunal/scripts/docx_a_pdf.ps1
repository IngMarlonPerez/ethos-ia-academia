# Convierte un .docx a PDF con Microsoft Word (COM). LibreOffice no se usa: altera tablas e imágenes.
# Uso: powershell -ExecutionPolicy Bypass -File docx_a_pdf.ps1 -Docx <archivo.docx> [-Pdf <archivo.pdf>]
param([Parameter(Mandatory = $true)][string]$Docx, [string]$Pdf)
$Docx = (Resolve-Path $Docx).Path
if (-not $Pdf) { $Pdf = [IO.Path]::ChangeExtension($Docx, '.pdf') }
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($Docx)
    $doc.SaveAs2($Pdf, 17)   # 17 = wdFormatPDF
    $doc.Close($false)
    Write-Output "PDF: $Pdf"
} finally {
    $word.Quit()
}
