# -*- coding: utf-8 -*-
"""
graficos_latencia_simulacion.py — dos figuras para «Resultados y análisis» de una práctica de red.

1) figura2_latencia_paquetes.png: latencia de cada paquete (ping) por conexión, desde los archivos
   de ping de Windows (`ping -n 50 ... > archivo.txt`).
2) figura3_real_vs_simulado.png: velocidad y latencia de las conexiones REALES (resultados.csv de
   medir_red.ps1) frente a los perfiles SIMULADOS (simulacion_redes.csv de
   laboratorio-docker/scripts/simular_redes.ps1). Las barras de los perfiles simulados van rayadas
   y rotuladas «(simulado)»: nunca se mezclan sin marcar.

Uso:
    python -I graficos_latencia_simulacion.py --reales resultados.csv --simulados simulacion_redes.csv \
        --ping "Wi-Fi 5 GHz=ping.txt" --ping "Wi-Fi 2,4 GHz=ping_24ghz.txt" --ping "Ethernet=ping_ethernet.txt" \
        --salida "<carpeta>"
"""
import argparse
import csv
import re
import statistics as st
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

COLORES = ['#1B3247', '#D98E04', '#2E8B57', '#8E44AD', '#C0392B']


def latencias(archivo):
    t = Path(archivo).read_text(encoding='utf-8', errors='ignore')
    return [int(x) for x in re.findall(r'tiempo[=<](\d+)\s*ms', t)]


def agrupa(filas):
    d = {}
    for r in filas:
        d.setdefault(r['conexion'], []).append(r)
    return {k: (st.mean(float(x['bajada_mbps']) for x in v), st.mean(float(x['subida_mbps']) for x in v),
                st.mean(float(x['ping_ms']) for x in v)) for k, v in d.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reales', required=True)
    ap.add_argument('--simulados')
    ap.add_argument('--ping', action='append', default=[], help='"Etiqueta=archivo_ping.txt"')
    ap.add_argument('--salida', required=True)
    a = ap.parse_args()
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)

    if a.ping:
        fig, ax = plt.subplots(figsize=(10, 4))
        for i, par in enumerate(a.ping):
            etq, arch = par.split('=', 1)
            v = latencias(arch)
            ax.plot(range(1, len(v) + 1), v, label=etq, color=COLORES[i % len(COLORES)], linewidth=1.6)
            print(f'{etq}: n={len(v)} mín={min(v)} máx={max(v)} media={st.mean(v):.1f} ms')
        ax.set_xlabel('Paquete (ping)'); ax.set_ylabel('Latencia (ms)')
        ax.set_title('Estabilidad de la latencia por tipo de conexión')
        ax.legend(frameon=False); ax.spines[['top', 'right']].set_visible(False)
        fig.tight_layout(); fig.savefig(out / 'figura2_latencia_paquetes.png', dpi=200)

    real = agrupa(list(csv.DictReader(open(a.reales, encoding='utf-8'))))
    sim = {}
    if a.simulados:
        sim = {k: v for k, v in agrupa(list(csv.DictReader(open(a.simulados, encoding='utf-8')))).items()
               if not k.lower().startswith('referencia')}
    G = {**real, **sim}
    orden = list(G)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={'width_ratios': [2.3, 1]})
    w = 0.38
    for i, k in enumerate(orden):
        h = '//' if k in sim else None
        etq = k.replace('Wi-Fi 2.4', 'Wi-Fi 2,4') + ('' if k in sim else '\n(real)')
        a1.bar(i - w / 2, G[k][0], w, color='#1B3247', hatch=h, edgecolor='white', label='Bajada' if i == 0 else None)
        a1.bar(i + w / 2, G[k][1], w, color='#6FA8DC', hatch=h, edgecolor='white', label='Subida' if i == 0 else None)
        a1.text(i - w / 2, G[k][0] * 1.02, f'{G[k][0]:.0f}', ha='center', fontsize=8)
        a1.text(i + w / 2, G[k][1] * 1.02, f'{G[k][1]:.0f}', ha='center', fontsize=8)
        a2.bar(i, G[k][2], 0.55, color='#999999', hatch=h, edgecolor='white')
        a2.text(i, G[k][2] * 1.03, f'{G[k][2]:.0f}', ha='center', fontsize=8)
        for ax in (a1, a2):
            pass
    nombres = [k.replace('Wi-Fi 2.4', 'Wi-Fi 2,4') + ('' if k in sim else '\n(real)') for k in orden]
    a1.set_xticks(range(len(orden))); a1.set_xticklabels(nombres, fontsize=8)
    a2.set_xticks(range(len(orden))); a2.set_xticklabels(nombres, fontsize=7, rotation=30, ha='right')
    a1.set_ylabel('Velocidad (Mbps)'); a1.set_title('Velocidad promedio (barras rayadas = simulación)')
    a2.set_ylabel('Latencia (ms)'); a2.set_title('Latencia promedio')
    a1.legend(frameon=False)
    for ax in (a1, a2):
        ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout(); fig.savefig(out / 'figura3_real_vs_simulado.png', dpi=200)
    print('Figuras guardadas en', out)


if __name__ == '__main__':
    main()
