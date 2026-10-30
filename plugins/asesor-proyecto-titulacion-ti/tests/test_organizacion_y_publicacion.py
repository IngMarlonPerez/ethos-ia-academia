# -*- coding: utf-8 -*-
"""Pruebas de las skills organizacion-repositorio, uso-etico-ia y publicacion-github (v1.1.0)."""
from __future__ import annotations

import json
import subprocess
import zipfile

import docx
import pytest

from conftest import PLUGIN, cargar, correr


def _docx(ruta, autor):
    d = docx.Document()
    d.add_paragraph('texto')
    d.core_properties.author = autor
    d.core_properties.last_modified_by = autor
    d.save(str(ruta))
    return ruta


def test_copiar_biblioteca_deja_el_generador_autocontenido(tmp_path):
    (tmp_path / 'titulacion.json').write_text(json.dumps({'perfil': 'unemi', 'autores': ['A', 'B']}), encoding='utf-8')
    r = correr('skills/documento-titulacion/scripts/copiar_biblioteca.py', tmp_path)
    assert r.returncode == 0, r.stderr
    lib = tmp_path / '_automatizacion' / 'lib'
    for nombre in ('docx_titulacion.py', 'formato_es.py', 'perfil.py', 'trazabilidad.py', 'tabla_trabajos_previos.py',
                   'matriz_decision.py'):
        assert (lib / nombre).exists()
    assert (tmp_path / '_automatizacion' / 'perfiles' / 'unemi.json').exists()
    esqueleto = (PLUGIN / 'skills/documento-titulacion/scripts/generador_avance.py').read_text(encoding='utf-8')
    assert 'installed_plugins' not in esqueleto and '.claude' not in esqueleto
    assert "LIB = Path(__file__).resolve().parent / 'lib'" in esqueleto
    assert 'core_properties.author' in esqueleto


def test_rastros_ia_detecta_firma_y_autor_ajeno_y_corrige(tmp_path):
    (tmp_path / 'main.py').write_text('x = 1  # ajuste a pedido del usuario\n', encoding='utf-8')
    (tmp_path / 'NOTAS.md').write_text('Co-Authored-By: Claude <noreply@anthropic.com>\n', encoding='utf-8')
    (tmp_path / 'ok.py').write_text('modelo = "gemini"  # proveedor del producto\n', encoding='utf-8')
    _docx(tmp_path / 'avance.docx', 'Otra Persona')
    anexo = tmp_path / 'ANEXO_USO_ETICO_IA'
    anexo.mkdir()
    (anexo / 'declaracion.md').write_text('Se usó Claude.', encoding='utf-8')
    r = correr('skills/uso-etico-ia/scripts/rastros_ia.py', tmp_path, '--autores', 'Ana Pérez; Luis Mora',
               '--excluir', 'ANEXO_USO_ETICO_IA')
    assert r.returncode == 1
    assert 'main.py:1' in r.stdout and 'NOTAS.md:1' in r.stdout and 'avance.docx' in r.stdout
    assert 'ok.py' not in r.stdout and 'declaracion.md' not in r.stdout
    (tmp_path / 'main.py').write_text('x = 1\n', encoding='utf-8')
    (tmp_path / 'NOTAS.md').write_text('Notas técnicas.\n', encoding='utf-8')
    r2 = correr('skills/uso-etico-ia/scripts/rastros_ia.py', tmp_path, '--autores', 'Ana Pérez; Luis Mora',
                '--excluir', 'ANEXO_USO_ETICO_IA', '--fijar-autoria')
    assert r2.returncode == 0, r2.stdout
    assert docx.Document(str(tmp_path / 'avance.docx')).core_properties.author == 'Ana Pérez; Luis Mora'
    with zipfile.ZipFile(tmp_path / 'avance.docx') as z:
        assert 'word/document.xml' in z.namelist()


def test_mover_a_revision_conserva_ruta_y_no_sobrescribe(tmp_path):
    (tmp_path / 'scripts').mkdir()
    (tmp_path / 'scripts' / 'viejo.bat').write_text('echo', encoding='utf-8')
    mod = cargar('skills/organizacion-repositorio/scripts/mover_a_revision.py')
    movidos = mod.mover(tmp_path, ['scripts/viejo.bat'], 'Scripts heredados', 'Producto anterior', 'No lo usa el pipeline')
    assert movidos == ['scripts/viejo.bat']
    assert (tmp_path / '_POR_REVISAR_ELIMINAR' / 'scripts' / 'viejo.bat').exists()
    assert not (tmp_path / 'scripts' / 'viejo.bat').exists()
    indice = (tmp_path / '_POR_REVISAR_ELIMINAR' / 'INDICE.md').read_text(encoding='utf-8')
    assert '`scripts/viejo.bat`' in indice and 'No lo usa el pipeline' in indice
    (tmp_path / 'scripts' / 'viejo.bat').write_text('otro', encoding='utf-8')
    with pytest.raises(SystemExit):
        mod.mover(tmp_path, ['scripts/viejo.bat'], 'x', 'y', 'z')


def test_inventario_marca_pesados_y_sensibles(tmp_path):
    (tmp_path / 'video.mp4').write_bytes(b'0' * 10)
    (tmp_path / '.env').write_text('CLAVE=1', encoding='utf-8')
    (tmp_path / 'node_modules').mkdir()
    mod = cargar('skills/organizacion-repositorio/scripts/inventario.py')
    inv = mod.inventario(tmp_path, 50)
    assert 'video.mp4' in inv['candidatos']['video']
    assert '.env' in inv['candidatos']['secreto local (.env)']
    assert any('node_modules' in x for x in inv['candidatos']['dependencias o cachés (se regeneran)'])


def _git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True)


@pytest.mark.skipif(subprocess.run(['git', '--version'], capture_output=True).returncode != 0, reason='sin git')
def test_preparar_publicacion_bloquea_env_y_carpeta_local(tmp_path):
    repo = tmp_path / 'repo'
    repo.mkdir()
    _git(repo, 'init', '-q')
    (repo / 'README.md').write_text('# Proyecto\n', encoding='utf-8')
    (repo / '.env').write_text('DB_PASSWORD=x\n', encoding='utf-8')
    (repo / '_POR_REVISAR_ELIMINAR').mkdir()
    (repo / '_POR_REVISAR_ELIMINAR' / 'a.txt').write_text('a', encoding='utf-8')
    lista = tmp_path / 'publicar.txt'
    r = correr('skills/publicacion-github/scripts/preparar_publicacion.py', repo, '--lista', lista)
    assert r.returncode == 1
    assert '.env' in r.stdout and '_POR_REVISAR_ELIMINAR/a.txt' in r.stdout
    (repo / '.gitignore').write_text('.env\n_POR_REVISAR_ELIMINAR/\n', encoding='utf-8')
    r2 = correr('skills/publicacion-github/scripts/preparar_publicacion.py', repo, '--lista', lista)
    assert 'Se publicarían 2 archivos' in r2.stdout
    assert '_POR_REVISAR_ELIMINAR/a.txt: carpeta solo local' not in r2.stdout


def test_control_numeracion_de_referencias_y_anexos(tmp_path):
    mod = cargar('skills/verificar-coherencia/scripts/verificar_coherencia.py', 'verificar_coherencia_num')
    d = docx.Document()
    d.add_heading('1. Introducción', level=1)
    d.add_heading('2. Referencias', level=1)
    d.add_heading('Anexos', level=1)
    mod.errores.clear()
    mod.control_numeracion(d)
    assert len(mod.errores) == 1 and '2. Referencias' in mod.errores[0]


def test_tabla_trabajos_previos_cierra_con_presente_trabajo():
    mod = cargar('skills/trabajos-previos/scripts/tabla_trabajos_previos.py')
    datos = {'trabajos': [{'cita': 'Pérez (2025)', 'problema': 'P', 'tecnica': 'T', 'tecnologias': {'lenguaje': 'Python'},
                           'arquitectura': 'aislado', 'validacion_metricas': 'CV', 'resultado': 'AUC 0,8',
                           'limitacion': 'una sede', 'relacion_con_este_trabajo': 'integra', 'decision': 'Incluido'}],
             'presente_trabajo': {'problema_tecnica': 'Abandono; RF', 'tecnologias': 'Python', 'arquitectura': 'desacoplada',
                                  'validacion_resultado': 'temporal', 'limitacion': 'sintético'}}
    filas = mod.filas_word(datos)
    assert filas[0][-1] == 'Qué aporta el presente caso'
    assert filas[-1][0] == 'Presente trabajo' and len(filas[-1]) == len(filas[0])
