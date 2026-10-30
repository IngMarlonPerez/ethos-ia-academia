# -*- coding: utf-8 -*-
"""
inventario_pdf.py — ¿cada DOI del corpus tiene su PDF real en la carpeta?

Regla de acceso abierto: todo DOI que entra al corpus debe tener su PDF descargado y legible. Un DOI sin PDF no se
cita: se registra con el código de exclusión E-OA y se busca un reemplazo de acceso abierto.

Lee el DOI impreso en las dos primeras páginas de cada PDF, así que sirve aunque los archivos tengan otros nombres.
También comprueba que cada archivo empiece con %PDF (que no sea una página HTML guardada con extensión .pdf).

Uso (la carpeta del proyecto solo se LEE; nada se escribe en ella):
    python inventario_pdf.py dois.txt --carpeta ARTICULOS_PDF
    python inventario_pdf.py incluidos.csv --carpeta ARTICULOS_PDF --salida control/inventario.csv

`dois.txt`: un DOI por línea. `.csv`: columna `doi` o `DOI`.
Códigos de salida: 0 todos presentes y válidos · 1 faltan DOI o hay PDF dañados.
Requiere pypdf (`pip install pypdf`) para leer el DOI dentro de los PDF.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

csv.field_size_limit(10 ** 8)
RE_DOI = re.compile(r'10\.\d{4,9}/[^\s"<>,;]+')


def norm_doi(d: str) -> str:
    d = (d or '').strip()
    return re.sub(r'^(https?://(dx\.)?doi\.org/|doi:\s*)', '', d, flags=re.I).lower().rstrip('.)')


def leer_dois(ruta: str) -> list[str]:
    p = Path(ruta)
    if p.suffix.lower() == '.txt':
        dois = [norm_doi(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
    else:
        dois = []
        with open(p, encoding='utf-8-sig') as f:
            for fila in csv.DictReader(f):
                g = {(k or '').lower().strip(): (v or '') for k, v in fila.items()}
                if norm_doi(g.get('doi', '')):
                    dois.append(norm_doi(g['doi']))
    return list(dict.fromkeys(dois))


def es_pdf_valido(ruta: Path) -> bool:
    try:
        with open(ruta, 'rb') as f:
            return f.read(5).startswith(b'%PDF')
    except OSError:
        return False


def doi_de_pdf(ruta: Path) -> str:
    """DOI impreso en las dos primeras páginas ('' si no se puede leer)."""
    try:
        from pypdf import PdfReader
        texto = ' '.join((p.extract_text() or '') for p in PdfReader(str(ruta)).pages[:2])
    except Exception:
        return ''
    m = RE_DOI.search(texto)
    return norm_doi(m.group(0)) if m else ''


def inventario(dois: list[str], carpeta: Path) -> dict:
    pdfs = sorted(p for p in carpeta.iterdir() if p.suffix.lower() == '.pdf')
    danados = [p.name for p in pdfs if not es_pdf_valido(p)]
    por_doi: dict[str, str] = {}
    sin_doi: list[str] = []
    for p in pdfs:
        if p.name in danados:
            continue
        d = doi_de_pdf(p)
        if d:
            por_doi.setdefault(d, p.name)
        else:
            sin_doi.append(p.name)
    filas = [{'doi': d, 'pdf': por_doi.get(d, ''), 'estado': 'presente' if d in por_doi else 'FALTA'} for d in dois]
    pedidos = set(dois)
    sobrantes = [nombre for d, nombre in por_doi.items() if d not in pedidos]
    return {'filas': filas, 'faltan': [f['doi'] for f in filas if f['estado'] == 'FALTA'],
            'danados': danados, 'sin_doi': sin_doi, 'sobrantes': sobrantes}


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('entrada')
    ap.add_argument('--carpeta', required=True)
    ap.add_argument('--salida', help='CSV opcional con el resultado (fuera de la carpeta de PDF)')
    a = ap.parse_args()
    carpeta = Path(a.carpeta)
    if not carpeta.is_dir():
        print(f'No existe la carpeta {carpeta}', file=sys.stderr)
        return 2
    dois = leer_dois(a.entrada)
    r = inventario(dois, carpeta)
    print(f"{len(dois) - len(r['faltan'])}/{len(dois)} DOI con PDF en la carpeta.")
    if r['faltan']:
        print('Faltan (excluir con E-OA o conseguir el PDF abierto):')
        for d in r['faltan']:
            print('  ', d)
    if r['danados']:
        print('PDF dañados (no empiezan con %PDF; suelen ser una página HTML o un bloqueo):')
        for n in r['danados']:
            print('  ', n)
    if r['sin_doi']:
        print('PDF sin DOI legible (revisar a mano):')
        for n in r['sin_doi']:
            print('  ', n)
    if r['sobrantes']:
        print('PDF que no corresponden a ningún DOI de la lista:')
        for n in r['sobrantes']:
            print('  ', n)
    if a.salida:
        Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
        with open(a.salida, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['doi', 'pdf', 'estado'])
            w.writeheader()
            w.writerows(r['filas'])
    return 1 if (r['faltan'] or r['danados']) else 0


if __name__ == '__main__':
    sys.exit(main())
