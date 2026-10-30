# -*- coding: utf-8 -*-
"""Matriz de consistencia (M1-M4 + PRISMA) a partir de config_trabajo.py. Usa matrices.py (misma carpeta).
    python -I matriz_consistencia.py <ruta/config_trabajo.py>
Genera 05_Base_datos/Matriz_consistencia.xlsx y 05_Base_datos/prisma_conteos.json (lo usa graficos_busqueda.py).
Honestidad: el nivel de lectura (PDF / RES / MET) de cada candidato queda registrado en M2c y en el PRISMA.
"""
import csv, importlib.util, json, os, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from matrices import construir  # noqa: E402

ACC = {"PDF": "PDF de acceso abierto leído", "RES": "Resumen (OpenAlex) + metadatos Scopus", "MET": "Título y palabras clave (resumen no disponible)"}
DEC = {"I": "Incluido", "N": "Elegible – no seleccionado"}
SIN_RESUMEN = "Resumen no disponible; se usó el título y las palabras clave de Scopus. Pendiente de lectura completa."


def cargar_config(ruta):
    ruta = os.path.abspath(ruta)
    spec = importlib.util.spec_from_file_location("config_trabajo", ruta)
    cfg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cfg)
    cfg.EV = os.path.dirname(os.path.dirname(ruta))
    return cfg


def main(ruta_cfg):
    cfg = cargar_config(ruta_cfg)
    bus = os.path.join(cfg.EV, "01_Busquedas_Scopus"); db = os.path.join(cfg.EV, "05_Base_datos")
    os.makedirs(db, exist_ok=True)
    sys.path.insert(0, os.path.dirname(os.path.abspath(ruta_cfg)))
    try:
        from referencias_apa import REFS
    except ImportError:
        REFS = []
    apa = {}
    for ref in REFS:
        m = re.search(r"https://doi\.org/(\S+)$", ref)
        if m:
            apa[m.group(1).lower()] = ref

    # IDs con la misma deduplicación por EID de la skill matrices-revision
    filas = {}
    for pref, archivo in cfg.CSVS.items():
        for i, r in enumerate(csv.DictReader(open(os.path.join(bus, archivo), encoding="utf-8-sig")), 1):
            eid = r.get("EID", "")
            if eid and any(eid == x[1].get("EID") for x in filas.values()):
                continue
            filas[f"{pref}-{i}"] = (pref, r)
    doi2id = {}
    for rid, (pref, r) in filas.items():
        if r["DOI"]:
            doi2id.setdefault(r["DOI"].lower(), rid)
    faltan = [d for d in cfg.CAND if d.lower() not in doi2id]
    assert not faltan, f"DOI de CAND que no están en los CSV (¿typo o falta la búsqueda por DOI?): {faltan}"

    qs = list(cfg.PREGUNTAS)
    cand = {d.lower(): c for d, c in cfg.CAND.items()}
    pasan = {doi2id[d] for d in cand}
    texto_completo = {doi2id[d]: ", ".join(q for q, v in zip(qs, c["sc"]) if v) or "—" for d, c in cand.items()}

    def motivo(titulo):
        for patron, m in cfg.REGLAS:
            if re.search(patron, titulo.lower()):
                return m
        return "E8 · Tema no pertinente a las preguntas del trabajo"

    elegibilidad, analisis, incluidos = [], [], []
    for doi, c in cand.items():
        rid = doi2id[doi]; r = filas[rid][1]
        dec = DEC[c["dec"]]; acc = ACC[c["acc"]]
        elegibilidad.append({"id": rid, "cita": c["cita"], "acceso": acc, "puntajes": dict(zip(qs, c["sc"])), "decision": dec, "motivo": c.get("mot", "")})
        if c["dec"] == "I":
            analisis.append({"cita": c["cita"], "titulo": r["Title"], "revista": f'{r["Source title"]}, {r["Volume"]}' + (f'({r["Issue"]})' if r["Issue"] else ""),
                             "contexto": "", "objetivo": c.get("obj", ""), "muestra": "No reportado en el resumen",
                             "metodo": "Lectura de texto completo (PDF abierto)" if c["acc"] == "PDF" else "Según resumen",
                             "hallazgos": c.get("hall") or SIN_RESUMEN, "limitaciones": "No evaluadas: lectura a nivel de resumen" if c["acc"] != "PDF" else "Lectura del PDF",
                             "conclusiones": c.get("hall", ""), "aportes": c.get("aportes", {}),
                             "evidencia": {"RES": "Resumen en OpenAlex (sin página de revista)", "PDF": "PDF en 02_PDF_articulos", "MET": "Sin resumen: pendiente de lectura completa"}[c["acc"]],
                             "decision": "Incluido"})
            incluidos.append({"cita": "(" + c["cita"].replace(" y ", " & ") + ")", "preguntas": ", ".join(q for q, v in zip(qs, c["sc"]) if v),
                              "pdf": cfg.PDFS.get(doi, "No recuperado"), "apa": apa.get(doi, "—")})
    incluidos.sort(key=lambda x: x["apa"].lower())

    titulo, resumen = [], []
    for rid, (pref, r) in filas.items():
        oa = "Sí" if r.get("Open Access", "").strip() else "No"
        pasa = rid in pasan
        titulo.append({"id": rid, "busqueda": pref, "anio": r["Year"], "autores": r["Authors"][:120], "titulo": r["Title"], "revista": r["Source title"],
                       "doi": r["DOI"], "oa": oa, "decision": "Pasa a resumen" if pasa else "Excluido (título)",
                       "motivo": "Título pertinente a las preguntas." if pasa else motivo(r["Title"])})
        if pasa:
            cita = f"{r['Authors'].split(';')[0]}{' et al.' if ';' in r['Authors'] else ''} ({r['Year']})"
            resumen.append({"id": rid, "cita": cita, "titulo": r["Title"], "oa": oa, "preguntas": texto_completo[rid],
                            "decision": "Pasa a texto completo", "motivo": "El resumen o los metadatos anticipan aporte directo a alguna pregunta."})
    n_tit, n_pasan = len(titulo), len(resumen)
    sin = sum(b["sin_filtros"] for b in cfg.BUSQUEDAS); con = sum(b["con_filtros"] for b in cfg.BUSQUEDAS)
    n_inc = sum(1 for e in elegibilidad if e["decision"] == "Incluido")
    n_pdf = sum(1 for c in cand.values() if c["acc"] == "PDF"); n_met = sum(1 for c in cand.values() if c["acc"] == "MET")
    prisma = [
        ("Identificación", "Registros identificados sin filtros", sin),
        ("Identificación", "Eliminados por filtros (tipo artículo, idioma, etapa)", sin - con),
        ("Identificación", "Registros con filtros", con),
        ("Identificación", "Duplicados entre ecuaciones (mismo EID)", con - n_tit),
        ("Cribado", "Registros únicos cribados por título", n_tit),
        ("Cribado", "Excluidos por título (reglas E1, E2, E8)", n_tit - n_pasan),
        ("Cribado", "Registros cribados por resumen o metadatos", n_pasan),
        ("Cribado", "Excluidos por resumen", 0),
        ("Elegibilidad", "Registros evaluados para elegibilidad (puntaje 0-2 por pregunta)", len(elegibilidad)),
        ("Elegibilidad", f"Con PDF abierto leído ({n_pdf}) · con resumen ({len(elegibilidad)-n_pdf-n_met}) · solo título y palabras clave ({n_met})", len(elegibilidad)),
        ("Elegibilidad", "Elegibles no seleccionados (aporte parcial o redundante)", len(elegibilidad) - n_inc),
        ("Inclusión", "Artículos incluidos", n_inc),
    ]
    d = {"actividad": cfg.TEMA, "fecha": cfg.FECHA, "autora": cfg.AUTORA, "institucion": "institucional (API oficial de Elsevier)", "preguntas": cfg.PREGUNTAS,
         "criterios": cfg.CRITERIOS, "busquedas": cfg.BUSQUEDAS, "prisma": prisma, "cribado_titulo": titulo, "cribado_resumen": resumen,
         "elegibilidad": elegibilidad, "analisis": analisis, "incluidos": incluidos, "tematica": [], "prisma2020": {}}
    for f, c, n in prisma:
        print(f"{f:15} {n:>6}  {c}")
    salida = os.path.join(db, "Matriz_consistencia.xlsx")
    construir(d, salida, png=False)
    cod = Counter(t["motivo"][:2] for t in titulo if t["decision"].startswith("Excluido"))
    inc_acc = Counter(c["acc"] for c in cand.values() if c["dec"] == "I")
    json.dump({"prisma": prisma, "n_pdf": n_pdf, "n_met": n_met, "n_res": len(elegibilidad) - n_pdf - n_met, "n_inc": n_inc, "n_eval": len(elegibilidad),
               "n_unicos": n_tit, "sin": sin, "con": con, "motivos_titulo": dict(cod), "incluidos_pdf": inc_acc["PDF"], "incluidos_res": inc_acc["RES"],
               "incluidos_met": inc_acc["MET"], "por_busqueda": dict(Counter(t["busqueda"] for t in titulo))},
              open(os.path.join(db, "prisma_conteos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK", salida)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "config_trabajo.py"))
