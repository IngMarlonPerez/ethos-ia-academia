# -*- coding: utf-8 -*-
"""Inventario DOI↔PDF (acceso abierto) y similitud preventiva (versión 1.2.0)."""
import importlib.util
import subprocess
import sys
from pathlib import Path

import docx
import pytest

PLUGIN = Path(__file__).resolve().parents[1]


def cargar(rel):
    ruta = PLUGIN / rel
    spec = importlib.util.spec_from_file_location(ruta.stem, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def correr(rel, *args):
    return subprocess.run([sys.executable, str(PLUGIN / rel), *map(str, args)], capture_output=True, text=True,
                          encoding='utf-8', errors='replace')


inv = cargar('skills/revision-sistematica/scripts/inventario_pdf.py')
sim = cargar('skills/redaccion-apa7/scripts/similitud.py')
INV = 'skills/revision-sistematica/scripts/inventario_pdf.py'
SIM = 'skills/redaccion-apa7/scripts/similitud.py'


def pdf_con_doi(ruta, doi):
    """PDF mínimo de una página con el DOI impreso (para probar la lectura con pypdf)."""
    pymupdf = pytest.importorskip('pymupdf')
    d = pymupdf.open()
    d.new_page().insert_text((72, 72), f'Artículo de prueba. https://doi.org/{doi}')
    d.save(str(ruta))
    d.close()


def test_norm_doi():
    assert inv.norm_doi('https://doi.org/10.1016/J.X.2024.1.') == '10.1016/j.x.2024.1'
    assert inv.norm_doi('doi: 10.1/AbC') == '10.1/abc'


def test_leer_dois_de_txt_y_csv(tmp_path):
    (tmp_path / 'a.txt').write_text('10.1/a\nhttps://doi.org/10.1/B\n10.1/a\n', encoding='utf-8')
    (tmp_path / 'a.csv').write_text('id,DOI\n1,10.2/x\n2,\n', encoding='utf-8')
    assert inv.leer_dois(str(tmp_path / 'a.txt')) == ['10.1/a', '10.1/b']
    assert inv.leer_dois(str(tmp_path / 'a.csv')) == ['10.2/x']


def test_inventario_detecta_faltantes_pdf_danado_y_sobrantes(tmp_path):
    carpeta = tmp_path / 'pdf'
    carpeta.mkdir()
    pdf_con_doi(carpeta / 'Perez_2024_tema.pdf', '10.1000/presente')
    pdf_con_doi(carpeta / 'Otro_2023.pdf', '10.1000/sobrante')
    (carpeta / 'Roto_2022.pdf').write_text('<html>bloqueado por Cloudflare</html>', encoding='utf-8')
    r = inv.inventario(['10.1000/presente', '10.1000/falta'], carpeta)
    assert r['faltan'] == ['10.1000/falta']
    assert r['danados'] == ['Roto_2022.pdf']
    assert r['sobrantes'] == ['Otro_2023.pdf']
    assert [f['estado'] for f in r['filas']] == ['presente', 'FALTA']


def test_cli_inventario_codigos_de_salida(tmp_path):
    carpeta = tmp_path / 'pdf'
    carpeta.mkdir()
    pdf_con_doi(carpeta / 'A.pdf', '10.1000/uno')
    (tmp_path / 'ok.txt').write_text('10.1000/uno\n', encoding='utf-8')
    (tmp_path / 'falta.txt').write_text('10.1000/uno\n10.1000/dos\n', encoding='utf-8')
    assert correr(INV, tmp_path / 'ok.txt', '--carpeta', carpeta).returncode == 0
    r = correr(INV, tmp_path / 'falta.txt', '--carpeta', carpeta, '--salida', tmp_path / 'c' / 'inv.csv')
    assert r.returncode == 1 and '10.1000/dos' in r.stdout and (tmp_path / 'c' / 'inv.csv').exists()
    assert not list(carpeta.glob('*.csv')), 'la carpeta del usuario solo se lee'


FUENTE = ('La gobernanza de datos en las organizaciones educativas exige roles claros, políticas documentadas y '
          'mecanismos de auditoría que permitan verificar el cumplimiento de la normativa vigente en cada ciclo.')


def test_similitud_marca_copia_literal_y_parafrasis_cercana():
    idx_n, idx_3 = sim.indexar([('Autor (2024)', FUENTE)], 8)
    copia = 'Como se sabe, la gobernanza de datos en las organizaciones educativas exige roles claros hoy.'
    fallas, _ = sim.analizar([copia], idx_n, idx_3, 8)
    assert fallas and 'Autor (2024)' in fallas[0][0]
    propia = 'Nuestro prototipo calcula el riesgo de abandono con un modelo de bosques aleatorios entrenado en 2025.'
    assert sim.analizar([propia], idx_n, idx_3, 8) == ([], [])


def test_similitud_ignora_titulos_leyendas_y_referencias(tmp_path):
    d = docx.Document()
    d.add_heading('Introducción', 1)
    d.add_paragraph('Un párrafo propio sin relación con la fuente.')
    d.add_paragraph('Figura 1. ' + FUENTE)
    d.add_heading('Referencias', 1)
    d.add_paragraph(FUENTE)
    ruta = tmp_path / 't.docx'
    d.save(str(ruta))
    assert sim.parrafos_docx(str(ruta)) == ['Un párrafo propio sin relación con la fuente.']


def test_cli_similitud_codigo_de_salida(tmp_path):
    (tmp_path / 'fuentes.csv').write_text(f'primer_autor,anio,resumen\nPérez,2024,"{FUENTE}"\n', encoding='utf-8')
    (tmp_path / 'copia.txt').write_text('La gobernanza de datos en las organizaciones educativas exige roles claros.',
                                        encoding='utf-8')
    (tmp_path / 'propio.txt').write_text('El modelo propuesto supera a la línea base en validación temporal.', encoding='utf-8')
    assert correr(SIM, tmp_path / 'copia.txt', '--fuentes', tmp_path / 'fuentes.csv').returncode == 1
    assert correr(SIM, tmp_path / 'propio.txt', '--fuentes', tmp_path / 'fuentes.csv').returncode == 0
    assert correr(SIM, tmp_path / 'propio.txt').returncode == 2
