# -*- coding: utf-8 -*-
"""
verificar_reglas.py — comprueba que el código cumple la arquitectura
DECLARADA en decisiones/arquitectura_reglas.json (ver plantillas/).

Reglas soportadas:
  - "desplegables": {"min": n, "max": n}           número de aplicaciones desplegables
  - "servicios_docker": {"min": n, "max": n}       servicios de aplicación en docker-compose
  - "componentes": {"nombre": ["ruta/prefijo", …]}  cómo se agrupan las carpetas del repo
  - "dependencias_prohibidas": [["origen", "destino"], …]   ningún import de origen → destino
  - "patrones_prohibidos": [{"componente", "patrones": [regex…], "motivo"}]
  - "estilo_esperado": texto que debe aparecer en el estilo inferido (p. ej. «desacoplado»)
  - "sin_bd_en_frontend": true
  - "excepciones": [{"regla": "texto que identifica la violación", "justificacion": "ADR-003 …"}]

Una violación que coincide con una excepción pasa a ser nota (queda documentada).

Uso:
    python verificar_reglas.py decisiones/arquitectura_reglas.json <repo>
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detectar_arquitectura as det  # noqa: E402


def _componente(rel: str, componentes: dict[str, list[str]]) -> str | None:
    mejor, largo = None, -1
    for nombre, prefijos in componentes.items():
        for pre in prefijos:
            pre = pre.strip('/').replace('\\', '/')
            if (rel == pre or rel.startswith(pre + '/')) and len(pre) > largo:
                mejor, largo = nombre, len(pre)
    return mejor


def verificar(reglas: dict, repo: Path, analisis: dict | None = None) -> tuple[list[str], list[str]]:
    repo = Path(repo).resolve()
    r = analisis or det.analizar(repo)
    violaciones: list[str] = []
    notas: list[str] = []
    comp = reglas.get('componentes', {})

    rango = reglas.get('desplegables')
    if rango:
        k = len(r['desplegables'])
        if k < rango.get('min', 0) or k > rango.get('max', 10 ** 6):
            violaciones.append(f"desplegables: {k} ({', '.join(r['desplegables'])}); se esperaban entre {rango.get('min')} y {rango.get('max')}.")
    rango = reglas.get('servicios_docker')
    if rango:
        apps = [s for s, v in r['servicios_docker_compose'].items() if 'build' in v]
        if len(apps) < rango.get('min', 0) or len(apps) > rango.get('max', 10 ** 6):
            violaciones.append(f"servicios de aplicación en docker-compose: {len(apps)}; se esperaban entre {rango.get('min')} y {rango.get('max')}.")
    esperado = reglas.get('estilo_esperado')
    if esperado:
        estilos = ' / '.join(e['estilo'] for e in r['estilo_inferido'])
        if esperado.lower() not in estilos.lower():
            violaciones.append(f"estilo: se declaró «{esperado}», pero el código sugiere «{estilos or 'sin señales'}».")
    if reglas.get('sin_bd_en_frontend') and r['bd_desde_frontend']:
        for x in r['bd_desde_frontend']:
            violaciones.append(f'el frontend accede a la base de datos: {x}')

    prohibidas = [tuple(x) for x in reglas.get('dependencias_prohibidas', [])]
    if prohibidas and comp:
        # Rehace el grafo archivo por archivo con los componentes declarados.
        for p in det.archivos(repo):
            if p.suffix not in ('.py', *det.JS):
                continue
            rel = p.relative_to(repo)
            origen = _componente(rel.as_posix(), comp)
            if origen is None:
                continue
            texto = det.leer(p)
            imports = []
            if p.suffix == '.py':
                for m in det.IMPORT_PY.finditer(texto):
                    destino = det.resolver_import_py(p, m.group(1) or m.group(2), repo)
                    imports.append((m.start(), destino))
            else:
                for m in det.IMPORT_JS.finditer(texto):
                    imports.append((m.start(), det.resolver_import_js(p, m.group(1), repo)))
            for pos, destino in imports:
                if destino is None or repo not in destino.parents:
                    continue
                dest = _componente(destino.relative_to(repo).as_posix(), comp)
                if dest and dest != origen and (origen, dest) in prohibidas:
                    violaciones.append(f'dependencia prohibida {origen} → {dest}: {rel.as_posix()}:{texto[:pos].count(chr(10)) + 1}')
    for regla in reglas.get('patrones_prohibidos', []):
        prefijos = comp.get(regla['componente'], [regla['componente']])
        patrones = [re.compile(x) for x in regla.get('patrones', [])]
        for p in det.archivos(repo):
            rel = p.relative_to(repo).as_posix()
            if p.suffix not in det.EXTENSIONES or not any(rel == x.strip('/') or rel.startswith(x.strip('/') + '/') for x in prefijos):
                continue
            if det.es_prueba(p.relative_to(repo)) and not regla.get('incluir_pruebas'):
                continue
            texto = det.leer(p)
            for patron in patrones:
                m = patron.search(texto)
                if m:
                    violaciones.append(f"{regla['componente']}: {regla.get('motivo', 'patrón prohibido')} — «{m.group(0)[:40]}» en "
                                       f"{rel}:{texto[:m.start()].count(chr(10)) + 1}")
    for app, deps in r.get('dependencias_declaradas_sin_uso', {}).items():
        notas.append(f"`{app}` declara dependencias que el código no importa: {', '.join(sorted(set(deps)))} (limpiar o justificar).")

    finales = []
    for v in violaciones:
        exc = next((e for e in reglas.get('excepciones', []) if e.get('regla') and e['regla'].lower() in v.lower()), None)
        if exc:
            notas.append(f"{v} — excepción justificada: {exc.get('justificacion', '')}")
        else:
            finales.append(v)
    return finales, notas


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    sys.stdout.reconfigure(encoding='utf-8')
    reglas = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    violaciones, notas = verificar(reglas, Path(sys.argv[2]))
    for x in notas:
        print('  NOTA:', x)
    for x in violaciones:
        print('  VIOLACIÓN:', x)
    print('El código cumple la arquitectura declarada.' if not violaciones else f'{len(violaciones)} violaciones.')
    return 1 if violaciones else 0


if __name__ == '__main__':
    sys.exit(main())
