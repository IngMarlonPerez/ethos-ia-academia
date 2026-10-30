# -*- coding: utf-8 -*-
"""Utilidades comunes de las pruebas del Asesor de Proyecto de Titulación de TI."""
from __future__ import annotations

import importlib.util
import struct
import subprocess
import sys
import zlib
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / 'scripts_comunes'))


def cargar(rel: str, nombre: str | None = None):
    """Importa un script del plugin por su ruta relativa."""
    ruta = PLUGIN / rel
    spec = importlib.util.spec_from_file_location(nombre or ruta.stem, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ruta.parent))
    spec.loader.exec_module(mod)
    return mod


def correr(rel: str, *args, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(PLUGIN / rel), *map(str, args)], capture_output=True, text=True,
                          encoding='utf-8', errors='replace', cwd=cwd)


def png_minimo(ruta: Path, ancho: int = 40, alto: int = 20) -> Path:
    """PNG válido de un color (para probar figuras sin Pillow)."""
    fila = b'\x00' + b'\xff\xff\xff' * ancho
    datos = zlib.compress(fila * alto)

    def bloque(tipo, contenido):
        return struct.pack('>I', len(contenido)) + tipo + contenido + struct.pack('>I', zlib.crc32(tipo + contenido) & 0xffffffff)

    ruta.write_bytes(b'\x89PNG\r\n\x1a\n' + bloque(b'IHDR', struct.pack('>IIBBBBB', ancho, alto, 8, 2, 0, 0, 0))
                     + bloque(b'IDAT', datos) + bloque(b'IEND', b''))
    return ruta


@pytest.fixture
def perfil_unemi():
    from perfil import cargar_perfil
    return cargar_perfil('unemi')
