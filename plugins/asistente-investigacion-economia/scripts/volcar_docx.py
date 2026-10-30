# -*- coding: utf-8 -*-
"""Vuelca un .docx a texto UTF-8 (párrafos con estilo, marcas de imagen y ecuación, y tablas).
    python -I volcar_docx.py <archivo.docx> [<salida.txt>]
Sin salida imprime en consola (la consola de Windows rompe las tildes: preferir archivo y leerlo con Read).
Copiar antes el .docx a una ruta corta si la original supera 260 caracteres.
"""
import sys
import docx
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

d = docx.Document(sys.argv[1])
salida = []
for ch in d.element.body.iterchildren():
    if ch.tag == qn("w:p"):
        p = Paragraph(ch, d)
        img = len(ch.findall(".//" + qn("w:drawing")))
        eq = len(ch.findall(".//" + qn("m:oMath")))
        marca = (f" <IMG x{img}>" if img else "") + (f" <EQ x{eq}>" if eq else "")
        salida.append(f"[{p.style.name}]{marca} {p.text}")
    elif ch.tag == qn("w:tbl"):
        t = Table(ch, d)
        salida.append("<TABLE>")
        for r in t.rows:
            salida.append(" | ".join(c.text.replace("\n", " / ") for c in r.cells))
        salida.append("</TABLE>")
texto = "\n".join(salida)
if len(sys.argv) > 2:
    open(sys.argv[2], "w", encoding="utf-8").write(texto)
    print("volcado:", sys.argv[2], "| párrafos y tablas:", len(salida))
else:
    sys.stdout.reconfigure(encoding="utf-8")
    print(texto)
