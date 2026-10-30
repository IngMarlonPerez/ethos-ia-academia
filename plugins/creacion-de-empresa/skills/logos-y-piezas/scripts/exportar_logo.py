#!/usr/bin/env python
"""Convierte el logotipo oficial en el juego de archivos que necesita una empresa: web, redes, papelería y documentos.

Parte de UN logotipo horizontal (símbolo a la izquierda + nombre) y produce, en la carpeta de salida:
  logo-color / logo-negro / logo-blanco .png        (fondo transparente; el negro es para sellos e impresión de 1 tinta)
  isotipo-color / isotipo-negro / isotipo-blanco .png   (sólo el símbolo; se separa solo si hay un hueco entre símbolo y texto)
  favicon-16/32/48.png, favicon.ico, apple-touch-icon.png (180), icon-192.png, icon-512.png
  foto-perfil-800.png (WhatsApp, Facebook, YouTube, LinkedIn), og-1200x630.png (vista previa al compartir el enlace)
  portada-facebook-820x312.png, portada-linkedin-1584x396.png, portada-youtube-2560x1440.png (contenido en la zona segura)
  paleta-swatch.png                                  (muestra de los colores de marca para imprenta)

Fuentes aceptadas (--fuente):
  * PNG/JPG con el logotipo sobre fondo BLANCO (--fondo blanco) o ya transparente (--fondo transparente)
  * PDF o .ai compatible con PDF: --mesa N elige el tablero (1 = primero). Usar el tablero de «color sobre blanco».
Para convertir el blanco en transparencia se usa «color a alfa»: si el logotipo tiene partes blancas internas se vuelven
transparentes; en ese caso conviene pedir al diseñador el PNG con transparencia real y usar --fondo transparente.

Uso:
    python exportar_logo.py --fuente "Logo.ai" --mesa 3 --fondo blanco --salida logos/ --empresa empresa.json
"""
import argparse
import io
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def cargar(fuente, mesa, ancho=3200):
    if fuente.lower().endswith((".pdf", ".ai")):
        import pymupdf
        with pymupdf.open(fuente, filetype="pdf") as d:
            if not 1 <= mesa <= len(d):
                sys.exit(f"El archivo tiene {len(d)} tablero(s); --mesa {mesa} no existe")
            p = d[mesa - 1]
            pm = p.get_pixmap(matrix=pymupdf.Matrix(ancho / p.rect.width, ancho / p.rect.width), alpha=False)
            return Image.open(io.BytesIO(pm.tobytes("png"))).convert("RGBA")
    return Image.open(fuente).convert("RGBA")


def blanco_a_alfa(im):
    """Color a alfa sobre blanco: recupera el color real y la transparencia de cada píxel."""
    a = np.asarray(im.convert("RGB"), dtype=np.float64) / 255.0
    alfa = 1.0 - a.min(axis=2)
    seguro = np.where(alfa > 1e-3, alfa, 1.0)[..., None]
    rgb = np.clip((a - (1.0 - alfa)[..., None]) / seguro, 0, 1)
    rgb[alfa <= 1e-3] = 0
    out = np.dstack([rgb, alfa])
    return Image.fromarray((out * 255).round().astype(np.uint8), "RGBA")


def recortar(im, margen=0.0, umbral=8):
    caja = im.getchannel("A").point(lambda v: 255 if v > umbral else 0).getbbox()
    if not caja:
        sys.exit("El logotipo quedó vacío: revisa --fondo y --mesa")
    im = im.crop(caja)
    m = round(max(im.size) * margen)
    if m:
        lienzo = Image.new("RGBA", (im.width + 2 * m, im.height + 2 * m), (0, 0, 0, 0))
        lienzo.paste(im, (m, m))
        im = lienzo
    return im


def separar_isotipo(im, umbral=8, hueco_min=0.012):
    """Símbolo = lo que hay antes del primer hueco vertical transparente de al menos hueco_min × ancho."""
    alfa = np.asarray(im.getchannel("A")) > umbral
    col = alfa.any(axis=0)
    minimo = max(3, round(im.width * hueco_min))
    i, n = 0, len(col)
    while i < n and not col[i]:
        i += 1
    inicio = i
    while i < n:
        if not col[i]:
            j = i
            while j < n and not col[j]:
                j += 1
            if j - i >= minimo and j < n:
                return recortar(im.crop((inicio, 0, i, im.height)))
            i = j
        else:
            i += 1
    return None


def mono(im, rgb):
    out = Image.new("RGBA", im.size, rgb + (255,))
    out.putalpha(im.getchannel("A"))
    return out


def ajustar(im, ancho=None, alto=None):
    r = min((ancho or 1e9) / im.width, (alto or 1e9) / im.height)
    return im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)


def sobre(fondo_rgb, tam, im, ocupa=0.6, pos=(0.5, 0.5)):
    lienzo = Image.new("RGB", tam, fondo_rgb)
    a = ajustar(im, round(tam[0] * ocupa), round(tam[1] * ocupa))
    lienzo.paste(a, (round((tam[0] - a.width) * pos[0]), round((tam[1] - a.height) * pos[1])), a)
    return lienzo


def hexrgb(h, d):
    h = (h or d).lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fuente", required=True)
    ap.add_argument("--mesa", type=int, default=1)
    ap.add_argument("--fondo", choices=["blanco", "transparente"], default="blanco")
    ap.add_argument("--empresa", help="empresa.json para los colores de marca")
    ap.add_argument("--color-fondo", help="color de fondo de portadas y foto de perfil (RRGGBB); por defecto el primario de la marca")
    ap.add_argument("--salida", required=True)
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    marca = json.load(open(a.empresa, encoding="utf-8")).get("marca", {}) if a.empresa else {}
    fondo = hexrgb(a.color_fondo or marca.get("color_primario"), "0A0F1A")
    acento = hexrgb(marca.get("color_acento"), "00D6FB")
    os.makedirs(a.salida, exist_ok=True)
    out = lambda n: os.path.join(a.salida, n)

    im = cargar(a.fuente, a.mesa)
    if a.fondo == "blanco":
        im = blanco_a_alfa(im)
    logo = recortar(im, 0.01)
    iso = separar_isotipo(logo)
    if iso is None:
        print("Aviso: no se encontró un hueco entre símbolo y texto; no se genera el isotipo. "
              "Entrega un isotipo aparte si el logotipo no es horizontal.")

    variantes = {"logo": logo}
    if iso is not None:
        variantes["isotipo"] = iso
    for nombre, v in variantes.items():
        ajustar(v, 2400, 2400).save(out(f"{nombre}-color.png"), optimize=True)
        ajustar(mono(v, (0, 0, 0)), 2400, 2400).save(out(f"{nombre}-negro.png"), optimize=True)
        ajustar(mono(v, (255, 255, 255)), 2400, 2400).save(out(f"{nombre}-blanco.png"), optimize=True)

    simbolo = iso if iso is not None else logo
    simbolo_blanco = mono(simbolo, (255, 255, 255))
    logo_blanco = mono(logo, (255, 255, 255))
    # íconos del sitio: símbolo en color sobre transparente
    for n in (16, 32, 48):
        c = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        s = ajustar(simbolo, round(n * 0.94), round(n * 0.94))
        c.paste(s, ((n - s.width) // 2, (n - s.height) // 2), s)
        c.save(out(f"favicon-{n}.png"))
    Image.open(out("favicon-48.png")).save(out("favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    # sobre fondo oscuro el símbolo va en blanco (el de color se pierde); sobre fondo claro, en color
    luminancia = (0.299 * fondo[0] + 0.587 * fondo[1] + 0.114 * fondo[2]) / 255
    sim_fondo = simbolo if luminancia > 0.5 else simbolo_blanco
    for n, nombre in ((180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png")):
        sobre(fondo, (n, n), sim_fondo, 0.7).save(out(nombre))
    sobre(fondo, (800, 800), sim_fondo, 0.62).save(out("foto-perfil-800.png"))

    def portada(nombre, tam, seguro):
        lienzo = Image.new("RGB", tam, fondo)
        d = ImageDraw.Draw(lienzo)
        d.rectangle([0, tam[1] - max(4, tam[1] // 90), tam[0], tam[1]], fill=acento)
        lg = ajustar(logo if luminancia > 0.5 else logo_blanco, round(seguro[0] * 0.8), round(seguro[1] * 0.7))
        lienzo.paste(lg, ((tam[0] - lg.width) // 2, (tam[1] - lg.height) // 2), lg)
        lienzo.save(out(nombre))

    portada("portada-facebook-820x312.png", (820, 312), (820, 312))
    portada("portada-linkedin-1584x396.png", (1584, 396), (1584, 396))
    portada("portada-youtube-2560x1440.png", (2560, 1440), (1546, 423))   # zona segura que no se recorta en TV ni móvil
    portada("og-1200x630.png", (1200, 630), (1000, 400))

    # paleta
    cols = [("Fondo", fondo), ("Acento", acento), ("Primario", hexrgb(marca.get("color_primario"), "0A1A2E")),
            ("Secundario", hexrgb(marca.get("color_secundario"), "5B6B72"))]
    sw = Image.new("RGB", (len(cols) * 300, 360), (255, 255, 255))
    d = ImageDraw.Draw(sw)
    for i, (n, c) in enumerate(cols):
        d.rectangle([i * 300 + 10, 10, i * 300 + 290, 250], fill=c)
        d.text((i * 300 + 14, 262), n, fill=(30, 40, 50))
        d.text((i * 300 + 14, 290), "#%02X%02X%02X" % c, fill=(30, 40, 50))
    sw.save(out("paleta-swatch.png"))
    print("Archivos en", os.path.abspath(a.salida))
    for f in sorted(os.listdir(a.salida)):
        print(" ", f, Image.open(out(f)).size)


if __name__ == "__main__":
    main()
