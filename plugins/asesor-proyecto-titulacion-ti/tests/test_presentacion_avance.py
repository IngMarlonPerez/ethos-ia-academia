# -*- coding: utf-8 -*-
"""Presentación de un avance sobre la del avance anterior y su guion (versión 1.3.0)."""
import hashlib
import json

import docx
from pptx import Presentation
from pptx.util import Inches

from conftest import PLUGIN, correr, png_minimo

SCRIPT = 'skills/presentacion-avance/scripts/presentacion_avance.py'
EJEMPLO = PLUGIN / 'skills/presentacion-avance/plantillas/presentacion-avance-ejemplo.json'


def base_anterior(ruta):
    """Presentación de un avance anterior: portada, una diapositiva propia de ese avance y cierre."""
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    for textos in (['DESARROLLO TRABAJO DE TITULACIÓN', 'TÍTULO ANTERIOR DEL TRABAJO'], ['Infografía del avance 1'],
                   ['Gracias']):
        s = prs.slides.add_slide(prs.slide_layouts[6])
        for i, t in enumerate(textos):
            s.shapes.add_textbox(Inches(1), Inches(1 + i), Inches(8), Inches(0.8)).text_frame.text = t
    prs.save(str(ruta))
    return ruta


def preparar(tmp_path):
    (tmp_path / 'presentacion_avance1').mkdir()
    base = base_anterior(tmp_path / 'presentacion_avance1' / 'PRESENTACION_AVANCE_I.pptx')
    carpeta = tmp_path / 'presentacion_avance2'
    carpeta.mkdir()
    (tmp_path / 'figuras').mkdir()
    for n in ('arquitectura', 'secuencia', 'estados', 'capturas'):
        png_minimo(tmp_path / 'figuras' / f'{n}.png', 60, 40)
    cfg = json.loads(EJEMPLO.read_text(encoding='utf-8'))
    cfg['diapositivas'] = [{**d, 'imagen': d['imagen'].replace('../../', '../')} if 'imagen' in d else d
                           for d in cfg['diapositivas']]
    for d in cfg['diapositivas']:
        if 'imagenes' in d:
            d['imagenes'] = [[r.replace('../../', '../'), p] for r, p in d['imagenes']]
    cfg['base'] = '../presentacion_avance1/PRESENTACION_AVANCE_I.pptx'
    cfg['cierre']['diapositiva_base'] = 3
    ruta = carpeta / 'presentacion.json'
    ruta.write_text(json.dumps(cfg, ensure_ascii=False), encoding='utf-8')
    return base, carpeta, ruta, cfg


def test_genera_presentacion_y_guion_sin_tocar_la_base(tmp_path):
    base, carpeta, ruta, cfg = preparar(tmp_path)
    huella = hashlib.md5(base.read_bytes()).hexdigest()
    r = correr(SCRIPT, ruta)
    assert r.returncode == 0, r.stderr
    assert hashlib.md5(base.read_bytes()).hexdigest() == huella  # la presentación anterior no cambia
    prs = Presentation(str(carpeta / cfg['salida']))
    assert len(prs.slides) == len(cfg['diapositivas']) + 2  # portada + contenido + cierre
    textos = [' '.join(sh.text_frame.text for sh in s.shapes if sh.has_text_frame) for s in prs.slides]
    assert 'AVANCE 2' in textos[0] and 'TÍTULO VIGENTE' in textos[0]
    assert 'Gracias' in textos[-1]
    assert not any('Infografía del avance 1' in t for t in textos)  # se quitan las del avance anterior
    assert prs.slides[1].notes_slide.notes_text_frame.text == cfg['diapositivas'][0]['notas']
    assert prs.core_properties.author == cfg['autor']
    guion = docx.Document(str(carpeta / (cfg['guion'] + '.docx')))
    titulos = [p.text for p in guion.paragraphs if p.style.name.startswith('Heading 1')]
    assert len(titulos) == len(cfg['diapositivas']) + 2
    assert (carpeta / (cfg['guion'] + '.md')).read_text(encoding='utf-8').count('## Diapositiva') == len(titulos)


def test_portada_sin_el_texto_a_reemplazar_se_detiene(tmp_path):
    _, carpeta, ruta, cfg = preparar(tmp_path)
    cfg['portada']['reemplazos'] = {'TEXTO QUE NO EXISTE': 'x'}
    ruta.write_text(json.dumps(cfg, ensure_ascii=False), encoding='utf-8')
    r = correr(SCRIPT, ruta)
    assert r.returncode != 0 and 'TEXTO QUE NO EXISTE' in (r.stderr + r.stdout)


def test_tipo_desconocido_se_informa(tmp_path):
    _, carpeta, ruta, cfg = preparar(tmp_path)
    cfg['diapositivas'].append({'tipo': 'inventado', 'titulo': 'x'})
    ruta.write_text(json.dumps(cfg, ensure_ascii=False), encoding='utf-8')
    r = correr(SCRIPT, ruta)
    assert r.returncode != 0 and 'inventado' in (r.stderr + r.stdout)
