"""Guarda en disco un archivo recuperado desde el Browser pane de Claude.

Cuando `javascript_tool` devuelve un texto muy largo (un PDF en base64, un CSV
o un RIS de Scopus), el harness lo guarda en un archivo tool-results/*.txt con
formato [{"type": "text", "text": ...}] y el contenido doblemente serializado
en JSON. Este script lo decodifica y escribe el archivo final.

Uso:
    python guardar_desde_navegador.py <tool_result.txt> <salida> [--b64 | --json-key CLAVE]

    --b64            el contenido es base64 (PDF u otro binario)
    --json-key CLAVE el contenido es un objeto JSON; se guarda el valor de CLAVE
    (sin opción)     el contenido es texto plano (CSV, RIS)
"""
import base64
import json
import re
import sys


def leer_contenido(ruta):
    data = json.load(open(ruta, encoding="utf-8"))
    texto = re.sub(r"\n\n\(captured at origin.*\)\s*$", "", data[0]["text"], flags=re.S)
    try:
        valor = json.loads(texto)
    except json.JSONDecodeError:
        return texto
    if isinstance(valor, str):
        try:
            return json.loads(valor)
        except json.JSONDecodeError:
            return valor
    return valor


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    origen, salida, opciones = sys.argv[1], sys.argv[2], sys.argv[3:]
    contenido = leer_contenido(origen)

    if "--json-key" in opciones:
        clave = opciones[opciones.index("--json-key") + 1]
        contenido = contenido[clave]

    if "--b64" in opciones:
        crudo = base64.b64decode(contenido)
        if salida.lower().endswith(".pdf") and crudo[:4] != b"%PDF":
            sys.exit("ERROR: el contenido no es un PDF valido")
        open(salida, "wb").write(crudo)
        print(f"OK {salida} ({len(crudo):,} bytes)")
    else:
        texto = contenido.lstrip("﻿")
        bom = "utf-8-sig" if salida.lower().endswith(".csv") else "utf-8"
        open(salida, "w", encoding=bom, newline="").write(texto)
        print(f"OK {salida} ({len(texto):,} caracteres)")


if __name__ == "__main__":
    main()
