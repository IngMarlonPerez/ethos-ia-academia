# -*- coding: utf-8 -*-
"""
poster.py — póster académico de 3 columnas (A0 por defecto): PPTX editable + PDF de imprenta + vista previa PNG.
El tamaño de letra se ajusta solo para que todo quepa (sin bajar del mínimo).

    python poster.py contenido.json -o documento/Poster_Apellido1_Apellido2 [--logo logo_blanco.png]

Bloques: seccion, parrafo, lista, numerados, cifras, tarjeta, destacado, figura, grafico, diagrama.
Ver plantillas/poster-ejemplo.json. Autores, tutor y carrera se toman de titulacion.json, nunca de memoria.
Adaptado del plugin «proyectos-academicos» (V. M. Lluilema Pisco).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts_comunes'))
from presentaciones import poster  # noqa: E402


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('contenido')
    ap.add_argument('-o', '--salida', required=True)
    ap.add_argument('--logo')
    a = ap.parse_args()
    print(json.dumps(poster.generar(a.contenido, a.salida, logo=a.logo or None), ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
