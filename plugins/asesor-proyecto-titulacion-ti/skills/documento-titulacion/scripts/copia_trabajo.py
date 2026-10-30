# -*- coding: utf-8 -*-
"""
copia_trabajo.py — crea una COPIA VERSIONADA del Word a partir del archivo original (o de la última
versión de la usuaria) y guarda su huella. El original nunca se modifica.

    python copia_trabajo.py documento/Avance_2.docx                 # siguiente versión libre: Avance_2_v02.docx
    python copia_trabajo.py documento/Avance_2.docx --version 3
    python copia_trabajo.py documento/Avance_2.docx --destino documento/versiones

Resultado: BASE_vNN.docx y BASE_vNN.huella.json (portada, encabezados, pies, secciones y estilos).
Si la usuaria edita el Word a mano, la copia nueva se hace desde SU archivo, no desde el del generador.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts_comunes'))
import versionado_docx as vd  # noqa: E402


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('original')
    ap.add_argument('--version', type=int)
    ap.add_argument('--destino')
    ap.add_argument('--nombre')
    a = ap.parse_args()
    try:
        docx_, huella_ = vd.crear_copia_versionada(a.original, a.version, a.destino, a.nombre)
    except FileExistsError as e:
        print(e, file=sys.stderr)
        return 1
    print(docx_)
    print(huella_)
    return 0


if __name__ == '__main__':
    sys.exit(main())
