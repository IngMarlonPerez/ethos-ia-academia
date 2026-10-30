#!/usr/bin/env python
"""Tablero de etapas de la empresa (se guarda en empresa.json → etapas y en 00_Control_Empresa.md).

    python tablero.py ver     --empresa empresa.json
    python tablero.py marcar 4 cerrada --empresa empresa.json --nota "inscrita el 2026-01-15, N.º 000000"
Estados: pendiente | en_curso | bloqueada | cerrada.  Una etapa sólo se cierra con su control cumplido (ver cada skill).
"""
import argparse
import json
import os
import sys

ESTADOS = ["pendiente", "en_curso", "bloqueada", "cerrada"]
ICONO = {"pendiente": "·", "en_curso": "▶", "bloqueada": "✖", "cerrada": "✔"}
NOMBRES = ["Inicio", "Nombre y marca", "Logos y piezas", "Papelería membretada", "Constitución SAS",
           "Obligaciones post-constitución", "Balance inicial SCVS", "Gobierno societario", "Sitio web corporativo",
           "Equipo y practicantes", "Verificación del expediente"]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", choices=["ver", "marcar"])
    ap.add_argument("etapa", nargs="?", type=int)
    ap.add_argument("estado", nargs="?", choices=ESTADOS)
    ap.add_argument("--empresa", required=True)
    ap.add_argument("--nota", default="")
    a = ap.parse_args()
    e = json.load(open(a.empresa, encoding="utf-8"))
    et = e.setdefault("etapas", {})
    for i, n in enumerate(NOMBRES):
        et.setdefault(str(i), {"nombre": n, "estado": "pendiente", "nota": ""})
    if a.accion == "marcar":
        if a.etapa is None or a.estado is None:
            sys.exit("Uso: marcar <n> <estado> --nota ...")
        et[str(a.etapa)]["estado"] = a.estado
        if a.nota:
            et[str(a.etapa)]["nota"] = a.nota
        json.dump(e, open(a.empresa, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    filas = ["| Etapa | Estado | Nota |", "|---|---|---|"]
    print(f"{e.get('razon_social') or '(sin razón social)'}")
    for i in range(len(NOMBRES)):
        x = et[str(i)]
        print(f" {ICONO[x['estado']]} {i:>2} {x['nombre']:<34} {x['estado']:<10} {x.get('nota', '')}")
        filas.append(f"| {i} · {x['nombre']} | {x['estado']} | {x.get('nota', '')} |")
    md = os.path.join(os.path.dirname(os.path.abspath(a.empresa)), "00_Resumen_y_Cronograma", "00_Control_Empresa.md")
    if a.accion == "marcar" and os.path.isdir(os.path.dirname(md)):
        open(md, "w", encoding="utf-8").write("# Control de la empresa\n\n" + "\n".join(filas) + "\n")


if __name__ == "__main__":
    main()
