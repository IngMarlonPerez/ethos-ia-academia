# -*- coding: utf-8 -*-
"""
aserciones.py — detecta si un guardado desde un Word viejo REVIRTIÓ una corrección ya hecha.

Cada corrección aplicada se registra en documento/aserciones.json:
    [{"descripcion": "Cifra de ROC-AUC corregida", "contiene": "0,912", "no_contiene": "0,91 "}]

    python aserciones.py registrar documento/aserciones.json "Descripción" --contiene "texto nuevo" --no-contiene "texto viejo"
    python aserciones.py verificar documento/Avance_2.docx documento/aserciones.json

Antes de editar o regenerar, verifica: si alguna falla, INFORMA a la usuaria y pregunta antes de reaplicarla.
Códigos de salida: 0 todas vigentes · 1 alguna revertida.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts_comunes'))
import versionado_docx as vd  # noqa: E402


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='accion', required=True)
    r = sub.add_parser('registrar')
    r.add_argument('archivo')
    r.add_argument('descripcion')
    r.add_argument('--contiene')
    r.add_argument('--no-contiene', dest='no_contiene')
    v = sub.add_parser('verificar')
    v.add_argument('doc')
    v.add_argument('archivo')
    a = ap.parse_args()

    ruta = Path(a.archivo)
    lista = json.loads(ruta.read_text(encoding='utf-8')) if ruta.exists() else []
    if a.accion == 'registrar':
        if not (a.contiene or a.no_contiene):
            ap.error('indica --contiene y/o --no-contiene')
        lista.append({k: v for k, v in {'descripcion': a.descripcion, 'contiene': a.contiene,
                                         'no_contiene': a.no_contiene}.items() if v})
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'Registrada ({len(lista)} en total).')
        return 0
    fallas = vd.verificar_aserciones(a.doc, lista)
    for desc, motivo in fallas:
        print(f'REVERTIDA: {desc} → {motivo}')
    print(f'{len(lista) - len({d for d, _ in fallas})} de {len(lista)} correcciones siguen vigentes.'
          if fallas else f'Todas las correcciones siguen vigentes ({len(lista)}).')
    return 1 if fallas else 0


if __name__ == '__main__':
    sys.exit(main())
