# -*- coding: utf-8 -*-
import json

import docx
import pytest

from conftest import cargar, correr, png_minimo

dt = cargar('skills/documento-titulacion/scripts/docx_titulacion.py', 'docx_titulacion')


def plantilla(ruta):
    d = docx.Document()
    d.add_heading('RESUMEN', 1)
    d.add_paragraph('Se desarrolló un prototipo que alcanzó un ROC-AUC de 0,912 según Pérez et al. (2024).')
    d.add_paragraph('Palabras clave: abandono, predicción, inteligencia de negocios')
    d.add_heading('1. Introducción', 1)
    d.add_paragraph('Como señala Pérez et al. (2024), el abandono es costoso (Zapata, 2025); el modelo logró 0,912.')
    d.add_heading('Referencias', 1)
    d.add_paragraph('Pérez, A., Mora, B., & Ruiz, C. (2024). Un artículo. Revista, 1(2), 3–4. https://doi.org/10.1/x')
    d.add_paragraph('Zapata, D. (2025). Otro artículo. Revista, 2(1), 5–6.')
    d.save(str(ruta))
    return ruta


def test_insertor_tabla_figura_codigo_y_referencia(tmp_path):
    doc = docx.Document(str(plantilla(tmp_path / 'p.docx')))
    ins = dt.Insertor(doc, {'formato': {'fuente': 'Arial', 'tam_pt': 12}})
    a = ins.titulo(dt.buscar(doc, 'Referencias'), '2. Análisis del caso', 1, salto_pagina=True, antes=True)
    a = ins.parrafo(a, 'Texto con **negrita** y *cursiva*.')
    a = ins.tabla(a, [['A', 'B'], ['1', '2']], 'Una tabla')
    a = ins.figura(a, png_minimo(tmp_path / 'f.png'), 'Una figura')
    a = ins.codigo(a, 'def f():\n    return 1', None)
    dt.insertar_referencia(doc, 'Zapata', dt.referencia_desde_markdown('Rivas, E. (2023). Título. *Revista, 9*(1), 1–2.'))
    salida = tmp_path / 's.docx'
    doc.save(str(salida))
    d = docx.Document(str(salida))
    textos = [p.text for p in d.paragraphs]
    assert 'Tabla 1' in textos and 'Figura 1' in textos and 'Una tabla' in textos
    assert textos.index('2. Análisis del caso') < textos.index('Referencias')
    assert textos.index('Rivas, E. (2023). Título. Revista, 9(1), 1–2.') == textos.index('Zapata, D. (2025). Otro artículo. Revista, 2(1), 5–6.') - 1
    rivas = next(p for p in d.paragraphs if p.text.startswith('Rivas'))
    assert any(r.italic for r in rivas.runs) and 'hyperlink' not in rivas._p.xml
    assert d.tables[0].rows[0]._tr.xml.count('tblHeader') == 1


def test_funcion_py_y_fragmento(tmp_path):
    f = tmp_path / 'm.py'
    f.write_text('X = 1\n\ndef suma(a, b):\n    """Suma."""\n    return a + b\n', encoding='utf-8')
    assert dt.funcion_py(f, 'suma').startswith('def suma(a, b):')
    assert dt.funcion_py(f, 'X') == 'X = 1'
    js = tmp_path / 'a.js'
    js.write_text('const a = 1\nexport function f() {\n  return a\n}\n', encoding='utf-8')
    assert dt.fragmento(js, 'export function f', '}', exacto=True) == 'export function f() {\n  return a\n}'
    with pytest.raises(KeyError):
        dt.funcion_py(f, 'no_existe')


def config(tmp_path, valor_artefacto):
    plantilla(tmp_path / 'doc.docx')
    (tmp_path / 'art').mkdir(exist_ok=True)
    (tmp_path / 'art/metrics.json').write_text(json.dumps({'temporal': {'roc_auc': valor_artefacto}}), encoding='utf-8')
    cfg = {'avance': 1, 'documento': 'doc.docx', 'pdf': None, 'estilo_referencias': 'NoExiste',
           'cifras': [{'nombre': 'ROC-AUC', 'archivo': 'art/metrics.json', 'ruta': 'temporal.roc_auc', 'decimales': 3,
                       'en': ['resumen', 'cuerpo']}],
           'comprobar': {'apa_plugin_investigacion': False, 'paginas_minimas': False}}
    (tmp_path / 'coherencia.json').write_text(json.dumps(cfg), encoding='utf-8')
    (tmp_path / 'perfil.json').write_text(json.dumps({
        'id': 't', 'secciones': [{'id': 'resumen', 'reglas': {'max_palabras': 150, 'max_palabras_clave': 5}}],
        'requisitos': {'min_referencias': 2, 'anios_referencias': 5}}), encoding='utf-8')


def test_verificar_coherencia_ok_y_cifra_distinta(tmp_path):
    config(tmp_path, 0.9121)
    r = correr('skills/verificar-coherencia/scripts/verificar_coherencia.py', '--raiz', tmp_path, '--config', 'coherencia.json',
               '--perfil', str(tmp_path / 'perfil.json'))
    assert r.returncode == 0, r.stdout + r.stderr
    assert 'Coherencia verificada' in r.stdout
    config(tmp_path, 0.8)
    r = correr('skills/verificar-coherencia/scripts/verificar_coherencia.py', '--raiz', tmp_path, '--config', 'coherencia.json',
               '--perfil', str(tmp_path / 'perfil.json'))
    assert r.returncode == 1 and 'Resumen: falta «ROC-AUC» = 0,800' in r.stdout


def test_lineas_unidas_titulos_numerados():
    vc = cargar('skills/verificar-coherencia/scripts/verificar_coherencia.py', 'vc')
    assert vc.lineas_unidas('1.1  \nDescripción \ntexto') == ['1.1 Descripción', 'texto']

