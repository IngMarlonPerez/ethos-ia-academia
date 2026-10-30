# -*- coding: utf-8 -*-
"""Póster académico editable (PPTX) de 3 columnas a partir de un JSON de contenido.
El tamaño de letra del cuerpo se elige solo: el mayor que permite que las tres columnas y las referencias quepan
(regla de tamaño adaptativo); luego se reparte el espacio sobrante para que las columnas terminen alineadas."""
import json
import os

from .pptx_kit import Lienzo, PAR_COLORES, alto_lineas, ancho_pt, PT_CM, exportar

TAMANOS = {'A0': (84.1, 118.9), 'A1': (59.4, 84.1), '90x120': (90.0, 120.0), '60x90': (60.0, 90.0)}


def _p(texto, **kw):
    d = dict(texto=texto); d.update(kw); return d


class Poster:
    def __init__(self, c):
        self.c = c
        w, h = TAMANOS.get(c.get('tamano', 'A0'), (84.1, 118.9)) if isinstance(c.get('tamano', 'A0'), str) else c['tamano']
        if c.get('orientacion') == 'horizontal':
            w, h = h, w
        self.W, self.H = w, h
        self.esc = w / 84.1                      # escala respecto de A0 vertical
        self.M = 2.0 * self.esc                  # margen
        self.gap = 1.4 * self.esc
        self.ncol = len(c['columnas'])
        self.CW = (w - 2 * self.M - (self.ncol - 1) * self.gap) / self.ncol

    # ---------------------------------------------------------------- medidas por bloque
    def tams(self, t):
        return dict(cuerpo=t, seccion=round(t * 1.45), tarjeta=round(t * 1.1), cifra=round(t * 2.1),
                    pie=max(round(t * 0.82), 16), ref=max(round(t * 0.7), 16))

    def alto_bloque(self, L, b, T):
        CW, e = self.CW, self.esc
        tipo = b['tipo']
        if tipo == 'seccion':
            return alto_lineas(len(L.lineas(b['titulo'], CW - 3.2 * e, T['seccion'], True)), T['seccion']) + 0.9 * e
        if tipo == 'parrafo':
            return L.alto_parrafos([_p(b['texto'], tam=T['cuerpo'])], CW, 0)
        if tipo == 'lista':
            return L.alto_parrafos([_p(x, tam=T['cuerpo'], vineta=True, espacio_despues=0.2 * e) for x in b['items']], CW, 0)
        if tipo == 'numerados':
            d = alto_lineas(1, T['cuerpo']) * 1.25
            return sum(max(d, L.alto_parrafos([_p(x, tam=T['cuerpo'])], CW - d - 0.5 * e, 0)) for x in b['items']) + \
                0.35 * e * (len(b['items']) - 1)
        if tipo == 'cifras':
            tot = 0
            for it in b['items']:
                wv = self._ancho_cifras(b, T)
                h_lab = L.alto_parrafos([_p(it['etiqueta'], tam=T['cuerpo'] * 0.9)], CW - wv - 0.9 * e, 0)
                tot += max(alto_lineas(1, T['cifra']), h_lab) + 0.8 * e
            return tot + 0.3 * e * (len(b['items']) - 1)
        if tipo in ('tarjeta', 'destacado'):
            pad = 0.6 * e
            pars = self._pars_tarjeta(b, T)
            return L.alto_parrafos(pars, CW, pad)
        if tipo == 'figura':
            from PIL import Image
            iw, ih = Image.open(b['ruta']).size
            w = CW * b.get('escala', 1.0)
            h = w * ih / iw
            if b.get('pie'):
                h += 0.3 * e + L.alto_parrafos([_p(b['pie'], tam=T['pie'])], CW, 0)
            return h
        if tipo == 'grafico':
            return b.get('alto_cm', CW * 0.62)
        if tipo == 'diagrama':
            return self._diagrama(b, T).alto_final()
        raise ValueError(f'Bloque desconocido: {tipo}')

    def _ancho_cifras(self, b, T):
        return max(ancho_pt(it['valor'], T['cifra'], True) for it in b['items']) * PT_CM + 0.8 * self.esc

    def _pars_tarjeta(self, b, T):
        destacado = b['tipo'] == 'destacado'
        fuerte = 'blanco' if destacado else PAR_COLORES.get(b.get('color', 'azul'), ('secundario',))[0]
        pars = []
        if b.get('titulo'):
            pars.append(_p(b['titulo'], negrita=True, tam=T['tarjeta'], color='F6A765' if destacado else fuerte,
                           espacio_despues=0.15 * self.esc))
        if b.get('texto'):
            pars.append(_p(b['texto'], tam=T['cuerpo'], color='blanco' if destacado else None,
                           espacio_despues=0.15 * self.esc if b.get('items') else 0))
        for x in b.get('items', []):
            pars.append(_p(x, tam=T['cuerpo'], vineta=True, color='blanco' if destacado else None,
                           espacio_despues=0.12 * self.esc))
        return pars

    def _diagrama(self, b, T):
        from . import figuras
        spec = dict(b['spec']); spec.update(ancho_cm=self.CW, tam=T['cuerpo'], paleta=self.c.get('paleta', 'unemi'))
        return figuras.TIPOS[spec['tipo']](spec)

    # ---------------------------------------------------------------- encabezado y referencias
    def alto_encabezado(self, L):
        e, c = self.esc, self.c['encabezado']
        tw = self.W - 2 * self.M - 1.6 * e
        self.t_titulo = 84 * e
        while len(L.lineas(c['titulo'], tw, self.t_titulo, True)) > 3 and self.t_titulo > 54 * e:
            self.t_titulo -= 2
        h = 0.9 * e + 3.0 * e + 0.6 * e
        h += alto_lineas(len(L.lineas(c['titulo'], tw, self.t_titulo, True)), self.t_titulo) + 0.5 * e
        if c.get('autores'):
            h += alto_lineas(len(L.lineas(c['autores'], tw, 40 * e, True)), 40 * e) + 0.2 * e
        if c.get('tutor'):
            h += alto_lineas(1, 32 * e) + 0.2 * e
        return h + 0.7 * e

    def alto_referencias(self, L, T):
        refs = self.c.get('referencias', [])
        if not refs:
            return 0
        rw = (self.W - 2 * self.M - 1.6 * self.esc - 1.0 * self.esc) / 2
        mitad = (len(refs) + 1) // 2
        hs = [L.alto_parrafos([_p(r, tam=T['ref'], espacio_despues=0.15 * self.esc) for r in grupo], rw, 0)
              for grupo in (refs[:mitad], refs[mitad:])]
        return max(hs) + alto_lineas(1, T['tarjeta']) + 1.4 * self.esc

    # ---------------------------------------------------------------- resolver tamaño
    def resolver(self):
        L = Lienzo(self.W, self.H, paleta=self.c.get('paleta', 'unemi'))
        he = self.alto_encabezado(L)
        rango = self.c.get('rango_cuerpo', [22, 40])
        for t in range(int(rango[1] * self.esc), int(rango[0] * self.esc) - 1, -1):
            T = self.tams(t)
            hr = self.alto_referencias(L, T)
            disp = self.H - 2 * self.M - he - self.gap - (hr + self.gap if hr else 0)
            alturas = []
            for col in self.c['columnas']:
                hs = [self.alto_bloque(L, b, T) for b in col]
                alturas.append((hs, sum(hs) + self._espacios(col)))
            if all(tot <= disp for _, tot in alturas):
                return t, T, he, hr, disp, alturas
        raise ValueError('El contenido no cabe ni con el tamaño mínimo de letra: recortar texto (no reducir más la letra).')

    def _espacios(self, col):
        return sum((0.45 if b['tipo'] == 'seccion' else 0.75) * self.esc for b in col[:-1])

    # ---------------------------------------------------------------- dibujar
    def construir(self, salida_base, logo=None, png_preview=True):
        t, T, he, hr, disp, alturas = self.resolver()
        L = Lienzo(self.W, self.H, paleta=self.c.get('paleta', 'unemi'))
        e, M = self.esc, self.M
        c = self.c['encabezado']
        # encabezado
        L.caja(M, M, self.W - 2 * M, he, relleno='primario', radio=0.5 * e)
        y = M + 0.9 * e
        logo = logo or self.c.get('logo')
        if logo and os.path.exists(logo):
            L.imagen(M + 0.8 * e, y, 9.0 * e, logo, h=3.0 * e)
        if c.get('institucion'):
            L.texto(M + 10.5 * e, y + 0.2 * e, self.W - 2 * M - 11.3 * e,
                    [_p(x, tam=30 * e, color='DCE7F2', alinear='der') for x in c['institucion'].split('\n')])
        y += 3.0 * e + 0.6 * e
        tw = self.W - 2 * M - 1.6 * e
        L.texto(M + 0.8 * e, y, tw, [_p(c['titulo'], tam=self.t_titulo, negrita=True, color='blanco')])
        y += alto_lineas(len(L.lineas(c['titulo'], tw, self.t_titulo, True)), self.t_titulo) + 0.5 * e
        if c.get('autores'):
            L.texto(M + 0.8 * e, y, tw, [_p(c['autores'], tam=40 * e, negrita=True, color='F6A765')])
            y += alto_lineas(len(L.lineas(c['autores'], tw, 40 * e, True)), 40 * e) + 0.2 * e
        if c.get('tutor'):
            L.texto(M + 0.8 * e, y, tw, [_p(c['tutor'], tam=32 * e, color='DCE7F2')])
        # columnas
        top = M + he + self.gap
        n_sec = 0
        for k, col in enumerate(self.c['columnas']):
            x = M + k * (self.CW + self.gap)
            hs, tot = alturas[k]
            huecos = max(1, len(col) - 1)
            extra = min((disp - tot) / huecos, 2.5 * e) if self.c.get('justificar', True) else 0
            yy = top
            for b, h in zip(col, hs):
                n_sec = self._dibujar_bloque(L, b, T, x, yy, h, n_sec)
                yy += h + (0.45 if b['tipo'] == 'seccion' else 0.75) * e + (extra if b['tipo'] != 'seccion' else 0)
        # referencias
        if hr:
            yr = self.H - M - hr
            L.caja(M, yr, self.W - 2 * M, hr, relleno='neutro_claro', radio=0.4 * e)
            L.texto(M + 0.8 * e, yr + 0.6 * e, 20 * e, [_p('Referencias', tam=T['tarjeta'], negrita=True, color='primario')])
            refs = self.c['referencias']
            mitad = (len(refs) + 1) // 2
            rw = (self.W - 2 * M - 1.6 * e - 1.0 * e) / 2
            for j, grupo in enumerate((refs[:mitad], refs[mitad:])):
                L.texto(M + 0.8 * e + j * (rw + 1.0 * e), yr + 0.6 * e + alto_lineas(1, T['tarjeta']) + 0.3 * e, rw,
                        [_p(r, tam=T['ref'], espacio_despues=0.15 * e) for r in grupo])
        L.guardar(salida_base + '.pptx')
        out = exportar(salida_base + '.pptx', png=False, svg=False, pdf=True)
        if png_preview:
            from . import render
            out['vista'] = render.pdf_a_png(out['pdf'], salida_base + '_vista.png', 1, 20)
        out['tam_cuerpo'] = t
        return out

    def _dibujar_bloque(self, L, b, T, x, y, h, n_sec):
        e, CW = self.esc, self.CW
        tipo = b['tipo']
        if tipo == 'seccion':
            n_sec += 1
            L.caja(x, y, CW, h, relleno='primario', radio=0.3 * e)
            d = min(h - 0.5 * e, 2.1 * e)
            L.caja(x + 0.35 * e, y + (h - d) / 2, d, d, [_p(str(b.get('numero', n_sec)), tam=T['seccion'] * 0.8,
                                                            negrita=True, color='blanco')],
                   relleno='acento', forma='elipse', alinear='centro', pad=0)
            L.caja(x + 0.35 * e + d + 0.5 * e, y, CW - d - 1.2 * e, h,
                   [_p(b['titulo'], tam=T['seccion'], negrita=True, color='blanco')], forma='rect', pad=0.05 * e)
        elif tipo == 'parrafo':
            L.texto(x, y, CW, [_p(b['texto'], tam=T['cuerpo'], alinear=b.get('alinear', 'izq'))])
        elif tipo == 'lista':
            L.texto(x, y, CW, [_p(it, tam=T['cuerpo'], vineta=True, espacio_despues=0.2 * e) for it in b['items']])
        elif tipo == 'numerados':
            d = alto_lineas(1, T['cuerpo']) * 1.25
            yy = y
            for i, it in enumerate(b['items']):
                hh = max(d, L.alto_parrafos([_p(it, tam=T['cuerpo'])], CW - d - 0.5 * e, 0))
                L.caja(x, yy, d, d, [_p(str(i + 1), tam=T['cuerpo'], negrita=True, color='blanco')], relleno='acento',
                       forma='elipse', alinear='centro', pad=0)
                L.texto(x + d + 0.5 * e, yy, CW - d - 0.5 * e, [_p(it, tam=T['cuerpo'])])
                yy += hh + 0.35 * e
        elif tipo == 'cifras':
            wv = self._ancho_cifras(b, T)
            yy = y
            for it in b['items']:
                h_lab = L.alto_parrafos([_p(it['etiqueta'], tam=T['cuerpo'] * 0.9)], CW - wv - 0.9 * e, 0)
                hh = max(alto_lineas(1, T['cifra']), h_lab) + 0.8 * e
                L.caja(x, yy, CW, hh, relleno='sec_claro', radio=0.3 * e)
                L.caja(x + 0.2 * e, yy, wv, hh, [_p(it['valor'], tam=T['cifra'], negrita=True, color='acento')],
                       forma='rect', alinear='centro', pad=0)
                L.caja(x + wv + 0.5 * e, yy, CW - wv - 0.9 * e, hh, [_p(it['etiqueta'], tam=T['cuerpo'] * 0.9)],
                       forma='rect', pad=0)
                yy += hh + 0.3 * e
        elif tipo in ('tarjeta', 'destacado'):
            fuerte, claro = PAR_COLORES.get(b.get('color', 'azul'), ('secundario', 'sec_claro'))
            if tipo == 'destacado':
                L.caja(x, y, CW, h, self._pars_tarjeta(b, T), relleno='primario', radio=0.3 * e, pad=0.6 * e, ancla='arriba')
            else:
                L.caja(x, y, CW, h, self._pars_tarjeta(b, T), relleno=claro, borde=fuerte, grosor=2.0, radio=0.3 * e,
                       pad=0.6 * e, ancla='arriba')
        elif tipo == 'figura':
            from PIL import Image
            iw, ih = Image.open(b['ruta']).size
            w = CW * b.get('escala', 1.0)
            hi = w * ih / iw
            L.imagen(x + (CW - w) / 2, y, w, b['ruta'], h=hi)
            if b.get('pie'):
                L.texto(x, y + hi + 0.3 * e, CW, [_p(b['pie'], tam=T['pie'], cursiva=True, color='neutro')])
        elif tipo == 'grafico':
            L.grafico(x, y, CW, h, b.get('tipo_grafico', 'barras'), b['categorias'], b['series'], tam=T['cuerpo'] * 0.85,
                      titulo_eje_valor=b.get('titulo_eje_valor'), colores=b.get('colores'))
        elif tipo == 'diagrama':
            L.pegar(self._diagrama(b, T), x, y)
        return n_sec


def generar(contenido, salida_base, logo=None):
    if isinstance(contenido, str):
        with open(contenido, encoding='utf8') as f:
            contenido = json.load(f)
    return Poster(contenido).construir(salida_base, logo=logo)
