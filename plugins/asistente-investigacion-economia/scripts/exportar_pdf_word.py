# -*- coding: utf-8 -*-
"""Exporta un .docx a PDF con Word real (COM), resolviendo las rutas largas con tildes: trabaja en %TEMP%\\eco_pdf.
Imprime páginas totales, nº de ecuaciones nativas (OMath) e imágenes, y las páginas del cuerpo (de «Introducción» a «Referencias»).
    python -I exportar_pdf_word.py <archivo.docx> [<salida.pdf>] [--inicio "Introducci"] [--fin "Referencias bibliogr"]
Requiere Word instalado. Rasteriza miniaturas en %TEMP%\\eco_pdf\\p01.png… para revisar a ojo (--miniaturas).
"""
import os, shutil, subprocess, sys, tempfile
sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))


def opcion(args, nombre, defecto):
    if nombre in args:
        i = args.index(nombre); v = args[i + 1]; del args[i:i + 2]; return v
    return defecto


def main(args):
    inicio = opcion(args, "--inicio", "Introducci"); fin = opcion(args, "--fin", "Referencias bibliogr")
    mini = "--miniaturas" in args
    args = [a for a in args if a != "--miniaturas"]
    docx = os.path.abspath(args[0]); pdf = os.path.abspath(args[1]) if len(args) > 1 else os.path.splitext(docx)[0] + ".pdf"
    tmp = os.path.join(tempfile.gettempdir(), "eco_pdf"); os.makedirs(tmp, exist_ok=True)
    t_docx, t_pdf = os.path.join(tmp, "t.docx"), os.path.join(tmp, "t.pdf")
    for f in (t_docx, t_pdf):
        if os.path.exists(f):
            os.remove(f)
    shutil.copyfile(docx, t_docx)
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(AQUI, "exportar_pdf_word.ps1"), "-Docx", t_docx, "-Pdf", t_pdf],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout.strip());
    if r.returncode or not os.path.exists(t_pdf):
        print("ERROR al exportar con Word:", r.stderr.strip()[:500]); sys.exit(1)
    shutil.copyfile(t_pdf, pdf)
    try:
        import pymupdf
        d = pymupdf.open(t_pdf)
        ini = fi = None
        for i, p in enumerate(d):
            t = p.get_text().strip()
            if ini is None and t.startswith(inicio): ini = i + 1
            if t.startswith(fin): fi = i
            if mini: p.get_pixmap(dpi=55).save(os.path.join(tmp, f"p{i + 1:02d}.png"))
        if ini and fi is not None:
            print(f"Cuerpo (de «{inicio}» a «{fin}»): páginas {ini} a {fi} = {fi - ini + 1} páginas")
        print("Palabras por página:", [len(p.get_text().split()) for p in d])
    except ImportError:
        print("(instalar pymupdf para contar las páginas del cuerpo)")
    print("PDF:", pdf)


if __name__ == "__main__":
    main(sys.argv[1:])
