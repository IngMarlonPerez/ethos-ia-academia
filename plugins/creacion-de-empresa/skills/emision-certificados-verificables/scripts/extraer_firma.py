"""Convierte la foto o escaneo de una firma manuscrita (tinta azul o negra sobre papel) en un PNG con fondo transparente.

Uso:  python extraer_firma.py firma_foto.png firma-fundador.png [--tinta azul|negra] [--ancho 1300]
Solo debe usarse con la firma de la propia persona y con su autorización. Es una firma VISUAL: no tiene validez de firma electrónica.
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("entrada"); ap.add_argument("salida")
ap.add_argument("--tinta", choices=["azul", "negra"], default="azul")
ap.add_argument("--ancho", type=int, default=1300, help="ancho aproximado de salida en px")
a = ap.parse_args()

src = Image.open(a.entrada).convert("RGB"); px = np.array(src).astype(float)
if a.tinta == "azul":   # el fondo del papel es gris/neutro; la tinta tiene mucho más azul que rojo/verde
    señal = px[:, :, 2] - (px[:, :, 0] + px[:, :, 1]) / 2; base, rango, color = 30, 150, (14, 32, 205)
else:                   # tinta negra: oscuridad relativa al fondo
    gris = px.mean(axis=2); fondo = np.percentile(gris, 85); señal = fondo - gris; base, rango, color = 35, 110, (10, 14, 24)
alfa = np.clip((señal - base) / rango, 0, 1)
al = Image.fromarray((alfa * 255).astype("uint8"), "L")
k = max(2, round(a.ancho / al.width))
al = al.resize((al.width * k, al.height * k), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.32 * k))
al = al.point(lambda v: 0 if v < 40 else min(255, int((v - 40) * 1.6)))
out = Image.new("RGBA", al.size, color + (0,)); out.putalpha(al)
bb = out.getbbox()
if not bb: raise SystemExit("No se detectó tinta: prueba --tinta negra o una foto con más contraste.")
out = out.crop((max(0, bb[0] - 12), max(0, bb[1] - 12), bb[2] + 12, bb[3] + 12)); out.save(a.salida, optimize=True)
print("ok", a.salida, out.size)
