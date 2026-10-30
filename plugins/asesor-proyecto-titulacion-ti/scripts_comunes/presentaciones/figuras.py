# -*- coding: utf-8 -*-
"""Motor de figuras académicas EDITABLES. Cada figura se describe en JSON y se produce como:
  .pptx  -> editable (PowerPoint, Google Slides, Canva: Importar archivo)
  .png   -> 300 dpi al ancho exacto de inserción (el texto mide 10 pt reales en Word)
  .svg   -> vectorial (póster, impresión)
  .json  -> la especificación, para regenerar o corregir la figura.
Tipos: comparativo, prisma, embudo, niveles, proceso, mapa, arbol, barras, linea_tiempo, cuadrantes, foda, ciclo."""
import json
import math
import os

from .pptx_kit import Lienzo, PAR_COLORES, alto_lineas, exportar

def _par(texto, **kw):
    d = dict(texto=texto); d.update(kw); return d


def _items(items, color=None, vinetas=None):
    vin = (len(items) > 1) if vinetas is None else vinetas
    return [_par(t, vineta=vin, color=color) for t in items]


def _colores(L, nombre):
    fuerte, claro = PAR_COLORES.get(nombre, (nombre, nombre))
    return fuerte, claro


# ------------------------------------------------------------------ 1. comparativo
def comparativo(s):
    W = s.get('ancho_cm', 13.0)
    L = Lienzo(W, paleta=s.get('paleta', 'sobria'), tam=s.get('tam', 10))
    k = L.k
    labw = s.get('ancho_etiqueta', 2.3 * k) if any(f.get('etiqueta') for f in s['filas']) else 0
    gap = 0.25 * k
    mid = 0.7 * k if s.get('flecha_central') else gap
    colw = (W - 0.1 - labw - (gap if labw else 0) - mid) / 2
    xL = 0.05
    xA = xL + labw + (gap if labw else 0)
    xB = xA + colw + mid
    cA, cB = [_colores(L, c) for c in s.get('colores', ['naranja', 'verde'])]
    y = 0.05
    enc = s.get('encabezados')
    if enc:
        hs = [L.alto_parrafos([_par(t, negrita=True)], colw) for t in enc]
        h = max(hs)
        L.caja(xA, y, colw, h, [_par(enc[0], negrita=True, color='blanco')], relleno=cA[0], alinear='centro')
        L.caja(xB, y, colw, h, [_par(enc[1], negrita=True, color='blanco')], relleno=cB[0], alinear='centro')
        y += h + 0.2 * k
    for f in s['filas']:
        pa, pb = _items(f.get('izquierda', [])), _items(f.get('derecha', []))
        h = max(L.alto_parrafos(pa, colw), L.alto_parrafos(pb, colw),
                L.alto_parrafos([_par(f.get('etiqueta', ''), negrita=True)], labw, 0.1 * k) if labw else 0)
        if labw:
            L.caja(xL, y, labw, h, [_par(f['etiqueta'], negrita=True, color='blanco')], relleno='primario',
                   alinear='centro', pad=0.1 * k)
        L.caja(xA, y, colw, h, pa, relleno=cA[1], borde=cA[0])
        L.caja(xB, y, colw, h, pb, relleno=cB[1], borde=cB[0])
        if s.get('flecha_central'):
            L.flecha(xA + colw + 0.08 * k, y + h / 2, xB - 0.08 * k, y + h / 2)
        y += h + 0.2 * k
    pie = s.get('pie')
    if pie:
        L.flecha(W / 2, y - 0.1 * k, W / 2, y + 0.35 * k)
        y += 0.45 * k
        cP = _colores(L, pie.get('color', 'azul'))
        pars = [_par(pie['titulo'], negrita=True, color=cP[0])] + [_par(t) for t in pie.get('items', [])]
        L.caja_auto(xL, y, W - 0.1, pars, relleno=cP[1], borde=cP[0], alinear='centro')
    return L


# ------------------------------------------------------------------ 2. PRISMA 2020
PRISMA_TXT = {
    'titulo': 'Identificación de estudios a través de bases de datos y registros',
    'fases': ['Identificación', 'Cribado', 'Incluidos'],
}


def validar_prisma(p):
    err = []
    ident = sum(p['identificacion']['bases'].values()) + sum(p['identificacion'].get('registros', {}).values())
    elim = p.get('duplicados', 0) + p.get('no_elegibles_automatizacion', 0) + p.get('eliminados_otros', 0)
    if p['cribados'] != ident - elim:
        err.append(f"cribados ({p['cribados']}) debería ser identificados ({ident}) - eliminados antes del cribado ({elim}) = {ident - elim}")
    if p['buscados'] != p['cribados'] - p['excluidos_cribado']:
        err.append(f"buscados ({p['buscados']}) debería ser cribados - excluidos = {p['cribados'] - p['excluidos_cribado']}")
    if p['evaluados'] != p['buscados'] - p.get('no_recuperados', 0):
        err.append(f"evaluados ({p['evaluados']}) debería ser buscados - no recuperados = {p['buscados'] - p.get('no_recuperados', 0)}")
    exc = sum(p.get('excluidos_texto', {}).values())
    if p['incluidos'] != p['evaluados'] - exc:
        err.append(f"incluidos ({p['incluidos']}) debería ser evaluados - excluidos a texto completo ({exc}) = {p['evaluados'] - exc}")
    return err


def prisma(s):
    err = validar_prisma(s)
    if err and not s.get('forzar'):
        raise ValueError('Las cifras PRISMA no cuadran:\n  - ' + '\n  - '.join(err))
    W = s.get('ancho_cm', 13.0)
    L = Lienzo(W, paleta=s.get('paleta', 'sobria'), tam=s.get('tam', 10))
    k = L.k
    fase_w, g1, g2 = 0.75 * k, 0.25 * k, 0.55 * k
    main_w = s.get('ancho_principal', (W - fase_w - g1 - g2) * 0.52)
    xF, xM = 0.05, 0.05 + fase_w + g1
    xR = xM + main_w + g2
    right_w = W - 0.05 - xR
    y = 0.05
    tit = [ _par(s.get('titulo', PRISMA_TXT['titulo']), negrita=True, color='blanco')]
    h = L.alto_parrafos(tit, W - xM - 0.05, 0.12 * k)
    L.caja(xM, y, W - xM - 0.05, h, tit, relleno='primario', alinear='centro', pad=0.12 * k)
    y += h + 0.3 * k
    n = lambda v: f'(n\u00a0=\u00a0{v})'
    idn = s['identificacion']
    main1 = [_par('Registros identificados desde:')] + \
            [_par(f'{b} {n(v)}', vineta=True) for b, v in idn['bases'].items()] + \
            [_par(f'{b} {n(v)}', vineta=True) for b, v in idn.get('registros', {}).items()]
    right1 = [_par('Registros eliminados antes del cribado:'),
              _par(f"Registros duplicados {n(s.get('duplicados', 0))}", vineta=True),
              _par(f"Marcados como no elegibles por herramientas de automatización {n(s.get('no_elegibles_automatizacion', 0))}", vineta=True),
              _par(f"Eliminados por otros motivos {n(s.get('eliminados_otros', 0))}", vineta=True)]
    filas = [('Identificación', main1, right1)]
    exc_crib = [_par(f"Registros excluidos {n(s['excluidos_cribado'])}")] + \
               [_par(f'{r} {n(v)}', vineta=True) for r, v in s.get('motivos_cribado', {}).items()]
    filas += [('Cribado', [_par(f"Registros cribados {n(s['cribados'])}")], exc_crib),
              ('Cribado', [_par(f"Publicaciones buscadas para su recuperación {n(s['buscados'])}")],
               [_par(f"Publicaciones no recuperadas {n(s.get('no_recuperados', 0))}")]),
              ('Cribado', [_par(f"Publicaciones evaluadas para decidir su elegibilidad {n(s['evaluados'])}")],
               [_par('Publicaciones excluidas:')] + [_par(f'{r} {n(v)}', vineta=True)
                                                     for r, v in s.get('excluidos_texto', {}).items()]),
              ('Incluidos', [_par(f"Estudios incluidos en la revisión {n(s['incluidos'])}"),
                             _par(f"Publicaciones de los estudios incluidos {n(s.get('incluidos_informes', s['incluidos']))}")], None)]
    from .pptx_kit import ancho_pt, PT_CM
    cuenta = {}
    for fase, _, _ in filas:
        cuenta[fase] = cuenta.get(fase, 0) + 1
    fases = {}
    for j, (fase, pm, pr) in enumerate(filas):
        hm = L.alto_parrafos(pm, main_w)
        hr = L.alto_parrafos(pr, right_w) if pr else 0
        minimo = ancho_pt(fase, L.tam, True) * PT_CM + 0.45 * k if cuenta[fase] == 1 else 0
        h = max(hm, hr, minimo)
        L.caja(xM, y, main_w, h, pm, relleno='blanco', borde='primario', grosor=1.0, radio=0.08 * k,
               alinear='centro' if len(pm) == 1 or fase == 'Incluidos' else 'izq')
        if pr:
            L.caja(xR, y, right_w, h, pr, relleno='neutro_claro', borde='neutro', grosor=0.75, radio=0.08 * k)
            L.flecha(xM + main_w + 0.05 * k, y + h / 2, xR - 0.05 * k, y + h / 2)
        if j < len(filas) - 1:
            L.flecha(xM + main_w / 2, y + h + 0.03 * k, xM + main_w / 2, y + h + 0.37 * k)
        fases.setdefault(fase, [y, y + h])[1] = y + h
        y += h + 0.4 * k
    for fase, (y0, y1) in fases.items():
        L.caja(xF, y0, fase_w, y1 - y0, [], relleno='sec_claro', borde='secundario', grosor=0.75, radio=0.08 * k)
        L.texto(xF + fase_w / 2 - (y1 - y0) / 2, y0 + (y1 - y0) / 2 - fase_w / 2, y1 - y0,
                [_par(fase, negrita=True, color='primario')], alinear='centro', ancla='medio', h=fase_w, rotacion=270)
    return L


# ------------------------------------------------------------------ 3. niveles (modelo ecológico / concéntrico)
def _tinte(hexa, f):
    r, g, b = int(hexa[:2], 16), int(hexa[2:4], 16), int(hexa[4:], 16)
    return '%02X%02X%02X' % tuple(int(c + (255 - c) * f) for c in (r, g, b))


def niveles(s):
    """Modelo ecológico o de niveles anidados: elipses concéntricas (niveles[0] = el más externo) con el nombre de cada
    nivel dentro de su banda (siempre a 10 pt) y una leyenda con la descripción."""
    from .pptx_kit import ancho_pt, PT_CM
    W = s.get('ancho_cm', 13.0)
    L = Lienzo(W, paleta=s.get('paleta', 'sobria'), tam=s.get('tam', 10))
    niv = s['niveles']
    ke = L.k
    k = len(niv)
    lh = alto_lineas(1, L.tam)
    t = lh + 0.2 * ke                 # grosor vertical de cada banda
    asp = s.get('aspecto', 1.55)
    centro = s.get('centro', '')
    wc = (ancho_pt(centro, L.tam, True) * PT_CM + 0.5 * ke) if centro else 0.8 * ke
    b = max(lh / 2 + 0.25 * ke, 0.45 * ke)
    a = max(asp * b, wc / 2 + 0.15 * ke)
    radios = [(a, b)]
    for i in range(k - 1, -1, -1):     # de dentro hacia fuera
        nb = b + t
        y_et = b + t / 2
        necesario = ancho_pt(niv[i]['nombre'], L.tam, True) * PT_CM / 2 + 0.2 * ke
        na = max(a + t * s.get('separacion_horizontal', 1.0), necesario / math.sqrt(max(0.05, 1 - (y_et / nb) ** 2)))
        radios.append((na, nb))
        a, b = na, nb
    A, B = radios[-1]
    base = L.pal['secundario']
    fills = [_tinte(base, 0.9 - 0.6 * i / max(1, k - 1)) for i in range(k)]
    leyenda_derecha = (W - 2 * A - 0.5 * ke) >= 4.2 * ke
    cx = 0.05 + A if leyenda_derecha else W / 2
    cy = 0.05 + B
    for i in range(k):                 # de fuera hacia dentro
        ra, rb = radios[k - i]
        L.elipse(cx - ra, cy - rb, 2 * ra, 2 * rb, relleno=fills[i], borde='blanco', grosor=1.5)
    for i in range(k):
        ra, rb = radios[k - i]
        _, rb_in = radios[k - i - 1]
        oscuro = i >= k * 0.6
        L.texto(cx - ra, cy - rb + (rb - rb_in - lh) / 2, 2 * ra,
                [_par(niv[i]['nombre'], negrita=True, color='blanco' if oscuro else 'primario')], alinear='centro', h=lh)
    ra, rb = radios[0]
    L.elipse(cx - ra, cy - rb, 2 * ra, 2 * rb, relleno='primario', borde='blanco', grosor=1.5)
    if centro:
        L.texto(cx - ra, cy - lh / 2, 2 * ra, [_par(centro, negrita=True, color='blanco')], alinear='centro', h=lh)
    # leyenda
    if leyenda_derecha:
        xl, wl, y = 0.05 + 2 * A + 0.5 * ke, W - (0.05 + 2 * A + 0.5 * ke) - 0.05, None
    else:
        xl, wl, y = 0.05, W - 0.1, cy + B + 0.35 * ke
    d = 0.36 * ke
    alturas = [L.alto_parrafos([_par(nv['nombre'], negrita=True), _par(nv.get('descripcion', ''))], wl - d - 0.2 * ke,
                               0.05 * ke) for nv in niv]
    total = sum(alturas) + 0.15 * ke * (k - 1)
    if y is None:
        y = 0.05 + max(0, (2 * B - total) / 2)
    for i, nv in enumerate(niv):
        h = alturas[i]
        L.elipse(xl, y + 0.08 * ke, d, d, relleno=fills[i], borde='secundario', grosor=0.75)
        L.caja(xl + d + 0.14 * ke, y, wl - d - 0.14 * ke, h, [_par(nv['nombre'], negrita=True, color='primario'),
                                                              _par(nv.get('descripcion', ''))], forma='rect',
               ancla='arriba', pad=0.05 * ke)
        y += h + 0.15 * ke
    L._y(cy + B)
    return L


# ------------------------------------------------------------------ 4. proceso
def proceso(s):
    W = s.get('ancho_cm', 13.0)
    L = Lienzo(W, paleta=s.get('paleta', 'sobria'), tam=s.get('tam', 10))
    pasos = s['pasos']
    n = len(pasos)
    fuerte, claro = _colores(L, s.get('color', 'azul'))
    k = L.k
    flecha_g = 0.55 * k
    horizontal = s.get('orientacion', 'horizontal') == 'horizontal'
    bw = (W - 0.1 - (n - 1) * flecha_g) / n if horizontal else 0
    if horizontal and bw < 2.3 * k:
        horizontal = False
    if horizontal:
        pars = [[_par(p['titulo'], negrita=True, color=fuerte)] + ([_par(p['texto'])] if p.get('texto') else []) for p in pasos]
        h = max(L.alto_parrafos(pp, bw) for pp in pars)
        d = 0.72 * k
        cy = 0.05 + (0.62 * k if s.get('numerado', True) else 0)
        extra = 0.2 * k if s.get('numerado', True) else 0
        for i, pp in enumerate(pars):
            x = 0.05 + i * (bw + flecha_g)
            L.caja(x, cy, bw, h + extra, pp, relleno=claro, borde=fuerte, alinear='centro', ancla='medio')
            if s.get('numerado', True):
                L.elipse(x + bw / 2 - d / 2, cy - 0.5 * k, d, d, relleno=fuerte, borde='blanco', grosor=1.5,
                         parrafos=[_par(str(i + 1), negrita=True, color='blanco')])
            if i < n - 1:
                L.flecha(x + bw + 0.07 * k, cy + (h + extra) / 2, x + bw + flecha_g - 0.07 * k, cy + (h + extra) / 2)
    else:
        y = 0.05
        d = 0.72 * k
        num_w = 0.8 * k if s.get('numerado', True) else 0
        sep = 0.2 * k if num_w else 0
        bw = W - 0.1 - num_w - sep
        for i, p in enumerate(pasos):
            pp = [_par(p['titulo'], negrita=True, color=fuerte)] + ([_par(p['texto'])] if p.get('texto') else [])
            h = max(L.alto_parrafos(pp, bw), 0.8 * k)
            if num_w:
                L.elipse(0.05, y + h / 2 - d / 2, d, d, relleno=fuerte, borde='blanco', grosor=1.5,
                         parrafos=[_par(str(i + 1), negrita=True, color='blanco')])
            L.caja(0.05 + num_w + sep, y, bw, h, pp, relleno=claro, borde=fuerte)
            if i < n - 1:
                xa = 0.05 + num_w + sep + bw / 2
                L.flecha(xa, y + h + 0.04 * k, xa, y + h + 0.36 * k)
            y += h + 0.4 * k
    return L


# ------------------------------------------------------------------ 5. mapa conceptual
def mapa(s):
    W = s.get('ancho_cm', 13.0)
    L = Lienzo(W, paleta=s.get('paleta', 'sobria'), tam=s.get('tam', 10))
    ramas = s['ramas']
    k = L.k
    cw = s.get('ancho_centro', 3.0 * k)
    g = 0.7 * k
    sw = (W - 0.1 - cw - 2 * g) / 2
    izq, der = ramas[:(len(ramas) + 1) // 2], ramas[(len(ramas) + 1) // 2:]
    colores = s.get('colores', ['azul', 'naranja', 'verde', 'gris', 'rojo', 'marino'])

    def columna(lista, x, off):
        y, cajas = 0.05, []
        for j, r in enumerate(lista):
            fuerte, claro = _colores(L, colores[(off + j) % len(colores)])
            pp = [_par(r['titulo'], negrita=True, color=fuerte if fuerte != 'neutro' else 'texto')] + _items(r.get('items', []))
            h = L.alto_parrafos(pp, sw)
            cajas.append((x, y, h, pp, fuerte, claro))
            y += h + 0.25 * k
        return cajas, y - 0.25 * k

    ci, hi = columna(izq, 0.05, 0)
    cd, hd = columna(der, 0.05 + sw + g + cw + g, len(izq))
    alto = max(hi, hd)
    # centrar verticalmente la columna más corta
    for cajas, h_col in ((ci, hi), (cd, hd)):
        off = (alto - h_col) / 2
        for k2, c in enumerate(cajas):
            cajas[k2] = (c[0], c[1] + off, *c[2:])
    pc = [_par(s['centro'], negrita=True, color='blanco')]
    hc = max(L.alto_parrafos(pc, cw), 1.2 * k)
    xc, yc = 0.05 + sw + g, 0.05 + alto / 2 - hc / 2
    for (x, y, h, pp, fuerte, claro) in ci:
        L.linea(x + sw, y + h / 2, xc, yc + hc / 2, color=fuerte, grosor=1.25)
    for (x, y, h, pp, fuerte, claro) in cd:
        L.linea(xc + cw, yc + hc / 2, x, y + h / 2, color=fuerte, grosor=1.25)
    for (x, y, h, pp, fuerte, claro) in ci + cd:
        L.caja(x, y, sw, h, pp, relleno=claro, borde=fuerte)
    L.caja(xc, yc, cw, hc, pc, relleno='primario', alinear='centro')
    return L


# ------------------------------------------------------------------ 6. árbol de problemas
def arbol(s):
    W = s.get('ancho_cm', 13.0)
    L = Lienzo(W, paleta=s.get('paleta', 'sobria'), tam=s.get('tam', 10))
    from .pptx_kit import ancho_pt, PT_CM
    etiquetas = [s.get('titulo_efectos', 'Efectos'), s.get('titulo_problema', 'Problema'), s.get('titulo_causas', 'Causas')]
    k = L.k
    fw = max(ancho_pt(e, L.tam, True) * PT_CM for e in etiquetas) + 0.4 * k
    g = 0.25 * k
    x0 = 0.05 + fw + g
    ancho_util = W - 0.05 - x0

    def etiqueta(texto_e, y, h, fuerte, claro):
        L.caja(0.05, y, fw, h, [_par(texto_e, negrita=True, color=fuerte)], relleno=claro, borde=fuerte, grosor=0.75,
               radio=0.08 * k, alinear='centro', pad=0.08 * k)

    def fila(items, y, fuerte, claro):
        n = len(items)
        bw = (ancho_util - (n - 1) * g) / n
        pars = [[_par(t)] for t in items]
        h = max(L.alto_parrafos(p, bw) for p in pars)
        centros = []
        for i, p in enumerate(pars):
            x = x0 + i * (bw + g)
            L.caja(x, y, bw, h, p, relleno=claro, borde=fuerte, alinear='centro')
            centros.append(x + bw / 2)
        return h, centros

    y = 0.05
    he, ce = fila(s['efectos'], y, *_colores(L, 'naranja'))
    etiqueta(etiquetas[0], y, he, 'acento', 'acento_claro')
    y += he + 0.55 * k
    pp = [_par(s['problema'], negrita=True, color='blanco')]
    hp = L.alto_parrafos(pp, ancho_util)
    for cx in ce:
        L.flecha(cx, y - 0.03 * k, cx, y - 0.5 * k)
    L.caja(x0, y, ancho_util, hp, pp, relleno='primario', alinear='centro')
    etiqueta(etiquetas[1], y, hp, 'primario', 'sec_claro')
    y += hp + 0.55 * k
    hc, cc = fila(s['causas'], y, *_colores(L, 'azul'))
    for cx in cc:
        L.flecha(cx, y - 0.03 * k, cx, y - 0.5 * k)
    etiqueta(etiquetas[2], y, hc, 'secundario', 'sec_claro')
    return L


# ------------------------------------------------------------------ 7. gráfico nativo
def barras(s):
    W = s.get('ancho_cm', 13.0)
    L = Lienzo(W, paleta=s.get('paleta', 'sobria'), tam=s.get('tam', 10))
    h = s.get('alto_cm') or max(5.0 * L.k, (0.75 * len(s['categorias']) + 1.6) * L.k)
    L.grafico(0.05, 0.05, W - 0.1, h, s.get('tipo_grafico', 'barras'), s['categorias'], s['series'],
              titulo_eje_valor=s.get('titulo_eje_valor'), etiquetas=s.get('etiquetas', True), max=s.get('max'),
              colores=s.get('colores'), tam=s.get('tam', 10), formato_etiqueta=s.get('formato_etiqueta'))
    return L


# ------------------------------------------------------------------ 8. línea de tiempo
def linea_tiempo(s):
    W = s.get('ancho_cm', 13.0)
    L = Lienzo(W, paleta=s.get('paleta', 'sobria'), tam=s.get('tam', 10))
    hitos = s['hitos']
    k = L.k
    n = len(hitos)
    paso = (W - 0.1) / n
    cw = min(paso * 1.85, 4.2 * k)
    pars = [[_par(h['titulo'], negrita=True, color='acento')] + ([_par(h['texto'])] if h.get('texto') else [])
            for h in hitos]
    alt = [L.alto_parrafos(p, cw) for p in pars]
    h_arr = max(alt[i] for i in range(0, n, 2))
    h_aba = max([alt[i] for i in range(1, n, 2)] or [0])
    yl = 0.05 + h_arr + 0.9 * k
    ph = 0.64 * k
    L.linea(0.05, yl, W - 0.05, yl, color='primario', grosor=2.25)
    for i, hti in enumerate(hitos):
        cx = 0.05 + paso * (i + 0.5)
        x = min(max(0.05, cx - cw / 2), W - 0.05 - cw)
        from .pptx_kit import ancho_pt, PT_CM
        wp = ancho_pt(str(hti['fecha']), L.tam, True) * PT_CM + 0.5 * k
        L.caja(cx - wp / 2, yl - ph / 2, wp, ph, [_par(str(hti['fecha']), negrita=True, color='blanco')],
               relleno='primario', borde='acento', grosor=1.5, forma='pildora', alinear='centro', pad=0.02)
        if i % 2 == 0:
            y = 0.05 + (h_arr - alt[i])
            L.linea(cx, y + alt[i], cx, yl - ph / 2, color='neutro', grosor=0.75)
        else:
            y = yl + 0.9 * k
            L.linea(cx, yl + ph / 2, cx, y, color='neutro', grosor=0.75)
        L.caja(x, y, cw, alt[i], pars[i], relleno='neutro_claro', borde='neutro', grosor=0.5, alinear='centro')
    L._y(yl + ph / 2 + (0.9 * k + h_aba if h_aba else 0))
    return L


# ------------------------------------------------------------------ 9. cuadrantes / FODA
def cuadrantes(s):
    W = s.get('ancho_cm', 13.0)
    L = Lienzo(W, paleta=s.get('paleta', 'sobria'), tam=s.get('tam', 10))
    q = s['cuadrantes']
    colores = s.get('colores', ['azul', 'verde', 'naranja', 'rojo'])
    k = L.k
    ey = 0.7 * k if s.get('titulo_y') else 0
    g = 0.2 * k
    cw = (W - 0.1 - ey - g) / 2
    pars = [[_par(c['titulo'], negrita=True, color=_colores(L, colores[i])[0])] + _items(c.get('items', [])) +
            ([_par(c['texto'])] if c.get('texto') else []) for i, c in enumerate(q)]
    y = 0.05
    if s.get('encabezados_columnas'):
        for j, t in enumerate(s['encabezados_columnas']):
            L.texto(0.05 + ey + j * (cw + g), y, cw, [_par(t, negrita=True, color='primario')], alinear='centro')
        y += alto_lineas(1, L.tam) + 0.15 * k
    y0 = y
    for fila in (0, 1):
        h = max(L.alto_parrafos(pars[2 * fila], cw), L.alto_parrafos(pars[2 * fila + 1], cw))
        for col in (0, 1):
            i = 2 * fila + col
            f, c = _colores(L, colores[i])
            L.caja(0.05 + ey + col * (cw + g), y, cw, h, pars[i], relleno=c, borde=f)
        y += h + g
    if s.get('titulo_y'):
        hh = y - g - y0
        L.texto(0.05 + ey / 2 - hh / 2, y0 + hh / 2 - ey / 2, hh, [_par(s['titulo_y'], negrita=True, color='primario')],
                alinear='centro', ancla='medio', h=ey, rotacion=270)
    return L


def foda(s):
    s = dict(s)
    s.setdefault('encabezados_columnas', ['Factores positivos', 'Factores negativos'])
    s.setdefault('titulo_y', None)
    t = s.get('textos', {})
    s['cuadrantes'] = [dict(titulo='Fortalezas', items=s.get('fortalezas', [])),
                       dict(titulo='Debilidades', items=s.get('debilidades', [])),
                       dict(titulo='Oportunidades', items=s.get('oportunidades', [])),
                       dict(titulo='Amenazas', items=s.get('amenazas', []))]
    s['colores'] = s.get('colores', ['verde', 'naranja', 'azul', 'rojo'])
    return cuadrantes(s)


# ------------------------------------------------------------------ 10. ciclo
def ciclo(s):
    W = s.get('ancho_cm', 13.0)
    L = Lienzo(W, paleta=s.get('paleta', 'sobria'), tam=s.get('tam', 10))
    et = s['etapas']
    n = len(et)
    k = L.k
    bw = s.get('ancho_caja', 3.2 * k)
    fuerte, claro = _colores(L, s.get('color', 'azul'))
    pars = [[_par(e['titulo'], negrita=True, color=fuerte)] + ([_par(e['texto'])] if e.get('texto') else []) for e in et]
    hs = [L.alto_parrafos(p, bw) for p in pars]
    hmax = max(hs)
    R = s.get('radio_cm', max(2.2 * k, (bw * 0.62) / math.sin(math.pi / n) if n > 2 else 2.5 * k))
    if s.get('centro'):
        R = max(R, bw / 2 + 1.7 * k)
    R = min(R, (W - bw) / 2 - 0.1)
    cx = W / 2
    cy = 0.05 + hmax / 2 + R
    pos = []
    for i in range(n):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
        pos.append((x, y))
    if s.get('centro'):
        pc = [_par(s['centro'], negrita=True, color='blanco')]
        wc = min(2.8 * k, 2 * (R - bw / 2) - 0.6 * k)
        hc = L.alto_parrafos(pc, wc)
        L.caja(cx - wc / 2, cy - hc / 2, wc, hc, pc, relleno='primario', alinear='centro')
    for i in range(n):
        (x1, y1), (x2, y2) = pos[i], pos[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d

        def recorte(h):
            # distancia desde el centro de la caja hasta su borde en la dirección (ux, uy)
            tx = (bw / 2) / abs(ux) if abs(ux) > 1e-6 else 1e9
            ty = (h / 2) / abs(uy) if abs(uy) > 1e-6 else 1e9
            return min(tx, ty) + 0.12 * k
        a, b = recorte(hs[i]), recorte(hs[(i + 1) % n])
        if d > a + b + 0.2 * k:
            L.flecha(x1 + ux * a, y1 + uy * a, x2 - ux * b, y2 - uy * b, color=fuerte, grosor=1.5)
    for i, (x, y) in enumerate(pos):
        L.caja(x - bw / 2, y - hs[i] / 2, bw, hs[i], pars[i], relleno=claro, borde=fuerte, alinear='centro')
    return L


# ------------------------------------------------------------------ 11. embudo (resumen de selección)
def embudo(s):
    """Resumen compacto del proceso de selección (póster y diapositivas): cifra grande + texto + exclusión al lado."""
    from .pptx_kit import ancho_pt, PT_CM
    W = s.get('ancho_cm', 13.0)
    L = Lienzo(W, paleta=s.get('paleta', 'sobria'), tam=s.get('tam', 10))
    pasos = s['pasos']
    t = L.tam
    k = L.k
    tn = round(t * 1.6)
    wn = max(ancho_pt(p['n'], tn, True) for p in pasos) * PT_CM + 0.5 * k
    hay_exc = any(p.get('exclusion') for p in pasos)
    we = s.get('ancho_exclusion', (W * 0.24) if hay_exc else 0)
    ge = 0.55 * k if hay_exc else 0
    bw = W - 0.1 - we - ge
    y = 0.05
    for i, p in enumerate(pasos):
        ultimo = i == len(pasos) - 1
        pt = [_par(p['texto'], negrita=ultimo, color='blanco' if ultimo else None)]
        h = max(L.alto_parrafos(pt, bw - wn - 0.1 * k), alto_lineas(1, tn) + 0.3 * k)
        pe = [_par(p['exclusion'], negrita=True, color='acento', alinear='centro')] if p.get('exclusion') else None
        if pe:
            h = max(h, L.alto_parrafos(pe, we) + 0.2 * k)
        L.caja(0.05, y, bw, h, [], relleno='primario' if ultimo else 'sec_claro', borde='primario' if ultimo else 'secundario',
               grosor=1.0)
        L.caja(0.05, y, wn, h, [_par(p['n'], tam=tn, negrita=True, color='acento' if ultimo else 'primario')],
               forma='rect', alinear='centro', pad=0.05)
        L.caja(0.05 + wn, y, bw - wn, h, pt, forma='rect', pad=0.1)
        if pe:
            L.flecha(0.05 + bw + 0.05, y + h / 2, 0.05 + bw + ge - 0.05, y + h / 2)
            L.caja(0.05 + bw + ge, y + 0.1, we, h - 0.2, pe, relleno='acento_claro', borde='acento', grosor=0.75,
                   alinear='centro')
        y += h
        if not ultimo:
            L.flecha(0.05 + bw / 2, y + 0.03, 0.05 + bw / 2, y + 0.42)
            y += 0.45
    return L


TIPOS = dict(embudo=embudo, comparativo=comparativo, prisma=prisma, niveles=niveles, proceso=proceso, mapa=mapa, arbol=arbol,
             barras=barras, linea_tiempo=linea_tiempo, cuadrantes=cuadrantes, foda=foda, ciclo=ciclo)


def generar(spec, base, svg=True):
    """spec: dict (o ruta a .json). base: ruta sin extensión (p. ej. .../Figuras/Figura4_Factores)."""
    if isinstance(spec, str):
        with open(spec, encoding='utf8') as f:
            spec = json.load(f)
    tipo = spec['tipo']
    if tipo not in TIPOS:
        raise ValueError(f'Tipo desconocido: {tipo}. Disponibles: {", ".join(TIPOS)}')
    L = TIPOS[tipo](spec)
    os.makedirs(os.path.dirname(os.path.abspath(base)), exist_ok=True)
    L.guardar(base + '.pptx')
    with open(base + '.json', 'w', encoding='utf8') as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
    out = exportar(base + '.pptx', svg=svg, alto_cm=L.alto_final())
    out.update(ancho_cm=L.ancho, alto_cm=L.alto_final())
    return out
