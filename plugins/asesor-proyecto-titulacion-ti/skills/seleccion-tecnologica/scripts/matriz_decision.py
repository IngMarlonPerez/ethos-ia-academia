# -*- coding: utf-8 -*-
"""
matriz_decision.py — matriz de decisión multicriterio ponderada con análisis
de sensibilidad y registro de decisión de arquitectura (ADR).

Sirve para las decisiones tecnológicas (lenguaje, framework, base de datos…)
y para la de estilo de arquitectura. Entrada: decisiones/DT-NN_<tema>.json
(ver plantillas/decision.json).

Qué hace:
  1. Valida: pesos que suman 100; al menos N candidatas (del perfil); cada
     celda con puntaje 1–5, justificación y fuente; ninguna fuente de prensa/blog.
  2. Calcula el puntaje ponderado (sobre 5) y el ranking.
  3. Sensibilidad: sube y baja cada peso un 20 % (renormalizando el resto) y
     comprueba si cambia la ganadora. Si cambia, la decisión es INESTABLE y
     se resuelve con el criterio de desempate declarado.
  4. Exporta: tabla para el Word (JSON), Excel con todas las decisiones y el
     ADR en Markdown (decisiones/adr/ADR-NN-<tema>.md).

Uso:
    python matriz_decision.py decisiones/DT-01_lenguaje.json [--perfil unemi] [--adr] [--tabla t.json]
    python matriz_decision.py decisiones/ --todas [--xlsx decisiones/Matriz_decisiones.xlsx] [--adr]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLUGIN / 'scripts_comunes'))
from formato_es import n  # noqa: E402
from perfil import cargar_perfil, leer_json  # noqa: E402

FUENTE_NO_VALIDA = re.compile(r'medium\.com|dev\.to|blog|wikipedia|reddit|stackoverflow\.com/questions|quora|diario|'
                              r'peri[oó]dico|geeksforgeeks|w3schools|tutorial|youtube', re.IGNORECASE)
VARIACION = 0.20


def _slug(s: str) -> str:
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'[^a-z0-9]+', '_', s).strip('_')[:40]


def validar(d: dict, perfil: dict) -> list[str]:
    e = []
    req = perfil.get('requisitos', {})
    minimo = req.get('min_estilos_arquitectura', 3) if d.get('tipo') == 'arquitectura' \
        else req.get('min_opciones_por_decision_tecnologica', 3)
    crit = d.get('criterios', [])
    cand = d.get('candidatas', [])
    total = sum(c.get('peso', 0) for c in crit)
    if abs(total - 100) > 1e-6:
        e.append(f'los pesos suman {total}, deben sumar 100.')
    if len(cand) < minimo:
        e.append(f'{len(cand)} candidatas (mínimo {minimo}).')
    for c in crit:
        if not c.get('origen'):
            e.append(f"criterio {c['id']} sin «origen» (RNF, objetivo o restricción de donde sale).")
    for k in cand:
        for c in crit:
            celda = k.get('puntajes', {}).get(c['id'])
            nombre = f"{k['nombre']} × {c['nombre']}"
            if not celda:
                e.append(f'{nombre}: sin puntaje.')
                continue
            if not (1 <= celda.get('valor', 0) <= 5):
                e.append(f'{nombre}: el puntaje debe estar entre 1 y 5.')
            if not celda.get('justificacion'):
                e.append(f'{nombre}: sin justificación.')
            fuente = celda.get('fuente', '')
            if not fuente:
                e.append(f'{nombre}: sin fuente.')
            elif FUENTE_NO_VALIDA.search(fuente):
                e.append(f'{nombre}: fuente no válida ({fuente}); usa artículos con DOI o documentación oficial.')
    return e


def puntajes(d: dict, pesos: dict | None = None) -> dict[str, float]:
    pesos = pesos or {c['id']: c['peso'] for c in d['criterios']}
    return {k['id']: sum(pesos[c] * k['puntajes'][c]['valor'] for c in pesos) / 100 for k in d['candidatas']}


def ganadora(p: dict[str, float]) -> str:
    return max(p, key=p.get)


def sensibilidad(d: dict) -> list[dict]:
    base = {c['id']: c['peso'] for c in d['criterios']}
    g0 = ganadora(puntajes(d))
    cambios = []
    for cid in base:
        for f in (1 - VARIACION, 1 + VARIACION):
            nuevo = dict(base)
            nuevo[cid] = base[cid] * f
            resto = sum(v for k, v in base.items() if k != cid)
            if resto:
                escala = (100 - nuevo[cid]) / resto
                for k in nuevo:
                    if k != cid:
                        nuevo[k] = base[k] * escala
            g = ganadora(puntajes(d, nuevo))
            if g != g0:
                cambios.append({'criterio': cid, 'factor': f, 'ganadora': g})
    return cambios


def resolver(d: dict) -> dict:
    p = puntajes(d)
    ranking = sorted(p.items(), key=lambda kv: -kv[1])
    cambios = sensibilidad(d)
    elegida = ranking[0][0]
    nota = 'estable: ninguna variación de ±20 % en un peso cambia la ganadora.'
    if cambios:
        desempate = d.get('desempate')
        empatadas = {ranking[0][0]} | {c['ganadora'] for c in cambios}
        if desempate:
            elegida = max(empatadas, key=lambda k: next(x for x in d['candidatas'] if x['id'] == k)['puntajes'][desempate]['valor'])
            nota = (f"INESTABLE: con ±20 % en {', '.join(sorted({c['criterio'] for c in cambios}))} cambia la ganadora "
                    f"({', '.join(sorted(empatadas))}); se resolvió con el criterio de desempate {desempate}.")
        else:
            nota = (f"INESTABLE: con ±20 % en {', '.join(sorted({c['criterio'] for c in cambios}))} cambia la ganadora; "
                    'declara un criterio de desempate («desempate»).')
    return {'puntajes': p, 'ranking': ranking, 'cambios': cambios, 'elegida': elegida, 'estabilidad': nota}


def tabla_word(d: dict, r: dict) -> list[list[str]]:
    nombres = {k['id']: k['nombre'] for k in d['candidatas']}
    filas = [['Criterio (peso)'] + [nombres[k] for k, _ in r['ranking']]]
    for c in d['criterios']:
        filas.append([f"{c['nombre']} ({c['peso']} %)"] +
                     [str(next(x for x in d['candidatas'] if x['id'] == k)['puntajes'][c['id']]['valor']) for k, _ in r['ranking']])
    filas.append(['**Puntaje ponderado (sobre 5)**'] + [f'**{n(v, 2)}**' for _, v in r['ranking']])
    return filas


def adr(d: dict, r: dict, numero: str) -> str:
    nombres = {k['id']: k['nombre'] for k in d['candidatas']}
    elegida = next(k for k in d['candidatas'] if k['id'] == r['elegida'])
    el = d.get('eleccion', {})
    lineas = [f"# ADR-{numero}: {d['decision']}", '',
              f"- **Estado:** {el.get('estado', 'Aceptada')} · **Fecha:** {el.get('fecha', date.today().isoformat())}",
              f"- **Decisión:** {elegida['nombre']}" + (f" (versión {elegida['version']})" if elegida.get('version') else ''), '',
              '## Contexto', '', d.get('contexto', ''), '',
              '## Criterios (origen → peso)', '']
    lineas += [f"- **{c['nombre']}** ({c['peso']} %): {c.get('descripcion', '')} *Origen:* {c.get('origen', '')}" for c in d['criterios']]
    lineas += ['', '## Opciones evaluadas', '']
    for k in d['candidatas']:
        lineas.append(f"### {k['nombre']} — {n(r['puntajes'][k['id']], 2)} / 5")
        for c in d['criterios']:
            celda = k['puntajes'][c['id']]
            lineas.append(f"- {c['nombre']}: **{celda['valor']}**. {celda['justificacion']} *Fuente:* {celda['fuente']}")
        lineas.append('')
    lineas += ['## Resultado', '', '| Opción | Puntaje |', '|---|---|']
    lineas += [f'| {nombres[k]} | {n(v, 2)} |' for k, v in r['ranking']]
    lineas += ['', f"**Sensibilidad:** {r['estabilidad']}", '',
               '## Decisión y razón', '', el.get('razon', '(completar: por qué la opción ganadora responde a los criterios)'), '',
               '## Consecuencias', '']
    lineas += [f'- {c}' for c in el.get('consecuencias', ['(completar: qué se gana, qué se sacrifica y qué riesgo queda)'])]
    if d.get('verificacion_codigo'):
        v = d['verificacion_codigo']
        lineas += ['', '## Verificación en el código', '',
                   f"`{v.get('archivo')}` debe fijar `{v.get('paquete')}` en la versión `{v.get('version')}` "
                   '(lo comprueba verificar_coherencia.py).']
    return '\n'.join(lineas) + '\n'


def verificar_versiones(carpeta: Path, repo: Path) -> tuple[list[str], list[str]]:
    """Compara verificacion_codigo de cada DT-*.json con lo que fija el repositorio."""
    e, a = [], []
    for ruta in sorted(Path(carpeta).glob('DT-*.json')):
        d = leer_json(ruta)
        v = d.get('verificacion_codigo')
        if not v:
            continue
        archivo = repo / v['archivo']
        if not archivo.exists():
            e.append(f"{ruta.name}: no existe {v['archivo']} en el repositorio.")
            continue
        texto = archivo.read_text(encoding='utf-8', errors='replace')
        paquete, version = v['paquete'], str(v['version'])
        encontrada = None
        if archivo.name == 'package.json':
            pj = json.loads(texto)
            for sec in ('dependencies', 'devDependencies', 'peerDependencies'):
                if paquete in pj.get(sec, {}):
                    encontrada = pj[sec][paquete].lstrip('^~>=')
        else:
            m = re.search(rf'(?im)^\s*"?{re.escape(paquete)}(?:\[[^\]]*\])?"?\s*(?:==|>=|~=|=|:)\s*"?([\w.\-+]+)', texto)
            encontrada = m.group(1) if m else None
        if encontrada is None:
            e.append(f"{ruta.name}: {paquete} no aparece en {v['archivo']}.")
        elif not encontrada.startswith(version):
            e.append(f"{ruta.name}: la decisión dice {paquete} {version}, pero {v['archivo']} fija {encontrada}.")
    return e, a


def procesar(ruta: Path, perfil: dict, con_adr: bool, tabla: str | None) -> tuple[dict, dict] | None:
    d = leer_json(ruta)
    errores = validar(d, perfil)
    print(f"\n{d.get('id', ruta.stem)} · {d['decision']}")
    if errores:
        for x in errores:
            print('  ERROR:', x)
        return None
    r = resolver(d)
    for k, v in r['ranking']:
        print(f"  {n(v, 2)}  {next(x['nombre'] for x in d['candidatas'] if x['id'] == k)}")
    print('  Sensibilidad:', r['estabilidad'])
    print('  Elegida:', next(x['nombre'] for x in d['candidatas'] if x['id'] == r['elegida']))
    if tabla:
        Path(tabla).write_text(json.dumps(tabla_word(d, r), indent=1, ensure_ascii=False), encoding='utf-8')
    if con_adr:
        numero = re.sub(r'\D', '', d.get('id', '')) or '00'
        numero = numero.zfill(3)
        destino = ruta.parent / 'adr' / f"ADR-{numero}-{_slug(d['decision'])}.md"
        destino.parent.mkdir(exist_ok=True)
        destino.write_text(adr(d, r, numero), encoding='utf-8')
        print('  ADR:', destino)
    return d, r


def exportar_xlsx(resultados: list[tuple[dict, dict]], salida: Path):
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    resumen = wb.create_sheet('Resumen')
    resumen.append(['Decisión', 'Tipo', 'Elegida', 'Puntaje', 'Segunda', 'Puntaje', 'Estabilidad'])
    for d, r in resultados:
        nombres = {k['id']: k['nombre'] for k in d['candidatas']}
        (g, pg), (s, ps) = r['ranking'][0], r['ranking'][1]
        resumen.append([d['decision'], d.get('tipo', 'tecnologia'), nombres[r['elegida']], round(pg, 2), nombres[s], round(ps, 2),
                        r['estabilidad']])
        ws = wb.create_sheet(d.get('id', 'DT')[:31])
        for fila in tabla_word(d, r):
            ws.append([x.replace('**', '') for x in fila])
    for ws in wb.worksheets:
        for c in ws[1]:
            c.font = Font(bold=True, color='FFFFFF')
            c.fill = PatternFill('solid', start_color='1F4E78')
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 28
            for c in col:
                c.alignment = Alignment(wrap_text=True, vertical='top')
    wb.save(str(salida))
    print('\nExcel:', salida)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('entrada', help='un DT-NN_*.json o la carpeta decisiones/ con --todas')
    ap.add_argument('--todas', action='store_true')
    ap.add_argument('--perfil', default='unemi')
    ap.add_argument('--adr', action='store_true', help='escribir el ADR en decisiones/adr/')
    ap.add_argument('--tabla', help='tabla para el Word (solo con un archivo)')
    ap.add_argument('--xlsx', help='Excel con todas las decisiones (con --todas)')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    entrada = Path(a.entrada)
    perfil = cargar_perfil(a.perfil, entrada.resolve().parent)
    rutas = sorted(entrada.glob('DT-*.json')) if a.todas else [entrada]
    resultados, fallas = [], 0
    for ruta in rutas:
        res = procesar(ruta, perfil, a.adr, None if a.todas else a.tabla)
        if res is None:
            fallas += 1
        else:
            resultados.append(res)
    if a.xlsx and resultados:
        exportar_xlsx(resultados, Path(a.xlsx))
    return 1 if fallas else 0


if __name__ == '__main__':
    sys.exit(main())
