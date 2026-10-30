# -*- coding: utf-8 -*-
"""Verifica cita <-> referencia en un .docx (APA 7) y cuenta palabras del cuerpo.
    python -I verificar_citas.py <archivo.docx> [--inicio "Introducción"] [--refs "Referencias bibliográficas"]
Salidas: referencias sin cita en el texto (error) y posibles citas sin referencia (revisar a ojo: incluye años de hechos históricos
y apellidos compuestos). Complementa a verificar_apa.py (formato).
"""
import os, re, sys, zipfile
from lxml import etree
sys.stdout.reconfigure(encoding="utf-8")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def opcion(args, nombre, defecto):
    if nombre in args:
        i = args.index(nombre); v = args[i + 1]; del args[i:i + 2]; return v
    return defecto


def main(args):
    inicio = opcion(args, "--inicio", "Introducción"); refs_t = opcion(args, "--refs", "Referencias bibliogr")
    root = etree.fromstring(zipfile.ZipFile(args[0]).read("word/document.xml"))
    paras = ["".join(t.text or "" for t in p.iter(W + "t")) for p in root.iter(W + "p")]
    paras = [p for p in paras if p.strip()]
    i_ref = max(i for i, p in enumerate(paras) if p.strip().startswith(refs_t))
    i_int = next(i for i, p in enumerate(paras) if p.strip().startswith(inicio))
    cuerpo = "\n".join(paras[i_int:i_ref])
    refs = [p for p in paras[i_ref + 1:] if re.match(r"^[A-ZÀ-ÝØ].*\(\d{4}[a-z]?\)\.", p)]
    print("Palabras del cuerpo:", len(cuerpo.split()), "| referencias:", len(refs))
    sin_cita = []
    for r in refs:
        m = re.match(r"^([^,]+),.*?\((\d{4})", r)
        ap, yr = m.group(1), m.group(2)
        if not (re.search(re.escape(ap) + r"[^.;()]{0,80}[,( ]\s*\(?" + yr, cuerpo) or re.search(re.escape(ap) + r".{0,60}" + yr, cuerpo)):
            sin_cita.append(r[:80])
    print("Referencias sin cita en el texto:", sin_cita or "ninguna")
    cites = set(re.findall(r"([A-ZÀ-ÝØ][\wÀ-ÿØø'’\-]+)(?: et al\.)?(?:,| y| &)?[^()]{0,40}?\(?\b((?:1[5-9]|20)\d{2})\b", cuerpo))
    aps = {re.match(r"^([^,]+),", r).group(1) for r in refs}
    print("Posibles citas sin referencia (revisar a ojo):", sorted((a, y) for a, y in cites if a not in aps))
    sys.exit(1 if sin_cita else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
