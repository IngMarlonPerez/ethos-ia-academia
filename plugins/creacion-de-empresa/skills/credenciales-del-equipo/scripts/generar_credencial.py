"""Genera credenciales digitales (PNG y PDF) desde empresa.json y personas.json."""
import argparse
import json
import os
import sys

import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1100, 1800
FUENTES = [("C:/Windows/Fonts/segoeui{}.ttf", "b"), ("/usr/share/fonts/truetype/dejavu/DejaVuSans{}.ttf", "-Bold")]


def hexc(v, defecto):
    v = (v or defecto).lstrip("#")
    return "#" + (v if len(v) == 6 else defecto)


def fuente(tam, bold, ruta):
    if ruta:
        return ImageFont.truetype(ruta, tam)
    for patron, negrita in FUENTES:
        try:
            return ImageFont.truetype(patron.format(negrita if bold else ""), tam)
        except OSError:
            continue
    return ImageFont.load_default()


def credencial(p, e, logo, ruta_fuente):
    def f(n, b=False):
        return fuente(n, b, ruta_fuente)

    marca = e.get("marca", {})
    azul = hexc(marca.get("color_primario"), "05111E")
    cian = hexc(marca.get("color_acento"), "04EBFF")
    suave, fondo = "#526373", "#f6f9fc"
    nombre = e.get("nombre_comercial") or e.get("razon_social", "EMPRESA")
    razon = e.get("razon_social", nombre)
    ciudad = e.get("ciudad", "")
    web = (e.get("sitio_web") or "").replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")

    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)

    def tw(t, fn):
        return d.textlength(t, font=fn)

    def centrado(y, t, fn, fill, x0=0, x1=W):
        d.text(((x0 + x1) / 2 - tw(t, fn) / 2, y), t, font=fn, fill=fill)

    # Cabecera
    d.rectangle([0, 0, W, 232], fill=azul)
    x_txt = 60
    if logo and os.path.exists(logo):
        lg = Image.open(logo).convert("RGBA")
        lg.thumbnail((120, 120))
        im.paste(lg, (60, 52), lg)
        x_txt = 200
    d.text((x_txt, 46), nombre.upper(), font=f(76 if len(nombre) <= 12 else 56, True), fill="#eaf2f8")
    d.text((x_txt + 2, 142), razon + (" · " + ciudad.upper() if ciudad else ""), font=f(26), fill="#93aabb")
    cargo = p["cargo"]
    d.text((W - 60 - tw(cargo, f(34, True)), 70), cargo, font=f(34, True), fill=cian)
    d.text((W - 60 - tw("CREDENCIAL OFICIAL", f(24, True)), 124), "CREDENCIAL OFICIAL", font=f(24, True), fill="#eaf2f8")
    d.rectangle([0, 232, W, 244], fill=cian)

    # Foto circular
    dia = 300
    ft = ImageOps.fit(Image.open(p["foto"]).convert("RGB"), (dia, dia), centering=(0.5, 0.25))
    m = Image.new("L", (dia * 3, dia * 3), 0)
    ImageDraw.Draw(m).ellipse([0, 0, dia * 3, dia * 3], fill=255)
    m = m.resize((dia, dia), Image.LANCZOS)
    cx, cy, r = W // 2, 420, dia // 2
    d.ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], fill=cian)
    d.ellipse([cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8], fill=azul)
    im.paste(ft, (cx - r, cy - r), m)

    # Nombre y etiqueta
    y = 610
    for linea in p["nombre"]:
        centrado(y, linea, f(64, True), azul)
        y += 76
    et, fe = p["etiqueta"], f(32, True)
    w = tw(et, fe) + 60
    d.rounded_rectangle([W / 2 - w / 2, y + 16, W / 2 + w / 2, y + 74], radius=29, fill=azul)
    centrado(y + 22, et, fe, cian)

    # Tabla de datos
    filas, t0, fh = p["filas"], y + 118, 74
    d.rounded_rectangle([70, t0, W - 70, t0 + fh * len(filas) + 14], radius=26, fill=fondo, outline="#d5e0ea", width=2)
    for i, (k, v) in enumerate(filas):
        yy = t0 + 7 + i * fh
        d.text((100, yy + 20), k, font=f(28, True), fill=suave)
        d.text((W - 100 - tw(v, f(30, True)), yy + 19), v, font=f(30, True), fill=azul)
        if i < len(filas) - 1:
            d.line([96, yy + fh, W - 96, yy + fh], fill="#dde6ee", width=2)

    # QR
    q = qrcode.QRCode(box_size=10, border=1, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(p["url"])
    q.make(fit=True)
    qi = q.make_image(fill_color=azul, back_color="white").convert("RGB").resize((330, 330), Image.NEAREST)
    qy = t0 + fh * len(filas) + 52
    d.rounded_rectangle([W / 2 - 220, qy, W / 2 + 220, qy + 400], radius=26, fill="white", outline="#d5e0ea", width=2)
    im.paste(qi, (W // 2 - 165, qy + 24))
    centrado(qy + 366, "Escanea para verificar", f(22, True), suave, W / 2 - 220, W / 2 + 220)

    # Pie
    d.rectangle([0, H - 80, W, H], fill="#0a1b2b")
    d.text((50, H - 56), "CREDENCIAL DIGITAL " + nombre.upper(), font=f(26, True), fill="#93aabb")
    if web:
        d.text((W - 50 - tw(web, f(28, True)), H - 57), web, font=f(28, True), fill=cian)
    return im


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--empresa")
    a.add_argument("--personas", required=True)
    a.add_argument("--logo")
    a.add_argument("--fuente")
    a.add_argument("--salida", default="credenciales")
    a = a.parse_args()
    e = json.load(open(a.empresa, encoding="utf-8")) if a.empresa else {}
    if not e:
        print("AVISO: sin empresa.json; se usan valores por defecto.", file=sys.stderr)
    base = os.path.dirname(os.path.abspath(a.personas))
    os.makedirs(a.salida, exist_ok=True)
    for p in json.load(open(a.personas, encoding="utf-8")):
        if not os.path.isabs(p["foto"]):
            p["foto"] = os.path.join(base, p["foto"])
        im = credencial(p, e, a.logo, a.fuente)
        im.save(os.path.join(a.salida, "credencial_%s.png" % p["id"]))
        im.save(os.path.join(a.salida, "credencial_%s.pdf" % p["id"]), resolution=150)
        print("ok", p["id"])


if __name__ == "__main__":
    main()
