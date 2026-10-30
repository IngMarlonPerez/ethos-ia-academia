# -*- coding: utf-8 -*-
"""Figuras de la metodología a partir de config_trabajo.py y prisma_conteos.json:
  fig_flujo_seleccion.png  (flujo PRISMA adaptado) y fig_evidencia_bibliometrica.png (barras por periodo + dispersión año-citas + cajas).
    python -I graficos_busqueda.py <ruta/config_trabajo.py>
Diseñadas a tamaño final (6 in de ancho) y verificadas contra textos superpuestos (lib_figuras.guardar).
"""
import csv, json, os, sys
import numpy as np
import matplotlib.pyplot as plt
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_figuras import lienzo, caja, flecha, guardar, GRIS, PALETA  # noqa: E402
from matriz_consistencia import cargar_config  # noqa: E402

FASE = {"Identificación": "#4C78A8", "Cribado": "#F58518", "Elegibilidad": "#54A24B", "Inclusión": "#1A3A7A"}
fmt = lambda n: f"{n:,}".replace(",", " ")


def flujo(P, out, nombre="fig_flujo_seleccion.png", n_busquedas=None):
    from matplotlib.patches import Rectangle
    fig, ax = lienzo(6.0, 6.6)
    cx, cw, rx, rw = 20, 44, 68, 31
    ys, hs = [86, 66, 46, 25, 5], [11, 11, 11, 15, 12]
    nb = n_busquedas or len(P.get("por_busqueda", {})) or 1
    txt = [f"Registros identificados en Scopus\n{nb} ecuaciones\nn = {fmt(P['sin'])}", f"Registros con filtros\n(artículos, idioma)\nn = {fmt(P['con'])}",
           f"Registros únicos cribados\npor título\nn = {fmt(P['n_unicos'])}",
           f"Evaluados para elegibilidad\n(resumen, metadatos o PDF)\npuntaje 0–2 por pregunta\nn = {P['n_eval']}", f"Artículos incluidos\nen el trabajo\nn = {P['n_inc']}"]
    fases = ["Identificación", "Identificación", "Cribado", "Elegibilidad", "Inclusión"]
    for y, h, t, f in zip(ys, hs, txt, fases):
        caja(ax, cx, y, cw, h, t, fc="#FFFFFF" if f != "Inclusión" else "#E1ECFA", ec=FASE[f], lw=1.6, fs=7.3, bold=(f == "Inclusión"))
    for i in range(4):
        flecha(ax, (cx + cw / 2, ys[i]), (cx + cw / 2, ys[i + 1] + hs[i + 1]))
    for nombre_f, (y0, y1) in {"Identificación": (ys[1], ys[0] + hs[0]), "Cribado": (ys[2], ys[2] + hs[2]), "Elegibilidad": (ys[3], ys[3] + hs[3]), "Inclusión": (ys[4], ys[4] + hs[4])}.items():
        ax.add_patch(Rectangle((1, y0), 7, y1 - y0, fc=FASE[nombre_f], ec="none"))
        ax.text(4.5, (y0 + y1) / 2, nombre_f, rotation=90, ha="center", va="center", color="white", fontsize=7.3, fontweight="bold")
    m = P["motivos_titulo"]
    ex = [(ys[0] - 9, 8, f"Excluidos por filtros\n(tipo, idioma)\nn = {fmt(P['sin'] - P['con'])}"), (ys[1] - 9, 8, f"Duplicados entre\necuaciones (EID)\nn = {P['con'] - P['n_unicos']}"),
          (ys[2] - 14, 20, f"Excluidos por título\nn = {fmt(P['n_unicos'] - P['n_eval'])}\nE8 tema no pertinente: {fmt(m.get('E8', 0))}\nE1 otra disciplina o\naplicación actual: {m.get('E1', 0)}\nE2 revisiones: {m.get('E2', 0)}"),
          (ys[3] - 10, 9, f"Elegibles no\nseleccionados\nn = {P['n_eval'] - P['n_inc']} (parcial o redundante)")]
    for (y, h, t), yy in zip(ex, [ys[0] - 5, ys[1] - 5, ys[2] - 4, ys[3] - 5.5]):
        caja(ax, rx, y, rw, h, t, fc="#F3F3F3", ec="#8A8A8A", fs=6.6)
        flecha(ax, (cx + cw / 2, yy), (rx, yy), color="#8A8A8A", lw=1.0)
    ax.text(cx + cw / 2, 1.3, f"Nivel de lectura de los {P['n_inc']} incluidos: PDF abierto {P['incluidos_pdf']} · resumen {P['incluidos_res']} · título y palabras clave {P['incluidos_met']}",
            ha="center", va="center", fontsize=6.3, color=GRIS, style="italic")
    return guardar(fig, out, nombre)


def bibliometria(cfg, bus, out, nombre="fig_evidencia_bibliometrica.png"):
    bloques = list(cfg.CORPUS)
    col = {b: PALETA[i % len(PALETA)] for i, b in enumerate(bloques)}
    datos = {}
    for b, f in cfg.CORPUS.items():
        rows = list(csv.DictReader(open(os.path.join(bus, f), encoding="utf-8-sig")))
        datos[b] = [(int(r["Year"]), int(r["Cited by"] or 0)) for r in rows if r["Year"].isdigit()]
    fig = plt.figure(figsize=(6.0, 5.2), constrained_layout=True)
    gs = fig.add_gridspec(3, 2, height_ratios=[1.0, 1.0, 0.13])
    a, b_, c, lg = fig.add_subplot(gs[0, :]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1]), fig.add_subplot(gs[2, :])
    lg.axis("off")
    k = len(bloques); w = 0.8 / max(k, 1); x = np.arange(len(cfg.PERIODOS))
    tope = max((max(v) for v in cfg.CONTEOS_PERIODO.values()), default=1)
    for i, bl in enumerate(bloques):
        v = cfg.CONTEOS_PERIODO.get(bl, [0] * len(x))
        barras = a.bar(x + (i - (k - 1) / 2) * w, v, w, color=col[bl], label=bl)
        for rect, val in zip(barras, v):
            a.text(rect.get_x() + rect.get_width() / 2, val + tope * .015, str(val), ha="center", va="bottom", fontsize=5.4, color="#333333")
    a.set_xticks(x); a.set_xticklabels(cfg.PERIODOS); a.set_ylim(0, tope * 1.15); a.set_ylabel("Artículos en Scopus")
    a.set_title("a) Producción por periodo y bloque temático", loc="left"); a.grid(axis="y", color="#E6E6E6", lw=.6); a.set_axisbelow(True)
    for bl in bloques:
        b_.scatter([y for y, _ in datos[bl]], [cc + 1 for _, cc in datos[bl]], s=7, alpha=.5, color=col[bl], edgecolor="none")
    b_.set_yscale("log"); b_.set_xlabel("Año de publicación"); b_.set_ylabel("Citas + 1 (log)"); b_.set_title("b) Año frente a citas", loc="left"); b_.grid(color="#EDEDED", lw=.5)
    bp = c.boxplot([np.log10(np.array([cc for _, cc in datos[bl]]) + 1) for bl in bloques], patch_artist=True, widths=.62,
                   medianprops={"color": "black", "lw": 1.1}, flierprops={"markersize": 1.8, "alpha": .35})
    for pb, bl in zip(bp["boxes"], bloques):
        pb.set_facecolor(col[bl]); pb.set_alpha(.85)
    c.set_xticklabels([f"B{i + 1}" for i in range(k)]); c.set_ylabel("log10(citas + 1)"); c.set_title("c) Distribución de citas", loc="left"); c.grid(axis="y", color="#EDEDED", lw=.5)
    h, l = a.get_legend_handles_labels()
    lg.legend(h, l, ncol=3, loc="center", frameon=False, fontsize=6.8, handlelength=1.2, columnspacing=1.2)
    stats = []
    for bl in bloques:
        aa = np.array([y for y, _ in datos[bl]]); cc = np.array([v for _, v in datos[bl]])
        stats.append([bl, len(aa), float(np.median(cc)), round(float(cc.mean()), 2), int(cc.max()), int(np.median(aa)), round(float(np.corrcoef(aa, np.log10(cc + 1))[0, 1]), 3)])
    return guardar(fig, out, nombre), stats


def main(ruta_cfg):
    cfg = cargar_config(ruta_cfg)
    bus = os.path.join(cfg.EV, "01_Busquedas_Scopus"); db = os.path.join(cfg.EV, "05_Base_datos"); out = os.path.join(cfg.EV, "03_Graficos")
    P = json.load(open(os.path.join(db, "prisma_conteos.json"), encoding="utf-8"))
    flujo(P, out, n_busquedas=len(cfg.CSVS))
    if cfg.CORPUS:
        _, stats = bibliometria(cfg, bus, out)
        with open(os.path.join(db, "resumen_estadistico.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f); w.writerow(["corpus", "n_registros", "mediana_citas", "media_citas", "max_citas", "anio_mediano", "correlacion_anio_log_citas"]); w.writerows(stats)
    print("Figuras en", out, "(abrir cada PNG y mirarlo)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "config_trabajo.py"))
