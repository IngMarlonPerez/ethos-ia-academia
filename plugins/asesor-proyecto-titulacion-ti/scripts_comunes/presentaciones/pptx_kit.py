# -*- coding: utf-8 -*-
"""Kit de dibujo editable sobre python-pptx: medición real del texto (métricas de Arial/Calibri), cajas con texto
que se ajustan a su contenido, flechas, círculos, gráficos nativos y exportación a PNG (300 dpi, ancho exacto) y SVG.
Todo lo que se dibuja queda EDITABLE en PowerPoint, Google Slides o Canva (importar .pptx)."""
import os
import re
import shutil
import tempfile
from functools import lru_cache

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Cm, Emu, Pt

# ------------------------------------------------------------------ paletas
PALETAS = {
    # sobria: para figuras de tesis/artículo (imprime bien y se lee en escala de grises)
    'sobria': dict(primario='1F3864', secundario='2F5597', sec_claro='DEEAF6', acento='C55A11', acento_claro='FBE5D6',
                   positivo='548235', positivo_claro='E2EFDA', neutro='7F7F7F', neutro_claro='F2F2F2',
                   negativo='B0413E', negativo_claro='F6E5E4', texto='222222', blanco='FFFFFF', linea='404040'),
    # unemi: identidad institucional (presentaciones, póster)
    'unemi': dict(primario='203145', secundario='2C4760', sec_claro='EAF1F8', acento='EC8532', acento_claro='FCE9D6',
                  positivo='2E7D5B', positivo_claro='E3F0E9', neutro='5A6B7B', neutro_claro='F3F6F9',
                  negativo='B0413E', negativo_claro='F6E5E4', texto='1E2A36', blanco='FFFFFF', linea='5A6B7B'),
    # grises: para guías que exigen figuras en blanco y negro
    'grises': dict(primario='262626', secundario='404040', sec_claro='E7E6E6', acento='595959', acento_claro='F2F2F2',
                   positivo='404040', positivo_claro='EDEDED', neutro='7F7F7F', neutro_claro='F7F7F7',
                   negativo='262626', negativo_claro='D9D9D9', texto='000000', blanco='FFFFFF', linea='404040'),
}
PAR_COLORES = {  # nombre amigable -> (clave borde/relleno fuerte, clave relleno claro)
    'azul': ('secundario', 'sec_claro'), 'naranja': ('acento', 'acento_claro'), 'verde': ('positivo', 'positivo_claro'),
    'gris': ('neutro', 'neutro_claro'), 'rojo': ('negativo', 'negativo_claro'), 'marino': ('primario', 'sec_claro'),
}

# ------------------------------------------------------------------ medición de texto
_FUENTES = {   # (familia, negrita, cursiva) -> nombres de archivo posibles (Windows, Linux)
    ('Arial', False, False): ('arial.ttf', 'LiberationSans-Regular.ttf'),
    ('Arial', True, False): ('arialbd.ttf', 'LiberationSans-Bold.ttf'),
    ('Arial', False, True): ('ariali.ttf', 'LiberationSans-Italic.ttf'),
    ('Arial', True, True): ('arialbi.ttf', 'LiberationSans-BoldItalic.ttf'),
    ('Calibri', False, False): ('calibri.ttf', 'Carlito-Regular.ttf'),
    ('Calibri', True, False): ('calibrib.ttf', 'Carlito-Bold.ttf'),
    ('Calibri', False, True): ('calibrii.ttf', 'Carlito-Italic.ttf'),
    ('Calibri', True, True): ('calibriz.ttf', 'Carlito-BoldItalic.ttf'),
}
_DIRS = [
    r'C:\Windows\Fonts',
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts'),
    '/usr/share/fonts/truetype/liberation', '/usr/share/fonts/truetype/crosextra', '/usr/share/fonts/liberation',
    '/Library/Fonts', '/System/Library/Fonts/Supplemental', '/usr/share/fonts/truetype', '/usr/share/fonts',
]


@lru_cache(maxsize=None)
def _fuente(fam, neg, cur):
    from PIL import ImageFont
    nombres = _FUENTES.get((fam, neg, cur), _FUENTES[('Arial', neg, cur)])
    buscados = {n.lower() for n in nombres}
    for d in _DIRS:
        if not d or not os.path.isdir(d):
            continue
        for raiz, _, archivos in os.walk(d):
            for a in archivos:
                if a.lower() in buscados:
                    return ImageFont.truetype(os.path.join(raiz, a), 1000)
    raise FileNotFoundError(f'No se encontró ninguna de las fuentes {nombres} (Arial/Calibri en Windows; '
                            'fonts-liberation y fonts-crosextra-carlito en Linux).')


def ancho_pt(texto, tam, negrita=False, cursiva=False, familia='Arial'):
    return _fuente(familia, negrita, cursiva).getlength(texto) * tam / 1000.0


def envolver(texto, ancho_disp_pt, tam, negrita=False, cursiva=False, familia='Arial'):
    """Parte el texto en líneas que caben en `ancho_disp_pt` (respeta saltos \\n). Palabras más largas que la
    línea se dejan solas (nunca se cortan)."""
    lineas = []
    for parrafo in str(texto).split('\n'):
        linea = ''
        for pal in parrafo.split(' '):
            prueba = (linea + ' ' + pal).strip()
            if not linea or ancho_pt(prueba, tam, negrita, cursiva, familia) <= ancho_disp_pt:
                linea = prueba
            else:
                lineas.append(linea); linea = pal
        lineas.append(linea)
    return lineas


PT_CM = 2.54 / 72.0
INTERLINEADO = 1.18   # alto de línea = tamaño x 1.18 (se fija como espaciado exacto: igual en PowerPoint y LibreOffice)


def alto_lineas(n, tam, inter=INTERLINEADO):
    return n * tam * inter * PT_CM


# ------------------------------------------------------------------ lienzo con operaciones diferidas
class Lienzo:
    """Se dibuja en cm. El alto final se calcula con lo dibujado (ajuste automático), salvo que se fije `alto`."""

    def __init__(self, ancho_cm, alto_cm=None, paleta='sobria', familia='Arial', tam=10, margen=0.1):
        self.ancho, self.alto_fijo = ancho_cm, alto_cm
        self.pal = PALETAS[paleta] if isinstance(paleta, str) else paleta
        self.familia, self.tam, self.margen = familia, tam, margen
        self.ops, self.max_y = [], 0.0
        self.k = tam / 10.0            # escala de espacios: todo lo diseñado para 10 pt crece con la letra
        self.kg = self.k ** 0.6        # escala de grosores de línea

    # ---------------- medición
    def lineas(self, texto, ancho_cm, tam=None, negrita=False, cursiva=False, sangria_cm=0.0):
        tam = tam or self.tam
        return envolver(texto, (ancho_cm - sangria_cm) * 0.985 / PT_CM, tam, negrita, cursiva, self.familia)

    def alto_parrafos(self, parrafos, ancho_cm, pad=None):
        """parrafos: lista de dict(texto, negrita, cursiva, tam, vineta). Devuelve alto en cm con padding."""
        pad = 0.15 * self.k if pad is None else pad
        n_alto = 0.0
        for p in parrafos:
            tam = p.get('tam', self.tam)
            sang = 0.35 * tam / 10.0 if p.get('vineta') else 0.0
            n = len(self.lineas(p['texto'], ancho_cm - 2 * pad, tam, p.get('negrita', False), p.get('cursiva', False), sang))
            n_alto += alto_lineas(n, tam) + p.get('espacio_despues', 0.0)
        return n_alto + 2 * pad

    def _y(self, y):
        self.max_y = max(self.max_y, y)

    # ---------------- primitivas
    def caja(self, x, y, w, h, parrafos=None, relleno=None, borde=None, grosor=1.0, radio=None, alinear='izq',
             ancla='medio', pad=None, forma='redondeada', color_texto=None, sombra=False):
        pad = 0.15 * self.k if pad is None else pad
        radio = 0.15 * self.k if radio is None else radio
        self.ops.append(('caja', dict(x=x, y=y, w=w, h=h, parrafos=parrafos or [], relleno=relleno, borde=borde,
                                      grosor=grosor, radio=radio, alinear=alinear, ancla=ancla, pad=pad, forma=forma,
                                      color_texto=color_texto, sombra=sombra)))
        self._y(y + h)
        return h

    def caja_auto(self, x, y, w, parrafos, min_h=0.0, **kw):
        h = max(min_h, self.alto_parrafos(parrafos, w, kw.get('pad')))
        return self.caja(x, y, w, h, parrafos, **kw)

    def texto(self, x, y, w, parrafos, alinear='izq', pad=0.0, ancla='arriba', h=None, rotacion=0, color_texto=None):
        h = h if h is not None else self.alto_parrafos(parrafos, w, pad)
        self.ops.append(('caja', dict(x=x, y=y, w=w, h=h, parrafos=parrafos, relleno=None, borde=None, grosor=0,
                                      radio=0, alinear=alinear, ancla=ancla, pad=pad, forma='rect', rotacion=rotacion,
                                      color_texto=color_texto, sombra=False)))
        self._y(y + h if not rotacion else y + h / 2 + w / 2)
        return h

    def flecha(self, x1, y1, x2, y2, color=None, grosor=1.25, punta=True, doble=False):
        self.ops.append(('flecha', dict(x1=x1, y1=y1, x2=x2, y2=y2, color=color or self.pal['linea'], grosor=grosor,
                                        punta=punta, doble=doble)))
        self._y(max(y1, y2))

    def linea(self, x1, y1, x2, y2, color=None, grosor=1.0, discontinua=False):
        self.ops.append(('flecha', dict(x1=x1, y1=y1, x2=x2, y2=y2, color=color or self.pal['linea'], grosor=grosor,
                                        punta=False, doble=False, discontinua=discontinua)))
        self._y(max(y1, y2))

    def elipse(self, x, y, w, h, relleno=None, borde=None, grosor=1.0, parrafos=None, ancla='medio'):
        self.ops.append(('caja', dict(x=x, y=y, w=w, h=h, parrafos=parrafos or [], relleno=relleno, borde=borde,
                                      grosor=grosor, radio=0, alinear='centro', ancla=ancla, pad=0.05, forma='elipse',
                                      color_texto=None, sombra=False)))
        self._y(y + h)

    def grafico(self, x, y, w, h, tipo, categorias, series, **kw):
        self.ops.append(('grafico', dict(x=x, y=y, w=w, h=h, tipo=tipo, categorias=categorias, series=series, kw=kw)))
        self._y(y + h)

    def imagen(self, x, y, w, ruta, h=None):
        from PIL import Image
        if h is None:
            iw, ih = Image.open(ruta).size
            h = w * ih / iw
        self.ops.append(('imagen', dict(x=x, y=y, w=w, h=h, ruta=ruta)))
        self._y(y + h)
        return h

    def pegar(self, otro, dx, dy):
        """Copia lo dibujado en otro lienzo (por ejemplo, un diagrama de figuras.py) desplazado a (dx, dy) cm,
        conservando su tamaño de letra y el grosor de sus líneas. Sirve para poner diagramas en diapositivas y pósteres."""
        for op, a in otro.ops:
            a = dict(a)
            if a.get('parrafos'):
                a['parrafos'] = [dict(p, tam=p.get('tam', otro.tam)) for p in a['parrafos']]
            if 'grosor' in a:
                a['grosor'] = a['grosor'] * otro.kg / self.kg
            for kx in ('x', 'x1', 'x2'):
                if kx in a:
                    a[kx] += dx
            for ky in ('y', 'y1', 'y2'):
                if ky in a:
                    a[ky] += dy
            if op == 'grafico':
                a['kw'] = dict(a['kw'], tam=a['kw'].get('tam', otro.tam))
            self.ops.append((op, a))
        self._y(dy + otro.max_y)
        return otro.alto_final()

    # ---------------- salida
    def alto_final(self):
        return self.alto_fijo or round(self.max_y + self.margen, 3)

    def construir(self, prs=None, slide=None):
        """Dibuja en `slide` (si se pasa) o crea una presentación de una diapositiva del tamaño del lienzo."""
        nueva = prs is None
        if nueva:
            prs = Presentation()
            # PowerPoint exige al menos 2,54 cm por lado: si la figura es más baja, el PNG se recorta al exportar
            prs.slide_width, prs.slide_height = Cm(max(2.54, self.ancho)), Cm(max(2.54, self.alto_final()))
            slide = prs.slides.add_slide(prs.slide_layouts[6])
        for tipo, a in self.ops:
            getattr(self, '_dib_' + tipo)(slide, a)
        return prs

    def guardar(self, ruta_pptx):
        prs = self.construir()
        prs.save(ruta_pptx)
        return ruta_pptx

    # ---------------- dibujo real
    def _color(self, c):
        if c is None:
            return None
        c = self.pal.get(c, c)
        return RGBColor.from_string(c.lstrip('#').upper())

    def _fuente_run(self, run, tam, negrita, cursiva, color):
        f = run.font
        f.size, f.bold, f.italic, f.name = Pt(tam), negrita, cursiva, self.familia
        f.color.rgb = color
        rpr = run._r.get_or_add_rPr()
        for tag in ('a:ea', 'a:cs'):
            e = rpr.find(qn(tag))
            if e is None:
                e = etree.SubElement(rpr, qn(tag))
            e.set('typeface', self.familia)

    def _parrafos(self, tf, parrafos, alinear, color_def):
        al = {'izq': PP_ALIGN.LEFT, 'centro': PP_ALIGN.CENTER, 'der': PP_ALIGN.RIGHT, 'just': PP_ALIGN.JUSTIFY}
        for k, p in enumerate(parrafos):
            par = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            tam = p.get('tam', self.tam)
            par.alignment = al[p.get('alinear', alinear)]
            par.line_spacing = Pt(tam * INTERLINEADO)
            par.space_before = Pt(0)
            par.space_after = Pt(p.get('espacio_despues', 0.0) / PT_CM)
            if p.get('vineta'):
                pPr = par._p.get_or_add_pPr()
                sang = 0.35 * tam / 10.0
                pPr.set('marL', str(int(Cm(sang)))); pPr.set('indent', str(-int(Cm(sang))))
                bf = etree.SubElement(pPr, qn('a:buFont')); bf.set('typeface', 'Arial')
                bc = etree.SubElement(pPr, qn('a:buChar')); bc.set('char', '•')
            segmentos = p.get('runs') or [(p['texto'], p.get('negrita', False), p.get('cursiva', False))]
            for txt, neg, cur in segmentos:
                r = par.add_run(); r.text = txt
                self._fuente_run(r, tam, neg, cur, self._color(p.get('color') or color_def))

    def _dib_caja(self, slide, a):
        forma = {'redondeada': MSO_SHAPE.ROUNDED_RECTANGLE, 'pildora': MSO_SHAPE.ROUNDED_RECTANGLE, 'rect': MSO_SHAPE.RECTANGLE, 'elipse': MSO_SHAPE.OVAL,
                 'hexagono': MSO_SHAPE.HEXAGON, 'chevron': MSO_SHAPE.CHEVRON, 'pentagono': MSO_SHAPE.PENTAGON}[a['forma']]
        if a['relleno'] is None and a['borde'] is None and a['forma'] == 'rect':
            sh = slide.shapes.add_textbox(Cm(a['x']), Cm(a['y']), Cm(a['w']), Cm(a['h']))
        else:
            sh = slide.shapes.add_shape(forma, Cm(a['x']), Cm(a['y']), Cm(a['w']), Cm(a['h']))
            if a['forma'] == 'redondeada':
                sh.adjustments[0] = min(0.5, a['radio'] / max(0.01, min(a['w'], a['h'])))
            elif a['forma'] == 'pildora':
                sh.adjustments[0] = 0.5
            if a['relleno']:
                sh.fill.solid(); sh.fill.fore_color.rgb = self._color(a['relleno'])
            else:
                sh.fill.background()
            if a['borde']:
                sh.line.color.rgb = self._color(a['borde']); sh.line.width = Pt(a['grosor'] * self.kg)
            else:
                sh.line.fill.background()
            if not a.get('sombra'):
                sppr = sh._element.spPr
                etree.SubElement(sppr, qn('a:effectLst'))  # sin sombra del tema
                for er in sh._element.iter(qn('a:effectRef')):
                    er.set('idx', '0')
        if a.get('rotacion'):
            sh.rotation = a['rotacion']
        tf = sh.text_frame
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.NONE
        pad = Cm(a['pad'])
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = pad
        tf.vertical_anchor = {'arriba': MSO_ANCHOR.TOP, 'medio': MSO_ANCHOR.MIDDLE, 'abajo': MSO_ANCHOR.BOTTOM}[a['ancla']]
        if a['parrafos']:
            self._parrafos(tf, a['parrafos'], a['alinear'], a.get('color_texto') or 'texto')

    def _dib_flecha(self, slide, a):
        c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(a['x1']), Cm(a['y1']), Cm(a['x2']), Cm(a['y2']))
        c.line.color.rgb = self._color(a['color']); c.line.width = Pt(a['grosor'] * self.kg)
        for er in c._element.iter(qn('a:effectRef')):
            er.set('idx', '0')
        ln = c.line._get_or_add_ln()
        if a.get('discontinua'):
            d = etree.SubElement(ln, qn('a:prstDash')); d.set('val', 'dash')
        if a.get('punta'):
            t = etree.SubElement(ln, qn('a:tailEnd')); t.set('type', 'triangle'); t.set('w', 'med'); t.set('len', 'med')
        if a.get('doble'):
            h = etree.SubElement(ln, qn('a:headEnd')); h.set('type', 'triangle'); h.set('w', 'med'); h.set('len', 'med')

    def _dib_imagen(self, slide, a):
        slide.shapes.add_picture(a['ruta'], Cm(a['x']), Cm(a['y']), Cm(a['w']), Cm(a['h']))

    def _dib_grafico(self, slide, a):
        kw = a['kw']
        cd = CategoryChartData()
        cd.categories = a['categorias']
        for s in a['series']:
            cd.add_series(s['nombre'], s['valores'])
        tipo = {'barras': XL_CHART_TYPE.BAR_CLUSTERED, 'columnas': XL_CHART_TYPE.COLUMN_CLUSTERED,
                'lineas': XL_CHART_TYPE.LINE_MARKERS, 'circular': XL_CHART_TYPE.PIE,
                'barras_apiladas': XL_CHART_TYPE.BAR_STACKED, 'columnas_apiladas': XL_CHART_TYPE.COLUMN_STACKED}[a['tipo']]
        gf = slide.shapes.add_chart(tipo, Cm(a['x']), Cm(a['y']), Cm(a['w']), Cm(a['h']), cd)
        ch = gf.chart
        ch.has_title = bool(kw.get('titulo_grafico'))
        if kw.get('titulo_grafico'):
            ch.chart_title.text_frame.text = kw['titulo_grafico']
        ch.font.size = Pt(kw.get('tam', self.tam)); ch.font.name = self.familia
        ch.font.color.rgb = self._color('texto')
        ch.has_legend = len(a['series']) > 1 or a['tipo'] == 'circular'
        if ch.has_legend:
            ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False
        colores = kw.get('colores') or ['secundario', 'acento', 'positivo', 'neutro', 'primario', 'negativo']
        plot = ch.plots[0]
        if a['tipo'] != 'circular':
            plot.gap_width = kw.get('separacion', 60)
            if len(a['series']) > 1 and 'apiladas' not in a['tipo']:
                plot.overlap = -10
            va = ch.value_axis
            va.has_major_gridlines = kw.get('rejilla', False)
            va.format.line.fill.background() if not kw.get('eje_valor_linea') else None
            va.tick_labels.font.size = Pt(kw.get('tam', self.tam))
            ca = ch.category_axis
            ca.tick_labels.font.size = Pt(kw.get('tam', self.tam))
            ca.format.line.color.rgb = self._color('linea')
            if kw.get('titulo_eje_valor'):
                va.has_title = True
                va.axis_title.text_frame.text = kw['titulo_eje_valor']
                r = va.axis_title.text_frame.paragraphs[0].runs[0]
                self._fuente_run(r, kw.get('tam', self.tam), False, False, self._color('texto'))
            if kw.get('max') is not None:
                va.maximum_scale = kw['max']
            va.minimum_scale = kw.get('min', 0)
            if kw.get('invertir_categorias', a['tipo'].startswith('barras')):
                ca.reverse_order = True
                from pptx.enum.chart import XL_TICK_LABEL_POSITION
                va.tick_label_position = XL_TICK_LABEL_POSITION.LOW
            for k, s in enumerate(plot.series):
                s.format.fill.solid(); s.format.fill.fore_color.rgb = self._color(colores[k % len(colores)])
                s.invert_if_negative = False
        else:
            pts = plot.series[0].points
            for k in range(len(a['categorias'])):
                pts[k].format.fill.solid(); pts[k].format.fill.fore_color.rgb = self._color(colores[k % len(colores)])
        if kw.get('etiquetas', True):
            plot.has_data_labels = True
            dl = plot.data_labels
            dl.font.size = Pt(kw.get('tam', self.tam)); dl.font.name = self.familia
            if kw.get('formato_etiqueta'):
                dl.number_format = kw['formato_etiqueta']; dl.number_format_is_linked = False
            if a['tipo'] in ('barras', 'columnas'):
                dl.position = XL_LABEL_POSITION.OUTSIDE_END


# ------------------------------------------------------------------ exportación
def exportar(ruta_pptx, png=True, svg=True, pdf=False, dpi=300, ancho_cm=None, alto_cm=None):
    """Convierte la primera diapositiva a PNG (dpi exactos, metadatos incluidos) y SVG. Devuelve dict de rutas.
    Usa LibreOffice o PowerPoint para el PDF y PyMuPDF para PNG/SVG (ver render.py)."""
    from . import render
    base = os.path.splitext(ruta_pptx)[0]
    tmp = tempfile.mkdtemp(prefix='exp_')
    pdf_tmp = render.pptx_a_pdf(ruta_pptx, tmp)
    out = {'pptx': ruta_pptx}
    if png:
        from PIL import Image
        render.pdf_a_png(pdf_tmp, os.path.join(tmp, 'img.png'), 1, dpi)
        im = Image.open(os.path.join(tmp, 'img.png')).convert('RGB')
        if alto_cm and alto_cm < 2.54:
            im = im.crop((0, 0, im.size[0], min(im.size[1], round(alto_cm / 2.54 * dpi))))
        im.save(base + '.png', dpi=(dpi, dpi))
        out['png'] = base + '.png'
        out['ancho_png_cm'] = round(im.size[0] / dpi * 2.54, 2)
    if svg:
        render.pdf_a_svg(pdf_tmp, base + '.svg')
        out['svg'] = base + '.svg'
    if pdf:
        shutil.copy(pdf_tmp, base + '.pdf'); out['pdf'] = base + '.pdf'
    shutil.rmtree(tmp, ignore_errors=True)
    return out
