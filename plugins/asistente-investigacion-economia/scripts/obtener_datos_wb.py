"""Descarga series del Banco Mundial (API) a JSON en la carpeta de trabajo.
Uso:  python -I obtener_datos_wb.py ECU 1999 2025 NY.GDP.MKTP.KD.ZG FP.CPI.TOTL.ZG NE.CON.PRVT.ZS ...
Cada serie queda en <CARPETA>/<codigo>.json (formato API). Carpeta por defecto: C:/w (ruta corta).
Códigos útiles: NY.GDP.MKTP.KD.ZG (crec. PIB real), FP.CPI.TOTL.ZG (inflación prom.),
NE.CON.PRVT.ZS (consumo hogares %PIB), NE.CON.GOVT.ZS (gobierno), NE.GDI.TOTL.ZS (FBK),
NE.GDI.FTOT.ZS (FBKF), NE.EXP.GNFS.ZS (X), NE.IMP.GNFS.ZS (M).
"""
import sys, json, urllib.request, os
pais, a, b, *series = sys.argv[1:]
out = os.environ.get('CARPETA', 'C:/w')
os.makedirs(out, exist_ok=True)
for s in series:
    url = f'https://api.worldbank.org/v2/country/{pais}/indicator/{s}?format=json&per_page=200&date={a}:{b}'
    data = json.load(urllib.request.urlopen(url))
    json.dump(data, open(f'{out}/{s}.json', 'w'))
    vals = sorted((r['date'], r['value']) for r in data[1] if r['value'] is not None)
    print(s, 'actualizado:', data[0].get('lastupdated'), '| n =', len(vals), '| últimos:', vals[-3:])
