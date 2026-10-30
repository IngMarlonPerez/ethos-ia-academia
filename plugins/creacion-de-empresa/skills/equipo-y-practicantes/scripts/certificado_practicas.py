#!/usr/bin/env python
"""Certificado de prácticas preprofesionales de la empresa, sobre su hoja membretada, para firma electrónica del representante legal.

Un párrafo de certificación + ficha + línea de firma. La redacción es neutra (no se infiere el género). El certificado NO se firma
aquí: queda con la línea de firma para que el representante firme con su firma electrónica.

Uso:
    python certificado_practicas.py --empresa empresa.json --membrete Membrete.docx --datos practicante.json --salida Certificado.docx [--pdf]

practicante.json:
    {"nombre": "Nombre Apellido", "identificacion": "0000000000", "carrera": "Ingeniería en Tecnologías de la Información",
     "universidad": "Universidad Estatal de Milagro – UNEMI", "itinerario": "Prácticas Laborales I", "area": "soporte técnico",
     "inicio": "21 de septiembre de 2026", "fin": "6 de octubre de 2026", "horas": 96,
     "resumen": "soporte técnico y administración de sistemas", "tutor": "Nombre del tutor profesional", "lugar_fecha": "Cuenca, 10 de octubre de 2026"}

Reglas: la fecha del certificado es igual o posterior a la de fin de la práctica (si es futura, déjala como campo por confirmar);
el representante firma solo cuando confirma que se cumplieron las horas.
"""
import argparse
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "papeleria-membretada", "scripts"))
from mdoc import MDoc, _p, _run, set_marca  # noqa: E402
import mdoc  # noqa: E402


def generar(e, d, membrete, destino, pdf=False):
    m = e.get("marca", {})
    set_marca(m.get("color_primario"), m.get("color_acento"), m.get("color_secundario"))
    rep = e["representante"]
    comercial = e.get("nombre_comercial")
    marca_txt = f" (nombre comercial **{comercial}**)" if comercial and comercial.upper() != e["razon_social"].upper() else ""
    ciudad = e.get("domicilio", {}).get("ciudad", "")
    doc = MDoc(template=membrete)
    doc.p(d.get("lugar_fecha") or "[[ciudad, fecha]]", jc="right", after=200)
    doc.title("CERTIFICADO DE PRÁCTICAS PREPROFESIONALES", f"Itinerario: {d['itinerario']}")
    doc.p(f"La Gerencia de **{e['razon_social']}**{marca_txt}, con domicilio en {ciudad}, **CERTIFICA** que **{d['nombre'].upper()}**, "
          f"con cédula de ciudadanía N.º {d['identificacion']}, estudiante de la carrera de {d['carrera']} de la **{d['universidad'].upper()}**, "
          f"realizó de manera exitosa sus prácticas preprofesionales, correspondientes al itinerario **{d['itinerario']}**, en el área de "
          f"**{d['area']}** de esta empresa, desde el {d['inicio']} hasta el {d['fin']}, cumpliendo **{d['horas']} horas**.", after=160)
    tutor = d.get("tutor") or "[[tutor profesional]]"
    doc.ficha([("Practicante", d["nombre"]), ("Cédula de ciudadanía", d["identificacion"]), ("Carrera", d["carrera"]),
               ("Universidad", d["universidad"]), ("Itinerario", d["itinerario"]), ("Área de práctica", d["area"][:1].upper() + d["area"][1:]),
               ("Periodo", f"Del {d['inicio']} al {d['fin']}"), ("Horas cumplidas", f"{d['horas']} horas"),
               ("Tutor profesional", f"{tutor} · {e['razon_social']}")], label_w=2600)
    doc.p(f"Durante este periodo, conforme al cronograma de actividades aprobado en el sistema de gestión académica de la universidad, desarrolló "
          f"actividades de {d['resumen']}, bajo la supervisión del tutor profesional, {tutor}.", after=140)
    doc.p("Se extiende el presente certificado a petición de la persona interesada, para que pueda hacer uso de este documento como estime conveniente.",
          after=100)
    bdr = f'<w:pBdr><w:top w:val="single" w:sz="8" w:space="4" w:color="{mdoc.NAVY}"/></w:pBdr>'
    ind = '<w:ind w:left="2300" w:right="2300"/>'
    for _ in range(5):
        doc.body.append(_p("", after=0, keep=True))
    doc.body.append(_p(_run(rep["nombre"], mdoc.NAVY, 20, b=True), jc="center", extra=bdr, ind=ind, keep=True))
    doc.body.append(_p(_run(rep.get("cargo", "Gerente General"), mdoc.GRAY, 18), jc="center", keep=True))
    doc.body.append(_p(_run(e["razon_social"], mdoc.GRAY, 18), jc="center"))
    doc.save(destino, title=f"Certificado de prácticas preprofesionales · {d['nombre']}", creator=e["razon_social"])
    if pdf:
        from pdf_word import convertir
        convertir(destino)
    return destino


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--empresa", required=True)
    ap.add_argument("--membrete", required=True)
    ap.add_argument("--datos", required=True)
    ap.add_argument("--salida", required=True)
    ap.add_argument("--pdf", action="store_true")
    a = ap.parse_args()
    e = json.load(open(a.empresa, encoding="utf-8"))
    d = json.load(open(a.datos, encoding="utf-8"))
    print("Certificado:", generar(e, d, a.membrete, a.salida, a.pdf))


if __name__ == "__main__":
    main()
