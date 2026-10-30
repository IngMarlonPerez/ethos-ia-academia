# -*- coding: utf-8 -*-
"""RIS para Zotero/Mendeley desde config_trabajo.py: autores, título, revista, vol., núm., páginas, DOI, resumen (AB), palabras clave (KW),
nota de selección (N1) y enlace al PDF (L1). Libros originales como TY BOOK. Segundo archivo con los elegibles no seleccionados.
    python -I ris_zotero.py <ruta/config_trabajo.py>
Requiere 05_Base_datos/openalex_metadatos.json (enriquecer_openalex.py) para resumen y autores completos (Scopus STANDARD solo da el primero).
"""
import csv, glob, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matriz_consistencia import cargar_config, ACC, DEC  # noqa: E402

PARTICULAS = {"de", "del", "la", "van", "von", "da", "dos", "di", "le"}


def nombre(a):
    a = a.strip()
    if a.isupper():
        a = a.title()
    p = a.split()
    if len(p) >= 3 and p[-2].lower() in PARTICULAS:
        return f"{' '.join(p[-2:])}, {' '.join(p[:-2])}"
    return f"{p[-1]}, {' '.join(p[:-1])}" if len(p) > 1 else a


def main(ruta_cfg):
    cfg = cargar_config(ruta_cfg)
    bus = os.path.join(cfg.EV, "01_Busquedas_Scopus"); db = os.path.join(cfg.EV, "05_Base_datos")
    qs = list(cfg.PREGUNTAS)
    meta = {}
    for f in glob.glob(os.path.join(bus, "scopus_*.csv")):
        for r in csv.DictReader(open(f, encoding="utf-8-sig")):
            if r["DOI"]:
                meta.setdefault(r["DOI"].lower(), r)
    oa = {}
    ruta_oa = os.path.join(db, "openalex_metadatos.json")
    if os.path.exists(ruta_oa):
        oa = {k.lower(): v for k, v in json.load(open(ruta_oa, encoding="utf-8")).items()}
    else:
        print("AVISO: falta openalex_metadatos.json; el RIS saldrá sin resúmenes ni autores completos (ejecutar enriquecer_openalex.py).")

    def registro(doi, c):
        r = meta[doi]; o = oa.get(doi, {})
        autores = o.get("authors") or [r["Authors"]]
        L = ["TY  - JOUR"] + ["AU  - " + nombre(a) for a in autores]
        L += ["PY  - " + r["Year"], "TI  - " + cfg.TITULOS_APA.get(doi, o.get("title_openalex") or r["Title"]), "JO  - " + r["Source title"]]
        for tag, col in (("VL", "Volume"), ("IS", "Issue"), ("EP", "Page end")):
            if r[col]:
                L.append(f"{tag}  - {r[col]}")
        L.append("SP  - " + (r["Page start"] or r["Art. No."])) if (r["Page start"] or r["Art. No."]) else None
        L += ["DO  - " + r["DOI"], "UR  - https://doi.org/" + r["DOI"], "LA  - " + cfg.IDIOMA.get(doi, "en")]
        if o.get("abstract"):
            L.append("AB  - " + o["abstract"])
        kws = [k.strip() for k in re.split(r"[;|]", r.get("Author Keywords", "")) if k.strip()] or o.get("keywords", [])
        L += ["KW  - " + k for k in kws]
        pts = ", ".join(f"{q}={v}" for q, v in zip(qs, c["sc"]) if v)
        L.append(f"N1  - Matriz de consistencia · Decisión: {DEC[c['dec']]} · Puntaje: {pts} · Nivel de lectura: {ACC[c['acc']]} · Citas en Scopus: {r['Cited by']}")
        if cfg.PDFS.get(doi):
            L.append("L1  - 02_PDF_articulos/" + cfg.PDFS[doi])
        return [x for x in L if x] + ["ER  - ", ""]

    inc, noinc = [], []
    for doi, c in {d.lower(): c for d, c in cfg.CAND.items()}.items():
        (inc if c["dec"] == "I" else noinc).extend(registro(doi, c))
    for au, y, t, pb in cfg.LIBROS:
        inc += ["TY  - BOOK", "AU  - " + au, f"PY  - {y}", "TI  - " + t, "PB  - " + pb, "N1  - Obra original citada (no indexada en Scopus)", "ER  - ", ""]
    open(os.path.join(bus, "referencias_incluidas_zotero.ris"), "w", encoding="utf-8").write("\n".join(inc))
    open(os.path.join(bus, "referencias_elegibles_no_seleccionadas.ris"), "w", encoding="utf-8").write("\n".join(noinc))
    print("RIS incluidos:", sum(1 for l in inc if l.startswith("ER")), "| no seleccionados:", sum(1 for l in noinc if l.startswith("ER")))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "config_trabajo.py"))
