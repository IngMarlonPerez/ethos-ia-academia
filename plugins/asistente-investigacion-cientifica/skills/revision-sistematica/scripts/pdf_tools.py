"""Herramientas para conseguir, leer y citar artículos científicos.

Uso desde la terminal (Python 3 con pypdf; `pip install pypdf` si falta):

  python pdf_tools.py oa DOI1 DOI2 ...
      Busca en OpenAlex las copias de acceso abierto de cada DOI (PDF de la editorial o de repositorios).

  python pdf_tools.py bajar URL salida.pdf
      Descarga con cabeceras de navegador y verifica que el archivo empiece con %PDF.
      Si falla (403, HTML, Cloudflare), hay que descargarlo desde el Browser pane con fetch + base64
      (ver SKILL.md, paso 5).

  python pdf_tools.py texto carpeta_pdfs carpeta_salida
      Extrae el texto de cada PDF con marcas [[PAG n]] (n = página del PDF) y además genera
      *_lectura.txt con introducción + marco teórico + discusión/conclusiones, sin métodos ni referencias.

  python pdf_tools.py pagina archivo.pdf "frase exacta a buscar"
      Devuelve en qué página del PDF aparece la frase. Para APA use la paginación de la revista
      (encabezado o pie de página), no la del visor.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"


def oa(dois):
    for doi in dois:
        try:
            url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/():.")
            w = json.load(urllib.request.urlopen(url, timeout=30))
            pdfs = [l.get("pdf_url") for l in w.get("locations", []) if l.get("pdf_url")]
            print(f"{doi}\n   OA={w['open_access']['is_oa']} ({w['open_access']['oa_status']})  PDF={pdfs[:3]}"
                  f"\n   landing={w['open_access'].get('oa_url')}")
        except Exception as e:
            print(f"{doi}\n   ERROR {e}")
        time.sleep(0.3)


def bajar(url, salida):
    r = subprocess.run(["curl", "-sL", "-A", UA, "-o", salida, "-w", "%{http_code}", url], capture_output=True, text=True)
    ok = os.path.exists(salida) and open(salida, "rb").read(4) == b"%PDF"
    if not ok and os.path.exists(salida):
        os.remove(salida)
    print(f"{'OK' if ok else 'FALLÓ'} HTTP {r.stdout} -> {salida}")
    return ok


def _limpiar(t):
    t = re.sub(r"-\n(?=[a-z])", "", t)
    return re.sub(r"[ \t]+", " ", t)


def texto(carpeta, salida):
    import logging
    import pypdf
    logging.disable(logging.WARNING)
    os.makedirs(salida, exist_ok=True)
    for f in sorted(os.listdir(carpeta)):
        if not f.lower().endswith(".pdf"):
            continue
        r = pypdf.PdfReader(os.path.join(carpeta, f))
        t = _limpiar("\n".join(f"\n[[PAG {i + 1}]]\n" + (p.extract_text() or "") for i, p in enumerate(r.pages)))
        base = os.path.splitext(f)[0]
        open(os.path.join(salida, base + ".txt"), "w", encoding="utf-8").write(t)
        refs = [m.start() for m in re.finditer(r"\n\s*(References|REFERENCES|Bibliography|Referencias)\s*\n", t)]
        cuerpo = t[:refs[-1]] if refs else t
        m = re.search(r"\n\s*(\d\.?\s*)?(Research )?(Methodology|Methods?|Research [Dd]esign|Data and [Mm]ethods?|"
                      r"Materials and [Mm]ethods|METHODS?|METHODOLOGY|MATERIAL)\b", cuerpo[len(cuerpo) // 6:])
        corte1 = len(cuerpo) // 6 + m.start() if m else int(len(cuerpo) * 0.35)
        conc = [x.start() for x in re.finditer(r"\n\s*(\d\.?\s*)?(Conclusions?|CONCLUSIONS?|Discussion|DISCUSSION|"
                                                r"Concluding [Rr]emarks|Considerations)\b", cuerpo)]
        corte2 = conc[-1] if conc and conc[-1] > corte1 else int(len(cuerpo) * 0.85)
        lectura = cuerpo[:corte1] + "\n\n[... MÉTODO Y RESULTADOS OMITIDOS ...]\n\n" + cuerpo[corte2:]
        open(os.path.join(salida, base + "_lectura.txt"), "w", encoding="utf-8").write(lectura)
        print(f"{f}: {len(r.pages)} págs · texto {len(t):,} · lectura {len(lectura):,} caracteres")


def pagina(pdf, frase):
    import logging
    import pypdf
    logging.disable(logging.WARNING)
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    objetivo = norm(frase)[:45]
    r = pypdf.PdfReader(pdf)
    hits = [i + 1 for i, p in enumerate(r.pages) if objetivo in norm(p.extract_text() or "")]
    print(f"Páginas del PDF: {hits or 'no encontrada'}")
    return hits


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    {"oa": lambda: oa(args), "bajar": lambda: bajar(*args), "texto": lambda: texto(*args),
     "pagina": lambda: pagina(*args)}.get(cmd, lambda: sys.exit(__doc__))()
