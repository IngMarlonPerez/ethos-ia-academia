# -*- coding: utf-8 -*-
"""
renderizar_diagramas.py — convierte los diagramas Mermaid (.mmd) del proyecto
a PNG con mermaid-cli (mmdc) usando el navegador ya instalado (Edge o Chrome),
sin descargar Chromium.

Además:
  - avisa si un PNG queda demasiado alto o demasiado plano para una página
    (a 6,2 pulgadas de ancho se vuelve ilegible): reorganiza el diagrama
    (subgrafos con direction TB/LR, enlaces entre subgrafos);
  - con --perfil, comprueba que exista al menos un diagrama de cada tipo UML
    exigido. Convención de nombres: uml_<tipo>_<tema>.mmd, con <tipo> en
    secuencia, colaboracion, estados, actividades, flujo_trabajo,
    entidad_relacion, casos_uso, arquitectura, despliegue.

Requisito: Node.js y @mermaid-js/mermaid-cli instalado en el proyecto
(npm install --save-dev @mermaid-js/mermaid-cli). El script NO lo instala.

Uso:
    python renderizar_diagramas.py diagramas/ [--escala 2] [--perfil unemi] [--solo uml_secuencia_login.mmd]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLUGIN / 'scripts_comunes'))
from perfil import cargar_perfil  # noqa: E402

def _headless_de_puppeteer() -> list[str]:
    """Chrome sin interfaz que puppeteer ya haya descargado: es el más confiable
    (Edge abierto con la sesión de la usuaria a veces no acepta otra instancia)."""
    base = Path.home() / '.cache' / 'puppeteer'
    return [str(p) for p in sorted(base.glob('chrome-headless-shell/*/*/chrome-headless-shell*'), reverse=True)
            if p.suffix in ('.exe', '')] + [str(p) for p in sorted(base.glob('chrome/*/*/chrome.exe'), reverse=True)]


NAVEGADORES = _headless_de_puppeteer() + [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/microsoft-edge',
]
RELACION_MAX, RELACION_MIN = 3.2, 0.35   # ancho/alto aceptable para una página vertical


def buscar_mmdc(desde: Path) -> list[str] | None:
    for carpeta in [desde, *desde.parents]:
        for nombre in ('mmdc.cmd', 'mmdc'):
            ruta = carpeta / 'node_modules' / '.bin' / nombre
            if ruta.exists():
                return [str(ruta)]
    global_ = shutil.which('mmdc')
    return [global_] if global_ else None


def configurar_navegador(carpeta: Path, ruta: str | None) -> Path:
    cfg = carpeta / 'puppeteer.json'
    if cfg.exists() and not ruta:
        return cfg
    nav = ruta or next((n for n in NAVEGADORES if Path(n).exists()), None)
    if not nav:
        sys.exit('No encontré Edge ni Chrome. Pasa la ruta con --navegador.')
    # Escribir JSON con json.dumps evita barras invertidas mal escapadas.
    cfg.write_text(json.dumps({'executablePath': nav, 'args': ['--no-sandbox']}, indent=2), encoding='utf-8')
    return cfg


def tamano_png(ruta: Path) -> tuple[int, int]:
    with open(ruta, 'rb') as f:
        cabecera = f.read(24)
    return struct.unpack('>II', cabecera[16:24])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('carpeta')
    ap.add_argument('--escala', default='2', help='factor de escala del PNG (mmdc -s); no uses -w')
    ap.add_argument('--navegador')
    ap.add_argument('--mmdc', help='ruta de mmdc si no está en node_modules/.bin del proyecto ni en el PATH')
    ap.add_argument('--perfil')
    ap.add_argument('--solo', nargs='*')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    carpeta = Path(a.carpeta).resolve()
    mmdc = [a.mmdc] if a.mmdc else buscar_mmdc(carpeta)
    if not mmdc:
        print('No está mermaid-cli. Pide autorización a la usuaria y ejecuta en la raíz del proyecto:\n'
              '  npm install --save-dev @mermaid-js/mermaid-cli\n'
              '(con la variable PUPPETEER_SKIP_DOWNLOAD=1 para no bajar Chromium: se usa Edge/Chrome).')
        return 1
    cfg = configurar_navegador(carpeta, a.navegador)
    entorno = dict(os.environ, PUPPETEER_SKIP_DOWNLOAD='1')
    fuentes = [carpeta / s for s in a.solo] if a.solo else sorted(carpeta.glob('*.mmd'))
    fallas, avisos = [], []
    for mmd in fuentes:
        png = mmd.with_suffix('.png')
        r = subprocess.run(mmdc + ['-i', str(mmd), '-o', str(png), '-s', str(a.escala), '-b', 'white', '-p', str(cfg)],
                           capture_output=True, text=True, encoding='utf-8', errors='replace', env=entorno)
        if (r.returncode != 0 or not png.exists()) and 'launch the browser' in (r.stderr + r.stdout):
            fallas.append(f'{mmd.name}: el navegador no arrancó ({json.loads(cfg.read_text(encoding="utf-8"))["executablePath"]}). '
                          'Cierra Edge o pasa otro con --navegador (p. ej. chrome-headless-shell de ~/.cache/puppeteer).')
            break
        if r.returncode != 0 or not png.exists():
            fallas.append(f'{mmd.name}: {(r.stderr or r.stdout).strip()[:400]}')
            continue
        ancho, alto = tamano_png(png)
        rel = ancho / alto
        estado = 'OK'
        if rel > RELACION_MAX:
            estado = 'MUY PLANO'
            avisos.append(f'{mmd.name}: {ancho}×{alto} px, demasiado plano; usa subgrafos con direction TB o flowchart TB.')
        elif rel < RELACION_MIN:
            estado = 'MUY ALTO'
            avisos.append(f'{mmd.name}: {ancho}×{alto} px, demasiado alto; usa flowchart LR con subgrafos direction TB.')
        print(f'  {estado:9} {png.name} ({ancho}×{alto})')
    if a.perfil:
        exigidos = cargar_perfil(a.perfil).get('requisitos', {}).get('uml_exigidos', [])
        nombres = ' '.join(p.stem.lower() for p in carpeta.glob('*.mmd'))
        faltan = [t for t in exigidos if f'uml_{t}' not in nombres]
        if faltan:
            fallas.append(f"faltan diagramas exigidos por el perfil: {', '.join(faltan)} (nombre: uml_<tipo>_<tema>.mmd)")
    for x in avisos:
        print('  AVISO:', x)
    for x in fallas:
        print('  ERROR:', x)
    return 1 if fallas else 0


if __name__ == '__main__':
    sys.exit(main())
