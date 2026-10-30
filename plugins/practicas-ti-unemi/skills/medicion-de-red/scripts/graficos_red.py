# -*- coding: utf-8 -*-
"""
graficos_red.py — figura de barras (velocidad y latencia) a partir de resultados.csv.

El CSV tiene las columnas: conexion,prueba,bajada_mbps,subida_mbps,ping_ms
(una fila por prueba; las crea medir_red.ps1). Se agrupa por conexión: promedio y
desviación estándar.

Uso:
    python -I graficos_red.py "<carpeta con resultados.csv>" [--salida figura1_velocidad.png]
"""
import argparse
import csv
import statistics as st
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('carpeta')
    ap.add_argument('--salida', default='figura1_velocidad.png')
    a = ap.parse_args()
    base = Path(a.carpeta)
    filas = list(csv.DictReader(open(base / 'resultados.csv', encoding='utf-8-sig')))
    conexiones = list(dict.fromkeys(f['conexion'] for f in filas))

    def vals(c, col):
        return [float(f[col]) for f in filas if f['conexion'] == c]

    def prom(c, col): return st.mean(vals(c, col))
    def desv(c, col):
        v = vals(c, col)
        return st.pstdev(v) if len(v) > 1 else 0

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={'width_ratios': [2, 1]})
    x = list(range(len(conexiones)))
    w = 0.35
    b1 = ax1.bar([i - w / 2 for i in x], [prom(c, 'bajada_mbps') for c in conexiones], w,
                 yerr=[desv(c, 'bajada_mbps') for c in conexiones], capsize=4, label='Bajada', color='#1B3247')
    b2 = ax1.bar([i + w / 2 for i in x], [prom(c, 'subida_mbps') for c in conexiones], w,
                 yerr=[desv(c, 'subida_mbps') for c in conexiones], capsize=4, label='Subida', color='#6FA8DC')
    ax1.set_xticks(x); ax1.set_xticklabels(conexiones)
    ax1.set_ylabel('Velocidad (Mbps)'); ax1.set_title('Velocidad promedio')
    ax1.bar_label(b1, fmt='%.1f', padding=3); ax1.bar_label(b2, fmt='%.1f', padding=3)
    ax1.legend(frameon=False)
    ax1.set_ylim(0, max(prom(c, 'bajada_mbps') for c in conexiones) * 1.3)

    b3 = ax2.bar(x, [prom(c, 'ping_ms') for c in conexiones], 0.5,
                 yerr=[desv(c, 'ping_ms') for c in conexiones], capsize=4, color='#999999')
    ax2.set_xticks(x); ax2.set_xticklabels(conexiones)
    ax2.set_ylabel('Latencia (ms)'); ax2.set_title('Latencia promedio')
    ax2.bar_label(b3, fmt='%.0f', padding=3)
    ax2.set_ylim(0, max(prom(c, 'ping_ms') + desv(c, 'ping_ms') for c in conexiones) * 1.3)
    for ax in (ax1, ax2):
        ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout()
    destino = base / a.salida
    fig.savefig(destino, dpi=200)
    print('Guardado:', destino)
    print('\nPromedios (para la tabla del informe):')
    for c in conexiones:
        print(f'  {c}: bajada {prom(c,"bajada_mbps"):.1f} | subida {prom(c,"subida_mbps"):.1f} | ping {prom(c,"ping_ms"):.0f} ms')


if __name__ == '__main__':
    main()
