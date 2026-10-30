# -*- coding: utf-8 -*-
"""
diapositivas.py — presentación completa desde un JSON, con tamaño de letra adaptativo por diapositiva.

    python diapositivas.py contenido.json -o documento/Sustentacion_Apellido1_Apellido2.pptx

El JSON indica «plantilla» (ruta a la plantilla institucional .pptx; vacío = diseño UNEMI básico 16:9), «portada»,
«diapositivas» y «notas» por diapositiva (guion del orador). Tipos: agenda, texto, tarjetas, cifras, diagrama, imagen,
tabla, comparativa, conclusiones, referencias, cita y cierre. Ver plantillas/diapositivas-ejemplo.json.
El cuerpo de cada diapositiva usa el mayor tamaño que cabe; si no cabe ni con el mínimo, avisa.
Adaptado del plugin «proyectos-academicos» (V. M. Lluilema Pisco).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts_comunes'))
from presentaciones import diapositivas  # noqa: E402


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('contenido')
    ap.add_argument('-o', '--salida', required=True)
    a = ap.parse_args()
    r = diapositivas.generar(a.contenido, a.salida)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    if r.get('avisos'):
        print('\nRevisar los avisos antes de entregar.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
