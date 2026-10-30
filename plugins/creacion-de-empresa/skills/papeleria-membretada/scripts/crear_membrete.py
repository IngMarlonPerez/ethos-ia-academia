#!/usr/bin/env python
"""Crea la hoja membretada (.docx) de una empresa a partir de empresa.json y su logotipo.

El membrete lleva: encabezado con logotipo a la izquierda y razón social / RUC / ciudad a la derecha, barra de acento,
marca de agua (isotipo muy tenue, detrás del texto), pie con dirección, teléfono, correo y web con íconos, el isotipo a
la derecha y «Página X de Y». Todo el cuerpo es un ejemplo editable (carta con fecha, texto y firma).

Uso:
    python crear_membrete.py --empresa empresa.json --logo logo_horizontal.png --isotipo isotipo.png --salida Membrete.docx
    python crear_membrete.py --ejemplo --logo logo.png --salida prueba.docx          # con datos de una empresa ficticia

Sólo requiere Pillow. Las imágenes deben ser PNG con fondo transparente (el logotipo de color sobre blanco).
El .docx resultante abre y se edita en Word; para PDF usar pdf_word.py o exportar_pdf_word.ps1 de esta misma skill.
"""
import argparse
import io
import json
import os
import re
import sys
import zipfile
from xml.sax.saxutils import escape

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(AQUI, "..", "assets", "membrete_base.docx")

EJEMPLO = {
    "razon_social": "EMPRESA EJEMPLO S.A.S.",
    "nombre_comercial": "Ejemplo",
    "ruc": "0999999999001",
    "domicilio": {"ciudad": "Cuenca", "provincia": "Azuay", "pais": "Ecuador"},
    "contacto": {"telefono": "+593 99 999 9999", "correo": "hola@ejemplo.ec", "web": "www.ejemplo.ec"},
    "representante": {"nombre": "Nombre Apellido", "cargo": "Gerente General"},
    "marca": {"color_primario": "0A1A2E", "color_acento": "00D6FB", "color_secundario": "5B6B72", "color_texto": "0A0F1A"},
}

# colores que trae la base y que se reemplazan por los de la marca
BASE_PRIMARIO, BASE_SECUNDARIO, BASE_TEXTO = "0A1A2E", "5B6B72", "0A0F1A"


def _hex(c, defecto):
    c = (c or defecto).lstrip("#").upper()
    if not re.fullmatch(r"[0-9A-F]{6}", c):
        raise SystemExit(f"Color inválido: {c} (se espera RRGGBB)")
    return c


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _png(im):
    b = io.BytesIO()
    im.save(b, "PNG", optimize=True)
    return b.getvalue()


def _abrir(ruta):
    im = Image.open(ruta).convert("RGBA")
    return im


def _limitar(im, ancho):
    if im.width > ancho:
        im = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
    return im


def barra(acento, primario):
    """Barra de 3000×18 px: acento al inicio y degradado hacia el color primario."""
    a, p = _rgb(acento), _rgb(primario)
    im = Image.new("RGB", (3000, 18))
    px = im.load()
    for x in range(3000):
        t = min(1.0, max(0.0, (x / 3000 - 0.33) / 0.33))
        c = tuple(round(a[i] + (p[i] - a[i]) * t) for i in range(3))
        for y in range(18):
            px[x, y] = c
    return _png(im)


def icono_recoloreado(blob, color):
    im = Image.open(io.BytesIO(blob)).convert("RGBA")
    r, g, b = _rgb(color)
    solido = Image.new("RGBA", im.size, (r, g, b, 255))
    solido.putalpha(im.getchannel("A"))
    return _png(solido)


def marca_de_agua(iso, opacidad=0.055):
    """Isotipo muy tenue aplanado sobre blanco y con pocos colores, para que el PDF pese poco."""
    iso = _limitar(iso, 700)
    a = iso.getchannel("A").point(lambda v: int(v * opacidad))
    fondo = Image.new("RGB", iso.size, (255, 255, 255))
    fondo.paste(iso.convert("RGB"), mask=a)
    return _png(fondo.quantize(colors=48, method=Image.Quantize.MEDIANCUT))


def _cambiar_extent(xml, rid, cx=None, cy=None):
    """Cambia el tamaño (EMU) del dibujo que usa la relación rid."""
    for m in re.finditer(r"<w:drawing>.*?</w:drawing>", xml, flags=re.S):
        bloque = m.group(0)
        if f'r:embed="{rid}"' in bloque:
            nuevo = re.sub(r'(<(?:wp:extent|a:ext) )cx="\d+" cy="\d+"', rf'\1cx="{cx}" cy="{cy}"', bloque)
            return xml.replace(bloque, nuevo)
    return xml


def _extent(xml, rid):
    for m in re.finditer(r"<w:drawing>.*?</w:drawing>", xml, flags=re.S):
        if f'r:embed="{rid}"' in m.group(0):
            e = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"', m.group(0))
            return int(e.group(1)), int(e.group(2))
    return None


def _quitar_dibujo(xml, rid):
    """Elimina el <w:r> que contiene el dibujo rid (y su alternativa en el mismo párrafo)."""
    for m in re.finditer(r"<w:r>(?:(?!</w:r>).)*?</w:r>", xml, flags=re.S):
        if f'r:embed="{rid}"' in m.group(0):
            return xml.replace(m.group(0), "", 1)
    return xml


def _quitar_contacto(xml, rid):
    """Quita ícono + texto + espacio posterior de un dato de contacto del pie."""
    runs = list(re.finditer(r"<w:r>(?:(?!</w:r>).)*?</w:r>", xml, flags=re.S))
    for i, m in enumerate(runs):
        if f'r:embed="{rid}"' in m.group(0):
            quitar = [m.group(0)]
            if i + 1 < len(runs):
                quitar.append(runs[i + 1].group(0))
            if i + 2 < len(runs) and not re.sub(r"<[^>]+>", "", runs[i + 2].group(0)).strip():
                quitar.append(runs[i + 2].group(0))
            for q in quitar:
                xml = xml.replace(q, "", 1)
            return xml
    return xml


def crear_membrete(empresa, logo, salida, isotipo=None, marca_agua=None):
    dom = empresa.get("domicilio", {})
    con = empresa.get("contacto", {})
    rep = empresa.get("representante", {})
    marca = empresa.get("marca", {})
    primario = _hex(marca.get("color_primario"), BASE_PRIMARIO)
    acento = _hex(marca.get("color_acento"), "00D6FB")
    secundario = _hex(marca.get("color_secundario"), BASE_SECUNDARIO)
    texto = _hex(marca.get("color_texto"), BASE_TEXTO)

    razon = empresa["razon_social"]
    comercial = empresa.get("nombre_comercial") or ""
    ciudad = dom.get("ciudad", "")
    pais = dom.get("pais", "Ecuador")
    valores = {
        "RAZON_SOCIAL": razon,
        "NOMBRE_MARCA": comercial or razon,
        "RUC": empresa.get("ruc", ""),
        "CIUDAD": ciudad,
        "CIUDAD_PAIS": f"{ciudad} – {pais}" if ciudad else pais,
        "DIRECCION": dom.get("direccion_membrete") or (f"{ciudad}, {pais}" if ciudad else pais),
        "TELEFONO": con.get("telefono", ""),
        "CORREO": con.get("correo", ""),
        "WEB": con.get("web", ""),
        "REPRESENTANTE": rep.get("nombre", "[Nombre del representante]"),
        "CARGO": rep.get("cargo", "Gerente General"),
        "PIE_MEDIO": (f"   ·   Nombre comercial: {comercial}   ·   "
                      if comercial and comercial.upper() != razon.upper() else "   ·   "),
    }

    logo_im = _limitar(_abrir(logo), 2400)
    iso_im = _limitar(_abrir(isotipo), 1000) if isotipo else None
    wm_fuente = _abrir(marca_agua) if marca_agua else iso_im

    zin = zipfile.ZipFile(BASE)
    medios = {
        "word/media/logo_horizontal.png": _png(logo_im),
        "word/media/barra_header.png": barra(acento, primario),
        "word/media/barra_footer.png": barra(acento, primario),
    }
    if iso_im is not None:
        medios["word/media/isotipo.png"] = _png(_limitar(iso_im, 320))
    if wm_fuente is not None:
        medios["word/media/marca_agua.png"] = marca_de_agua(wm_fuente)
    for ico in ("ubicacion", "telefono", "correo", "web"):
        n = f"word/media/ico_{ico}.png"
        medios[n] = icono_recoloreado(zin.read(n), acento)

    os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)
    zout = zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        datos = zin.read(item.filename)
        n = item.filename
        if n in medios:
            datos = medios[n]
        elif n in ("word/header1.xml", "word/footer1.xml", "word/document.xml", "docProps/core.xml"):
            x = datos.decode("utf-8")
            if n == "word/header1.xml":
                # el logotipo conserva su proporción; la altura base es la del membrete original
                cx0, cy0 = _extent(x, "rIdLogo")
                ratio = logo_im.width / logo_im.height
                cy = cy0
                cx = round(cy * ratio)
                if cx > 3000000:
                    cx, cy = 3000000, round(3000000 / ratio)
                x = _cambiar_extent(x, "rIdLogo", cx, cy)
                if wm_fuente is None:
                    x = _quitar_dibujo(x, "rIdWm")
                else:
                    r = wm_fuente.width / wm_fuente.height
                    w = 3240000
                    h = round(w / r)
                    if h > 4300000:
                        h, w = 4300000, round(4300000 * r)
                    x = _cambiar_extent(x, "rIdWm", w, h)
            if n == "word/footer1.xml":
                if iso_im is None:
                    x = _quitar_dibujo(x, "rIdCube")
                else:
                    cx0, cy0 = _extent(x, "rIdCube")
                    r = iso_im.width / iso_im.height
                    x = _cambiar_extent(x, "rIdCube", round(cy0 * r), cy0)
                for clave, rid in (("DIRECCION", "rIdIcoUbi"), ("TELEFONO", "rIdIcoTel"),
                                   ("CORREO", "rIdIcoMail"), ("WEB", "rIdIcoWeb")):
                    if not valores[clave]:
                        x = _quitar_contacto(x, rid)
            for k, v in valores.items():
                x = x.replace("{{" + k + "}}", escape(v))
            if n != "docProps/core.xml":
                x = x.replace(BASE_PRIMARIO, primario).replace(BASE_SECUNDARIO, secundario).replace(BASE_TEXTO, texto)
            datos = x.encode("utf-8")
        zout.writestr(item, datos)
    zout.close()
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--empresa", help="empresa.json con los datos de la empresa")
    ap.add_argument("--ejemplo", action="store_true", help="usa los datos de una empresa ficticia")
    ap.add_argument("--logo", required=True, help="logotipo horizontal (PNG con fondo transparente)")
    ap.add_argument("--isotipo", help="símbolo solo (PNG transparente): pie y marca de agua")
    ap.add_argument("--marca-agua", help="imagen distinta para la marca de agua (por defecto, el isotipo)")
    ap.add_argument("--salida", required=True)
    a = ap.parse_args()
    if a.ejemplo:
        empresa = EJEMPLO
    elif a.empresa:
        empresa = json.load(open(a.empresa, encoding="utf-8"))
    else:
        sys.exit("Indica --empresa empresa.json o --ejemplo")
    print("Membrete creado:", crear_membrete(empresa, a.logo, a.salida, a.isotipo, a.marca_agua))


if __name__ == "__main__":
    main()
