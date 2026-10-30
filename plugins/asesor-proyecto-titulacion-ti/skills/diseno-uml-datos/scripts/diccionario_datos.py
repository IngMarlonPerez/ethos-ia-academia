# -*- coding: utf-8 -*-
"""
diccionario_datos.py — diccionario de datos generado desde el ESQUEMA REAL
de la base (no escrito a mano: el documento no puede describir una columna
que la base no tiene).

Motores: SQLite (sin dependencias), SQL Server (pyodbc), PostgreSQL
(psycopg / psycopg2), MySQL (pymysql). Lee tablas, columnas, tipos, nulos,
claves primarias y foráneas, y vistas. Las descripciones de negocio vienen de
un JSON aparte (descripciones.json) que se mantiene a mano:

    {"tablas": {"fact_ventas": "Hecho central: una fila por venta"},
     "columnas": {"monto": "Valor neto de la venta (USD)", "fact_ventas.fecha_id": "…"}}

Una columna sin descripción queda marcada «(sin descripción: completar)»; el
script sale con código 1 si queda alguna (control de la etapa 7).

La contraseña NUNCA va en la línea de comandos ni en el repositorio: la URL
se lee de una variable de entorno (por defecto DICCIONARIO_URL).

Uso:
    python diccionario_datos.py --motor sqlite --url ruta/base.db --desc descripciones.json --json dd.json --md dd.md
    set DICCIONARIO_URL=DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=X;UID=u;PWD=…;TrustServerCertificate=yes
    python diccionario_datos.py --motor sqlserver --desc descripciones.json --json dd.json --md dd.md [--tablas t1 t2] [--vistas VIS_%]
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

SIN = '(sin descripción: completar)'


def _tipo(tipo: str, largo=None, prec=None, esc=None) -> str:
    t = (tipo or '').upper()
    if t in ('VARCHAR', 'NVARCHAR', 'CHAR', 'NCHAR', 'CHARACTER VARYING') and largo:
        return f"{t}({'MAX' if largo == -1 else largo})"
    if t in ('DECIMAL', 'NUMERIC') and prec:
        return f'{t}({prec},{esc or 0})'
    return t


def leer_sqlite(url: str) -> tuple[list, set, dict, list]:
    con = sqlite3.connect(url)
    cols, pks, fks = [], set(), {}
    tablas = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    for t in tablas:
        for cid, nombre, tipo, notnull, _, pk in con.execute(f'PRAGMA table_info("{t}")'):
            cols.append((t, nombre, (tipo or '').upper(), not notnull))
            if pk:
                pks.add((t, nombre))
        for fila in con.execute(f'PRAGMA foreign_key_list("{t}")'):
            fks[(t, fila[3])] = fila[2]
    vistas = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")]
    con.close()
    return cols, pks, fks, vistas


def leer_information_schema(con, motor: str, vistas_patron: str | None) -> tuple[list, set, dict, list]:
    cur = con.cursor()
    esquema_filtro = {'sqlserver': "c.TABLE_SCHEMA NOT IN ('sys','INFORMATION_SCHEMA')",
                      'postgres': "c.TABLE_SCHEMA NOT IN ('pg_catalog','information_schema')",
                      'mysql': 'c.TABLE_SCHEMA = DATABASE()'}[motor]
    cur.execute(f"""
        SELECT c.TABLE_NAME, c.COLUMN_NAME, c.DATA_TYPE, c.CHARACTER_MAXIMUM_LENGTH, c.NUMERIC_PRECISION,
               c.NUMERIC_SCALE, c.IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS c
        JOIN INFORMATION_SCHEMA.TABLES t ON t.TABLE_NAME = c.TABLE_NAME AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
        WHERE t.TABLE_TYPE = 'BASE TABLE' AND {esquema_filtro}
        ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION""")
    cols = [(t, c, _tipo(ty, l, p, e), n == 'YES') for t, c, ty, l, p, e, n in cur.fetchall()]
    cur.execute("""
        SELECT ku.TABLE_NAME, ku.COLUMN_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku ON ku.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
             AND ku.TABLE_NAME = tc.TABLE_NAME
        WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'""")
    pks = {(t, c) for t, c in cur.fetchall()}
    if motor == 'sqlserver':
        cur.execute("""SELECT OBJECT_NAME(fk.parent_object_id), COL_NAME(fc.parent_object_id, fc.parent_column_id),
                              OBJECT_NAME(fk.referenced_object_id)
                       FROM sys.foreign_keys fk JOIN sys.foreign_key_columns fc ON fc.constraint_object_id = fk.object_id""")
    elif motor == 'mysql':
        cur.execute("""SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                       WHERE REFERENCED_TABLE_NAME IS NOT NULL AND TABLE_SCHEMA = DATABASE()""")
    else:
        cur.execute("""SELECT kcu.TABLE_NAME, kcu.COLUMN_NAME, ccu.TABLE_NAME
                       FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                       JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                       JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu ON ccu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
                       WHERE tc.CONSTRAINT_TYPE = 'FOREIGN KEY'""")
    fks = {(t, c): ref for t, c, ref in cur.fetchall()}
    filtro = f" AND TABLE_NAME LIKE '{vistas_patron}'" if vistas_patron else ''
    cur.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS WHERE 1=1{filtro} ORDER BY TABLE_NAME")
    vistas = [r[0] for r in cur.fetchall()]
    return cols, pks, fks, vistas


def conectar(motor: str, url: str):
    if motor == 'sqlserver':
        import pyodbc
        return pyodbc.connect(url, timeout=15)
    if motor == 'postgres':
        try:
            import psycopg
            return psycopg.connect(url)
        except ImportError:
            import psycopg2
            return psycopg2.connect(url)
    if motor == 'mysql':
        import pymysql
        partes = dict(x.split('=', 1) for x in url.split(';') if '=' in x)
        return pymysql.connect(host=partes.get('host', 'localhost'), user=partes.get('user'), password=partes.get('password'),
                               database=partes.get('database'), port=int(partes.get('port', 3306)))
    raise ValueError(motor)


def construir(cols, pks, fks, vistas, desc: dict, solo: list[str] | None) -> dict:
    dt, dc = desc.get('tablas', {}), desc.get('columnas', {})
    esquema = {}
    for t, c, tipo, nulo in cols:
        if solo and t not in solo:
            continue
        clave = 'PK' if (t, c) in pks else (f'FK → {fks[(t, c)]}' if (t, c) in fks else '')
        esquema.setdefault(t, {'descripcion': dt.get(t, SIN), 'columnas': []})['columnas'].append(
            {'columna': c, 'tipo': tipo, 'clave': clave, 'nulo': bool(nulo), 'descripcion': dc.get(f'{t}.{c}', dc.get(c, SIN))})
    return {'tablas': esquema, 'vistas': vistas}


def a_markdown(d: dict, titulo: str) -> str:
    l = [f'# {titulo}', '', 'Generado desde el esquema real por diccionario_datos.py. No editar a mano.', '']
    for t, info in d['tablas'].items():
        l += [f'## {t}', '', info['descripcion'], '', '| Columna | Tipo | Clave | Nulo | Descripción |', '|---|---|---|---|---|']
        l += [f"| {c['columna']} | {c['tipo']} | {c['clave']} | {'Sí' if c['nulo'] else 'No'} | {c['descripcion']} |" for c in info['columnas']]
        l.append('')
    if d['vistas']:
        l += ['## Vistas', ''] + [f'- `{v}`' for v in d['vistas']]
    return '\n'.join(l) + '\n'


def filas_word(d: dict, tabla: str) -> list[list[str]]:
    """Filas para Insertor.tabla() de una tabla del diccionario."""
    return [['Columna', 'Tipo', 'Clave', 'Descripción']] + [
        [c['columna'], c['tipo'], c['clave'], c['descripcion']] for c in d['tablas'][tabla]['columnas']]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--motor', required=True, choices=['sqlite', 'sqlserver', 'postgres', 'mysql'])
    ap.add_argument('--url', help='solo para SQLite (ruta del archivo); en los demás se usa la variable de entorno')
    ap.add_argument('--variable', default='DICCIONARIO_URL', help='variable de entorno con la cadena de conexión')
    ap.add_argument('--desc', help='JSON de descripciones de negocio')
    ap.add_argument('--tablas', nargs='*')
    ap.add_argument('--vistas', help="patrón LIKE de vistas a listar, p. ej. 'VIS[_]%%'")
    ap.add_argument('--json')
    ap.add_argument('--md')
    ap.add_argument('--titulo', default='Diccionario de datos')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    if a.motor == 'sqlite':
        cols, pks, fks, vistas = leer_sqlite(a.url)
    else:
        url = os.environ.get(a.variable)
        if not url:
            sys.exit(f'Define la variable de entorno {a.variable} con la cadena de conexión (nunca en el repositorio).')
        con = conectar(a.motor, url)
        cols, pks, fks, vistas = leer_information_schema(con, a.motor, a.vistas)
        con.close()
    desc = json.loads(Path(a.desc).read_text(encoding='utf-8')) if a.desc else {}
    d = construir(cols, pks, fks, vistas, desc, a.tablas)
    if a.json:
        Path(a.json).write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding='utf-8')
    if a.md:
        Path(a.md).write_text(a_markdown(d, a.titulo), encoding='utf-8')
    faltan = [f'{t}.{c["columna"]}' for t, i in d['tablas'].items() for c in i['columnas'] if c['descripcion'] == SIN]
    faltan += [f'{t} (tabla)' for t, i in d['tablas'].items() if i['descripcion'] == SIN]
    n_cols = sum(len(i['columnas']) for i in d['tablas'].values())
    print(f"{len(d['tablas'])} tablas, {n_cols} columnas, {len(d['vistas'])} vistas.")
    if faltan:
        print(f'Sin descripción ({len(faltan)}): ' + ', '.join(faltan[:30]) + (' …' if len(faltan) > 30 else ''))
        return 1
    print('Todas las tablas y columnas tienen descripción.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
