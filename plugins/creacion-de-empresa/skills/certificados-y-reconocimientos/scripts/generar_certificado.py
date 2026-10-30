"""Certificados, menciones de honor y reconocimientos de una empresa u organización.
Tamaño estándar: A4 horizontal, 297 x 210 mm, a 300 ppp (3508 x 2480 px). El PDF sale a ese tamaño exacto.

Uso:
  python generar_certificado.py --config config.json --lista lista.json --salida emitidos/
  python generar_certificado.py --config config.json --plantillas --salida plantillas/   (una plantilla por tipo)

config.json  (identidad de quien emite; ver ../ejemplos/config_ethos_ia.json)
  marca, razon_social, ciudad, logo, color_primario, color_acento, firmante, cargo_firmante,
  url_verificacion, aviso_pie, quien_otorga, autoridad
lista.json   (una entrada por certificado)
  {"tipo": "mencion" | "capacitacion" | "logro", "codigo": "...", "nombre": "...", "fecha": "...",
   "motivo": "...",                                   (mencion)
   "curso": "...", "horas": 40, "nota": "9,5/10",      (capacitacion)
   "logro": "...",                                     (logro: p. ej. «completar el reto Kernel Cero (31 niveles)»)
   "ciudad": "..."}                                    (opcional; por defecto la de config)
"""
import argparse, json, math, os, sys
import qrcode
from PIL import Image, ImageDraw, ImageFont

W, H = 3508, 2480          # A4 horizontal a 300 ppp
GRIS = "#526373"
ORO_CLARO, ORO, ORO_OSC = (236, 208, 140), (185, 151, 91), (128, 98, 44)
SEG, SEGB, GEO, GEOB = "segoeui.ttf", "segoeuib.ttf", "georgia.ttf", "georgiab.ttf"
FUENTES_DIR = "C:/Windows/Fonts/"

TIPOS = {
    "mencion": dict(titulo="MENCIÓN DE HONOR", art="la", seccion="RECONOCIMIENTO AL MÉRITO"),
    "capacitacion": dict(titulo="CERTIFICADO DE CAPACITACIÓN", art="el", seccion="FORMACIÓN Y CAPACITACIÓN"),
    "logro": dict(titulo="CERTIFICADO DE LOGRO", art="el", seccion="RECONOCIMIENTO DE LOGRO"),
}
C = {}  # configuración activa


def F(nombre, n):
    return ImageFont.truetype(FUENTES_DIR + nombre, n)


def mezcla(a, b, t):
    t = max(0, min(1, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def dorado(ancho, alto):
    g = Image.new("RGB", (ancho, alto))
    px = g.load()
    for x in range(ancho):
        t = x / max(ancho - 1, 1)
        c = mezcla(ORO_OSC, ORO_CLARO, t * 2) if t < 0.5 else mezcla(ORO_CLARO, ORO_OSC, (t - 0.5) * 2)
        for y in range(alto):
            px[x, y] = c
    return g


def texto_dorado(im, y, t, fn):
    d = ImageDraw.Draw(im)
    w = int(d.textlength(t, font=fn))
    m = Image.new("L", (w + 20, fn.size * 2), 0)
    ImageDraw.Draw(m).text((10, 0), t, font=fn, fill=255)
    im.paste(dorado(m.width, m.height), (int(W / 2 - m.width / 2), y), m)


def centrado(d, y, t, fn, fill, x0=0, x1=W, tracking=0):
    if tracking:
        total = sum(d.textlength(ch, font=fn) + tracking for ch in t) - tracking
        x = (x0 + x1) / 2 - total / 2
        for ch in t:
            d.text((x, y), ch, font=fn, fill=fill)
            x += d.textlength(ch, font=fn) + tracking
    else:
        d.text(((x0 + x1) / 2 - d.textlength(t, font=fn) / 2, y), t, font=fn, fill=fill)


def ajustar(d, t, nombre, n, ancho_max, minimo=60):
    while n > minimo and d.textlength(t, font=F(nombre, n)) > ancho_max:
        n -= 4
    return F(nombre, n)


def parrafo(d, t, fn, ancho, fill, y, interlineado=1.5):
    lineas, cur = [], ""
    for p in t.split():
        prueba = (cur + " " + p).strip()
        if d.textlength(prueba, font=fn) <= ancho:
            cur = prueba
        else:
            lineas.append(cur)
            cur = p
    lineas.append(cur)
    for l in lineas:
        centrado(d, y, l, fn, fill)
        y += int(fn.size * interlineado)
    return y


def guilloche(d, x0, y0, x1, y1, amp=16, ciclos=70, color=(214, 190, 140)):
    for fase in (0, math.pi):
        for horizontal in (True, False):
            largo = (x1 - x0) if horizontal else (y1 - y0)
            a, b = [], []
            for i in range(0, int(largo), 4):
                v = amp * math.sin(2 * math.pi * ciclos * i / largo + fase)
                if horizontal:
                    a.append((x0 + i, y0 + v)); b.append((x0 + i, y1 + v))
                else:
                    a.append((x0 + v, y0 + i)); b.append((x1 + v, y0 + i))
            d.line(a, fill=color, width=2)
            d.line(b, fill=color, width=2)


def esquina(d, x, y, sx, sy):
    ang = {(1, 1): (0, 90), (-1, 1): (90, 180), (1, -1): (270, 360), (-1, -1): (180, 270)}[(sx, sy)]
    for r, w in ((150, 6), (118, 3), (86, 3)):
        d.arc([x - r, y - r, x + r, y + r], ang[0], ang[1], fill=ORO, width=w)


def medalla(im, cx, cy, r=225):
    azul, cian = C["color_primario"], C["color_acento"]
    d = ImageDraw.Draw(im)
    d.polygon([(cx - 95, cy), (cx + 95, cy), (cx + 95, cy + 760), (cx, cy + 660), (cx - 95, cy + 760)], fill=azul)
    d.line([(cx - 95, cy), (cx - 95, cy + 760), (cx, cy + 660), (cx + 95, cy + 760), (cx + 95, cy)], fill=cian, width=5)
    for i in range(r, 0, -2):
        d.ellipse([cx - i, cy - i, cx + i, cy + i], fill=mezcla(ORO_OSC, ORO_CLARO, 0.25 + (1 - i / r) * 1.1))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ORO_OSC, width=5)
    d.ellipse([cx - r + 28, cy - r + 28, cx + r - 28, cy + r - 28], outline=(250, 235, 190), width=4)
    d.ellipse([cx - r + 150, cy - r + 150, cx + r - 150, cy + r - 150], fill=azul, outline=ORO_OSC, width=5)
    texto = ("%s · %s · %s · " % (C["razon_social"], C["marca"], C["ciudad"])).upper()
    fn = F(SEGB, 30 if len(texto) < 60 else 24)
    paso, rad = 2 * math.pi / len(texto), r - 88
    capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
    for i, ch in enumerate(texto):
        ang = -math.pi / 2 + i * paso
        w = d.textlength(ch, font=fn)
        c = Image.new("RGBA", (110, 110), (0, 0, 0, 0))
        ImageDraw.Draw(c).text((55 - w / 2, 32), ch, font=fn, fill=(70, 50, 15, 255))
        c = c.rotate(-math.degrees(ang) - 90, resample=Image.BICUBIC, center=(55, 55))
        capa.alpha_composite(c, (int(cx + rad * math.cos(ang) - 55), int(cy + rad * math.sin(ang) - 55)))
    im.paste(capa, (0, 0), capa)
    logo = Image.open(C["logo"]).convert("RGBA")
    logo.thumbnail((200, 200))
    im.paste(logo, (cx - logo.width // 2, cy - logo.height // 2), logo)


def certificado(c):
    t = TIPOS[c["tipo"]]
    azul, cian = C["color_primario"], C["color_acento"]
    ciudad = c.get("ciudad", C["ciudad"])
    im = Image.new("RGB", (W, H), "#fdfdfb")
    marca_agua = Image.open(C["logo"]).convert("RGBA")
    marca_agua.thumbnail((1500, 1500))
    marca_agua.putalpha(marca_agua.getchannel("A").point(lambda v: int(v * 0.05)))
    im.paste(marca_agua, (W // 2 - marca_agua.width // 2, H // 2 - marca_agua.height // 2 + 80), marca_agua)
    d = ImageDraw.Draw(im)
    d.rectangle([110, 110, W - 110, H - 110], outline=ORO, width=7)
    guilloche(d, 150, 150, W - 150, H - 150)
    d.rectangle([205, 205, W - 205, H - 205], outline=ORO, width=3)
    d.rectangle([222, 222, W - 222, H - 222], outline=azul, width=2)
    for x, y, sx, sy in ((222, 222, 1, 1), (W - 222, 222, -1, 1), (222, H - 222, 1, -1), (W - 222, H - 222, -1, -1)):
        esquina(d, x, y, sx, sy)
    # encabezado
    logo = Image.open(C["logo"]).convert("RGBA")
    logo.thumbnail((190, 190))
    marca = ajustar(d, C["marca"].upper(), SEGB, 130, 1500, 70)
    x0 = int(W / 2 - (logo.width + 40 + d.textlength(C["marca"].upper(), font=marca)) / 2)
    im.paste(logo, (x0, 290), logo)
    d.text((x0 + logo.width + 40, 298), C["marca"].upper(), font=marca, fill=azul)
    centrado(d, 478, ("%s  ·  %s" % (C["razon_social"], C["ciudad"])).upper(), F(SEG, 38), GRIS, tracking=6)
    texto_dorado(im, 600, t["seccion"], F(GEOB, 84))
    d = ImageDraw.Draw(im)
    centrado(d, 750, "En nombre de %s y por autoridad de %s, hace notorio." % (C["quien_otorga"], C["autoridad"]), F(SEG, 44), azul)
    centrado(d, 810, "Que:", F(SEG, 44), azul)
    nombre = c["nombre"].upper()
    centrado(d, 940, nombre, ajustar(d, nombre, GEO, 140, W - 900), azul)
    if c["tipo"] == "mencion":
        cuerpo = "En reconocimiento a %s, se le otorga %s" % (c["motivo"], t["art"])
    elif c["tipo"] == "logro":
        cuerpo = "Ha logrado %s, por lo que se le otorga %s" % (c["logro"], t["art"])
    else:
        extra = ", con una duración de %s horas" % c["horas"] if c.get("horas") else ""
        nota = " y una calificación de %s" % c["nota"] if c.get("nota") else ""
        cuerpo = "Ha aprobado el curso «%s»%s%s, por lo que se le otorga %s" % (c["curso"], extra, nota, t["art"])
    y = parrafo(d, cuerpo, F(SEG, 52), 2150, azul, 1210)
    centrado(d, y + 20, t["titulo"], ajustar(d, t["titulo"], GEOB, 128, W - 900), azul)
    y = y + 215
    y = parrafo(d, "En tal virtud, %s le guardará las consideraciones que corresponden. Dado y firmado en la ciudad de %s, el %s."
                % (C["quien_otorga"], ciudad, c["fecha"]), F(SEG, 44), 2400, GRIS, y + 30)
    centrado(d, y + 40, "Registro de certificados de %s · Folio %s" % (C["marca"], c["codigo"]), F(SEG, 28), GRIS, tracking=2)
    medalla(im, W - 560, 470, 225)
    d = ImageDraw.Draw(im)
    fx0, fx1 = 520, 1480
    d.line([fx0, 2050, fx1, 2050], fill=azul, width=3)
    centrado(d, 2068, C["firmante"], F(SEGB, 44), azul, fx0, fx1)
    centrado(d, 2126, C["cargo_firmante"], F(SEG, 34), GRIS, fx0, fx1)
    q = qrcode.QRCode(box_size=10, border=1, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(C["url_verificacion"].rstrip("/") + "/" + c["codigo"])
    q.make(fit=True)
    qi = q.make_image(fill_color=azul, back_color="white").convert("RGB").resize((300, 300), Image.NEAREST)
    qx = W - 1230
    im.paste(qi, (qx, 1860))
    d.rectangle([qx - 8, 1852, qx + 308, 2168], outline="#d5e0ea", width=3)
    d.text((qx + 350, 1905), "CÓDIGO", font=F(SEGB, 28), fill=GRIS)
    d.text((qx + 350, 1945), c["codigo"], font=F(SEGB, 38), fill=azul)
    d.text((qx + 350, 2010), "Verifica este documento en", font=F(SEG, 30), fill=GRIS)
    d.text((qx + 350, 2052), C["url_verificacion"].replace("https://", "").replace("www.", "").rstrip("/"), font=F(SEGB, 28), fill="#0b5f75")
    centrado(d, H - 265, C["aviso_pie"], F(SEG, 26), GRIS)
    return im


def cargar_config(ruta):
    cfg = json.load(open(ruta, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(ruta))
    cfg.setdefault("marca", cfg.get("razon_social", "Empresa"))
    cfg.setdefault("razon_social", cfg["marca"])
    cfg.setdefault("ciudad", "Cuenca, Ecuador")
    cfg.setdefault("color_primario", "#05111e")
    cfg.setdefault("color_acento", "#04ebff")
    cfg.setdefault("quien_otorga", cfg["marca"])
    cfg.setdefault("autoridad", "su Gerencia General")
    cfg.setdefault("aviso_pie", "Certificado emitido por %s. No constituye título académico ni certificación de otra entidad." % cfg["marca"])
    for k in ("firmante", "cargo_firmante", "logo", "url_verificacion"):
        if k not in cfg:
            sys.exit("Falta '%s' en %s" % (k, ruta))
    if not os.path.isabs(cfg["logo"]):
        cfg["logo"] = os.path.join(base, cfg["logo"])
    return cfg


def plantillas():
    return [
        dict(tipo="mencion", codigo="CERT-0001", nombre="Nombre y Apellido", fecha="__ de ______ de ____",
             motivo="su compromiso, excelencia técnica y aporte sobresaliente"),
        dict(tipo="capacitacion", codigo="CERT-0001", nombre="Nombre y Apellido", fecha="__ de ______ de ____",
             curso="Nombre del curso", horas=40, nota="10/10"),
        dict(tipo="logro", codigo="CERT-0001", nombre="Nombre y Apellido", fecha="__ de ______ de ____",
             logro="el reto completo"),
    ]


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--config", required=True)
    a.add_argument("--lista")
    a.add_argument("--plantillas", action="store_true")
    a.add_argument("--salida", default="certificados")
    a = a.parse_args()
    C.update(cargar_config(a.config))
    items = plantillas() if a.plantillas else json.load(open(a.lista, encoding="utf-8"))
    os.makedirs(a.salida, exist_ok=True)
    for c in items:
        im = certificado(c)
        base = os.path.join(a.salida, "%s_%s" % (c["tipo"], c["codigo"]))
        im.save(base + ".png", dpi=(300, 300))
        im.save(base + ".pdf", resolution=300)   # 3508 x 2480 px a 300 ppp = 297 x 210 mm
        print("ok", base)


if __name__ == "__main__":
    main()
