# -*- coding: utf-8 -*-
"""
perfil.py — lectura del proyecto (`titulacion.json`) y del perfil institucional.

El perfil describe lo que exige la universidad: formato, secciones de la
plantilla con sus mínimos de páginas, requisitos (trabajos previos,
referencias, anexos), diagramas UML exigidos, carpeta de entrega y matrices
oficiales. El plugin trae `perfiles/unemi.json`; un proyecto de otra
universidad guarda el suyo en `_automatizacion/perfil_<id>.json` y lo nombra
en `titulacion.json` → "perfil".

    from perfil import cargar_proyecto
    proyecto, perfil, raiz = cargar_proyecto('.')
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
ARCHIVO_PROYECTO = 'titulacion.json'


def leer_json(ruta: Path | str) -> dict:
    return json.loads(Path(ruta).read_text(encoding='utf-8'))


def escribir_json(ruta: Path | str, datos: dict) -> None:
    Path(ruta).write_text(json.dumps(datos, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def cargar_perfil(ref: str = 'unemi', base: Path | None = None) -> dict:
    """`ref` es el id de un perfil del plugin ('unemi') o la ruta de un JSON."""
    if ref.lower().endswith('.json'):
        ruta = Path(ref)
        if not ruta.is_absolute() and base is not None:
            ruta = base / ruta
    else:
        ruta = PLUGIN_ROOT / 'perfiles' / f'{ref}.json'
    if not ruta.exists():
        raise FileNotFoundError(f'No existe el perfil {ruta}')
    return leer_json(ruta)


def buscar_raiz(desde: Path | str = '.') -> Path | None:
    """Sube desde `desde` hasta encontrar titulacion.json."""
    p = Path(desde).resolve()
    for carpeta in [p, *p.parents]:
        if (carpeta / ARCHIVO_PROYECTO).exists():
            return carpeta
    return None


def cargar_proyecto(desde: Path | str = '.') -> tuple[dict, dict, Path]:
    raiz = buscar_raiz(desde)
    if raiz is None:
        raise FileNotFoundError(f'No hay {ARCHIVO_PROYECTO} en {Path(desde).resolve()} ni en sus carpetas superiores. '
                                'Usa la skill iniciar-titulacion.')
    proyecto = leer_json(raiz / ARCHIVO_PROYECTO)
    return proyecto, cargar_perfil(proyecto.get('perfil', 'unemi'), raiz), raiz


def secciones_con_minimo(perfil: dict, avance: int | None = None) -> list[dict]:
    """Secciones (no sus partes) con min_paginas, opcionalmente de un avance."""
    return [s for s in perfil.get('secciones', [])
            if s.get('min_paginas') and (avance is None or s.get('avance') == avance)]


def md5(ruta: Path | str) -> str:
    h = hashlib.md5()
    with open(ruta, 'rb') as f:
        for bloque in iter(lambda: f.read(1 << 20), b''):
            h.update(bloque)
    return h.hexdigest()
