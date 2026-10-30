# -*- coding: utf-8 -*-
"""Generador de diapositivas completas sobre la plantilla institucional UNEMI (o sin plantilla).
Duplica la carátula, la diapositiva de contenido y el cierre de la plantilla (con su fondo, logo y franjas), dibuja el
contenido con el kit editable y elige el tamaño de letra de cada diapositiva según la cantidad de texto."""
import copy
import json
import math
import os

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from pptx.util import Cm, Emu, Pt

from .pptx_kit import Lienzo, PALETAS, alto_lineas, ancho_pt, PT_CM
from . import figuras

ICONOS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'assets', 'iconos')
ANCHO_REF = 67.733     # ancho de la plantilla UNEMI grande (cm); los tamaños validados se escalan desde aquí


def icono(nombre, color='blanco'):
    """Ruta del PNG del banco de íconos (colores: blanco, marino, naranja, gris). None si no existe."""
    if not nombre:
        return None
    r = os.path.join(ICONOS, 'png', color, f'{nombre}.png')
    return r if os.path.exists(r) else None


def lista_iconos():
    with open(os.path.join(ICONOS, 'iconos.json'), encoding='utf8') as f:
        return json.load(f)


def _p(texto, **kw):
    d = dict(texto=texto); d.update(kw); return d


# ------------------------------------------------------------------ manejo de la plantilla
_REL_ATTRS = [qn('r:embed'), qn('r:link'), qn('r:id')]


def duplicar(prs, origen):
    """Copia una diapositiva (fondo, formas, imágenes) al final de la presentación."""
    nueva = prs.slides.add_slide(origen.slide_layout)
    for sh in list(nueva.shapes):
        sh._element.getparent().remove(sh._element)
    mapa = {}
    for rid, rel in origen.part.rels.items():
        if rel.reltype.endswith('/image') or rel.reltype.endswith('/media') or rel.reltype.endswith('/video'):
            mapa[rid] = nueva.part.relate_to(rel._target, rel.reltype)
        elif rel.reltype.endswith('/hyperlink'):
            mapa[rid] = nueva.part.relate_to(rel.target_ref, rel.reltype, is_external=True)

    def remapear(el):
        for e in el.iter():
            for at in _REL_ATTRS:
                if e.get(at) in mapa:
                    e.set(at, mapa[e.get(at)])
        return el
    bg = origen._element.cSld.find(qn('p:bg'))
    if bg is not None:
        nueva._element.cSld.insert(0, remapear(copy.deepcopy(bg)))
    arbol = nueva.shapes._spTree
    for el in origen.shapes._spTree:
        if etree.QName(el).localname in ('sp', 'pic', 'grpSp', 'graphicFrame', 'cxnSp'):
            arbol.append(remapear(copy.deepcopy(el)))
    return nueva


def eliminar(prs, indices):
    lst = prs.slides._sldIdLst
    ids = list(lst)
    for i in sorted(indices, reverse=True):
        rid = ids[i].get(qn('r:id'))
        prs.part.drop_rel(rid)
        lst.remove(ids[i])


def poner_texto(shape, texto, ajustar=True):
    """Reemplaza el texto de una forma conservando el formato de su primer run (admite varias líneas). Con ajustar,
    reduce el tamaño (hasta el 60 %) si el texto nuevo ocupa más líneas que el de ejemplo, para no invadir la forma
    siguiente de la plantilla."""
    tf = shape.text_frame
    lineas_antes = max(1, len(tf.text.split('\n')))
    p0 = tf.paragraphs[0]
    r0 = p0.runs[0] if p0.runs else p0.add_run()
    for r in p0.runs[1:]:
        r._r.getparent().remove(r._r)
    for p in tf.paragraphs[1:]:
        p._p.getparent().remove(p._p)
    lineas = str(texto).split('\n')
    r0.text = lineas[0]
    ultimo = p0._p
    for ln in lineas[1:]:
        np_ = copy.deepcopy(p0._p)
        ultimo.addnext(np_); ultimo = np_
        rs = np_.findall(qn('a:r'))
        rs[0].find(qn('a:t')).text = ln
    sz = r0.font.size.pt if r0.font.size else None
    if sz is None:
        cand = shape._element.xpath('.//a:rPr/@sz | .//a:endParaRPr/@sz | .//a:defRPr/@sz')
        sz = int(cand[0]) / 100 if cand else None
    if ajustar and sz:
        tam = sz
        ancho = (Emu(shape.width).cm - 0.5) * 0.95 / PT_CM
        from .pptx_kit import envolver
        def n_lineas(t):
            return sum(len(envolver(x, ancho, t, bool(r0.font.bold))) for x in lineas)
        t = tam
        while n_lineas(t) > max(lineas_antes, len(lineas)) and t > tam * 0.6:
            t -= 1
        if t != tam:
            for r in tf._txBody.iter(qn('a:rPr')):
                r.set('sz', str(int(t * 100)))


# ------------------------------------------------------------------ generador
class Generador:
    def __init__(self, c):
        self.c = c
        self.plantilla = c.get('plantilla')
        if self.plantilla:
            self.prs = Presentation(self.plantilla)
            self.base = list(self.prs.slides)
        else:
            self.prs = Presentation()
            self.prs.slide_width, self.prs.slide_height = Cm(33.867), Cm(19.05)
            self.base = []
        self.W = Emu(self.prs.slide_width).cm
        self.H = Emu(self.prs.slide_height).cm
        self.f = self.W / ANCHO_REF
        e = self.f
        self.x0, self.x1 = 4.23 * e, 63.5 * e
        self.bw = self.x1 - self.x0
        self.y_tit, self.y_sub = 2.33 * e, 7.04 * e
        self.y_fin = 35.2 * e if self.plantilla else self.H - 1.2 * e
        self.escala = c.get('escala_texto', 1.0)
        self.avisos = []
        self.n_base = len(self.base)

    # -------------------------------------------------- diapositivas base
    def _nueva(self, cual):
        if self.plantilla:
            idx = {'portada': 0, 'contenido': 1, 'cierre': min(2, self.n_base - 1)}[cual]
            s = duplicar(self.prs, self.base[idx])
            if cual == 'contenido':
                for sh in list(s.shapes):   # quitar TITULO / Subtítulo de ejemplo: se dibujan con medidas exactas
                    if sh.has_text_frame and sh.text_frame.text.strip() in ('TITULO', 'Subtítulo', 'TÍTULO'):
                        sh._element.getparent().remove(sh._element)
            return s
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        pal = PALETAS['unemi']
        fondo = s.background.fill
        fondo.solid()
        fondo.fore_color.rgb = RGBColor.from_string(pal['primario'] if cual in ('portada', 'cierre') else 'FFFFFF')
        return s

    def portada(self, d):
        s = self._nueva('portada')
        if self.plantilla:
            reemplazos = {'nombre de la asignatura': d.get('asignatura') or d.get('titulo'),
                          'tecnologías de la información': d.get('carrera'), 'estudiante:': d.get('etiqueta_autores'),
                          'nombres': d.get('autores'), 'tema': d.get('etiqueta_tema'), 'nombre del tema': d.get('tema'),
                          'nombre del docente': d.get('docente'), 'cargo y dedicación del docente': d.get('cargo')}
            for sh in s.shapes:
                if not sh.has_text_frame:
                    continue
                t = ' '.join(sh.text_frame.text.lower().split())
                for k, v in reemplazos.items():
                    if v is not None and (t == k or t.startswith(k)):
                        poner_texto(sh, v)
                        break
            restos = [sh.text_frame.text for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.strip().lower() in
                      ('nombres', 'nombre del tema', 'nombre del docente', 'cargo y dedicación del docente')]
            if restos:
                self.avisos.append(f'Portada: quedan textos de ejemplo sin reemplazar: {restos}')
        else:
            L = Lienzo(self.W, self.H, paleta='unemi', tam=28 * self.f)
            L.texto(3 * self.f, self.H * 0.28, self.W - 6 * self.f,
                    [_p(d.get('titulo') or d.get('tema', ''), tam=64 * self.f, negrita=True, color='blanco', alinear='centro', espacio_despues=0.8 * self.f),
                     _p(d.get('autores', ''), tam=36 * self.f, negrita=True, color='F6A765', alinear='centro', espacio_despues=0.5 * self.f),
                     _p(d.get('tema', ''), tam=30 * self.f, color='DCE7F2', alinear='centro'),
                     _p(d.get('docente', ''), tam=28 * self.f, color='DCE7F2', alinear='centro')])
            L.construir(self.prs, s)
        self._notas(s, d)
        return s

    def cierre(self, d=None):
        s = self._nueva('cierre')
        if not self.plantilla:
            L = Lienzo(self.W, self.H, paleta='unemi', tam=40 * self.f)
            L.texto(0, self.H * 0.42, self.W, [_p((d or {}).get('texto', 'Gracias'), tam=60 * self.f, negrita=True,
                                                  color='blanco', alinear='centro')])
            L.construir(self.prs, s)
        self._notas(s, d or {})
        return s

    def _notas(self, s, d):
        if d.get('notas'):
            s.notes_slide.notes_text_frame.text = d['notas']

    # -------------------------------------------------- contenido
    def contenido(self, d):
        s = self._nueva('contenido')
        e = self.f
        cab = Lienzo(self.W, self.H, paleta='unemi', tam=24 * e)
        cab.texto(self.x0, self.y_tit, self.bw, [_p(d['titulo'], tam=46 * e, negrita=True, color='acento')])
        y_ini = self.y_tit + alto_lineas(len(cab.lineas(d['titulo'], self.bw, 46 * e, True)), 46 * e) + 0.9 * e
        if d.get('subtitulo'):
            y_sub = max(self.y_sub, y_ini - 0.5 * e)
            cab.texto(self.x0, y_sub, self.bw, [_p(d['subtitulo'], tam=32 * e, negrita=True, color='primario')])
            y_ini = y_sub + alto_lineas(len(cab.lineas(d['subtitulo'], self.bw, 32 * e, True)), 32 * e) + 1.2 * e
        cab.construir(self.prs, s)
        disp = self.y_fin - y_ini
        tipo = d['tipo']
        rango = d.get('rango', RANGOS.get(tipo, (18, 28)))
        mejor = None
        for t in range(int(rango[1] * e * self.escala), int(rango[0] * e * self.escala) - 1, -1):
            L = Lienzo(self.W, self.H, paleta='unemi', tam=t)
            alto = getattr(self, '_' + tipo)(L, d, self.x0, 0, t)
            if alto <= disp:
                mejor = (L, alto, t)
                break
        if mejor is None:
            t = int(rango[0] * e * self.escala)
            L = Lienzo(self.W, self.H, paleta='unemi', tam=t)
            alto = getattr(self, '_' + tipo)(L, d, self.x0, 0, t)
            mejor = (L, alto, t)
            self.avisos.append(f'"{d["titulo"]}": el contenido no cabe ni con {t} pt: dividir la diapositiva o recortar texto.')
        L, alto, t = mejor
        libre = max(0, disp - alto)
        centrar = d.get('alinear') == 'centro' or (d.get('alinear') is None and libre > 0.3 * disp)
        dy = y_ini + (libre / 2 if centrar else min(libre / 3, 2.5 * e))
        final = Lienzo(self.W, self.H, paleta='unemi', tam=t)
        final.pegar(L, 0, dy)
        for op, a in final.ops:
            if op == 'tabla':
                pass
        final.construir(self.prs, s)
        for fn in getattr(L, '_post', []):
            fn(s, dy)
        self._notas(s, d)
        return s, t

    # ---- tipos (cada uno dibuja en L desde y0 y devuelve el alto usado)
    def _texto(self, L, d, x, y0, t):
        e = self.f
        w = self.bw
        img = d.get('imagen')
        dest = d.get('destacado')
        if img or dest:
            w = self.bw * (0.5 if img else 0.58)
        pars = []
        for linea in d.get('parrafos', []):
            if linea.startswith('- '):
                pars.append(_p(linea[2:], vineta=True, espacio_despues=0.25 * t / 24))
            else:
                pars.append(_p(linea, espacio_despues=0.45 * t / 24))
        h = L.texto(x, y0, w, pars)
        xr, wr = x + w + 1.2 * e, self.bw - w - 1.2 * e
        if img:
            from PIL import Image
            iw, ih = Image.open(img).size
            hi = min(wr * ih / iw, 26 * e)
            wi = hi * iw / ih
            L.imagen(xr + (wr - wi) / 2, y0, wi, img, h=hi)
            h = max(h, hi)
        elif dest:
            pd = [_p(dest.get('titulo', ''), negrita=True, color='F6A765', tam=t * 1.1, espacio_despues=0.3 * e)] if dest.get('titulo') else []
            pd.append(_p(dest['texto'], color='blanco', tam=t))
            hd = L.alto_parrafos(pd, wr, 0.9 * e)
            L.caja(xr, y0, wr, hd, pd, relleno='primario', radio=0.5 * e, pad=0.9 * e, ancla='medio')
            if dest.get('icono') and icono(dest['icono'], 'naranja'):
                pass
            h = max(h, hd)
        return h

    def _agenda(self, L, d, x, y0, t):
        e = self.f
        items = d['items']
        cols = 2 if len(items) > 3 else 1
        g = 1.0 * e
        cw = (self.bw - (cols - 1) * g) / cols
        chip = alto_lineas(1, t) + 0.9 * e
        filas = math.ceil(len(items) / cols)
        hs = []
        for i, it in enumerate(items):
            hs.append(max(chip, L.alto_parrafos([_p(it, negrita=True, color='primario')], cw - chip - 1.4 * e, 0.3 * e)))
        y = y0
        for fila in range(filas):
            h = max(hs[fila * cols:(fila + 1) * cols])
            for c in range(cols):
                i = fila * cols + c
                if i >= len(items):
                    break
                xx = x + c * (cw + g)
                L.caja(xx, y, cw, h + 0.4 * e, relleno='sec_claro', radio=0.4 * e)
                L.caja(xx + 0.4 * e, y + (h + 0.4 * e - chip) / 2, chip * 1.25, chip,
                       [_p(f'{i + 1:02d}', negrita=True, color='blanco', tam=t)], relleno='acento', radio=0.3 * e,
                       alinear='centro', pad=0)
                L.caja(xx + chip * 1.25 + 0.9 * e, y, cw - chip * 1.25 - 1.2 * e, h + 0.4 * e,
                       [_p(items[i], negrita=True, color='primario')], forma='rect', pad=0.2 * e)
            y += h + 0.4 * e + 0.6 * e
        return y - y0 - 0.6 * e

    def _tarjetas(self, L, d, x, y0, t):
        e = self.f
        items = d['items']
        n = len(items)
        cols = {1: 1, 2: 2, 3: 3, 4: 2, 5: 3, 6: 3}.get(n, 3)
        g = 1.0 * e
        cw = (self.bw - (cols - 1) * g) / cols
        dc = 2.6 * e * max(0.8, t / (24 * e))
        pad = 0.7 * e
        pars = [[_p(it['titulo'], negrita=True, color='acento', tam=t * 1.1, alinear='centro', espacio_despues=0.25 * e)] +
                ([_p(it['texto'], alinear='centro')] if it.get('texto') else []) for it in items]
        hs = [L.alto_parrafos(p, cw, pad) + (dc + 0.5 * e if items[k].get('icono') else 0) for k, p in enumerate(pars)]
        y = y0
        for fila in range(math.ceil(n / cols)):
            h = max(hs[fila * cols:(fila + 1) * cols])
            en_fila = items[fila * cols:(fila + 1) * cols]
            xoff = x + (self.bw - (len(en_fila) * cw + (len(en_fila) - 1) * g)) / 2
            for c, it in enumerate(en_fila):
                k = fila * cols + c
                xx = xoff + c * (cw + g)
                L.caja(xx, y, cw, h, relleno='sec_claro', radio=0.45 * e)
                yy = y + pad
                ic = icono(it.get('icono'), 'blanco')
                if it.get('icono'):
                    L.elipse(xx + cw / 2 - dc / 2, yy, dc, dc, relleno='primario')
                    if ic:
                        L.imagen(xx + cw / 2 - dc * 0.3, yy + dc * 0.2, dc * 0.6, ic, h=dc * 0.6)
                    else:
                        self.avisos.append(f'Ícono no encontrado: {it.get("icono")}')
                    yy += dc + 0.5 * e
                L.caja(xx, yy - pad, cw, h - (yy - y) + pad, pars[k], forma='rect', ancla='arriba', pad=pad)
            y += h + g
        return y - y0 - g

    def _cifras(self, L, d, x, y0, t):
        e = self.f
        items = d['items']
        n = len(items)
        g = 1.0 * e
        cw = (self.bw - (n - 1) * g) / n
        tv = t * 2.2
        pars = [[_p(it['valor'], negrita=True, color='acento', tam=tv, alinear='centro', espacio_despues=0.2 * e),
                 _p(it['etiqueta'], alinear='centro')] for it in items]
        h = max(L.alto_parrafos(p, cw, 0.8 * e) for p in pars)
        for i, p in enumerate(pars):
            L.caja(x + i * (cw + g), y0, cw, h, p, relleno='sec_claro', radio=0.45 * e, pad=0.8 * e)
        y = y0 + h
        if d.get('texto'):
            y += 1.0 * e
            y += L.texto(x, y, self.bw, [_p(d['texto'])])
        return y - y0

    def _diagrama(self, L, d, x, y0, t):
        spec = dict(d['spec'])
        spec.update(ancho_cm=spec.get('ancho_cm', self.bw), tam=t, paleta='unemi')
        sub = figuras.TIPOS[spec['tipo']](spec)
        xo = x + (self.bw - spec['ancho_cm']) / 2
        L.pegar(sub, xo, y0)
        return sub.alto_final()

    def _imagen(self, L, d, x, y0, t):
        from PIL import Image
        e = self.f
        iw, ih = Image.open(d['ruta']).size
        disp_h = (self.y_fin - self.y_sub - 3 * e) * (t / (RANGOS['imagen'][1] * e * self.escala))
        hi = min(disp_h, self.bw * ih / iw)
        wi = hi * iw / ih
        L.imagen(x + (self.bw - wi) / 2, y0, wi, d['ruta'], h=hi)
        h = hi
        if d.get('pie'):
            h += 0.4 * e + L.texto(x, y0 + hi + 0.4 * e, self.bw, [_p(d['pie'], cursiva=True, color='neutro',
                                                                     tam=t * 0.8, alinear='centro')])
        return h

    def _comparativa(self, L, d, x, y0, t):
        e = self.f
        g = 1.2 * e
        cw = (self.bw - g) / 2
        pad = 0.8 * e
        lados = [(d['izquierda'], 'positivo', 'positivo_claro', 'correcto'), (d['derecha'], 'negativo', 'negativo_claro', 'error')]
        pars = [[_p(lado['titulo'], negrita=True, color=f, tam=t * 1.15, espacio_despues=0.35 * e)] +
                [_p(it, vineta=True, espacio_despues=0.2 * e) for it in lado['items']] for lado, f, c, i in lados]
        di = alto_lineas(1, t * 1.15)
        h = max(L.alto_parrafos(p, cw - (di + 0.4 * e) * 0, pad) for p in pars)
        for k, ((lado, f, c, ic), p) in enumerate(zip(lados, pars)):
            xx = x + k * (cw + g)
            L.caja(xx, y0, cw, h, relleno=c, borde=f, grosor=1.5, radio=0.45 * e)
            ruta = icono(lado.get('icono', ic), 'marino')
            p = [dict(p[0], texto=p[0]['texto'])] + p[1:]
            if ruta:
                L.imagen(xx + pad, y0 + pad + 0.05 * e, di, ruta, h=di)
                p[0] = dict(p[0], texto='      ' + p[0]['texto'])
            L.caja(xx, y0, cw, h, p, forma='rect', ancla='arriba', pad=pad)
        return h

    def _conclusiones(self, L, d, x, y0, t):
        e = self.f
        dc = alto_lineas(1, t * 1.1) + 0.8 * e
        y = y0
        for i, it in enumerate(d['items']):
            titulo, texto = (it.get('titulo'), it.get('texto')) if isinstance(it, dict) else (None, it)
            pars = ([_p(titulo, negrita=True, color='primario', tam=t * 1.1, espacio_despues=0.15 * e)] if titulo else []) + \
                   [_p(texto)]
            h = max(dc + 0.6 * e, L.alto_parrafos(pars, self.bw - dc - 1.6 * e, 0.3 * e))
            L.caja(x, y, self.bw, h, relleno='neutro_claro', radio=0.4 * e)
            L.elipse(x + 0.5 * e, y + (h - dc) / 2, dc, dc, relleno='acento',
                     parrafos=[_p(str(i + 1), negrita=True, color='blanco', tam=t)])
            L.caja(x + dc + 1.0 * e, y, self.bw - dc - 1.3 * e, h, pars, forma='rect', pad=0.3 * e)
            y += h + 0.5 * e
        return y - y0 - 0.5 * e

    def _referencias(self, L, d, x, y0, t):
        e = self.f
        y = y0
        for r in d['items']:
            h = L.alto_parrafos([_p(r)], self.bw - 1.4 * e, 0.35 * e)
            L.caja(x, y, self.bw, h, relleno='neutro_claro', radio=0.3 * e)
            L.caja(x, y + 0.25 * e, 0.18 * e, h - 0.5 * e, relleno='acento', radio=0.05 * e, forma='rect')
            L.caja(x + 0.9 * e, y, self.bw - 1.2 * e, h, [_p(r)], forma='rect', pad=0.35 * e)
            y += h + 0.4 * e
        return y - y0 - 0.4 * e

    def _cita(self, L, d, x, y0, t):
        e = self.f
        di = 3.0 * e
        ruta = icono('cita', 'naranja')
        y = y0
        if ruta:
            L.imagen(x + self.bw / 2 - di / 2, y, di, ruta, h=di)
            y += di + 0.8 * e
        pars = [_p(d['texto'], cursiva=True, color='primario', alinear='centro', tam=t, espacio_despues=0.6 * e)]
        if d.get('autor'):
            pars.append(_p(d['autor'], negrita=True, color='acento', alinear='centro', tam=t * 0.75))
        y += L.texto(x + self.bw * 0.1, y, self.bw * 0.8, pars)
        return y - y0

    def _tabla(self, L, d, x, y0, t):
        """Tabla nativa (editable). Se mide aquí y se dibuja después de construir el lienzo."""
        e = self.f
        enc, filas = d['encabezados'], d['filas']
        anchos = d.get('anchos')
        tot = sum(anchos) if anchos else len(enc)
        ws = [self.bw * (a / tot) for a in anchos] if anchos else [self.bw / len(enc)] * len(enc)
        pad = 0.25 * e
        altos = []
        for k, fila in enumerate([enc] + filas):
            altos.append(max(alto_lineas(len(L.lineas(str(v), w - 2 * pad - 0.2 * e, t, k == 0)), t) + 2 * pad
                             for v, w in zip(fila, ws)))
        total = sum(altos)

        def dibujar(slide, dy, t=t, ws=ws, altos=altos):
            gf = slide.shapes.add_table(len(filas) + 1, len(enc), Cm(x), Cm(y0 + dy), Cm(self.bw), Cm(total))
            tb = gf.table
            pal = PALETAS['unemi']
            for j, w in enumerate(ws):
                tb.columns[j].width = Cm(w)
            for i, fila in enumerate([enc] + filas):
                tb.rows[i].height = Cm(altos[i])
                for j, v in enumerate(fila):
                    c = tb.cell(i, j)
                    c.margin_left = c.margin_right = c.margin_top = c.margin_bottom = Cm(pad)
                    c.fill.solid()
                    c.fill.fore_color.rgb = RGBColor.from_string(pal['primario'] if i == 0 else
                                                                 (pal['sec_claro'] if i % 2 else 'FFFFFF'))
                    tf = c.text_frame; tf.word_wrap = True
                    tf.paragraphs[0].text = ''
                    r = tf.paragraphs[0].add_run(); r.text = str(v)
                    r.font.size = Pt(t); r.font.name = 'Arial'
                    r.font.bold = i == 0 or (j == 0 and d.get('primera_columna_negrita', True))
                    r.font.color.rgb = RGBColor.from_string('FFFFFF' if i == 0 else pal['texto'])
        L._post = getattr(L, '_post', []) + [dibujar]
        return total

    # -------------------------------------------------- todo el archivo
    def construir(self, salida):
        c = self.c
        tamanos = []
        if c.get('portada'):
            self.portada(c['portada'])
        for d in c.get('diapositivas', []):
            if d['tipo'] == 'cierre':
                self.cierre(d)
            else:
                _, t = self.contenido(d)
                tamanos.append((d['titulo'], round(t / self.f)))
        if c.get('cierre', True) and not any(d['tipo'] == 'cierre' for d in c.get('diapositivas', [])):
            self.cierre(c.get('cierre') if isinstance(c.get('cierre'), dict) else {})
        if self.n_base:
            eliminar(self.prs, range(self.n_base))
        self.prs.save(salida)
        return dict(archivo=salida, diapositivas=len(self.prs.slides), tamanos_cuerpo_equivalentes=tamanos,
                    avisos=self.avisos)


# rango de tamaño de cuerpo (pt) por tipo, en la escala de la plantilla UNEMI grande (reglas validadas)
RANGOS = {'texto': (18, 48), 'agenda': (20, 44), 'tarjetas': (18, 40), 'cifras': (18, 40), 'diagrama': (16, 40),
          'imagen': (18, 24), 'comparativa': (18, 44), 'conclusiones': (18, 40), 'referencias': (16, 28),
          'cita': (28, 60), 'tabla': (16, 36)}


def generar(contenido, salida):
    if isinstance(contenido, str):
        base = os.path.dirname(os.path.abspath(contenido))
        with open(contenido, encoding='utf8') as f:
            contenido = json.load(f)
        if contenido.get('plantilla') and not os.path.isabs(contenido['plantilla']):
            contenido['plantilla'] = os.path.join(base, contenido['plantilla'])
        for d in contenido.get('diapositivas', []):      # rutas de imágenes relativas al JSON
            for k in ('imagen', 'ruta'):
                if isinstance(d.get(k), str) and not os.path.isabs(d[k]):
                    d[k] = os.path.join(base, d[k])
    return Generador(contenido).construir(salida)
