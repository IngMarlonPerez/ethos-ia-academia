#!/usr/bin/env python
"""Genera los TXT del balance inicial para el portal de la SCVS a partir de las PLANTILLAS OFICIALES que entrega la Superintendencia.

Por qué se parte de la plantilla oficial y no de una lista propia: el portal exige todas las cuentas del plan, en el orden de su
plantilla, una por línea («código valor», dos decimales, punto decimal, sin separador de miles, saltos de línea CRLF). Este script
copia la plantilla tal cual y sólo cambia los valores. Las cuentas «padre» (1, 101, 10101…, 3, 30, 301…) se calculan como la suma
de sus hijas, de modo que sólo hay que indicar los saldos de las cuentas de último nivel.

Uso:
    python generar_txt_scvs.py --situacion-plantilla FORMATOS/ESTADO_SITUACION_FINANCIERA.txt \
        --resultados-plantilla FORMATOS/ESTADO_RESULTADO_INTEGRAL.txt --valores valores.json --salida "Balance Inicial SCVS"
    python generar_txt_scvs.py --situacion-plantilla ... --resultados-plantilla ... --caso pagado --capital 200 --salida ...

valores.json:  {"situacion": {"1010101": 200.00, "30101": 200.00}, "resultados": {}}
Atajos (--caso):  pagado       -> 1010101 (Caja) = capital y 30101 = capital
                  por_pagar    -> 30101 = capital y 30102 = -capital       (el capital no pagado resta del patrimonio)
Salida: situacionFinanciera.txt y resultadoIntegral.txt (los nombres que usa el manual de la SCVS).
"""
import argparse
import json
import os
import re
import sys


def leer(ruta):
    raw = open(ruta, "rb").read().decode("latin-1")
    fin = "\r\n" if "\r\n" in raw else "\n"
    lineas = raw.split(fin)
    return lineas, fin


def padres(codigos):
    """Padre = el prefijo más largo que también sea una cuenta del plan."""
    conj = set(codigos)
    p = {}
    for c in conj:
        for k in range(len(c) - 1, 0, -1):
            if c[:k] in conj:
                p[c] = c[:k]
                break
    return p


def calcular(codigos, hojas):
    p = padres(codigos)
    hijos = {}
    for c, par in p.items():
        hijos.setdefault(par, []).append(c)
    desconocidas = [c for c in hojas if c not in set(codigos)]
    if desconocidas:
        sys.exit(f"Cuentas que no existen en la plantilla: {desconocidas}")
    no_hoja = [c for c in hojas if c in hijos]
    if no_hoja:
        sys.exit(f"{no_hoja} tienen subcuentas: indica el saldo en la subcuenta de último nivel")
    memo = {}

    def total(c):
        if c in memo:
            return memo[c]
        memo[c] = round(hojas[c], 2) if c in hojas else round(sum(total(h) for h in hijos.get(c, [])), 2)
        return memo[c]

    return {c: total(c) for c in codigos}, hijos


def generar(plantilla, hojas, destino):
    lineas, fin = leer(plantilla)
    filas = [(i, l.split()) for i, l in enumerate(lineas) if l.strip()]
    for _, partes in filas:
        if len(partes) != 2 or not re.fullmatch(r"\d+", partes[0]):
            sys.exit(f"Línea inesperada en la plantilla: {partes}")
    codigos = [p[0] for _, p in filas]
    if len(codigos) != len(set(codigos)):
        sys.exit("La plantilla tiene códigos repetidos")
    valores, hijos = calcular(codigos, hojas)
    salida = list(lineas)
    for i, (cod, _) in filas:
        salida[i] = f"{cod} {valores[cod]:.2f}"
    texto = fin.join(salida)
    with open(destino, "w", encoding="ascii", newline="") as f:
        f.write(texto)
    # verificación: formato y suma de cada padre
    leidas = [l for l in texto.split(fin) if l.strip()]
    assert all(re.fullmatch(r"\d+ -?\d+\.\d{2}", l) for l in leidas), "formato"
    for par, hs in hijos.items():
        assert abs(valores[par] - sum(valores[h] for h in hs)) < 0.005, f"no cuadra {par}"
    return len(leidas), valores


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--situacion-plantilla", required=True)
    ap.add_argument("--resultados-plantilla", required=True)
    ap.add_argument("--valores", help="JSON con saldos de cuentas de último nivel")
    ap.add_argument("--caso", choices=["pagado", "por_pagar"])
    ap.add_argument("--capital", type=float, help="capital suscrito (con --caso)")
    ap.add_argument("--cuenta-efectivo", default="1010101", help="cuenta donde ingresa el capital pagado (por defecto Caja)")
    ap.add_argument("--salida", required=True)
    a = ap.parse_args()

    sit, res = {}, {}
    if a.valores:
        v = json.load(open(a.valores, encoding="utf-8"))
        sit, res = v.get("situacion", {}), v.get("resultados", {})
    if a.caso:
        if a.capital is None:
            sys.exit("--caso requiere --capital")
        sit = dict(sit)
        sit["30101"] = a.capital
        if a.caso == "pagado":
            sit[a.cuenta_efectivo] = a.capital
        else:
            sit["30102"] = -a.capital
    os.makedirs(a.salida, exist_ok=True)
    n1, v1 = generar(a.situacion_plantilla, sit, os.path.join(a.salida, "situacionFinanciera.txt"))
    n2, v2 = generar(a.resultados_plantilla, res, os.path.join(a.salida, "resultadoIntegral.txt"))
    print(f"situacionFinanciera.txt: {n1} cuentas | resultadoIntegral.txt: {n2} cuentas")
    act, pas, pat = v1.get("1", 0), v1.get("2", 0), v1.get("3", 0)
    print(f"Activo {act:.2f} | Pasivo {pas:.2f} | Patrimonio {pat:.2f} | Activo - (Pasivo + Patrimonio) = {act - pas - pat:.2f}")
    if abs(act - pas - pat) > 0.005:
        sys.exit("ERROR: el Activo no es igual a Pasivo + Patrimonio; el portal no lo dará por CUADRADO")
    print("Cuadra. Falta la prueba real: subirlos al portal y pulsar «Auditar y cuadrar» (no envía nada).")


if __name__ == "__main__":
    main()
