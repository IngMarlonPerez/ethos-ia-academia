# -*- coding: utf-8 -*-
"""
tabla_trabajos_previos.py — valida y exporta la tabla de trabajos previos
(literatura/trabajos_previos.json).

Validación (control de la etapa 2):
  - al menos `min_trabajos_previos` del perfil con decisión «Incluido»;
  - cada incluido fue leído completo (texto_completo_leido) y tiene al menos
    una evidencia con página;
  - Arquitectura y Tecnologías llenas (la arquitectura se evalúa SIEMPRE en
    la literatura);
  - DOI en cada uno (fuente académica verificable); ninguna fuente de prensa;
  - si se pasa el texto del documento: cada trabajo incluido se cita.

Exportación:
  --tabla tabla.json   filas para Insertor.tabla() (columnas resumidas para el Word)
  --md tabla.md        la tabla completa en Markdown
  --conteos            cuántos trabajos usan cada lenguaje/framework/base de datos/arquitectura
                       (evidencia para seleccion-tecnologica y decision-arquitectura)

Uso:
    python tabla_trabajos_previos.py literatura/trabajos_previos.json [--perfil unemi] [--tabla t.json] [--md t.md] [--conteos]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLUGIN / 'scripts_comunes'))
from perfil import cargar_perfil, leer_json  # noqa: E402

PRENSA = re.compile(r'diario|peri[oó]dico|expreso|universo|comercio|primicias|noticia|blog|medium\.com|wikipedia',
                    re.IGNORECASE)
COLUMNAS_WORD = ['Autor (año)', 'Problema y técnica', 'Tecnologías', 'Arquitectura', 'Validación y resultado',
                 'Limitación', 'Qué aporta el presente caso']


def _sin_tildes(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()


def incluidos(datos: dict) -> list[dict]:
    return [t for t in datos.get('trabajos', []) if not t.get('_ejemplo') and t.get('decision', 'Incluido') == 'Incluido']


def _tecnologias(t: dict) -> str:
    tec = t.get('tecnologias') or {}
    if isinstance(tec, str):
        return tec
    return '; '.join(f'{k.replace("_", " ")}: {v}' for k, v in tec.items() if v)


def validar(datos: dict, perfil: dict, cuerpo: str | None = None) -> tuple[list[str], list[str], str]:
    errores, avisos = [], []
    minimo = perfil.get('requisitos', {}).get('min_trabajos_previos', 10)
    lista = incluidos(datos)
    if any(t.get('_ejemplo') for t in datos.get('trabajos', [])):
        avisos.append('la tabla todavía tiene el trabajo de ejemplo (_ejemplo): bórralo.')
    if len(lista) < minimo:
        errores.append(f'{len(lista)} trabajos incluidos (mínimo {minimo}).')
    cuerpo_n = _sin_tildes(cuerpo) if cuerpo else None
    for t in lista:
        nombre = t.get('cita') or t.get('id')
        if not t.get('texto_completo_leido'):
            errores.append(f'{nombre}: no consta la lectura del texto completo (texto_completo_leido).')
        if not any(e.get('pagina') for e in t.get('evidencia', [])):
            errores.append(f'{nombre}: sin evidencia textual con página.')
        if not (t.get('arquitectura') or '').strip():
            errores.append(f'{nombre}: falta la columna Arquitectura (escribe «no reporta» si el artículo no la describe).')
        if not _tecnologias(t).strip():
            errores.append(f'{nombre}: falta la columna Tecnologías (escribe «no reporta» si no las describe).')
        if not t.get('doi'):
            avisos.append(f'{nombre}: sin DOI; confirma que sea una fuente académica verificable.')
        texto_fuente = ' '.join(str(t.get(k, '')) for k in ('fuente', 'referencia_apa'))
        if PRENSA.search(texto_fuente):
            errores.append(f'{nombre}: parece una fuente de prensa o blog; solo se aceptan fuentes académicas.')
        if cuerpo_n is not None:
            apellido = _sin_tildes(re.split(r'[\s,(]', nombre.strip(), maxsplit=1)[0])
            if apellido and apellido not in cuerpo_n:
                errores.append(f'{nombre}: está en la tabla pero no se cita en el documento.')
    if lista and not datos.get('presente_trabajo'):
        avisos.append('falta «presente_trabajo»: la tabla comparativa debe cerrar con la fila del caso propio.')
    arqs = Counter(_sin_tildes(t.get('arquitectura', '')).strip() for t in lista)
    resumen = f'{len(lista)} incluidos (mínimo {minimo}); arquitecturas distintas reportadas: {len(arqs)}.'
    return errores, avisos, resumen


def filas_word(datos: dict) -> list[list[str]]:
    """Tabla comparativa explícita frente al caso: una fila por trabajo incluido y,
    al final, la fila «Presente trabajo» (clave `presente_trabajo` del JSON)."""
    filas = [COLUMNAS_WORD]
    for t in incluidos(datos):
        filas.append([
            t.get('cita', ''),
            f"{t.get('problema', '')}. *Técnica:* {t.get('tecnica', '')}".strip(),
            _tecnologias(t),
            t.get('arquitectura', ''),
            f"{t.get('validacion_metricas', '')}. {t.get('resultado', '')}".strip(),
            t.get('limitacion', ''),
            t.get('relacion_con_este_trabajo', ''),
        ])
    p = datos.get('presente_trabajo')
    if p:
        filas.append(['Presente trabajo', p.get('problema_tecnica', ''), p.get('tecnologias', ''), p.get('arquitectura', ''),
                      p.get('validacion_resultado', ''), p.get('limitacion', ''), '—'])
    return filas


def conteos(datos: dict) -> dict:
    c: dict[str, Counter] = {'arquitectura': Counter(), 'lenguaje': Counter(), 'frameworks': Counter(),
                             'base_datos': Counter()}
    for t in incluidos(datos):
        c['arquitectura'][t.get('arquitectura', '').strip() or 'no reporta'] += 1
        tec = t.get('tecnologias') or {}
        if isinstance(tec, dict):
            for k in ('lenguaje', 'frameworks', 'base_datos'):
                for v in re.split(r'[;,/]', tec.get(k, '') or ''):
                    if v.strip():
                        c[k][v.strip()] += 1
    return {k: dict(v.most_common()) for k, v in c.items()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('archivo')
    ap.add_argument('--perfil', default='unemi')
    ap.add_argument('--tabla')
    ap.add_argument('--md')
    ap.add_argument('--conteos', action='store_true')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    datos = leer_json(a.archivo)
    errores, avisos, resumen = validar(datos, cargar_perfil(a.perfil, Path(a.archivo).resolve().parent))
    if a.tabla:
        Path(a.tabla).write_text(json.dumps(filas_word(datos), indent=1, ensure_ascii=False), encoding='utf-8')
    if a.md:
        filas = filas_word(datos)
        md = ['| ' + ' | '.join(filas[0]) + ' |', '|' + '---|' * len(filas[0])]
        md += ['| ' + ' | '.join(str(x).replace('|', '/') for x in f) + ' |' for f in filas[1:]]
        Path(a.md).write_text('\n'.join(md) + '\n', encoding='utf-8')
    if a.conteos:
        print(json.dumps(conteos(datos), indent=2, ensure_ascii=False))
    print(resumen)
    for x in avisos:
        print('  AVISO:', x)
    for e in errores:
        print('  ERROR:', e)
    return 1 if errores else 0


if __name__ == '__main__':
    sys.exit(main())
