# -*- coding: utf-8 -*-
"""Versionado y protección del Word, aserciones, diapositivas, póster y control de calidad (versión 1.2.0)."""
import json
import py_compile
import sys

import docx
import pytest

from conftest import PLUGIN, correr, png_minimo

import versionado_docx as vd  # scripts_comunes está en sys.path (conftest)

DOC = 'skills/documento-titulacion/scripts'


def documento(ruta, encabezado='LOGO UNEMI', cuerpo=('Primer párrafo.', 'Segundo párrafo.'), logo=None):
    d = docx.Document()
    sec = d.sections[0]
    sec.header.paragraphs[0].text = encabezado
    if logo:
        sec.header.paragraphs[0].add_run().add_picture(str(logo))
    sec.footer.paragraphs[0].text = 'Pie de página'
    d.add_paragraph('Portada: Título del proyecto')
    d.add_heading('RESUMEN', 1)
    for t in cuerpo:
        d.add_paragraph(t)
    d.add_heading('Referencias', 1)
    d.add_paragraph('Pérez, A. (2024). Un artículo. Revista, 1(2), 3–4.')
    d.save(str(ruta))
    return ruta


def test_huella_intacta_si_solo_se_agrega_contenido(tmp_path):
    base = documento(tmp_path / 'a.docx', logo=png_minimo(tmp_path / 'logo.png'))
    h = vd.huella(str(base))
    d = docx.Document(str(base))
    d.add_paragraph('Párrafo nuevo del lote.')
    d.save(str(tmp_path / 'b.docx'))
    dif = vd.comparar_huellas(h, vd.huella(str(tmp_path / 'b.docx')))
    assert not [x for x in dif if x[0] == 'FALLA']


def test_huella_detecta_encabezado_alterado(tmp_path):
    base = documento(tmp_path / 'a.docx')
    h = vd.huella(str(base))
    alterado = documento(tmp_path / 'b.docx', encabezado='OTRO ENCABEZADO')
    fallas = [t for n, t in vd.comparar_huellas(h, vd.huella(str(alterado))) if n == 'FALLA']
    assert any('Cambió el contenido de' in t and 'header' in t for t in fallas), fallas


def test_huella_detecta_logo_cambiado(tmp_path):
    a = documento(tmp_path / 'a.docx', logo=png_minimo(tmp_path / 'l1.png', 40, 20))
    b = documento(tmp_path / 'b.docx', logo=png_minimo(tmp_path / 'l2.png', 60, 30))
    assert any(n == 'FALLA' for n, _ in vd.comparar_huellas(vd.huella(str(a)), vd.huella(str(b))))


def test_solo_inserciones(tmp_path):
    a = documento(tmp_path / 'a.docx')
    d = docx.Document(str(a))
    d.add_paragraph('Añadido.')
    d.save(str(tmp_path / 'ins.docx'))
    assert vd.solo_inserciones(str(a), str(tmp_path / 'ins.docx')) == []
    mod = documento(tmp_path / 'mod.docx', cuerpo=('Primer párrafo CAMBIADO.', 'Segundo párrafo.'))
    assert vd.solo_inserciones(str(a), str(mod))


def test_copia_versionada_no_toca_el_original_ni_sobrescribe(tmp_path):
    orig = documento(tmp_path / 'Avance_2.docx')
    bytes_antes = orig.read_bytes()
    v2, h2 = vd.crear_copia_versionada(str(orig))
    v3, _ = vd.crear_copia_versionada(str(orig))
    assert v2.endswith('Avance_2_v02.docx') and v3.endswith('Avance_2_v03.docx')
    assert json.loads(open(h2, encoding='utf-8').read())['secciones']
    assert orig.read_bytes() == bytes_antes
    with pytest.raises(FileExistsError):
        vd.crear_copia_versionada(str(orig), version=2)


def test_archivo_automatico_empieza_en_v01(tmp_path):
    salida = documento(tmp_path / 'Avance_2.docx')
    v1, _ = vd.crear_copia_versionada(str(salida), destino=str(tmp_path / 'versiones'), desde=1)
    v2, _ = vd.crear_copia_versionada(str(salida), destino=str(tmp_path / 'versiones'), desde=1)
    assert v1.endswith('Avance_2_v01.docx') and v2.endswith('Avance_2_v02.docx')


def test_base_sin_version():
    assert vd.base_sin_version('x/Avance_2_v05.docx') == 'Avance_2'
    assert vd.base_sin_version('Avance_2_RESPALDO_ANTES_CAMBIO.docx') == 'Avance_2'


def test_restaurar_encabezados_desde_la_plantilla(tmp_path):
    plantilla = documento(tmp_path / 'plantilla.docx', encabezado='ENCABEZADO OFICIAL',
                          logo=png_minimo(tmp_path / 'logo.png'))
    perdido = docx.Document()
    perdido.add_heading('RESUMEN', 1)
    perdido.add_paragraph('Texto que no debe cambiar.')
    perdido.save(str(tmp_path / 'perdido.docx'))
    assert vd.comparar_con_plantilla(str(tmp_path / 'perdido.docx'), str(plantilla))
    acciones = vd.restaurar_encabezados(str(tmp_path / 'perdido.docx'), str(plantilla), str(tmp_path / 'ok.docx'))
    assert acciones
    assert not [x for x in vd.comparar_con_plantilla(str(tmp_path / 'ok.docx'), str(plantilla)) if x[0] == 'FALLA']
    assert [p.text for p in docx.Document(str(tmp_path / 'ok.docx')).paragraphs] == ['RESUMEN', 'Texto que no debe cambiar.']


def test_aserciones_detectan_una_correccion_revertida(tmp_path):
    d = documento(tmp_path / 'a.docx', cuerpo=('El ROC-AUC fue 0,912.', 'Otro párrafo.'))
    ok = [{'descripcion': 'cifra', 'contiene': '0,912', 'no_contiene': '0,91 '}]
    assert vd.verificar_aserciones(str(d), ok) == []
    revertida = documento(tmp_path / 'r.docx', cuerpo=('El ROC-AUC fue 0,91 .', 'Otro párrafo.'))
    assert vd.verificar_aserciones(str(revertida), ok)


def test_cli_huella_y_aserciones(tmp_path):
    a = documento(tmp_path / 'a.docx')
    h = tmp_path / 'h.json'
    assert correr(f'{DOC}/huella.py', 'crear', a, '-o', h).returncode == 0
    assert correr(f'{DOC}/huella.py', 'verificar', a, '--contra', h).returncode == 0
    otro = documento(tmp_path / 'o.docx', encabezado='DISTINTO')
    r = correr(f'{DOC}/huella.py', 'verificar', otro, '--contra', h)
    assert r.returncode == 1 and 'ALTERADA' in r.stdout
    ase = tmp_path / 'aserciones.json'
    assert correr(f'{DOC}/aserciones.py', 'registrar', ase, 'cifra', '--contiene', 'Primer').returncode == 0
    assert correr(f'{DOC}/aserciones.py', 'verificar', a, ase).returncode == 0
    assert correr(f'{DOC}/aserciones.py', 'registrar', ase, 'x', '--contiene', 'NO EXISTE').returncode == 0
    assert correr(f'{DOC}/aserciones.py', 'verificar', a, ase).returncode == 1
    r = correr(f'{DOC}/copia_trabajo.py', a)
    assert r.returncode == 0 and (tmp_path / 'a_v02.docx').exists()
    assert correr(f'{DOC}/diff_versiones.py', a, tmp_path / 'a_v02.docx', '--solo-inserciones').returncode == 0


def test_todos_los_scripts_compilan():
    for ruta in list((PLUGIN / 'skills').rglob('*.py')) + list((PLUGIN / 'scripts_comunes').rglob('*.py')):
        py_compile.compile(str(ruta), cfile=str(PLUGIN / '.pytest_cache' / 'x.pyc'), doraise=True)


# ───────────── presentaciones ─────────────
@pytest.fixture
def contenido(tmp_path):
    ruta = tmp_path / 'diap.json'
    ruta.write_text((PLUGIN / 'skills/entrega-y-sustentacion/plantillas/diapositivas-ejemplo.json').read_text(encoding='utf-8'),
                    encoding='utf-8')
    return ruta


def test_banco_de_iconos():
    from presentaciones import diapositivas
    assert len(diapositivas.lista_iconos()) >= 85
    for color in ('blanco', 'marino', 'naranja', 'gris'):
        assert diapositivas.icono('candado', color)
    assert diapositivas.icono('no_existe') is None


def test_diapositivas_se_generan_y_pasan_el_control(contenido, tmp_path):
    salida = tmp_path / 'Sustentacion.pptx'
    r = correr('skills/entrega-y-sustentacion/scripts/diapositivas.py', contenido, '-o', salida)
    assert r.returncode == 0, r.stderr
    assert salida.exists()
    from pptx import Presentation
    assert len(Presentation(str(salida)).slides) >= 12
    qa = correr('skills/entrega-y-sustentacion/scripts/qa_pptx.py', salida, '--sin-pdf')
    assert qa.returncode == 0, qa.stdout


def test_qa_detecta_marcador_de_plantilla(tmp_path):
    from pptx import Presentation
    from pptx.util import Cm
    prs = Presentation()
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    tb = sl.shapes.add_textbox(Cm(1), Cm(1), Cm(10), Cm(2))
    tb.text_frame.text = 'Haga clic para editar el título'
    ruta = tmp_path / 'p.pptx'
    prs.save(str(ruta))
    r = correr('skills/entrega-y-sustentacion/scripts/qa_pptx.py', ruta, '--sin-pdf')
    assert r.returncode == 1 and 'marcador de plantilla' in r.stdout


def _hay_exportador():
    from presentaciones import render
    return bool(render.buscar_soffice()) or (sys.platform == 'win32' and
                                             __import__('os').path.exists(r'C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE'))


@pytest.mark.skipif('not _hay_exportador()', reason='Se necesita PowerPoint o LibreOffice para el PDF del póster')
def test_poster_genera_pdf_y_vista(tmp_path):
    ruta = tmp_path / 'poster.json'
    ruta.write_text((PLUGIN / 'skills/entrega-y-sustentacion/plantillas/poster-ejemplo.json').read_text(encoding='utf-8'),
                    encoding='utf-8')
    r = correr('skills/entrega-y-sustentacion/scripts/poster.py', ruta, '-o', tmp_path / 'Poster')
    assert r.returncode == 0, r.stderr
    assert (tmp_path / 'Poster.pptx').exists() and (tmp_path / 'Poster.pdf').exists()
    assert (tmp_path / 'Poster_vista.png').exists()
