# -*- coding: utf-8 -*-
"""Pruebas del generador del manual de arquitectura para el tribunal."""
from __future__ import annotations

import json
import struct
import zlib

import pytest
from docx import Document

from conftest import PLUGIN, cargar

gen = cargar('skills/manual-arquitectura-tribunal/scripts/gen_manual_arquitectura.py')


def _png(ruta):
    """PNG mínimo de 1×1 píxel."""
    def bloque(tipo, datos):
        return struct.pack('>I', len(datos)) + tipo + datos + struct.pack('>I', zlib.crc32(tipo + datos))
    ruta.write_bytes(b'\x89PNG\r\n\x1a\n' + bloque(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
                     + bloque(b'IDAT', zlib.compress(b'\x00\xff\xff\xff')) + bloque(b'IEND', b''))


def _manual(tmp_path, bloques):
    (tmp_path / 'diagramas').mkdir()
    _png(tmp_path / 'diagramas' / 'arquitectura.png')
    return {
        'raiz': str(tmp_path), 'autores': ['Ana Autora', 'Beto Autor'],
        'portada': {'titulo': 'Sistema X · Guía de arquitectura', 'subtitulo': 'Prueba', 'lineas': ['UNEMI']},
        'bloques': bloques,
    }


def test_genera_todos_los_tipos_de_bloque(tmp_path):
    datos = _manual(tmp_path, [
        {'tipo': 'h1', 'texto': '1. La arquitectura'},
        {'tipo': 'p', 'texto': 'Cliente-servidor **desacoplado**.'},
        {'tipo': 'vineta', 'texto': 'El frontend **nunca** toca la base.'},
        {'tipo': 'codigo', 'texto': 'raiz/\n├── backend/'},
        {'tipo': 'tabla', 'encabezado': ['Capa', 'Carpeta'], 'filas': [['API', '`backend/api/`']], 'anchos': [4, 8]},
        {'tipo': 'demo', 'texto': 'abra `main.py` en la línea 78.'},
        {'tipo': 'imagen', 'ruta': 'diagramas/arquitectura.png', 'ancho': 5, 'pie': 'Figura 1.'},
        {'tipo': 'salto'},
        {'tipo': 'h2', 'texto': 'Preguntas'},
    ])
    salida = gen.Manual(datos).generar(tmp_path / 'salida' / 'guia.docx')
    doc = Document(salida)
    texto = '\n'.join(p.text for p in doc.paragraphs)
    assert 'Sistema X · Guía de arquitectura' in texto
    assert '1. La arquitectura' in texto and 'Preguntas' in texto
    assert doc.core_properties.author == 'Ana Autora; Beto Autor'
    assert len(doc.inline_shapes) == 1
    celdas = [c.text for t in doc.tables for f in t.rows for c in f.cells]
    assert 'backend/api/' in celdas
    assert any(c.startswith('Para la demostración') and 'main.py' in c for c in celdas)


def test_figura_inexistente_falla(tmp_path):
    datos = _manual(tmp_path, [{'tipo': 'imagen', 'ruta': 'no/existe.png', 'pie': 'x'}])
    with pytest.raises(FileNotFoundError):
        gen.Manual(datos).generar(tmp_path / 'guia.docx')


def test_tipo_desconocido_falla(tmp_path):
    with pytest.raises(ValueError):
        gen.Manual(_manual(tmp_path, [{'tipo': 'otro'}])).generar(tmp_path / 'guia.docx')


def test_ejemplo_vicmar_bien_formado():
    datos = json.loads((PLUGIN / 'skills/manual-arquitectura-tribunal/plantillas/manual-ejemplo.json')
                       .read_text(encoding='utf-8'))
    tipos = {'h1', 'h2', 'h3', 'p', 'vineta', 'codigo', 'tabla', 'demo', 'imagen', 'salto'}
    assert {'raiz', 'autores', 'portada', 'bloques'} <= datos.keys()
    assert all(b['tipo'] in tipos for b in datos['bloques'])
    assert sum(b['tipo'] == 'demo' for b in datos['bloques']) >= 5
    texto = json.dumps(datos, ensure_ascii=False)
    assert 'Claude' not in texto and 'Anthropic' not in texto
