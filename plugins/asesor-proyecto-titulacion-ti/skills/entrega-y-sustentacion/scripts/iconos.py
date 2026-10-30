# -*- coding: utf-8 -*-
"""
iconos.py — banco de íconos propio (85 íconos de línea, licencia ISC de Lucide) en blanco, marino, naranja y gris.

    python iconos.py                          # lista todos los nombres con sus etiquetas
    python iconos.py --buscar servidor        # busca por nombre o etiqueta
    python iconos.py --ruta candado --color marino   # ruta del PNG (256 px) para diapositivas o póster

En el JSON de diapositivas basta con «icono»: «candado». Los SVG editables están en assets/iconos/svg/.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts_comunes'))
from presentaciones import diapositivas  # noqa: E402


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--buscar')
    ap.add_argument('--ruta')
    ap.add_argument('--color', default='marino', choices=['blanco', 'marino', 'naranja', 'gris'])
    a = ap.parse_args()
    if a.ruta:
        r = diapositivas.icono(a.ruta, a.color)
        print(r or f'No existe el ícono «{a.ruta}» en color {a.color}')
        return 0 if r else 1
    for nombre, v in sorted(diapositivas.lista_iconos().items()):
        if not a.buscar or a.buscar.lower() in (nombre + ' ' + v['etiquetas']).lower():
            print(f'{nombre:22} {v["etiquetas"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
