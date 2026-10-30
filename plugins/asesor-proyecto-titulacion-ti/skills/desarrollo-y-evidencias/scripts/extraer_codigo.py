# -*- coding: utf-8 -*-
"""
extraer_codigo.py — muestra el fragmento de código que el generador del Word
insertará (mismas funciones que docx_titulacion.funcion_py / fragmento).

Uso:
    python extraer_codigo.py backend/ml/entrenar.py entrenar_modelo          # función/clase/asignación de Python
    python extraer_codigo.py src/services/api.js "export async function consultar" "^}"   # desde … hasta
      (hasta que empieza con ^ = línea exacta, sin espacios: ^} → la primera línea que sea solo «}»)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'documento-titulacion' / 'scripts'))
from docx_titulacion import fragmento, funcion_py  # noqa: E402


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) not in (3, 4):
        print(__doc__)
        return 2
    ruta = sys.argv[1]
    if len(sys.argv) == 3:
        texto = funcion_py(ruta, sys.argv[2])
    else:
        hasta = sys.argv[3]
        texto = fragmento(ruta, sys.argv[2], hasta[1:], exacto=True) if hasta.startswith('^') else fragmento(ruta, sys.argv[2], hasta)
    print(texto)
    print(f'\n({len(texto.splitlines())} líneas)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
