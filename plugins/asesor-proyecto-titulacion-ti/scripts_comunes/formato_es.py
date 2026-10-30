# -*- coding: utf-8 -*-
"""
formato_es.py — números con la norma de los documentos en español:
coma decimal, punto de miles y espacio antes del signo de porcentaje.

    n(0.9974)      -> '0,997'
    n(1234.5, 1)   -> '1.234,5'
    pct(0.925)     -> '92,5 %'
    miles(14508)   -> '14.508'
    media_de(0.8, 0.02) -> '0,800 ± 0,020'
"""
from __future__ import annotations


def n(x: float, d: int = 3) -> str:
    return f'{x:,.{d}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def pct(x: float, d: int = 1) -> str:
    """x es una proporción (0-1)."""
    return f'{n(x * 100, d)} %'


def miles(x: float) -> str:
    return f'{int(round(x)):,}'.replace(',', '.')


def media_de(media: float, desviacion: float, d: int = 3) -> str:
    return f'{n(media, d)} ± {n(desviacion, d)}'
