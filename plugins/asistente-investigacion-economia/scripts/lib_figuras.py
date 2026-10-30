# -*- coding: utf-8 -*-
"""Helpers de figuras en matplotlib con VERIFICACIÓN AUTOMÁTICA de textos superpuestos o fuera del lienzo.
Diseñar a tamaño final: ancho útil del Word UNEMI ≈ 6.0 in (15 cm); fuente 6.5–8 pt. Leyendas fuera del área de datos (fila inferior).

    from lib_figuras import *
    fig, ax = lienzo(6.0, 3.5)           # lienzo 0-100 x 0-100 para diagramas
    caja(ax, 5, 60, 40, 25, "Texto", fc="#EAF0FA"); flecha(ax, (25, 60), (25, 40))
    guardar(fig, OUT, "fig3_algo.png")   # imprime OK o la lista de textos que se pisan
Después ABRIR cada PNG con Read y mirarlo: el verificador no ve flechas ni cajas que cortan texto.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle  # noqa: F401

NAVY = "#1A3A7A"; GRIS = "#5B6573"
PALETA = ["#4C78A8", "#F58518", "#54A24B", "#E45756", "#8C6BB1"]   # accesible; un color por escuela/serie

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 8.5, "axes.titleweight": "bold", "axes.labelsize": 7.8, "xtick.labelsize": 7.2,
                     "ytick.labelsize": 7.2, "savefig.facecolor": "white"})


def revisar(fig, nombre, tol=1.0):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.canvas.get_width_height()
    items = []
    for t in fig.findobj(matplotlib.text.Text):
        if not t.get_visible() or not t.get_text().strip():
            continue
        if t.axes is not None and not t.axes.axison:
            continue
        bb = t.get_window_extent(r)
        if bb.width >= 1 and bb.height >= 1:
            items.append((t.get_text().replace("\n", " ")[:40], bb))
    problemas = [f"fuera del lienzo: «{tx}»" for tx, bb in items if bb.x0 < -tol or bb.y0 < -tol or bb.x1 > W + tol or bb.y1 > H + tol]
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i][1], items[j][1]
            if min(a.x1, b.x1) - max(a.x0, b.x0) > 1.5 and min(a.y1, b.y1) - max(a.y0, b.y0) > 1.5:
                problemas.append(f"se pisan: «{items[i][0]}» y «{items[j][0]}»")
    print(("OK   " if not problemas else "REVISAR ") + nombre, *problemas, sep="\n   " if problemas else " ")
    return problemas


def guardar(fig, carpeta, nombre, dpi=250):
    os.makedirs(carpeta, exist_ok=True)
    p = revisar(fig, nombre)
    fig.savefig(os.path.join(carpeta, nombre), dpi=dpi)
    plt.close(fig)
    return p


def lienzo(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    return fig, ax


def caja(ax, x, y, w, h, txt, fc="#EAF0FA", ec=NAVY, fs=7.4, bold=False, tc="#111111", lw=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2", fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", color=tc, linespacing=1.3)


def flecha(ax, a, b, color=NAVY, rad=0.0, lw=1.2):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=9, lw=lw, color=color, connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))
