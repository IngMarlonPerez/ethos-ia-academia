#!/usr/bin/env python
"""Crea el expediente de una empresa nueva: carpetas numeradas, empresa.json (la fuente única de datos) y el tablero de etapas.

No sobrescribe nada: si la carpeta ya existe, sólo agrega lo que falte.

Uso:
    python iniciar_empresa.py "C:/ruta/Mi Empresa" --razon-social "MI EMPRESA S.A.S." --nombre-comercial "Mi Marca" \
        --ciudad Cuenca --provincia Azuay --representante "Nombre Apellido" --cargo "Gerente General"
"""
import argparse
import json
import os
import re
import sys

CARPETAS = [
    "00_Resumen_y_Cronograma",
    "01_Nombre_y_Marca/logos",
    "01_Nombre_y_Marca/guia",
    "02_Datos_Societarios",
    "03_SCVS_Constitucion",
    "04_SRI",
    "05_Municipio",
    "06_Firma_Electronica_y_CNE",
    "07_Gobierno_Societario",
    "08_Papeleria_Membretada",
    "09_Balance_Inicial_SCVS",
    "10_Sitio_Web",
    "11_Equipo_y_Practicantes",
    "99_Auditoria",
]

ETAPAS = [
    (0, "Inicio", "empresa.json y carpetas"),
    (1, "Nombre y marca", "nombre disponible (SCVS, SENADI, dominio, redes), paleta y guía"),
    (2, "Logos y piezas", "logotipo oficial exportado: web, redes, sello, favicon"),
    (3, "Papelería membretada", "membrete .docx/.pdf con RUC correcto; plantillas de documentos"),
    (4, "Constitución SAS", "reserva, formulario de 7 secciones, firma, inscripción"),
    (5, "Obligaciones post-constitución", "RUC, SRI, patente, cuenta bancaria, IESS, contador"),
    (6, "Balance inicial SCVS", "TXT + anexos firmados + envío"),
    (7, "Gobierno societario", "acuerdo de accionistas, cesiones, actas, nombramientos"),
    (8, "Sitio web corporativo", "sitio terminado, seguro, con SEO y sin texto de obra en curso"),
    (9, "Equipo y practicantes", "convenio, cesión de PI, perfiles del equipo, certificados"),
    (10, "Verificación del expediente", "RUC, nombres y datos coherentes en todos los documentos"),
]

PLANTILLA = {
    "razon_social": "",
    "nombre_comercial": "",
    "tipo_societario": "S.A.S.",
    "ruc": "",
    "clave_archivos": "",
    "nombres_anteriores": [],
    "textos_prohibidos": ["próximamente", "en construcción", "coming soon"],
    "domicilio": {"pais": "Ecuador", "provincia": "", "ciudad": "", "direccion": "", "direccion_membrete": ""},
    "contacto": {"telefono": "", "correo": "", "web": ""},
    "representante": {"nombre": "", "cargo": "Gerente General", "identificacion": ""},
    "socios": [{"nombre": "", "identificacion": "", "acciones": 0}],
    "capital": {"suscrito": 200, "pagado": 0, "acciones": 200, "valor_nominal": 1, "plazo_pago_meses": 24},
    "constitucion": {"expediente": "", "tramite": "", "inscripcion_numero": "", "inscripcion_fecha": "",
                     "nombramiento_numero": ""},
    "actividades_ciiu": {"principal": "", "complementarias": []},
    "marca": {"color_primario": "0A1A2E", "color_acento": "00D6FB", "color_secundario": "5B6B72", "color_texto": "0A0F1A",
              "color_fondo_digital": "0A0F1A", "tipografia_web": ""},
    "redes": {},
    "etapas": {},
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("carpeta")
    ap.add_argument("--razon-social", default="")
    ap.add_argument("--nombre-comercial", default="")
    ap.add_argument("--ciudad", default="")
    ap.add_argument("--provincia", default="")
    ap.add_argument("--pais", default="Ecuador")
    ap.add_argument("--representante", default="")
    ap.add_argument("--cargo", default="Gerente General")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    for c in CARPETAS:
        os.makedirs(os.path.join(a.carpeta, c), exist_ok=True)

    ruta = os.path.join(a.carpeta, "empresa.json")
    if os.path.exists(ruta):
        print("empresa.json ya existe: no se toca.")
    else:
        e = json.loads(json.dumps(PLANTILLA))
        e["razon_social"] = a.razon_social
        e["nombre_comercial"] = a.nombre_comercial
        e["clave_archivos"] = re.sub(r"[^A-Z0-9]", "", (a.nombre_comercial or a.razon_social).split(" S.A.S")[0].upper().split()[0]) if (a.nombre_comercial or a.razon_social) else ""
        e["domicilio"].update(pais=a.pais, provincia=a.provincia, ciudad=a.ciudad)
        e["representante"].update(nombre=a.representante, cargo=a.cargo)
        e["etapas"] = {str(n): {"nombre": nom, "estado": "pendiente", "nota": ""} for n, nom, _ in ETAPAS}
        e["etapas"]["0"]["estado"] = "cerrada"
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(e, f, ensure_ascii=False, indent=2)
        print("Creado", ruta)

    # empresa.json guarda cédulas y datos personales: nunca se publica
    gi = os.path.join(a.carpeta, ".gitignore")
    lineas = open(gi, encoding="utf-8").read().splitlines() if os.path.exists(gi) else []
    for x in ("empresa.json", "06_Firma_Electronica_y_CNE/", "*.p12", "*.pfx", ".env*"):
        if x not in lineas:
            lineas.append(x)
    open(gi, "w", encoding="utf-8").write("\n".join(lineas) + "\n")

    tablero = os.path.join(a.carpeta, "00_Resumen_y_Cronograma", "00_Control_Empresa.md")
    if not os.path.exists(tablero):
        out = ["# Control de la empresa", "", "Se actualiza con `tablero.py` (skill asistente-creacion-empresa).", "",
               "| Etapa | Qué debe quedar | Estado | Nota |", "|---|---|---|---|"]
        for n, nom, que in ETAPAS:
            out.append(f"| {n} · {nom} | {que} | {'cerrada' if n == 0 else 'pendiente'} | |")
        open(tablero, "w", encoding="utf-8").write("\n".join(out) + "\n")
        print("Creado", tablero)
    print("Expediente listo en", os.path.abspath(a.carpeta))
    print("Siguiente: completar empresa.json (skill iniciar-empresa) y seguir con nombre-y-marca.")


if __name__ == "__main__":
    main()
