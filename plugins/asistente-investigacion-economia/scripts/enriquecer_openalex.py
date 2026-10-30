# -*- coding: utf-8 -*-
"""Resumen, autores completos, palabras clave y acceso abierto de OpenAlex (datos CC0) para los DOI de uno o varios CSV de Scopus.
    python -I enriquecer_openalex.py <salida.json> <csv1> [<csv2> ...] [--correo tu@correo]
(Scopus STANDARD no entrega resúmenes y solo da el primer autor: este paso los completa.)
"""
import csv, json, os, sys, time, urllib.parse, urllib.request
sys.stdout.reconfigure(encoding="utf-8")


def resumen(inv):
    if not inv:
        return ""
    pos = {}
    for w, idx in inv.items():
        for i in idx:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))


def main(argv):
    correo = "usuario@example.com"
    if "--correo" in argv:
        i = argv.index("--correo"); correo = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    salida, csvs = argv[0], argv[1:]
    dois = set()
    for f in csvs:
        for r in csv.DictReader(open(f, encoding="utf-8-sig")):
            if r.get("DOI"):
                dois.add(r["DOI"].lower())
    res = {}
    for doi in sorted(dois):
        url = "https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(doi, safe="/():")
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": f"mailto:{correo}"}), timeout=40))
            o = d.get("open_access") or {}
            res[doi] = {"abstract": resumen(d.get("abstract_inverted_index")), "keywords": [k["display_name"] for k in (d.get("keywords") or [])][:8],
                        "oa_status": o.get("oa_status"), "oa_url": o.get("oa_url"), "cited_by_openalex": d.get("cited_by_count"), "language": d.get("language"),
                        "authors": [a["author"]["display_name"] for a in d.get("authorships", [])], "title_openalex": d.get("title"), "type": d.get("type")}
        except Exception as e:  # DOI inexistente o sin red: se registra y se sigue
            res[doi] = {"error": str(e)}
        time.sleep(0.15)
    os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(res), "DOI; con resumen:", sum(1 for v in res.values() if v.get("abstract")), "; con error:", sum(1 for v in res.values() if v.get("error")))


if __name__ == "__main__":
    main(sys.argv[1:])
