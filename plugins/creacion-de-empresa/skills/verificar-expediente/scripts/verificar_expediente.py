#!/usr/bin/env python
"""Revisa que los documentos de la empresa usen los datos oficiales de empresa.json y no datos viejos o equivocados.

Nació de un error real: el RUC personal del gerente (su cédula + «001») quedó en el membrete y en documentos firmados, cuando el
RUC de la sociedad es otro. Este control busca, en .docx, .pdf, .txt, .md, .json, .xlsx, .html y .csv:
  1. RUC distintos del oficial (cualquier número de 13 dígitos que termine en 001) y, si coincide con «cédula + 001», lo dice.
  2. Nombres anteriores de la empresa (empresa.json → nombres_anteriores), p. ej. la razón social que no se pudo reservar.
  3. Cualquier texto prohibido (empresa.json → textos_prohibidos), p. ej. «próximamente», «en construcción».
  4. Cédulas de personas ajenas al expediente cuando se pide --carpeta-compartida (datos personales en material que se publica).

Uso:
    python verificar_expediente.py --empresa empresa.json --carpeta "ruta/del/expediente" [--carpeta-compartida] [--json salida.json]
Código de salida: 0 sin hallazgos, 1 con hallazgos.
"""
import argparse
import json
import os
import re
import sys
import zipfile

EXT = {".docx", ".pdf", ".txt", ".md", ".json", ".xlsx", ".html", ".htm", ".csv", ".tsx", ".ts", ".js", ".jsx"}
IGNORAR = {"node_modules", ".git", ".next", "__pycache__", "dist", "build", ".venv"}
MAX_BYTES = 40 * 1024 * 1024


def texto_docx(ruta):
    """Cuerpo, encabezados y pies: el RUC suele estar en el encabezado del membrete."""
    partes = []
    with zipfile.ZipFile(ruta) as z:
        for n in z.namelist():
            if re.match(r"word/(document|header\d*|footer\d*|footnotes|endnotes)\.xml$", n):
                x = z.read(n).decode("utf-8", errors="ignore")
                x = re.sub(r"</w:p>", "\n", x)
                partes.append(re.sub(r"<[^>]+>", "", x))
    return "\n".join(partes)


def texto_xlsx(ruta):
    partes = []
    with zipfile.ZipFile(ruta) as z:
        for n in z.namelist():
            if n.startswith("xl/sharedStrings") or n.startswith("xl/worksheets/"):
                partes.append(re.sub(r"<[^>]+>", " ", z.read(n).decode("utf-8", errors="ignore")))
    return "\n".join(partes)


def texto_pdf(ruta):
    try:
        import pymupdf
    except ImportError:
        return ""
    with pymupdf.open(ruta) as d:
        return "\n".join(p.get_text() for p in d)


def leer(ruta):
    ext = os.path.splitext(ruta)[1].lower()
    try:
        if ext == ".docx":
            return texto_docx(ruta)
        if ext == ".xlsx":
            return texto_xlsx(ruta)
        if ext == ".pdf":
            return texto_pdf(ruta)
        return open(ruta, "rb").read().decode("utf-8", errors="ignore")
    except Exception as e:  # archivo corrupto, protegido, etc.
        return f"\x00ERROR:{e}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--empresa", required=True)
    ap.add_argument("--carpeta", required=True)
    ap.add_argument("--carpeta-compartida", action="store_true", help="la carpeta se comparte o publica: marca cédulas ajenas")
    ap.add_argument("--json", help="guarda los hallazgos en este archivo")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    e = json.load(open(a.empresa, encoding="utf-8"))
    ruc = re.sub(r"\D", "", e["ruc"])
    cedulas = {re.sub(r"\D", "", e["representante"].get("identificacion", ""))}
    for s in e.get("socios", []):
        cedulas.add(re.sub(r"\D", "", s.get("identificacion", "")))
    cedulas.discard("")
    ruc_personales = {c + "001": c for c in cedulas}
    anteriores = [n for n in e.get("nombres_anteriores", []) if n]
    prohibidos = [t for t in e.get("textos_prohibidos", ["próximamente", "en construcción", "coming soon"]) if t]

    hallazgos, revisados = [], 0
    for dp, dirs, fs in os.walk(a.carpeta):
        dirs[:] = [d for d in dirs if d not in IGNORAR]
        for f in fs:
            ruta = os.path.join(dp, f)
            if os.path.splitext(f)[1].lower() not in EXT or f.startswith("~$") or f == "empresa.json":
                continue  # empresa.json es la fuente de los datos oficiales y de las listas de lo prohibido
            try:
                if os.path.getsize(ruta) > MAX_BYTES:
                    continue
            except OSError:
                continue
            txt = leer(ruta)
            revisados += 1
            rel = os.path.relpath(ruta, a.carpeta)
            if txt.startswith("\x00ERROR"):
                hallazgos.append((rel, "no se pudo leer", txt[7:80]))
                continue
            for m in re.finditer(r"(?<!\d)(\d{10}001)(?!\d)", txt):
                v = m.group(1)
                if v != ruc:
                    ctx = txt[max(0, m.start() - 30):m.end() + 10].replace("\n", " ")
                    nota = "RUC personal del representante o socio (cédula + 001)" if v in ruc_personales else "RUC distinto del oficial"
                    hallazgos.append((rel, f"{nota}: {v}", ctx.strip()))
            bajo = txt.lower()
            for n in anteriores:
                if n.lower() in bajo:
                    hallazgos.append((rel, f"nombre anterior de la empresa: «{n}»", ""))
            for t in prohibidos:
                if t.lower() in bajo:
                    hallazgos.append((rel, f"texto prohibido: «{t}»", ""))
            if a.carpeta_compartida:
                for m in re.finditer(r"(?<!\d)(\d{10})(?!\d)", txt):
                    if m.group(1) not in cedulas and m.group(1) + "001" != ruc and not m.group(1).startswith(ruc[:10]):
                        if re.fullmatch(r"(0[1-9]|1\d|2[0-4]|30)\d{8}", m.group(1)):  # prefijo de provincia ecuatoriana
                            hallazgos.append((rel, f"posible cédula en carpeta compartida: {m.group(1)[:3]}•••••{m.group(1)[-2:]}", ""))
                            break

    vistos, unicos = set(), []
    for h in hallazgos:
        if h[:2] not in vistos:
            vistos.add(h[:2])
            unicos.append(h)
    print(f"Archivos revisados: {revisados} | RUC oficial: {ruc}")
    if not unicos:
        print("Sin hallazgos.")
    for rel, que, ctx in unicos:
        print(f"- {rel}\n    {que}" + (f"\n    …{ctx}…" if ctx else ""))
    if a.json:
        json.dump([dict(archivo=r, hallazgo=q, contexto=c) for r, q, c in unicos], open(a.json, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    sys.exit(1 if unicos else 0)


if __name__ == "__main__":
    main()
