# -*- coding: utf-8 -*-
"""
render.py — convierte PPTX a PDF/PNG/SVG sin depender de herramientas de Linux.

Orden de preferencia:
  PPTX → PDF : LibreOffice (soffice) si existe; si no, Microsoft PowerPoint por COM (Windows).
  PDF  → PNG : PyMuPDF; si no, pdftoppm.
  PDF  → SVG : PyMuPDF; si no, pdftocairo.

Así el módulo funciona en el Windows de la usuaria (con Office) y en un entorno Linux con LibreOffice.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_SOFFICE_COMUN = [
    r'C:\Program Files\LibreOffice\program\soffice.exe',
    r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
    '/Applications/LibreOffice.app/Contents/MacOS/soffice',
]


def _pymupdf():
    try:
        import pymupdf
        return pymupdf
    except ImportError:
        try:
            import fitz
            return fitz
        except ImportError:
            return None


def buscar_soffice() -> str | None:
    return shutil.which('soffice') or next((r for r in _SOFFICE_COMUN if os.path.exists(r)), None)


def _powerpoint_a_pdf(pptx: str, pdf: str) -> None:
    """Exporta con PowerPoint (COM). ppSaveAsPDF = 32. Requiere Microsoft PowerPoint en Windows."""
    guion = (
        "$ErrorActionPreference='Stop'\n"
        "$app = New-Object -ComObject PowerPoint.Application\n"
        "try {\n"
        f"  $p = $app.Presentations.Open('{pptx}', $true, $true, $false)\n"
        f"  $p.SaveAs('{pdf}', 32)\n"
        "  $p.Close()\n"
        "} finally { $app.Quit() }\n"
    )
    with tempfile.NamedTemporaryFile('w', suffix='.ps1', delete=False, encoding='utf-8-sig') as f:
        f.write(guion)
        ps1 = f.name
    try:
        r = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps1],
                           capture_output=True, text=True, timeout=600)
    finally:
        os.unlink(ps1)
    if r.returncode != 0 or not os.path.exists(pdf):
        raise RuntimeError(f'PowerPoint no pudo exportar a PDF: {r.stderr.strip() or r.stdout.strip()}')


def pptx_a_pdf(pptx: str, outdir: str | None = None) -> str:
    """Devuelve la ruta del PDF. Lanza RuntimeError si no hay LibreOffice ni PowerPoint."""
    pptx = os.path.abspath(pptx)
    outdir = os.path.abspath(outdir or tempfile.mkdtemp(prefix='render_'))
    os.makedirs(outdir, exist_ok=True)
    pdf = os.path.join(outdir, Path(pptx).stem + '.pdf')
    soffice = buscar_soffice()
    if soffice:
        subprocess.run([soffice, '--headless', '--convert-to', 'pdf', '--outdir', outdir, pptx], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
        return pdf
    if sys.platform == 'win32':
        _powerpoint_a_pdf(pptx, pdf)
        return pdf
    raise RuntimeError('No hay LibreOffice (soffice) ni PowerPoint para exportar a PDF. Instala LibreOffice o usa Windows con Office.')


def pdf_a_png(pdf: str, salida: str, pagina: int = 1, dpi: int = 300) -> str:
    mu = _pymupdf()
    if mu:
        doc = mu.open(pdf)
        try:
            doc[pagina - 1].get_pixmap(dpi=dpi).save(salida)
        finally:
            doc.close()
        return salida
    base = salida[:-4] if salida.lower().endswith('.png') else salida
    subprocess.run(['pdftoppm', '-f', str(pagina), '-l', str(pagina), '-r', str(dpi), '-png', '-singlefile', pdf, base], check=True)
    return base + '.png'


def pdf_a_svg(pdf: str, salida: str, pagina: int = 1) -> str:
    mu = _pymupdf()
    if mu:
        doc = mu.open(pdf)
        try:
            Path(salida).write_text(doc[pagina - 1].get_svg_image(), encoding='utf-8')
        finally:
            doc.close()
        return salida
    subprocess.run(['pdftocairo', '-svg', '-f', str(pagina), '-l', str(pagina), pdf, salida], check=True)
    return salida


def num_paginas(pdf: str) -> int:
    mu = _pymupdf()
    if not mu:
        raise RuntimeError('Falta PyMuPDF (pip install pymupdf).')
    doc = mu.open(pdf)
    try:
        return doc.page_count
    finally:
        doc.close()


def hoja_contactos(pdf: str, salida: str, columnas: int = 6, dpi: int = 30) -> str | None:
    """Miniaturas de todas las páginas en una sola imagen, para revisar la maquetación de un vistazo."""
    from PIL import Image, ImageDraw
    mu = _pymupdf()
    if not mu:
        raise RuntimeError('Falta PyMuPDF (pip install pymupdf).')
    doc = mu.open(pdf)
    try:
        ims = []
        for pag in doc:
            pix = pag.get_pixmap(dpi=dpi)
            ims.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
    finally:
        doc.close()
    if not ims:
        return None
    w, h = ims[0].size
    filas = (len(ims) + columnas - 1) // columnas
    hoja = Image.new('RGB', (columnas * (w + 10) + 10, filas * (h + 24) + 10), 'white')
    dr = ImageDraw.Draw(hoja)
    for k, im in enumerate(ims):
        x, y = 10 + (k % columnas) * (w + 10), 10 + (k // columnas) * (h + 24)
        hoja.paste(im, (x, y + 14))
        dr.rectangle([x - 1, y + 13, x + w, y + 14 + h], outline='#999999')
        dr.text((x, y), str(k + 1), fill='black')
    hoja.save(salida)
    return salida
