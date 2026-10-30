#!/usr/bin/env python
"""Calendario de plazos de una S.A.S. ecuatoriana recién inscrita, calculado desde la fecha de inscripción.

Imprime una tabla en Markdown (o la guarda con --salida) con: qué hacer, ante quién, fecha límite, base y cuánto falta.
Los plazos son los que se confirmaron en la constitución de una empresa real (manuales y correos de la SCVS, ley de compañías,
calendario del SRI); la columna «Verificar» marca los que dependen de una resolución que puede cambiar.

Uso:
    python calendario_plazos.py --inscripcion 2026-01-15 [--inicio-actividades 2026-01-15] [--ruc 0999999999001] [--hoy 2026-02-01]
                                [--plazo-pago-capital-meses 24] [--duracion-nombramiento-anios 5] [--salida calendario.md]
"""
import argparse
import calendar
import datetime as dt
import sys

# Calendario del SRI: día de vencimiento según el noveno dígito del RUC (declaraciones mensuales y de renta de sociedades)
DIA_SRI = {1: 10, 2: 12, 3: 14, 4: 16, 5: 18, 6: 20, 7: 22, 8: 24, 9: 26, 0: 28}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def sumar_meses(d, n):
    m = d.month - 1 + n
    y, m = d.year + m // 12, m % 12 + 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def f(d):
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]} de {d.year}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inscripcion", required=True, help="fecha de inscripción en el Registro de Sociedades (AAAA-MM-DD)")
    ap.add_argument("--inicio-actividades", help="por defecto, la fecha de inscripción (el RUC la toma de ahí)")
    ap.add_argument("--ruc", help="RUC de la compañía: se usa el 9.º dígito para las fechas del SRI")
    ap.add_argument("--hoy", help="fecha de referencia (por defecto, hoy)")
    ap.add_argument("--plazo-pago-capital-meses", type=int, default=24)
    ap.add_argument("--duracion-nombramiento-anios", type=int, default=5)
    ap.add_argument("--salida")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ins = dt.date.fromisoformat(a.inscripcion)
    ini = dt.date.fromisoformat(a.inicio_actividades) if a.inicio_actividades else ins
    hoy = dt.date.fromisoformat(a.hoy) if a.hoy else dt.date.today()
    pago = sumar_meses(ins, a.plazo_pago_capital_meses)
    nombr = sumar_meses(ins, 12 * a.duracion_nombramiento_anios)

    filas = [
        ("RUC activo y actividades correctas", "SRI", "al día siguiente de la inscripción",
         "La S.A.S. recibe el RUC automáticamente ~24 h después de inscribirse. Consultarlo en SRI en línea y revisar actividades, "
         "establecimiento y nombre comercial. El RUC de la sociedad NO es la cédula del gerente + 001.", "No"),
        ("Balance inicial en el portal de la SCVS (estados financieros iniciales, comprobante de depósito o declaración, asiento de diario, RUC)",
         "SCVS", ins + dt.timedelta(days=30),
         "30 días desde la inscripción (correo «Compañía Constituida»). Ojo: el art. 54 del Reglamento de las S.A.S. dice que se presentan "
         "dentro de los 30 días posteriores al plazo de pago del capital; ante la duda, presentar dentro de los 30 días del correo.", "Sí"),
        ("Patente municipal (declaración y pago)", "GAD municipal", ini + dt.timedelta(days=30),
         "30 días desde el inicio de actividades (Cuenca: formulario 106). Ver ordenanza del cantón.", "Sí"),
        ("Cuenta bancaria de la compañía y depósito del capital", "Banco", pago,
         f"Plazo máximo de {a.plazo_pago_capital_meses} meses desde la inscripción (cláusula del acto constitutivo). Mientras no se pague, el capital figura por pagar.", "No"),
        ("Presentar a la SCVS el comprobante y el asiento del pago del capital", "SCVS", pago + dt.timedelta(days=30),
         "Si el capital se pagó después del balance inicial: art. 54 del Reglamento de las S.A.S.", "Sí"),
        ("Factura electrónica activa antes de la primera venta", "SRI", None,
         "Obligatoria para sociedades. Requiere firma electrónica de la compañía y clave del SRI.", "No"),
        ("Registro patronal del IESS al contratar personal", "IESS", None,
         "Aviso de entrada dentro de los primeros 15 días de iniciada la relación laboral (Ley de Seguridad Social).", "Sí"),
        ("Notificar a la SCVS cada cesión de acciones", "SCVS", None,
         "Dentro de 8 días de anotada en el libro de acciones y accionistas. Un cambio de representante legal bloquea la clave de la compañía.", "Sí"),
        ("Renovar el nombramiento del representante legal", "SCVS", nombr - dt.timedelta(days=30),
         f"El nombramiento dura {a.duracion_nombramiento_anios} años desde la inscripción ({f(nombr)}). Iniciar la renovación 30 días antes.", "No"),
    ]
    if a.ruc and len(a.ruc) >= 9 and a.ruc[8].isdigit():
        dia = DIA_SRI[int(a.ruc[8])]
        filas.append((f"Declaración de IVA mensual (RUC con 9.º dígito {a.ruc[8]})", "SRI", None,
                      f"Cada mes, hasta el día {dia} del mes siguiente (calendario del SRI según el noveno dígito). Sin ventas también se declara en cero.", "Sí"))
        filas.append((f"Impuesto a la renta de sociedades (RUC con 9.º dígito {a.ruc[8]})", "SRI", None,
                      f"Cada año en abril, hasta el día {dia}, por el ejercicio anterior.", "Sí"))
    filas.append(("Estados financieros anuales a la SCVS", "SCVS", None,
                  "Cada año por el ejercicio anterior (abril, según la resolución vigente de la SCVS). El primero corresponde al año de la constitución.", "Sí"))

    out = [f"# Calendario de plazos · inscripción {f(ins)}", "",
           f"Referencia: {f(hoy)}. El plazo ante la SCVS no se traslada por fines de semana (el traslado del Código Tributario no le aplica): "
           "si vence en día no laborable, presentar antes.", "",
           "| Qué | Ante quién | Fecha límite | Faltan | Detalle | Verificar |", "|---|---|---|---|---|---|"]
    orden = lambda x: (0 if isinstance(x[2], str) else 1 if x[2] else 2, x[2] if isinstance(x[2], dt.date) else dt.date.min)
    for que, quien, fecha, detalle, ver in sorted(filas, key=orden):
        if isinstance(fecha, str):
            falta, cuando = "—", fecha
        elif fecha:
            d = (fecha - hoy).days
            falta = f"{d} días" if d >= 0 else f"**vencido hace {-d} días**"
            cuando = f(fecha)
        else:
            falta, cuando = "—", "según el caso"
        out.append(f"| {que} | {quien} | {cuando} | {falta} | {detalle} | {ver} |")
    out += ["", "«Verificar» = confirmar el plazo vigente en el portal o la norma antes de depender de la fecha."]
    texto = "\n".join(out)
    if a.salida:
        open(a.salida, "w", encoding="utf-8").write(texto + "\n")
        print("Guardado en", a.salida)
    print(texto)


if __name__ == "__main__":
    main()
