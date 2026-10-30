# -*- coding: utf-8 -*-
"""
inventario.py — radiografía de la carpeta de un proyecto de titulación antes de
reorganizarla: tamaño por carpeta de primer nivel, archivos grandes y
candidatos a revisar (videos, comprimidos, PDF de artículos, entornos, .env,
copias de respaldo, archivos temporales de Office, scripts .bat de otros
productos). Solo lee; no mueve ni borra nada.

Uso:
    python inventario.py <raíz> [--grande-mb 50] [--json inventario.json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

PESADOS_DIRS = {'node_modules', 'venv', '.venv', '__pycache__', 'dist', 'build', '.git', '.pytest_cache', 'site-packages'}
REGLAS = [
    ('video', re.compile(r'(?i)\.(mp4|mov|avi|mkv|webm)$')),
    ('comprimido', re.compile(r'(?i)\.(zip|rar|7z|tar|gz)$')),
    ('pdf (posible artículo con derechos)', re.compile(r'(?i)\.pdf$')),
    ('secreto local (.env)', re.compile(r'(^|/)\.env($|\.)(?!example)')),
    ('respaldo o copia', re.compile(r'(?i)(\.bak|\.old|_old|_copia|copia de|backup|\(\d\))')),
    ('temporal de Office', re.compile(r'(^|/)~\$')),
    ('script .bat', re.compile(r'(?i)\.bat$')),
    ('entorno virtual roto o duplicado', re.compile(r'(?i)(^|/)venv_[^/]+/')),
]


def tam_carpeta(p: Path) -> int:
    total = 0
    for d, _, fs in os.walk(p):
        for f in fs:
            try:
                total += (Path(d) / f).stat().st_size
            except OSError:
                pass
    return total


def inventario(raiz: Path, grande_mb: float) -> dict:
    primer_nivel = []
    for p in sorted(raiz.iterdir()):
        if p.name == '.git':
            continue
        b = tam_carpeta(p) if p.is_dir() else p.stat().st_size
        primer_nivel.append({'ruta': p.name + ('/' if p.is_dir() else ''), 'mb': round(b / 1e6, 1)})
    grandes, candidatos = [], {}
    for d, subdirs, fs in os.walk(raiz):
        rel_d = Path(d).relative_to(raiz).as_posix()
        for s in list(subdirs):
            if s in PESADOS_DIRS:
                if s != '.git':
                    candidatos.setdefault('dependencias o cachés (se regeneran)', []).append(f'{rel_d}/{s}'.lstrip('./'))
                subdirs.remove(s)
        for f in fs:
            rel = f'{rel_d}/{f}'.lstrip('./') if rel_d != '.' else f
            try:
                mb = (Path(d) / f).stat().st_size / 1e6
            except OSError:
                continue
            if mb >= grande_mb:
                grandes.append({'ruta': rel, 'mb': round(mb, 1)})
            for nombre, rx in REGLAS:
                if rx.search(rel):
                    candidatos.setdefault(nombre, []).append(rel)
    return {'primer_nivel': primer_nivel, 'grandes': sorted(grandes, key=lambda x: -x['mb']), 'candidatos': candidatos}


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('raiz')
    ap.add_argument('--grande-mb', type=float, default=50)
    ap.add_argument('--json')
    a = ap.parse_args()
    inv = inventario(Path(a.raiz).resolve(), a.grande_mb)
    print('Primer nivel (MB):')
    for x in sorted(inv['primer_nivel'], key=lambda x: -x['mb']):
        print(f"  {x['mb']:>9.1f}  {x['ruta']}")
    print(f'\nArchivos de {a.grande_mb:g} MB o más: {len(inv["grandes"])}')
    for x in inv['grandes'][:30]:
        print(f"  {x['mb']:>9.1f}  {x['ruta']}")
    print('\nCandidatos a revisar:')
    for k, v in inv['candidatos'].items():
        print(f'  {k}: {len(v)}  (p. ej. {", ".join(v[:3])})')
    if a.json:
        Path(a.json).write_text(json.dumps(inv, indent=2, ensure_ascii=False), encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
