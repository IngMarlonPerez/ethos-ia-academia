# -*- coding: utf-8 -*-
import json
from pathlib import Path

from conftest import cargar

det = cargar('skills/decision-arquitectura/scripts/detectar_arquitectura.py', 'detectar_arquitectura')
ver = cargar('skills/decision-arquitectura/scripts/verificar_reglas.py', 'verificar_reglas')


def escribir(base: Path, archivos: dict[str, str]):
    for rel, texto in archivos.items():
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto, encoding='utf-8')


def spa_api(base: Path):
    escribir(base, {
        'package.json': json.dumps({'dependencies': {'react': '19', 'express': '4', 'mssql': '11'}}),
        'src/App.jsx': "import React from 'react'\nimport { consultar } from './services/api'\n",
        'src/services/api.js': "export const consultar = () => fetch('/api/x')\n",
        'backend/requirements.txt': 'fastapi==0.115\npyodbc==5\n',
        'backend/main.py': 'from fastapi import FastAPI\nfrom api.rutas import router\napp = FastAPI()\n',
        'backend/api/__init__.py': '',
        'backend/api/rutas.py': "from fastapi import APIRouter\nfrom core.servicio import calcular\nrouter = APIRouter()\n"
                                "@router.get('/x')\ndef x():\n    return calcular()\n",
        'backend/core/__init__.py': '',
        'backend/core/servicio.py': 'import pyodbc\nfrom api.rutas import router\ndef calcular():\n    return 1\n',
    })


def test_spa_mas_api_en_capas(tmp_path):
    spa_api(tmp_path)
    r = det.analizar(tmp_path)
    estilos = ' / '.join(e['estilo'] for e in r['estilo_inferido'])
    assert 'cliente-servidor desacoplado' in estilos and 'backend en capas' in estilos
    assert r['desplegables'] == ['(raíz)', 'backend']
    assert r['frameworks_por_aplicacion']['backend']['FastAPI'] == 'backend'
    # Express y mssql declarados pero nunca importados → dependencias muertas, no un backend.
    assert set(r['dependencias_declaradas_sin_uso']['(raíz)']) == {'express', 'mssql'}
    assert 'backend/api -> backend/core' in r['dependencias_entre_componentes']
    assert r['rutas_api'].get('FastAPI/Flask') == 1


def test_monolito(tmp_path):
    escribir(tmp_path, {
        'requirements.txt': 'flask==3\n',
        'app.py': "from flask import Flask, render_template\napp = Flask(__name__)\n@app.route('/')\ndef i():\n    return render_template('i.html')\n",
        'templates/i.html': '<h1>hola</h1>',
    })
    r = det.analizar(tmp_path)
    assert [e['estilo'] for e in r['estilo_inferido']] == ['monolito']


def test_microservicios(tmp_path):
    compose = 'services:\n' + ''.join(f'  svc{i}:\n    build: ./svc{i}\n' for i in range(3)) + '  db:\n    image: postgres:16\n'
    archivos = {'docker-compose.yml': compose}
    for i in range(3):
        archivos[f'svc{i}/requirements.txt'] = 'fastapi\n'
        archivos[f'svc{i}/main.py'] = "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/s')\ndef s():\n    return 1\n"
    escribir(tmp_path, archivos)
    r = det.analizar(tmp_path)
    assert any(e['estilo'] == 'microservicios' for e in r['estilo_inferido'])
    assert 'PostgreSQL' in r['bases_de_datos']


def test_reglas_detectan_dependencia_prohibida_y_bd_en_cliente(tmp_path):
    spa_api(tmp_path)
    escribir(tmp_path, {'src/components/Malo.jsx': "import sql from 'mssql'\nconst q = 'SELECT nombre FROM alumnos'\n"})
    reglas = {
        'estilo_esperado': 'cliente-servidor desacoplado',
        'desplegables': {'min': 2, 'max': 2},
        'sin_bd_en_frontend': True,
        'componentes': {'cliente': ['src'], 'api': ['backend/api'], 'dominio': ['backend/core']},
        'dependencias_prohibidas': [['dominio', 'api']],
        'patrones_prohibidos': [{'componente': 'cliente', 'patrones': ['(?i)SELECT\\s+.+\\s+FROM'], 'motivo': 'SQL en el cliente'}],
    }
    violaciones, notas = ver.verificar(reglas, tmp_path)
    texto = '\n'.join(violaciones)
    assert 'dependencia prohibida dominio → api' in texto and 'backend/core/servicio.py:2' in texto
    assert 'el frontend accede a la base de datos' in texto
    assert 'SQL en el cliente' in texto
    assert any('declara dependencias que el código no importa' in n for n in notas)
    # Una excepción justificada convierte la violación en nota.
    reglas['excepciones'] = [{'regla': 'SQL en el cliente', 'justificacion': 'texto de ayuda (ADR-003)'}]
    violaciones, notas = ver.verificar(reglas, tmp_path)
    assert not any('SQL en el cliente' in v for v in violaciones)
    assert any('ADR-003' in n for n in notas)
