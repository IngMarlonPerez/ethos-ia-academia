# Actualiza la tabla de contenido y los campos de un .docx con Microsoft Word y exporta el PDF.
# Uso: powershell -ExecutionPolicy Bypass -File docx_a_pdf.ps1 -Docx "documento\Avance_2.docx"
# Si Word no está instalado, usa LibreOffice (soffice) y avisa que la tabla de contenido no se actualiza.
param([Parameter(Mandatory=$true)][string]$Docx)
$ruta = (Resolve-Path -LiteralPath $Docx).Path
$pdf = [System.IO.Path]::ChangeExtension($ruta, '.pdf')
try {
    $word = New-Object -ComObject Word.Application -ErrorAction Stop
} catch {
    $soffice = Get-Command soffice -ErrorAction SilentlyContinue
    if (-not $soffice) { $soffice = Get-Item "C:\Program Files\LibreOffice\program\soffice.exe" -ErrorAction SilentlyContinue }
    if (-not $soffice) { Write-Error "No hay Microsoft Word ni LibreOffice para exportar el PDF."; exit 1 }
    & $soffice.Source --headless --convert-to pdf --outdir (Split-Path $ruta) $ruta | Out-Null
    "AVISO: PDF exportado con LibreOffice; la tabla de contenido NO se actualizó (ábrelo en Word y pulsa F9)."
    "PDF: $pdf"
    exit 0
}
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($ruta, $false, $false)
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    $doc.Fields.Update() | Out-Null
    $doc.Save()
    $doc.SaveAs([ref]$pdf, [ref]17)
    "paginas: " + $doc.ComputeStatistics(2)
    $doc.Close([ref]$false)
    "PDF: $pdf"
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
