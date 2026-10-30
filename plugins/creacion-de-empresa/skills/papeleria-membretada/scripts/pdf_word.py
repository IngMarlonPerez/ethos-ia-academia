"""Conversión de Word a PDF usando Word instalado (Windows).

Resuelve dos problemas reales:
  1. Word no abre rutas de más de 259 caracteres: cada archivo se copia a una carpeta temporal corta (con Python) y el PDF se copia de vuelta.
  2. Word puede colgarse sin error: cada conversión tiene tiempo límite y, si se agota, se mata esa instancia de Word y se reintenta una vez.

    from pdf_word import convertir, convertir_carpeta
    convertir("informe.docx")                       # genera informe.pdf junto al original
    convertir_carpeta("C:/ruta/carpeta")            # todos los .docx sin PDF actualizado (recursivo)

Línea de comandos:  python pdf_word.py <carpeta o archivo.docx>
"""
import os, shutil, subprocess, sys, tempfile, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
PS1 = os.path.join(HERE, "docx_a_pdf.ps1")


def _matar_word():
    subprocess.run(["taskkill", "/F", "/IM", "WINWORD.EXE"], capture_output=True)


def _intento(src, dst, timeout):
    r = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", PS1, "-in", src, "-out", dst],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    return r.returncode == 0 and os.path.exists(dst)


def convertir(docx, pdf=None, timeout=120):
    """Convierte un .docx a PDF. Devuelve la ruta del PDF. Lanza RuntimeError si Word no responde tras reintentar."""
    pdf = pdf or os.path.splitext(docx)[0] + ".pdf"
    tmp = os.path.join(tempfile.gettempdir(), "empresa_pdf")
    os.makedirs(tmp, exist_ok=True)
    uid = uuid.uuid4().hex[:8]
    src, dst = os.path.join(tmp, f"c{uid}.docx"), os.path.join(tmp, f"c{uid}.pdf")
    shutil.copyfile(docx, src)
    ok = False
    for _ in range(2):
        try:
            ok = _intento(src, dst, timeout)
        except subprocess.TimeoutExpired:
            ok = False
        if ok:
            break
        _matar_word()
    if not ok:
        raise RuntimeError(f"Word no pudo convertir {docx}")
    shutil.copyfile(dst, pdf)
    for f in (src, dst):
        try:
            os.remove(f)
        except OSError:
            pass
    return pdf


def convertir_carpeta(root, timeout=120):
    """Convierte todos los .docx de la carpeta (recursivo) cuyo PDF no existe o es más antiguo. Devuelve la lista de PDF creados."""
    hechos = []
    for dp, _, fs in os.walk(root):
        for f in sorted(fs):
            if f.lower().endswith(".docx") and not f.startswith("~$"):
                src = os.path.join(dp, f)
                pdf = os.path.splitext(src)[0] + ".pdf"
                if os.path.exists(pdf) and os.path.getmtime(pdf) > os.path.getmtime(src):
                    continue
                hechos.append(convertir(src, pdf, timeout))
    return hechos


if __name__ == "__main__":
    t = sys.argv[1]
    for p in (convertir_carpeta(t) if os.path.isdir(t) else [convertir(t)]):
        print("PDF:", p)
