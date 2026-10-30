# -*- coding: utf-8 -*-
"""
sistema_experto.py — sistema experto basado en reglas (didáctico).

Motor de encadenamiento hacia adelante: una regla se activa si TODAS sus condiciones
están entre los hechos del caso; si se activan varias, gana la que tiene más
condiciones (la más específica). Cada conclusión indica la regla que la produjo
(trazabilidad: la ventaja del sistema experto frente a un modelo generativo).

Uso:
    python -I sistema_experto.py reglas.json casos.json [--salida salida.txt]

reglas.json:  {"R1": {"si": ["fiebre_alta", "..."], "entonces": "Cuadro compatible con ..."}, ...}
casos.json:   {"Caso 1": ["fiebre_alta", "tos_seca", ...], ...}

Es un ejercicio educativo: los diagnósticos simulados NO sustituyen a un profesional.
"""
import argparse
import json
import sys
from pathlib import Path


def inferir(reglas: dict, hechos: set):
    mejor = None
    for nombre, r in reglas.items():
        cond = set(r['si'])
        if cond <= hechos and (mejor is None or len(cond) > len(reglas[mejor]['si'])):
            mejor = nombre
    return mejor


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('reglas')
    ap.add_argument('casos')
    ap.add_argument('--salida')
    a = ap.parse_args()
    reglas = json.loads(Path(a.reglas).read_text(encoding='utf-8'))
    casos = json.loads(Path(a.casos).read_text(encoding='utf-8'))
    lineas = []
    for caso, hechos in casos.items():
        r = inferir(reglas, set(hechos))
        if r:
            lineas.append(f"{caso}: {reglas[r]['entonces']} | Regla {r}: {' + '.join(sorted(reglas[r]['si']))}")
        else:
            lineas.append(f"{caso}: sin regla aplicable (fuera de la base de conocimiento)")
    texto = '\n'.join(lineas)
    print(texto)
    if a.salida:
        Path(a.salida).write_text(texto + '\n', encoding='utf-8')


if __name__ == '__main__':
    sys.exit(main())
