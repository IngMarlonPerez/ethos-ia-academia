# -*- coding: utf-8 -*-
import copy
import json

from conftest import PLUGIN, cargar

md = cargar('skills/seleccion-tecnologica/scripts/matriz_decision.py')
PLANTILLA = json.loads((PLUGIN / 'skills/seleccion-tecnologica/plantillas/decision.json').read_text(encoding='utf-8'))


def test_plantilla_valida_y_ranking(perfil_unemi):
    assert md.validar(PLANTILLA, perfil_unemi) == []
    r = md.resolver(PLANTILLA)
    assert r['elegida'] == 'python'
    assert [k for k, _ in r['ranking']] == ['python', 'java', 'node']
    assert abs(r['puntajes']['python'] - 4.5) < 1e-9
    assert r['cambios'] == [] and r['estabilidad'].startswith('estable')


def test_pesos_que_no_suman_100_y_pocas_candidatas(perfil_unemi):
    d = copy.deepcopy(PLANTILLA)
    d['criterios'][0]['peso'] = 10
    d['candidatas'] = d['candidatas'][:2]
    errores = md.validar(d, perfil_unemi)
    assert any('suman' in e for e in errores)
    assert any('2 candidatas (mínimo 3)' in e for e in errores)


def test_fuente_de_blog_rechazada(perfil_unemi):
    d = copy.deepcopy(PLANTILLA)
    d['candidatas'][0]['puntajes']['C1']['fuente'] = 'https://medium.com/algo'
    assert any('fuente no válida' in e for e in md.validar(d, perfil_unemi))


def test_ganadora_inestable_se_resuelve_con_desempate():
    d = copy.deepcopy(PLANTILLA)
    d['criterios'] = [{'id': 'A', 'nombre': 'A', 'peso': 55, 'origen': 'x'}, {'id': 'B', 'nombre': 'B', 'peso': 45, 'origen': 'y'}]
    p = lambda a, b: {'A': {'valor': a, 'justificacion': 'j', 'fuente': 'f'}, 'B': {'valor': b, 'justificacion': 'j', 'fuente': 'f'}}
    d['candidatas'] = [{'id': 'x', 'nombre': 'X', 'puntajes': p(5, 2)}, {'id': 'y', 'nombre': 'Y', 'puntajes': p(3, 4)},
                       {'id': 'z', 'nombre': 'Z', 'puntajes': p(1, 1)}]
    d['desempate'] = 'B'
    r = md.resolver(d)
    assert r['cambios'], 'con ±20 % en un peso la ganadora debe cambiar'
    assert r['elegida'] == 'y' and 'INESTABLE' in r['estabilidad']


def test_adr_y_tabla_word():
    r = md.resolver(PLANTILLA)
    texto = md.adr(PLANTILLA, r, '001')
    assert texto.startswith('# ADR-001') and 'Sensibilidad' in texto and 'Python' in texto
    tabla = md.tabla_word(PLANTILLA, r)
    assert tabla[0][1] == 'Python' and tabla[-1][1] == '**4,50**'


def test_verificar_versiones(tmp_path):
    (tmp_path / 'dec').mkdir()
    (tmp_path / 'repo/backend').mkdir(parents=True)
    (tmp_path / 'repo/backend/requirements.txt').write_text('fastapi==0.115.0\nscikit-learn==1.9.1\n', encoding='utf-8')
    (tmp_path / 'repo/package.json').write_text('{"dependencies": {"react": "^19.1.0"}}', encoding='utf-8')
    ok = {'verificacion_codigo': {'archivo': 'backend/requirements.txt', 'paquete': 'scikit-learn', 'version': '1.9'}}
    mal = {'verificacion_codigo': {'archivo': 'package.json', 'paquete': 'react', 'version': '18'}}
    (tmp_path / 'dec/DT-01_a.json').write_text(json.dumps(ok), encoding='utf-8')
    (tmp_path / 'dec/DT-02_b.json').write_text(json.dumps(mal), encoding='utf-8')
    errores, _ = md.verificar_versiones(tmp_path / 'dec', tmp_path / 'repo')
    assert len(errores) == 1 and 'react' in errores[0] and '19.1.0' in errores[0]
