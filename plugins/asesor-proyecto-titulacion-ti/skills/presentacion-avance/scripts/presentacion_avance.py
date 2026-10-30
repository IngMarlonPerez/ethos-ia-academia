"""Presentación de un avance del proyecto de titulación sobre la presentación del avance anterior, y su guion.

Conserva el diseño de la presentación anterior: usa su portada (con el título y el número de avance actualizados),
un diseño de contenido con su fondo y logo, y su diapositiva de cierre. Las diapositivas de contenido se arman desde
un JSON con tipos de diapositiva; las notas de cada una son el guion del orador, que además se exporta a Word y a
Markdown para leerlo mientras se presenta.

    python presentacion_avance.py contenido.json
    python presentacion_avance.py contenido.json --solo-guion

Rutas relativas del JSON: respecto de la carpeta del JSON. Ver plantillas/presentacion-avance-ejemplo.json.
"""
import argparse
import json
from pathlib import Path

import docx
from docx.shared import Pt as DPt
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

FUENTE = 'Arial'


def rgb(h):
    return RGBColor.from_string(h.lstrip('#').upper())


class Lienzo:
    """Primitivas de dibujo con la paleta del proyecto."""

    def __init__(self, colores):
        self.P = rgb(colores.get('primario', '203145'))
        self.A = rgb(colores.get('acento', 'E87D1E'))
        self.G = rgb(colores.get('texto_secundario', '555F6B'))
        self.C = rgb(colores.get('claro', 'EEF2F6'))
        self.B = RGBColor(0xFF, 0xFF, 0xFF)

    def texto(self, s, x, y, w, h, contenido, tam=16, color=None, negrita=False, alinear=PP_ALIGN.LEFT,
              ancla=MSO_ANCHOR.TOP):
        """contenido: str, o lista de párrafos; cada párrafo str o lista de [texto, negrita]."""
        tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = ancla
        for m in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'):
            setattr(tf, m, Inches(0.04))
        for i, par in enumerate(contenido if isinstance(contenido, list) else [contenido]):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = alinear
            p.space_after = Pt(4)
            for t, b in (par if isinstance(par, list) else [(par, negrita)]):
                r = p.add_run()
                r.text = t
                r.font.name, r.font.size, r.font.bold = FUENTE, Pt(tam), b
                r.font.color.rgb = color or self.P
        return tb

    def caja(self, s, x, y, w, h, relleno=None, borde=None, redondeada=True):
        f = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if redondeada else MSO_SHAPE.RECTANGLE,
                               Inches(x), Inches(y), Inches(w), Inches(h))
        if redondeada:
            f.adjustments[0] = 0.08
        f.fill.solid()
        f.fill.fore_color.rgb = relleno or self.C
        if borde:
            f.line.color.rgb = borde
            f.line.width = Pt(1)
        else:
            f.line.fill.background()
        f.shadow.inherit = False
        return f

    def circulo(self, s, x, y, d, etiqueta, relleno=None, tam=14):
        f = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
        f.fill.solid()
        f.fill.fore_color.rgb = relleno or self.A
        f.line.fill.background()
        tf = f.text_frame
        for m in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'):
            setattr(tf, m, 0)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = str(etiqueta)
        r.font.name, r.font.size, r.font.bold, r.font.color.rgb = FUENTE, Pt(tam), True, self.B

    def imagen(self, s, ruta, x, y, w_max, h_max):
        with Image.open(ruta) as im:
            ar = im.width / im.height
        w, h = w_max, w_max / ar
        if h > h_max:
            h, w = h_max, h_max * ar
        pic = s.shapes.add_picture(str(ruta), Inches(x + (w_max - w) / 2), Inches(y), Inches(w), Inches(h))
        pic.line.color.rgb = RGBColor(0xC8, 0xD0, 0xD8)
        pic.line.width = Pt(0.75)

    def dato(self, s, x, y, w, cifra, etiqueta, oscuro=False):
        self.texto(s, x, y, w, 0.75, cifra, tam=34, color=self.A, negrita=True)
        self.texto(s, x, y + 0.72, w, 0.6, etiqueta, tam=12, color=self.B if oscuro else self.G)

    def panel(self, s, x, y, w, h, d):
        """Recuadro oscuro: titulo, cifras [[cifra, etiqueta]], texto, puntos, filas [[texto, valor]], nota."""
        self.caja(s, x, y, w, h, relleno=self.P)
        yy = y + 0.2
        if d.get('titulo'):
            self.texto(s, x + 0.3, yy, w - 0.6, 0.4, d['titulo'], tam=14, color=self.A, negrita=True)
            yy += 0.5
        for c, e in d.get('cifras', []):
            self.texto(s, x + 0.3, yy, w - 0.6, 0.75, c, tam=34, color=self.B, negrita=True)
            self.texto(s, x + 0.3, yy + 0.72, w - 0.6, 0.7, e, tam=13, color=self.B)
            yy += 1.6
        if d.get('texto'):
            self.texto(s, x + 0.3, yy, w - 0.6, y + h - yy - 0.1, d['texto'], tam=13, color=self.B)
        if d.get('puntos'):
            self.texto(s, x + 0.3, yy, w - 0.6, y + h - yy - 0.1, ['• ' + t for t in d['puntos']], tam=14,
                       color=self.B)
        if d.get('nota'):
            self.texto(s, x + 0.3, y + h - 1.0, w - 0.6, 0.9, d['nota'], tam=12, color=self.C)


def nueva(prs, L, layout, d):
    s = prs.slides.add_slide(layout)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    if d.get('seccion'):
        L.texto(s, 0.6, 0.32, 8.4, 0.35, d['seccion'].upper(), tam=12, color=L.A, negrita=True)
    L.texto(s, 0.6, 0.62, 9.6, 0.7, d['titulo'], tam=28, negrita=True)
    return s


# ------------------------------------------------------------------ tipos de diapositiva (área útil 0.6–12.7 × 1.45–6.7)

def agenda(s, L, d, base):
    for i, (n, t, desc) in enumerate(d['partes']):
        x, y = 0.6 + (i % 2) * 6.15, 1.75 + (i // 2) * 2.35
        L.caja(s, x, y, 5.85, 2.05)
        L.circulo(s, x + 0.3, y + 0.35, 0.8, n, tam=24)
        L.texto(s, x + 1.35, y + 0.35, 4.3, 0.5, t, tam=20, negrita=True)
        L.texto(s, x + 1.35, y + 0.95, 4.3, 0.9, desc, tam=15, color=L.G)


def lista_panel(s, L, d, base):
    """intro, puntos [[etiqueta, texto]] o [[etiqueta, título, detalle]], panel, pie."""
    y = 1.5
    if d.get('intro'):
        L.texto(s, 0.6, y, 6.3, 1.2, d['intro'], tam=16, color=L.G)
        y += 1.35
    paso = min(1.08, (5.75 - y) / max(len(d['puntos']), 1))
    for i, p in enumerate(d['puntos']):
        yy = y + i * paso
        L.circulo(s, 0.6, yy + 0.05, 0.55, p[0], tam=12)
        if len(p) == 2:
            L.texto(s, 1.3, yy, 5.7, 0.6, p[1], tam=15, ancla=MSO_ANCHOR.MIDDLE)
        else:
            L.texto(s, 1.3, yy - 0.05, 6.0, 0.45, p[1], tam=17, negrita=True)
            L.texto(s, 1.3, yy + 0.4, 6.0, 0.55, p[2], tam=12, color=L.G)
    L.panel(s, 7.4 if d.get('intro') else 8.2, 1.5, 5.3 if d.get('intro') else 4.5, 4.4 if d.get('pie') else 5.2,
            d['panel'])
    if d.get('pie'):
        L.texto(s, 0.6, 6.0, 12.1, 0.6, d['pie'], tam=13, color=L.G)


def objetivos(s, L, d, base):
    L.caja(s, 0.6, 1.5, 12.1, 1.25, relleno=L.P)
    L.texto(s, 0.9, 1.6, 11.5, 1.05, [[('Objetivo general. ', True), (d['general'], False)]], tam=15, color=L.B,
            ancla=MSO_ANCHOR.MIDDLE)
    n = len(d['especificos'])
    w = (12.1 - 0.23 * (n - 1)) / n
    for i, (k, v, desc) in enumerate(d['especificos']):
        x = 0.6 + i * (w + 0.23)
        L.caja(s, x, 3.0, w, 2.35)
        L.texto(s, x + 0.2, 3.15, w - 0.35, 0.4, k, tam=13, color=L.A, negrita=True)
        L.texto(s, x + 0.2, 3.5, w - 0.35, 0.5, v, tam=20, negrita=True)
        L.texto(s, x + 0.2, 4.05, w - 0.35, 1.2, desc, tam=13, color=L.G)
    for i, (q, desc) in enumerate(d.get('que_como_para_que', [])):
        L.texto(s, 0.6 + i * 4.1, 5.6, 3.9, 1.0, [[(q + ' ', True), (desc, False)]], tam=13)


def tarjetas_cifras(s, L, d, base):
    """tarjetas [[etiqueta, título, detalle, destacada]], cifras [[cifra, etiqueta]], recuadro {titulo, puntos}, pie."""
    for i, (k, t, desc, dest) in enumerate(d['tarjetas']):
        y = 1.55 + i * 1.3
        L.caja(s, 0.6, y, 6.0, 1.15, borde=L.A if dest else None)
        L.texto(s, 0.85, y + 0.12, 1.0, 0.4, k, tam=13, color=L.A if dest else L.G, negrita=True)
        L.texto(s, 1.85, y + 0.08, 4.6, 0.45, t, tam=17, negrita=True)
        L.texto(s, 1.85, y + 0.52, 4.6, 0.6, desc, tam=12, color=L.G)
    for i, (c, e) in enumerate(d.get('cifras', [])):
        L.dato(s, 7.2 + i * 2.9, 1.55, 2.6, c, e)
    if d.get('recuadro'):
        L.caja(s, 7.2, 3.2, 5.5, 2.5)
        L.texto(s, 7.45, 3.3, 5.1, 0.4, d['recuadro']['titulo'], tam=14, negrita=True)
        L.texto(s, 7.45, 3.75, 5.1, 1.9, ['• ' + p for p in d['recuadro']['puntos']], tam=14, color=L.G)
    if d.get('pie'):
        L.texto(s, 0.6, 5.65, 12.1, 0.9, d['pie'], tam=13, color=L.G)


def tabla_barras(s, L, d, base):
    """tabla (primera fila = encabezado), nota_tabla, barras [[etiqueta, valor 0–1, texto]], panel, pie, nota."""
    filas = d['tabla']
    t = s.shapes.add_table(len(filas), len(filas[0]), Inches(0.6), Inches(1.7), Inches(5.6),
                           Inches(0.55 * len(filas))).table
    for i, fila in enumerate(filas):
        for j, v in enumerate(fila):
            c = t.cell(i, j)
            c.text = str(v)
            p = c.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.runs[0] if p.runs else p.add_run()
            r.font.name, r.font.size, r.font.bold = FUENTE, Pt(15), i == 0 or j == 0
            c.fill.solid()
            c.fill.fore_color.rgb = L.P if i == 0 else (L.C if j == 0 else L.B)
            r.font.color.rgb = L.B if i == 0 else L.P
    y_tabla = 1.7 + 0.55 * len(filas)
    if d.get('nota_tabla'):
        L.texto(s, 0.6, y_tabla + 0.1, 5.6, 0.5, d['nota_tabla'], tam=12, color=L.G)
    for i, (k, v, txt) in enumerate(d.get('barras', [])):
        y = 1.75 + i * 0.75
        L.texto(s, 6.8, y, 1.6, 0.4, k, tam=15, negrita=True)
        L.caja(s, 8.4, y + 0.08, 3.4, 0.32, relleno=L.C, redondeada=False)
        L.caja(s, 8.4, y + 0.08, max(3.4 * float(v), 0.02), 0.32, relleno=L.A, redondeada=False)
        L.texto(s, 11.9, y, 0.9, 0.4, txt, tam=15, negrita=True)
    if d.get('panel'):
        L.caja(s, 6.8, 4.25, 5.9, 1.45, relleno=L.P)
        L.texto(s, 7.1, 4.35, 5.4, 0.6, d['panel']['titulo'], tam=24, color=L.B, negrita=True)
        L.texto(s, 7.1, 4.95, 5.4, 0.7, d['panel'].get('texto', ''), tam=13, color=L.B)
    if d.get('pie'):
        L.texto(s, 0.6, max(y_tabla + 0.7, 4.6), 5.9, 2.0, d['pie'], tam=13, color=L.G)
    if d.get('nota'):
        L.texto(s, 6.8, 5.9, 5.9, 0.6, d['nota'], tam=12, color=L.G)


def fases(s, L, d, base):
    """fases [[etiqueta, título, detalle]], destacada (índice), subtitulo, pasos [texto], pie."""
    n = len(d['fases'])
    w = (12.1 - 0.2 * (n - 1)) / n
    for i, (k, t, desc) in enumerate(d['fases']):
        x = 0.6 + i * (w + 0.2)
        oscura = i == d.get('destacada', -1)
        L.caja(s, x, 1.6, w, 1.9, relleno=L.P if oscura else L.C)
        L.texto(s, x + 0.15, 1.7, w - 0.25, 0.35, k, tam=12, color=L.A, negrita=True)
        L.texto(s, x + 0.15, 2.05, w - 0.25, 0.45, t, tam=17, color=L.B if oscura else L.P, negrita=True)
        L.texto(s, x + 0.15, 2.55, w - 0.25, 0.9, desc, tam=12, color=L.B if oscura else L.G)
    if d.get('subtitulo'):
        L.texto(s, 0.6, 3.75, 12.1, 0.4, d['subtitulo'], tam=14, negrita=True)
    pasos = d.get('pasos', [])
    if pasos:
        w = 12.1 / len(pasos)
        for i, (k, t) in enumerate(pasos):
            x = 0.6 + i * w
            L.circulo(s, x + w / 2 - 0.28, 4.35, 0.55, k, relleno=L.A if i else L.G, tam=11)
            L.texto(s, x, 5.0, w - 0.1, 0.6, t, tam=12, color=L.G, alinear=PP_ALIGN.CENTER)
    if d.get('pie'):
        L.texto(s, 0.6, 5.85, 12.1, 0.8, d['pie'], tam=13, color=L.G)


def imagen_lateral(s, L, d, base):
    """imagen, recuadro {titulo, cifra, etiqueta_cifra, filas [[texto, valor, destacada]], subtitulo, puntos}."""
    L.imagen(s, base / d['imagen'], 0.6, 1.45, 7.5, 5.3)
    r = d['recuadro']
    L.caja(s, 8.4, 1.45, 4.3, 5.3)
    y = 1.6
    if r.get('cifra'):
        L.dato(s, 8.65, y, 3.8, r['cifra'], r.get('etiqueta_cifra', ''))
        y += 1.4
    if r.get('titulo'):
        L.texto(s, 8.65, y, 3.8, 0.4, r['titulo'], tam=15, negrita=True)
        y += 0.5
    for t, v, dest in r.get('filas', []):
        L.texto(s, 8.65, y, 2.6, 0.45, t, tam=14)
        L.texto(s, 11.3, y, 1.2, 0.45, v, tam=14, color=L.A if dest else L.G, negrita=True, alinear=PP_ALIGN.RIGHT)
        y += 0.55
    if r.get('filas'):
        y += 0.15
    if r.get('subtitulo'):
        L.texto(s, 8.65, y, 3.8, 0.4, r['subtitulo'], tam=15, negrita=True)
        y += 0.45
    if r.get('puntos'):
        L.texto(s, 8.65, y, 3.8, 6.6 - y, ['• ' + p for p in r['puntos']], tam=13, color=L.G)


def galeria(s, L, d, base):
    """imagenes [[ruta, pie]] (2 a 4)."""
    n = len(d['imagenes'])
    w = (12.1 - 0.18 * (n - 1)) / n
    alto = 4.6 if n <= 2 else 4.4
    for i, (ruta, pie) in enumerate(d['imagenes']):
        x = 0.6 + i * (w + 0.18)
        L.imagen(s, base / ruta, x, 1.5, w, alto)
        L.texto(s, x, 1.6 + alto, w, 0.5, pie, tam=12 if n > 2 else 13, negrita=True, alinear=PP_ALIGN.CENTER)


def cifras_imagen(s, L, d, base):
    """cifras [[cifra, etiqueta]] (hasta 3) a la izquierda e imagen a la derecha."""
    for i, (c, e) in enumerate(d['cifras']):
        L.dato(s, 0.6, 1.5 + i * 1.6, 3.6, c, e)
    L.imagen(s, base / d['imagen'], 4.5, 1.45, 8.2, 5.25)


def conclusiones(s, L, d, base):
    """puntos [texto], panel {titulo, puntos}, pie."""
    for i, c in enumerate(d['puntos']):
        y = 1.6 + i * 1.0
        L.circulo(s, 0.6, y, 0.55, i + 1, tam=14)
        L.texto(s, 1.35, y - 0.02, 5.6, 0.9, c, tam=14)
    L.panel(s, 7.3, 1.55, 5.4, 5.1, d['panel'])
    if d.get('pie'):
        L.texto(s, 0.6, 5.85, 6.4, 0.8, d['pie'], tam=13, color=L.G)


TIPOS = {f.__name__: f for f in (agenda, lista_panel, objetivos, tarjetas_cifras, tabla_barras, fases,
                                 imagen_lateral, galeria, cifras_imagen, conclusiones)}


# ------------------------------------------------------------------ portada, cierre y guion

def actualizar_portada(slide, reemplazos):
    """Reemplaza el texto de los cuadros cuyo texto empieza con cada clave (conserva el formato del primer run)."""
    hechos = set()
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        for clave, nuevo in reemplazos.items():
            if sh.text_frame.text.strip().upper().startswith(clave.upper()):
                pars = sh.text_frame.paragraphs
                pars[0].runs[0].text = nuevo
                for r in pars[0].runs[1:]:
                    r.text = ''
                for p in pars[1:]:
                    for r in p.runs:
                        r.text = ''
                hechos.add(clave)
    faltan = set(reemplazos) - hechos
    if faltan:
        raise SystemExit(f'No se encontraron en la portada los textos: {sorted(faltan)}')


def guion(cfg, diapositivas, base):
    """Escribe el guion (una sección por diapositiva) en Markdown y en Word."""
    md = [f"# {cfg.get('guion_titulo', 'Guion de la presentación')}", '']
    if cfg.get('guion_subtitulo'):
        md += [cfg['guion_subtitulo'], '']
    palabras = sum(len(d.get('notas', '').split()) for d in diapositivas)
    minutos = round(palabras / 140)
    md += [f'Texto para leer mientras se presenta. Duración aproximada: {minutos} minutos ({palabras} palabras a unas '
           '140 palabras por minuto).', '']
    for i, d in enumerate(diapositivas, 1):
        md += [f"## Diapositiva {i}. {d['titulo']}", '']
        md += [p.strip() for p in d.get('notas', '').split('\n\n')] + [''] if d.get('notas') else ['', '']
    salida = base / cfg['guion']
    salida.with_suffix('.md').write_text('\n'.join(md), encoding='utf-8')
    w = docx.Document()
    w.styles['Normal'].font.name = 'Arial'
    w.styles['Normal'].font.size = DPt(12)
    w.add_heading(cfg.get('guion_titulo', 'Guion de la presentación'), 0)
    if cfg.get('guion_subtitulo'):
        w.add_paragraph(cfg['guion_subtitulo'])
    w.add_paragraph(md[4] if cfg.get('guion_subtitulo') else md[2])
    for i, d in enumerate(diapositivas, 1):
        w.add_heading(f"Diapositiva {i}. {d['titulo']}", 1)
        for p in d.get('notas', '').split('\n\n'):
            if p.strip():
                w.add_paragraph(p.strip())
    if cfg.get('autor'):
        w.core_properties.author = w.core_properties.last_modified_by = cfg['autor']
    w.save(str(salida.with_suffix('.docx')))
    return palabras, minutos


def eliminar(prs, indice):
    ids = prs.slides._sldIdLst
    sld = ids[indice]
    prs.part.drop_rel(sld.rId)
    ids.remove(sld)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('json')
    ap.add_argument('--solo-guion', action='store_true')
    a = ap.parse_args()
    ruta = Path(a.json).resolve()
    cfg = json.loads(ruta.read_text(encoding='utf-8'))
    base = ruta.parent
    portada_cfg = cfg['portada']
    todas = [{'titulo': portada_cfg.get('titulo_guion', 'Portada'), 'notas': portada_cfg.get('notas', '')}]
    todas += cfg['diapositivas']
    if cfg.get('cierre'):
        todas.append({'titulo': cfg['cierre'].get('titulo_guion', 'Cierre'), 'notas': cfg['cierre'].get('notas', '')})
    if not a.solo_guion:
        prs = Presentation(str(base / cfg['base']))
        n_base = len(prs.slides)
        L = Lienzo(cfg.get('colores', {}))
        layout = prs.slide_layouts[cfg.get('layout_contenido', 1)]
        portada = prs.slides[cfg.get('portada_base', 1) - 1]
        actualizar_portada(portada, portada_cfg.get('reemplazos', {}))
        portada.notes_slide.notes_text_frame.text = portada_cfg.get('notas', '')
        for d in cfg['diapositivas']:
            if d['tipo'] not in TIPOS:
                raise SystemExit(f"Tipo desconocido «{d['tipo']}». Tipos: {', '.join(TIPOS)}")
            s = nueva(prs, L, layout, d)
            TIPOS[d['tipo']](s, L, d, base)
            if d.get('notas'):
                s.notes_slide.notes_text_frame.text = d['notas']
        # Se quitan al final las diapositivas del avance anterior que no se conservan (así los nombres internos de
        # las nuevas no chocan) y el cierre pasa al final.
        conservar = {cfg.get('portada_base', 1) - 1}
        cierre = cfg.get('cierre', {}).get('diapositiva_base')
        if cierre:
            conservar.add(cierre - 1)
        for i in sorted(set(range(n_base)) - conservar, reverse=True):
            eliminar(prs, i)
        if cierre:
            ids = prs.slides._sldIdLst
            sld = ids[1 if cierre - 1 > cfg.get('portada_base', 1) - 1 else 0]
            ids.remove(sld)
            ids.append(sld)
        if cfg.get('autor'):
            prs.core_properties.author = prs.core_properties.last_modified_by = cfg['autor']
        prs.core_properties.title = cfg.get('titulo_documento', '')
        prs.save(str(base / cfg['salida']))
        print(f"Escrito {cfg['salida']}: {len(prs.slides)} diapositivas")
    if cfg.get('guion'):
        palabras, minutos = guion(cfg, todas, base)
        print(f"Guion: {cfg['guion']}.docx y .md ({palabras} palabras, unos {minutos} minutos)")


if __name__ == '__main__':
    main()
