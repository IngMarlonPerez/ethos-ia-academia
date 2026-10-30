"""Diagrama de flujo PRISMA 2020 (bases de datos) como imagen PNG.

Sigue la plantilla oficial de PRISMA 2020 para revisiones nuevas que solo buscan en bases de datos
(Page et al., 2021, https://www.prisma-statement.org): Identificación → Cribado → Incluidos.

Uso desde otro script:
    from diagrama_prisma import conteos_desde_datos, dibujar
    dibujar(conteos_desde_datos(d), "PRISMA_2020.png")

Uso directo (ejemplo con números de prueba):
    python diagrama_prisma.py salida.png
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

AZUL = (27, 50, 71)
AZUL_CLARO = (220, 227, 236)
NARANJA = (242, 140, 40)
NEGRO = (33, 33, 33)
BLANCO = (255, 255, 255)


def _fuente(tam, negrita=False):
    candidatos = ["arialbd.ttf" if negrita else "arial.ttf", "DejaVuSans-Bold.ttf" if negrita else "DejaVuSans.ttf"]
    for nombre in candidatos:
        for carpeta in ("C:/Windows/Fonts", "/usr/share/fonts/truetype/dejavu", "/Library/Fonts", ""):
            ruta = os.path.join(carpeta, nombre) if carpeta else nombre
            try:
                return ImageFont.truetype(ruta, tam)
            except OSError:
                continue
    return ImageFont.load_default()


def conteos_desde_datos(d):
    """Calcula los números del diagrama a partir del diccionario de matrices.py.

    Se puede forzar cualquier valor con d["prisma2020"] = {"clave": n, ...}.
    """
    b = d.get("busquedas", [])
    por_base = {}
    for x in b:
        base = x.get("base", "Scopus")
        por_base[base] = por_base.get(base, 0) + int(x.get("sin_filtros", 0))
    sin = sum(int(x.get("sin_filtros", 0)) for x in b)
    con = sum(int(x.get("con_filtros", 0)) for x in b)
    n_tit = len(d.get("cribado_titulo", []))
    eleg = d.get("elegibilidad", [])
    buscados = len(eleg)
    no_rec = sum(1 for r in eleg if str(r.get("decision", "")).startswith("No recuperado"))
    incluidos = sum(1 for r in eleg if str(r.get("decision", "")).startswith("Incluido"))
    evaluados = buscados - no_rec
    motivos = {}
    for r in eleg:
        dec = str(r.get("decision", ""))
        if dec.startswith("Incluido") or dec.startswith("No recuperado"):
            continue
        m = r.get("motivo_corto") or "Aporte menor o redundante"
        motivos[m] = motivos.get(m, 0) + 1
    c = {
        "por_base": por_base,
        "identificados": sin,
        "filtros_automaticos": sin - con,
        "duplicados": con - n_tit,
        "cribados": n_tit,
        "excluidos_cribado": n_tit - buscados,
        "buscados": buscados,
        "no_recuperados": no_rec,
        "evaluados": evaluados,
        "excluidos_elegibilidad": motivos,
        "incluidos": incluidos,
    }
    c.update(d.get("prisma2020", {}))
    return c


def _caja(dib, x, y, w, h, lineas, borde=AZUL, relleno=BLANCO, tam=17):
    dib.rectangle([x, y, x + w, y + h], outline=borde, width=3, fill=relleno)
    f = _fuente(tam)
    alto = sum(f.getbbox(t)[3] + 6 for t in lineas)
    yy = y + (h - alto) / 2
    for t in lineas:
        ancho = f.getlength(t)
        dib.text((x + (w - ancho) / 2, yy), t, font=f, fill=NEGRO)
        yy += f.getbbox(t)[3] + 6


def _flecha(dib, x1, y1, x2, y2):
    dib.line([x1, y1, x2, y2], fill=NEGRO, width=3)
    if x1 == x2:  # vertical hacia abajo
        dib.polygon([(x2 - 9, y2 - 14), (x2 + 9, y2 - 14), (x2, y2)], fill=NEGRO)
    else:  # horizontal hacia la derecha
        dib.polygon([(x2 - 14, y2 - 9), (x2 - 14, y2 + 9), (x2, y2)], fill=NEGRO)


def _banda(img, x, y, w, h, texto, color):
    banda = Image.new("RGB", (h, w), color)
    d2 = ImageDraw.Draw(banda)
    f = _fuente(20, negrita=True)
    ancho = f.getlength(texto)
    d2.text(((h - ancho) / 2, (w - 24) / 2), texto, font=f, fill=BLANCO)
    img.paste(banda.rotate(90, expand=True), (x, y))


def dibujar(c, ruta_png, titulo="Diagrama de flujo PRISMA 2020"):
    W, H = 1500, 1320
    img = Image.new("RGB", (W, H), BLANCO)
    dib = ImageDraw.Draw(img)
    ft = _fuente(26, negrita=True)
    dib.text(((W - ft.getlength(titulo)) / 2, 22), titulo, font=ft, fill=AZUL)

    X1, X2, WC = 120, 860, 560
    bases = "; ".join(f"{k} (n = {v:,})".replace(",", ".") for k, v in c["por_base"].items()) or f"(n = {c['identificados']})"

    _caja(dib, X1, 90, WC, 50, ["Identificación de estudios en bases de datos"], relleno=AZUL_CLARO, tam=19)
    # Identificación
    _caja(dib, X1, 170, WC, 180, ["Registros identificados en:", bases, f"Total (n = {c['identificados']:,})".replace(",", ".")])
    _caja(dib, X2, 170, WC, 180, ["Registros eliminados antes del cribado:",
                                   f"Por filtros automáticos* (n = {c['filtros_automaticos']:,})".replace(",", "."),
                                   f"Duplicados o ya cribados (n = {c['duplicados']:,})".replace(",", ".")])
    _flecha(dib, X1 + WC, 260, X2, 260)
    # Cribado
    _caja(dib, X1, 400, WC, 110, ["Registros cribados", "(título y resumen)", f"(n = {c['cribados']:,})".replace(",", ".")])
    _caja(dib, X2, 400, WC, 110, ["Registros excluidos", f"(n = {c['excluidos_cribado']:,})".replace(",", ".")])
    _flecha(dib, X1 + WC / 2, 350, X1 + WC / 2, 400)
    _flecha(dib, X1 + WC, 455, X2, 455)

    _caja(dib, X1, 560, WC, 110, ["Textos completos buscados", "para su recuperación", f"(n = {c['buscados']})"])
    _caja(dib, X2, 560, WC, 110, ["Textos completos no recuperados", f"(n = {c['no_recuperados']})"])
    _flecha(dib, X1 + WC / 2, 510, X1 + WC / 2, 560)
    _flecha(dib, X1 + WC, 615, X2, 615)

    motivos = c["excluidos_elegibilidad"]
    lineas_m = ["Textos completos excluidos:"] + [f"{m} (n = {n})" for m, n in motivos.items()] if motivos else \
        ["Textos completos excluidos", "(n = 0)"]
    alto_m = max(130, 40 + 30 * len(lineas_m))
    _caja(dib, X1, 720, WC, 130, ["Textos completos evaluados", "para elegibilidad", f"(n = {c['evaluados']})"])
    _caja(dib, X2, 720, WC, alto_m, lineas_m, tam=16)
    _flecha(dib, X1 + WC / 2, 670, X1 + WC / 2, 720)
    _flecha(dib, X1 + WC, 785, X2, 785)
    # Incluidos
    y_inc = max(900, 720 + alto_m + 40)
    _caja(dib, X1, y_inc, WC, 120, ["Estudios incluidos en la revisión", f"(n = {c['incluidos']})"], borde=NARANJA, tam=19)
    _flecha(dib, X1 + WC / 2, 850, X1 + WC / 2, y_inc)

    _banda(img, 40, 170, 60, 180, "Identificación", AZUL)
    _banda(img, 40, 400, 60, 450, "Cribado", AZUL)
    _banda(img, 40, y_inc, 60, 120, "Incluidos", NARANJA)

    nota = ("* Años, tipo de documento, idioma y etapa de publicación aplicados en la base de datos. "
            "Adaptado de Page et al. (2021), declaración PRISMA 2020.")
    fn = _fuente(15)
    dib.text((X1, y_inc + 150), nota, font=fn, fill=(89, 89, 89))
    img = img.crop((0, 0, W, min(H, y_inc + 190)))
    os.makedirs(os.path.dirname(os.path.abspath(ruta_png)) or ".", exist_ok=True)
    img.save(ruta_png, dpi=(200, 200))
    return ruta_png


if __name__ == "__main__":
    prueba = {"por_base": {"Scopus": 693}, "identificados": 693, "filtros_automaticos": 551, "duplicados": 0, "cribados": 142,
              "excluidos_cribado": 129, "buscados": 13, "no_recuperados": 2, "evaluados": 11,
              "excluidos_elegibilidad": {"Aporte menor o redundante": 3}, "incluidos": 8}
    print("OK", dibujar(prueba, sys.argv[1] if len(sys.argv) > 1 else "PRISMA_2020_prueba.png"))
