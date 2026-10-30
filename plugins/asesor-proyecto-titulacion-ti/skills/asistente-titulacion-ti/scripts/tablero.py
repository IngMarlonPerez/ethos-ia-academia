# -*- coding: utf-8 -*-
"""
tablero.py — estado del pipeline del proyecto de titulación.

    python tablero.py estado                         etapa actual, controles pendientes y siguiente skill
    python tablero.py marcar 3 cerrada --nota "…"    registra el cierre (o en_curso / pendiente / no_aplica)
    python tablero.py avance 2                       cambia el avance actual
    python tablero.py regenerar                      reescribe 00_Control_Titulacion.md desde titulacion.json

Se ejecuta desde cualquier carpeta dentro del proyecto (busca titulacion.json hacia arriba).
"""
from __future__ import annotations

import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLUGIN / 'scripts_comunes'))
from perfil import cargar_proyecto, escribir_json  # noqa: E402
from pipeline import ESTADOS, ETAPAS, escribir_tablero, estado_inicial, etapa_actual, marcar  # noqa: E402


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 2 or sys.argv[1] not in ('estado', 'marcar', 'avance', 'regenerar'):
        print(__doc__)
        return 2
    proyecto, perfil, raiz = cargar_proyecto('.')
    proyecto.setdefault('etapas', estado_inicial())
    orden = sys.argv[1]
    if orden == 'marcar':
        n, estado = int(sys.argv[2]), sys.argv[3]
        nota = sys.argv[sys.argv.index('--nota') + 1] if '--nota' in sys.argv else ''
        marcar(proyecto, n, estado, nota)
    elif orden == 'avance':
        proyecto['avance_actual'] = int(sys.argv[2])
    if orden != 'estado':
        escribir_json(raiz / 'titulacion.json', proyecto)
        print(f'Tablero actualizado: {escribir_tablero(raiz, proyecto)}')
    e = etapa_actual(proyecto)
    print(f"Proyecto: {proyecto.get('tema')} · Perfil {perfil['id']} · Avance {proyecto.get('avance_actual', 1)}")
    for et in ETAPAS:
        st = proyecto['etapas'].get(str(et['n']), {}).get('estado', 'pendiente')
        print(f"  {ESTADOS[st]} {et['n']:>2} · {et['nombre']}")
    print(f"\nSiguiente: etapa {e['n']} · {e['nombre']} → skill(s): {', '.join(e['skills'])}")
    print(f"Control para cerrarla: {e['control']}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
