#!/usr/bin/env python
"""Convierte una plantilla Markdown de la empresa en un .docx sobre su hoja membretada, rellenando los {{datos}}.

Uso:
    python plantilla_a_docx.py --plantilla acta.md --empresa empresa.json --membrete Membrete.docx --salida acta.docx \
        [--datos datos.json] [--pdf]

Datos disponibles en la plantilla:
  {{razon_social}}, {{ruc}}, {{representante.nombre}}, {{domicilio.ciudad}}… (cualquier clave de empresa.json con punto para anidar)
  {{datos.xxx}}   (claves de --datos), {{hoy}} = fecha de hoy en español, {{ciudad}} = ciudad del domicilio
  Lo que no se pueda rellenar queda como [[campo por completar]] resaltado en amarillo: así se ve qué falta antes de firmar.

Sintaxis (subconjunto de Markdown):
  # Título | subtítulo            título centrado          ## Sección           encabezado con barra de acento
  ### Subsección                  párrafo suelto           - viñeta             1. cláusula numerada (se deja como párrafo)
  > nota                          cuadro informativo       >! advertencia       cuadro de advertencia
  | A | B |  y  |---|---|        tabla (la primera fila es el encabezado)
  @firmas Nombre|Cargo|C.C. ;; Nombre|Cargo|C.C.      dos firmas lado a lado
  @salto                          salto de página          **negrita**  ~~cursiva~~  `código`
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from mdoc import MDoc, set_marca  # noqa: E402

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def aplanar(d, pref=""):
    out = {}
    for k, v in d.items():
        clave = f"{pref}{k}"
        if isinstance(v, dict):
            out.update(aplanar(v, clave + "."))
        else:
            out[clave] = v
    return out


def contexto(empresa, datos):
    ctx = aplanar(empresa)
    ctx.update(aplanar(datos, "datos."))
    hoy = dt.date.today()
    ctx["hoy"] = f"{hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}"
    ctx["ciudad"] = empresa.get("domicilio", {}).get("ciudad", "")
    return ctx


def rellenar(texto, ctx):
    faltan = []

    def sub(m):
        k = m.group(1)
        v = ctx.get(k)
        if v in (None, ""):
            faltan.append(k)
            return f"[[{k.replace('datos.', '').replace('_', ' ')}]]"
        return str(v)

    return re.sub(r"\{\{\s*([\w.]+)\s*\}\}", sub, texto), sorted(set(faltan))


def render(md, d):
    lineas = md.splitlines()
    i = 0
    while i < len(lineas):
        l = lineas[i].rstrip()
        if not l.strip():
            i += 1
        elif l.startswith("# "):
            t, _, sub = l[2:].partition("|")
            d.title(t.strip(), sub.strip() or None)
            i += 1
        elif l.startswith("## "):
            d.h1(l[3:].strip())
            i += 1
        elif l.startswith("### "):
            d.h2(l[4:].strip())
            i += 1
        elif l.startswith(">!"):
            d.callout(l[2:].strip(), "warn")
            i += 1
        elif l.startswith(">"):
            d.callout(l[1:].strip(), "info")
            i += 1
        elif l.startswith("@salto"):
            d.page_break()
            i += 1
        elif l.startswith("@firmas"):
            lados = [tuple(x.strip() for x in lado.split("|")) for lado in l[len("@firmas"):].split(";;")]
            d.signatures(lados[0], lados[1] if len(lados) > 1 else ("", ""))
            i += 1
        elif l.startswith("|"):
            filas = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                celdas = [c.strip() for c in lineas[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in celdas):
                    filas.append(celdas)
                i += 1
            d.table(filas[0], filas[1:])
        elif l.startswith("- "):
            items = []
            while i < len(lineas) and lineas[i].startswith("- "):
                items.append(lineas[i][2:].strip())
                i += 1
            d.bullets(items)
        elif re.fullmatch(r"-{3,}", l.strip()):
            d.spacer(160)
            i += 1
        else:
            d.p(l.strip())
            i += 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plantilla", required=True)
    ap.add_argument("--empresa", required=True)
    ap.add_argument("--membrete", required=True)
    ap.add_argument("--salida", required=True)
    ap.add_argument("--datos")
    ap.add_argument("--pdf", action="store_true")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    empresa = json.load(open(a.empresa, encoding="utf-8"))
    datos = json.load(open(a.datos, encoding="utf-8")) if a.datos else {}
    marca = empresa.get("marca", {})
    set_marca(marca.get("color_primario"), marca.get("color_acento"), marca.get("color_secundario"))
    texto, faltan = rellenar(open(a.plantilla, encoding="utf-8").read(), contexto(empresa, datos))
    d = MDoc(template=a.membrete)
    render(texto, d)
    d.save(a.salida, title=os.path.splitext(os.path.basename(a.salida))[0], creator=empresa["razon_social"])
    print("Documento:", a.salida)
    if faltan:
        print("Campos sin dato (quedan resaltados en amarillo):", ", ".join(faltan))
    if a.pdf:
        from pdf_word import convertir
        print("PDF:", convertir(a.salida))


if __name__ == "__main__":
    main()
