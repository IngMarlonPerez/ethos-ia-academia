# -*- coding: utf-8 -*-
"""
render_consola.py — convierte TEXTO REAL de una consola (salida de un comando, transcripción
de una terminal, log) en una imagen PNG con aspecto de consola, para usarla como evidencia.

La imagen se rotula siempre en la barra superior (p. ej. «salida real», «transcripción de la
terminal de la sesión», «extracto: se omiten las líneas de progreso»). No se maquilla ni se
inventa texto: el contenido es el que se pasa en el archivo.

Uso:
    python -I render_consola.py salida.txt imagen.png --titulo "Windows PowerShell · Prueba de cifrado · 22/10/2026"
        [--enmascarar-ip-privadas] [--ancho 1280]

Las líneas que empiezan con «PS ...>», «PS> » o «$ » se resaltan como comando.
Con --enmascarar-ip-privadas, las direcciones 192.168.x.y, 172.16-31.x.y y 10.x.y.z se muestran
como 192.168.x.x / etc. (útil para pathping, ipconfig o netsh).

Fuente del texto cuando viene de las pestañas de terminal de la app: herramienta
mcp__terminal__read_terminal (tab_id) → copiar el texto original, sin editarlo.
"""
import argparse
import html
import re
import subprocess
import sys
from pathlib import Path

CSS = """body{margin:0;background:#0c0c0c;color:#cccccc;font-family:Consolas,'Cascadia Mono',monospace;font-size:15px}
.bar{background:#1f1f1f;color:#ddd;padding:8px 16px;font-family:Segoe UI,Arial;font-size:13px}
pre{margin:0;padding:16px 20px;line-height:1.5;white-space:pre-wrap}.c{color:#f9f1a5}"""
HTML_A_PNG = Path(__file__).with_name('html_a_png.ps1')


def enmascarar(t: str) -> str:
    t = re.sub(r'\b192\.168\.\d{1,3}\.\d{1,3}\b', '192.168.x.x', t)
    t = re.sub(r'\b172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}\b', '172.x.x.x', t)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('texto')
    ap.add_argument('png')
    ap.add_argument('--titulo', required=True)
    ap.add_argument('--ancho', type=int, default=1280)
    ap.add_argument('--enmascarar-ip-privadas', action='store_true')
    a = ap.parse_args()
    t = Path(a.texto).read_text(encoding='utf-8', errors='replace')
    t = t.replace('�nimo', 'ínimo').replace('�ximo', 'áximo')   # acentos del ping en consolas OEM
    if a.enmascarar_ip_privadas:
        t = enmascarar(t)
    cuerpo = []
    for l in t.strip('\n').splitlines():
        e = html.escape(l)
        m = re.match(r'^(PS[^>]*>|\$)(.*)$', l)
        if m:
            e = html.escape(m.group(1)) + '<span class="c">' + html.escape(m.group(2)) + '</span>'
        cuerpo.append(e)
    pagina = (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}body{{width:{a.ancho}px}}</style></head>'
              f'<body><div class="bar">{html.escape(a.titulo)}</div><pre>' + '\n'.join(cuerpo) + '</pre></body></html>')
    png = Path(a.png)
    png.parent.mkdir(parents=True, exist_ok=True)
    hp = png.with_suffix('.html')
    hp.write_text(pagina, encoding='utf-8')
    alto = 40 + 24 * (len(cuerpo) + 1)
    subprocess.run(['pwsh', '-NoProfile', '-File', str(HTML_A_PNG), '-Origen', str(hp), '-Png', str(png),
                    '-Ancho', str(a.ancho), '-Alto', str(alto)], check=True)
    print('Imagen:', png)


if __name__ == '__main__':
    sys.exit(main())
