# -*- coding: utf-8 -*-
import csv
import json
import os
import sqlite3
from pathlib import Path

import docx
import pytest

from conftest import PLUGIN, cargar, correr

_CANDIDATAS_PLANTILLA = [
    Path(os.environ.get('PLANTILLA_UNEMI', '')),
    Path(r'C:\\Tesis\\documentacion\plantillas_unemi\Formato de trabajo de titulación.docx'),
    Path(r'C:\\Tesis\\Avance 1 del proyecto\Formato de trabajo de titulación.docx'),
]
PLANTILLA_UNEMI = next((c for c in _CANDIDATAS_PLANTILLA if str(c) not in ('', '.') and c.is_file()), _CANDIDATAS_PLANTILLA[1])


def test_anonimizar_determinista_y_consistente(tmp_path):
    for nombre, filas in {'a.csv': [['cedula', 'nombres', 'genero', 'nota'], ['0912345678', 'Ana', 'F', '9'], ['0102030405', 'Luis', 'M', '7']],
                          'b.csv': [['cedula', 'periodo'], ['0912345678', '2024-1'], ['0912345678', '2024-2']]}.items():
        with open(tmp_path / nombre, 'w', encoding='utf-8-sig', newline='') as f:
            csv.writer(f).writerows(filas)
    args = ['--archivos', tmp_path / 'a.csv', tmp_path / 'b.csv', '--columna', 'cedula=cedula_ec', '--columna', 'nombres=nombres',
            '--genero', 'genero']
    salidas = []
    for i in range(2):
        r = correr('skills/proteccion-datos/scripts/anonimizar.py', *args, '--salida', tmp_path / f'out{i}')
        assert r.returncode == 0, r.stderr
        salidas.append((tmp_path / f'out{i}/a.csv').read_text(encoding='utf-8-sig'))
    assert salidas[0] == salidas[1]                       # misma semilla → mismo resultado
    a = list(csv.DictReader(open(tmp_path / 'out0/a.csv', encoding='utf-8-sig')))
    b = list(csv.DictReader(open(tmp_path / 'out0/b.csv', encoding='utf-8-sig')))
    anon = cargar('skills/proteccion-datos/scripts/anonimizar.py')
    assert a[0]['cedula'].startswith('00') and anon.digito_verificador(a[0]['cedula'][:9]) == int(a[0]['cedula'][9])
    assert b[0]['cedula'] == b[1]['cedula'] == a[0]['cedula']   # tablas siguen unidas
    assert a[0]['nota'] == '9' and 'Ana' != a[0]['nombres']


def test_buscar_secretos(tmp_path):
    (tmp_path / 'app.py').write_text('password = "Secreto2024!"\n', encoding='utf-8')
    (tmp_path / 'ok.py').write_text('password = os.environ["DB_PASSWORD"]\nconectar(password=clave)\n', encoding='utf-8')
    r = correr('skills/proteccion-datos/scripts/buscar_secretos.py', tmp_path)
    assert r.returncode == 1 and 'app.py:1' in r.stdout and 'Secreto2024' not in r.stdout   # enmascarado
    (tmp_path / 'app.py').unlink()
    r = correr('skills/proteccion-datos/scripts/buscar_secretos.py', tmp_path)
    assert r.returncode == 0, r.stdout


def test_diccionario_sqlite(tmp_path):
    db = tmp_path / 'b.db'
    con = sqlite3.connect(db)
    con.executescript('CREATE TABLE cliente (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL);'
                      'CREATE TABLE pedido (id INTEGER PRIMARY KEY, cliente_id INTEGER REFERENCES cliente(id), total REAL);'
                      'CREATE VIEW v_pedidos AS SELECT * FROM pedido;')
    con.close()
    desc = tmp_path / 'd.json'
    desc.write_text(json.dumps({'tablas': {'cliente': 'Clientes', 'pedido': 'Pedidos'},
                                'columnas': {'id': 'Identificador', 'nombre': 'Nombre', 'cliente_id': 'Cliente', 'total': 'Total'}}),
                    encoding='utf-8')
    r = correr('skills/diseno-uml-datos/scripts/diccionario_datos.py', '--motor', 'sqlite', '--url', db, '--desc', desc,
               '--json', tmp_path / 'dd.json', '--md', tmp_path / 'dd.md')
    assert r.returncode == 0, r.stdout + r.stderr
    d = json.loads((tmp_path / 'dd.json').read_text(encoding='utf-8'))
    col = {c['columna']: c for c in d['tablas']['pedido']['columnas']}
    assert col['id']['clave'] == 'PK' and col['cliente_id']['clave'] == 'FK → cliente'
    assert d['vistas'] == ['v_pedidos']
    desc.write_text(json.dumps({'tablas': {}, 'columnas': {}}), encoding='utf-8')
    r = correr('skills/diseno-uml-datos/scripts/diccionario_datos.py', '--motor', 'sqlite', '--url', db, '--desc', desc)
    assert r.returncode == 1 and 'Sin descripción' in r.stdout


def test_perfil_desde_plantilla_sintetica(tmp_path):
    d = docx.Document()
    d.add_heading('RESUMEN', 1)
    d.add_paragraph('Un párrafo con un máximo de 150 palabras.')
    d.add_paragraph('Palabras Claves: máximo cinco palabras.')
    d.add_heading('Introducción', 1)
    d.add_heading('Descripción', 2)
    d.add_paragraph('Contexto. (La extensión de este apartado se limita a un mínimo de 2 páginas)')
    d.add_heading('Diseño', 2)
    d.add_paragraph('Arquitectura.')
    d.add_paragraph('(La extensión de este apartado se limita a un mínimo de 2 páginas)')
    d.add_paragraph('UML.')
    d.add_paragraph('(La extensión de este apartado se limita a un mínimo de 3 páginas)')
    d.add_heading('Referencias', 1)
    d.add_paragraph('Formato APA, mínimo 20 referencias de los últimos 5 años.')
    d.save(str(tmp_path / 'p.docx'))
    ppp = cargar('skills/iniciar-titulacion/scripts/perfil_desde_plantilla.py')
    perfil = ppp.extraer(tmp_path / 'p.docx', 'x', 'X')
    sec = {s['id']: s for s in perfil['secciones']}
    assert sec['resumen']['reglas'] == {'max_palabras': 150, 'max_palabras_clave': 5}
    assert sec['1.1']['min_paginas'] == 2 and sec['1.1']['marca_pdf'] == '1.1 Descripción'
    assert sec['1.2']['min_paginas'] == 5 and [p['min_paginas'] for p in sec['1.2']['partes']] == [2, 3]
    assert perfil['requisitos']['min_referencias'] == 20 and perfil['requisitos']['anios_referencias'] == 5


@pytest.mark.skipif(not PLANTILLA_UNEMI.exists(), reason='plantilla real de la UNEMI no disponible en esta máquina')
def test_perfil_desde_plantilla_unemi_real():
    ppp = cargar('skills/iniciar-titulacion/scripts/perfil_desde_plantilla.py')
    perfil = ppp.extraer(PLANTILLA_UNEMI, 'unemi', 'UNEMI')
    minimos = {s['id']: s.get('min_paginas') for s in perfil['secciones'] if s.get('min_paginas')}
    assert minimos == {'1.1': 2, '1.2': 1, '1.3': 3, '2.1': 3, '3.1': 3, '3.2': 6, '3.3': 6, '4': 1}
    assert perfil['requisitos']['min_trabajos_previos'] == 10 and len(perfil['requisitos']['preguntas_esta_relacionado']) == 7


def test_perfil_unemi_coherente(perfil_unemi):
    ids = {s['id'] for s in perfil_unemi['secciones']}
    for avance in perfil_unemi['avances'].values():
        assert set(avance['secciones']) <= ids
    skills = {p.name for p in (PLUGIN / 'skills').iterdir()}
    for s in perfil_unemi['secciones']:
        for sk in [s.get('skill')] + [p.get('skill') for p in s.get('partes', [])]:
            assert sk is None or sk in skills, sk
    assert sum(p['min_paginas'] for p in next(s for s in perfil_unemi['secciones'] if s['id'] == '3.2')['partes']) == 6


def test_iniciar_tablero_matrices(tmp_path):
    raiz = tmp_path / 'tesis'
    r = correr('skills/iniciar-titulacion/scripts/iniciar_titulacion.py', raiz, '--tema', 'Prueba', '--autores', 'A; B')
    assert r.returncode == 0, r.stderr
    for rel in ('titulacion.json', '00_Control_Titulacion.md', '_automatizacion/coherencia.json', 'literatura/trabajos_previos.json',
                'requerimientos/requerimientos.json', 'entregables/PROTOTIPO_FUNCIONAL'):
        assert (raiz / rel).exists(), rel
    (raiz / 'titulacion.json').write_text((raiz / 'titulacion.json').read_text(encoding='utf-8').replace('"Prueba"', '"Prueba editada"'),
                                          encoding='utf-8')
    r = correr('skills/iniciar-titulacion/scripts/iniciar_titulacion.py', raiz, '--tema', 'Otra', '--autores', 'C')
    assert 'Prueba editada' in (raiz / 'titulacion.json').read_text(encoding='utf-8')   # nunca sobrescribe
    r = correr('skills/asistente-titulacion-ti/scripts/tablero.py', 'marcar', '0', 'cerrada', '--nota', 'ok', cwd=raiz)
    assert r.returncode == 0 and 'Siguiente: etapa 1' in r.stdout
    assert '✅ | 0 · Inicio' in (raiz / '00_Control_Titulacion.md').read_text(encoding='utf-8')
    r = correr('skills/matrices-titulacion/scripts/matrices_titulacion.py', cwd=raiz)
    assert r.returncode == 0 and (raiz / 'documento/Matrices_Metodologicas.xlsx').exists(), r.stderr
    r = correr('skills/entrega-y-sustentacion/scripts/armar_entrega.py', '--revisar', cwd=raiz)
    assert r.returncode == 1 and 'VACÍA: CODIGO_FUENTE' in r.stdout


def test_trazabilidad_y_trabajos_previos(perfil_unemi):
    tz = cargar('skills/analisis-requerimientos/scripts/trazabilidad.py')
    datos = {
        'objetivos': [{'id': 'OE1', 'texto': 'Analizar'}],
        'alternativas': [{'id': f'A{i}', 'nombre': f'A{i}', 'seleccionada': i == 2} for i in range(3)],
        'historias': [{'id': 'HU-01', 'objetivos': ['OE1'], 'criterios': [{'dado': 'a', 'cuando': 'b', 'entonces': 'c'}]}],
        'rf': [{'id': 'RF-01', 'objetivo': 'OE1', 'historias': ['HU-01'], 'pruebas': ['PR-01']}],
        'rnf': [{'id': 'RNF-01', 'atributo': 'Privacidad', 'requerimiento': 'x', 'pruebas': ['PR-01']}],
        'metricas': [{'id': 'M-01', 'objetivo': 'OE1', 'meta': '>= 0,8'}],
        'pruebas': [{'id': 'PR-01'}],
    }
    assert tz.validar(datos, perfil_unemi) == ([], [])
    datos['rf'][0]['pruebas'] = []
    e, _ = tz.validar(datos, perfil_unemi)
    assert any('RF-01: no tiene prueba' in x for x in e)
    assert tz.tablas(datos)['trazabilidad'][1][2] == 'RF-01'

    tp = cargar('skills/trabajos-previos/scripts/tabla_trabajos_previos.py')
    trabajo = {'cita': 'Pérez et al. (2024)', 'doi': '10.1/x', 'texto_completo_leido': True, 'evidencia': [{'pagina': 'p. 3'}],
               'arquitectura': 'cliente-servidor', 'tecnologias': {'lenguaje': 'Python'}, 'decision': 'Incluido'}
    e, _, _ = tp.validar({'trabajos': [dict(trabajo, cita=f'Autor{i} (2024)') for i in range(10)]}, perfil_unemi)
    assert e == []
    e, _, _ = tp.validar({'trabajos': [dict(trabajo, arquitectura='')] * 10}, perfil_unemi)
    assert any('Arquitectura' in x for x in e)
    e, _, _ = tp.validar({'trabajos': [dict(trabajo, fuente='Diario El Universo')] * 10}, perfil_unemi)
    assert any('prensa' in x for x in e)
    assert tp.conteos({'trabajos': [trabajo] * 3})['lenguaje'] == {'Python': 3}
