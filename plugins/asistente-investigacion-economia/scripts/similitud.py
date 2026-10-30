# -*- coding: utf-8 -*-
"""
similitud.py — control PREVENTIVO de similitud, antes de Turnitin o Compilatio.

Compara cada oración propia con los resúmenes o textos de las fuentes y marca las que comparten secuencias largas
de palabras (paráfrasis demasiado cercana). No sustituye a un detector oficial: avisa dónde reescribir desde la idea
y no desde la frase.

Uso:
    python similitud.py texto.docx|texto.md|texto.txt --fuentes incluidos.csv [--columna resumen]
    python similitud.py texto.docx --carpeta textos_fuente/        # .txt de pdf_tools.py texto
Umbrales: 8 palabras seguidas idénticas = FALLA · ≥ 35 % de trigramas compartidos = ADVERTENCIA.
Códigos de salida: 0 sin copia literal · 1 hay oraciones con copia literal.
En un .docx se revisa el cuerpo: no los títulos, las leyendas, las notas ni las Referencias.
Adaptado del plugin «proyectos-academicos» (V. M. Lluilema Pisco).
"""
from __future__ import annotations

import argparse
import csv
import glob
import os
import re
import sys
import unicodedata

csv.field_size_limit(10 ** 8)
RE_REFS = re.compile(r'^(referencias|bibliograf)', re.I)
RE_ANEXOS = re.compile(r'^(anexos?|ap[eé]ndices?)\b', re.I)
RE_LEYENDA = re.compile(r'^(figura|tabla|nota[.:]|fuente:|ilustraci[oó]n|gr[aá]fico|cuadro)\b', re.I)


def tokens(s: str) -> list[str]:
    s = re.sub(r'\[\[PAG \d+\]\]', ' ', s)
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.findall(r'[a-z0-9ñ]+', s)


def oraciones(parrafo: str) -> list[str]:
    return [o.strip() for o in re.split(r'(?<=[.!?…])\s+', parrafo) if o.strip()]


def recorte(s: str, n: int = 120) -> str:
    s = ' '.join(s.split())
    return s if len(s) <= n else s[:n - 1] + '…'


def parrafos_docx(ruta: str) -> list[str]:
    import docx
    out, zona = [], 'cuerpo'
    for p in docx.Document(ruta).paragraphs:
        t = p.text.strip()
        nombre = (p.style.name or '').lower() if p.style is not None else ''
        es_titulo = nombre.startswith(('heading', 'título', 'titulo'))
        if es_titulo:
            if RE_REFS.match(t):
                zona = 'referencias'
            elif RE_ANEXOS.match(t):
                zona = 'anexos'
            continue
        if zona == 'referencias' or not t or RE_LEYENDA.match(t) or nombre.startswith(('toc', 'tdc')):
            continue
        out.append(t)
    return out


def indexar(fuentes: list[tuple[str, str]], n: int):
    idx_n: dict[tuple, str] = {}
    idx_3: dict[tuple, set] = {}
    for nombre, texto in fuentes:
        tk = tokens(texto)
        for i in range(len(tk) - n + 1):
            idx_n.setdefault(tuple(tk[i:i + n]), nombre)
        for i in range(len(tk) - 2):
            idx_3.setdefault(tuple(tk[i:i + 3]), set()).add(nombre)
    return idx_n, idx_3


def analizar(parrafos: list[str], idx_n, idx_3, n: int = 8) -> tuple[list, list]:
    """Devuelve (fallas, advertencias): listas de (fuente(s), oración)."""
    fallas, adv = [], []
    for p in parrafos:
        for o in oraciones(p):
            tk = tokens(o)
            exactas = {idx_n[tuple(tk[i:i + n])] for i in range(len(tk) - n + 1) if tuple(tk[i:i + n]) in idx_n}
            tri = [tuple(tk[i:i + 3]) for i in range(len(tk) - 2)]
            comp: dict[str, int] = {}
            for t3 in tri:
                for f in idx_3.get(t3, ()):
                    comp[f] = comp.get(f, 0) + 1
            peor = max(comp.items(), key=lambda x: x[1]) if comp else (None, 0)
            prop = peor[1] / len(tri) if tri else 0
            if exactas:
                fallas.append((', '.join(sorted(exactas)), o))
            elif prop >= 0.35 and len(tri) >= 8:
                adv.append((f'{peor[0]} ({prop:.0%})', o))
    return fallas, adv


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('texto')
    ap.add_argument('--fuentes', help='CSV con los resúmenes de los estudios')
    ap.add_argument('--columna', default='resumen')
    ap.add_argument('--carpeta', help='carpeta con textos .txt de las fuentes')
    ap.add_argument('--n', type=int, default=8, help='palabras seguidas idénticas que cuentan como copia')
    a = ap.parse_args()

    fuentes: list[tuple[str, str]] = []
    if a.fuentes:
        with open(a.fuentes, encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                if r.get(a.columna):
                    autor = r.get('primer_autor') or (r.get('autores') or r.get('Authors') or '')[:30]
                    fuentes.append((f"{autor} ({r.get('anio') or r.get('Year') or ''})", r[a.columna]))
    if a.carpeta:
        for f in glob.glob(os.path.join(a.carpeta, '*.txt')):
            with open(f, encoding='utf-8', errors='replace') as h:
                fuentes.append((os.path.basename(f), h.read()))
    if not fuentes:
        print('Sin fuentes: pasa --fuentes incluidos.csv o --carpeta con textos .txt', file=sys.stderr)
        return 2
    if a.texto.lower().endswith('.docx'):
        parrafos = parrafos_docx(a.texto)
    else:
        with open(a.texto, encoding='utf-8') as f:
            parrafos = [p for p in re.split(r'\n\s*\n', f.read()) if p.strip()]
    idx_n, idx_3 = indexar(fuentes, a.n)
    fallas, adv = analizar(parrafos, idx_n, idx_3, a.n)
    for src, o in fallas:
        print(f'[FALLA] {a.n}+ palabras idénticas a {src}: «{recorte(o)}»')
    for src, o in adv:
        print(f'[ADVERTENCIA] trigramas compartidos con {src}: «{recorte(o)}»')
    print(f'\nOraciones con copia literal: {len(fallas)} · paráfrasis muy cercanas: {len(adv)}. '
          'Reescribe desde la idea, no desde la frase.')
    return 1 if fallas else 0


if __name__ == '__main__':
    sys.exit(main())
