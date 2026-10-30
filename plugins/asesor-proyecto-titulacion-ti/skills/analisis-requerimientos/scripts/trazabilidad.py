# -*- coding: utf-8 -*-
"""
trazabilidad.py — valida requerimientos/requerimientos.json y genera las
tablas de la sección 2.1 (alternativas, actores, HU, RF, RNF, métricas y
matriz de trazabilidad objetivo → HU → RF → componente → prueba).

Control de la etapa 3:
  - al menos `min_alternativas_solucion` alternativas y una seleccionada;
  - cada objetivo específico tiene ≥ 1 historia, ≥ 1 RF y ≥ 1 métrica;
  - cada historia tiene criterios Dado/Cuando/Entonces y cada RF su historia;
  - cada RF y RNF tiene al menos una prueba declarada en "pruebas";
  - hay al menos un RNF de privacidad;
  - (con --repo) el archivo de implementación de cada RF y el de cada prueba existen.

Uso:
    python trazabilidad.py requerimientos/requerimientos.json [--perfil unemi] [--repo ../codigo] [--tablas tablas.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLUGIN / 'scripts_comunes'))
from perfil import cargar_perfil, leer_json  # noqa: E402


def _reales(lista):
    return [x for x in lista if isinstance(x, dict) and not x.get('_ejemplo')]


def validar(datos: dict, perfil: dict, repo: Path | None = None) -> tuple[list[str], list[str]]:
    e, a = [], []
    req = perfil.get('requisitos', {})
    obj = _reales(datos.get('objetivos', []))
    alt = _reales(datos.get('alternativas', []))
    hu = _reales(datos.get('historias', []))
    rf = _reales(datos.get('rf', []))
    rnf = _reales(datos.get('rnf', []))
    met = _reales(datos.get('metricas', []))
    pr = {p['id']: p for p in _reales(datos.get('pruebas', []))}
    if any(x.get('_ejemplo') for k in ('objetivos', 'historias', 'rf', 'rnf', 'metricas', 'pruebas', 'alternativas')
           for x in datos.get(k, []) if isinstance(x, dict)):
        a.append('quedan elementos de ejemplo (_ejemplo) en requerimientos.json.')
    if not obj:
        e.append('no hay objetivos específicos.')
    minimo = req.get('min_alternativas_solucion', 3)
    if len(alt) < minimo:
        e.append(f'{len(alt)} alternativas de solución (mínimo {minimo}).')
    if alt and not any(x.get('seleccionada') for x in alt):
        e.append('ninguna alternativa está marcada como seleccionada.')
    for o in obj:
        oid = o['id']
        if not any(oid in h.get('objetivos', []) for h in hu):
            e.append(f'{oid} no tiene historias de usuario.')
        if not any(r.get('objetivo') == oid for r in rf):
            e.append(f'{oid} no tiene requerimientos funcionales.')
        if not any(m.get('objetivo') == oid for m in met):
            e.append(f'{oid} no tiene métrica de calidad.')
    ids_hu = {h['id'] for h in hu}
    for h in hu:
        crit = h.get('criterios', [])
        if not crit or not all(c.get('dado') and c.get('cuando') and c.get('entonces') for c in crit):
            e.append(f"{h['id']}: criterios de aceptación incompletos (Dado/Cuando/Entonces).")
    for r in rf:
        if not set(r.get('historias', [])) & ids_hu:
            e.append(f"{r['id']}: no está ligado a ninguna historia de usuario.")
    for r in rf + rnf:
        pruebas = r.get('pruebas', [])
        if not pruebas:
            e.append(f"{r['id']}: no tiene prueba.")
        for p in pruebas:
            if p not in pr:
                e.append(f"{r['id']}: la prueba {p} no está declarada en «pruebas».")
    if not any('privac' in (x.get('atributo', '') + x.get('requerimiento', '')).lower() for x in rnf):
        e.append('falta un RNF de privacidad / protección de datos personales.')
    for m in met:
        if not m.get('meta'):
            e.append(f"{m['id']}: métrica sin meta.")
    if repo is not None:
        for r in rf:
            ruta = r.get('implementacion')
            if ruta and not (repo / ruta).exists():
                e.append(f"{r['id']}: no existe el archivo de implementación {ruta}.")
        for p in pr.values():
            if p.get('archivo') and not (repo / p['archivo']).exists():
                a.append(f"{p['id']}: no existe {p['archivo']} en el repositorio.")
    return e, a


def tablas(datos: dict) -> dict[str, list[list[str]]]:
    obj = _reales(datos.get('objetivos', []))
    hu = _reales(datos.get('historias', []))
    rf = _reales(datos.get('rf', []))
    rnf = _reales(datos.get('rnf', []))
    met = _reales(datos.get('metricas', []))
    alt = _reales(datos.get('alternativas', []))
    actores = {x['id']: x for x in _reales(datos.get('actores', []))}
    crit = datos.get('criterios_alternativas', [])
    matriz = {k: v for k, v in datos.get('matriz_alternativas', {}).items() if not k.startswith('_')}
    t = {
        'alternativas': [['Criterio'] + [x['nombre'] + (' (seleccionada)' if x.get('seleccionada') else '') for x in alt]]
        + [[c] + [matriz.get(x['id'], {}).get(c, '') for x in alt] for c in crit],
        'actores': [['Actor', 'Perfil', 'Necesidad principal', 'Conocimiento técnico']]
        + [[x['actor'], x.get('perfil', ''), x.get('necesidad', ''), x.get('conocimiento_tecnico', '')] for x in actores.values()],
        'historias': [['ID', 'Historia de usuario', 'Criterio de aceptación (Dado / Cuando / Entonces)', 'Pieza']]
        + [[h['id'], f"Como {h.get('como', '')}, quiero {h.get('quiero', '')} para {h.get('para', '')}.",
            ' '.join(f"*Dado* {c['dado']}, *cuando* {c['cuando']}, *entonces* {c['entonces']}." for c in h.get('criterios', [])),
            h.get('pieza', '')] for h in hu],
        'rf': [['ID', 'Pieza', 'Requerimiento funcional', 'HU', 'Obj.', 'Implementación']]
        + [[r['id'], r.get('pieza', ''), r.get('requerimiento', ''), ', '.join(r.get('historias', [])), r.get('objetivo', ''),
            r.get('implementacion', '')] for r in rf],
        'rnf': [['ID', 'Atributo (ISO/IEC 25010)', 'Requerimiento', 'Cómo se verifica']]
        + [[r['id'], f"{r.get('atributo', '')} ({r.get('iso25010', '')})", r.get('requerimiento', ''), r.get('verificacion', '')]
           for r in rnf],
        'metricas': [['Métrica', 'Pieza', 'Meta', 'Objetivo']]
        + [[m.get('metrica', ''), m.get('pieza', ''), m.get('meta', ''), m.get('objetivo', '')] for m in met],
        'trazabilidad': [['Objetivo específico', 'Historias', 'Requerimientos', 'Componente', 'Prueba o evidencia']],
    }
    for o in obj:
        h = [x['id'] for x in hu if o['id'] in x.get('objetivos', [])]
        r = [x for x in rf if x.get('objetivo') == o['id']]
        comps = sorted({x.get('pieza', '') for x in r if x.get('pieza')})
        pruebas = sorted({p for x in r for p in x.get('pruebas', [])} | {m['id'] for m in met if m.get('objetivo') == o['id']})
        t['trazabilidad'].append([f"{o['id']}. {o.get('texto', '')}", ', '.join(h), ', '.join(x['id'] for x in r),
                                  ', '.join(comps), ', '.join(pruebas)])
    return t


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('archivo')
    ap.add_argument('--perfil', default='unemi')
    ap.add_argument('--repo')
    ap.add_argument('--tablas', help='guardar las tablas para el Word en este JSON')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    datos = leer_json(a.archivo)
    e, av = validar(datos, cargar_perfil(a.perfil, Path(a.archivo).resolve().parent), Path(a.repo) if a.repo else None)
    if a.tablas:
        Path(a.tablas).write_text(json.dumps(tablas(datos), indent=1, ensure_ascii=False), encoding='utf-8')
        print(f'Tablas guardadas en {a.tablas}')
    for x in av:
        print('  AVISO:', x)
    for x in e:
        print('  ERROR:', x)
    print('Trazabilidad completa.' if not e else f'{len(e)} problemas de trazabilidad.')
    return 1 if e else 0


if __name__ == '__main__':
    sys.exit(main())
