# -*- coding: utf-8 -*-
"""
copiar_biblioteca.py — copia al proyecto la biblioteca que usa el generador
del documento, para que el repositorio del estudiante sea AUTOCONTENIDO: el
generador no apunta a ninguna carpeta de la herramienta ni de la máquina de
quien lo creó, y cualquiera que clone el repositorio puede regenerar el Word.

Copia a <proyecto>/_automatizacion/lib/:
  docx_titulacion.py, formato_es.py, versionado_docx.py, perfil.py, trazabilidad.py,
  tabla_trabajos_previos.py y matriz_decision.py
y a <proyecto>/_automatizacion/perfiles/ el perfil institucional en uso.

Se vuelve a ejecutar después de actualizar el plugin (sobrescribe lib/).

Uso:
    python copiar_biblioteca.py <raíz del proyecto> [--destino _automatizacion]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[3]
ARCHIVOS = {
    'docx_titulacion.py': PLUGIN / 'skills/documento-titulacion/scripts/docx_titulacion.py',
    'formato_es.py': PLUGIN / 'scripts_comunes/formato_es.py',
    'versionado_docx.py': PLUGIN / 'scripts_comunes/versionado_docx.py',
    'perfil.py': PLUGIN / 'scripts_comunes/perfil.py',
    'trazabilidad.py': PLUGIN / 'skills/analisis-requerimientos/scripts/trazabilidad.py',
    'tabla_trabajos_previos.py': PLUGIN / 'skills/trabajos-previos/scripts/tabla_trabajos_previos.py',
    'matriz_decision.py': PLUGIN / 'skills/seleccion-tecnologica/scripts/matriz_decision.py',
}
LEEME = """# Biblioteca del generador del documento

Copia local de las funciones que usa el generador del documento de titulación
(inserción en la plantilla oficial, formato numérico en español, perfil
institucional, tablas de requerimientos, trabajos previos y decisiones).
Está en el repositorio para que el documento se pueda regenerar en cualquier
computadora sin instalar nada más que las dependencias de Python.
"""


def copiar(raiz: Path, destino: str = '_automatizacion') -> list[Path]:
    base = raiz / destino
    lib = base / 'lib'
    lib.mkdir(parents=True, exist_ok=True)
    copiados = []
    for nombre, origen in ARCHIVOS.items():
        shutil.copy2(origen, lib / nombre)
        copiados.append(lib / nombre)
    (lib / 'LEEME.md').write_text(LEEME, encoding='utf-8')
    # Perfil institucional: perfil.py busca <lib>/../perfiles/<id>.json
    perfil_id = 'unemi'
    proyecto = raiz / 'titulacion.json'
    if proyecto.exists():
        perfil_id = json.loads(proyecto.read_text(encoding='utf-8')).get('perfil', 'unemi')
    if not str(perfil_id).lower().endswith('.json'):
        (base / 'perfiles').mkdir(exist_ok=True)
        shutil.copy2(PLUGIN / 'perfiles' / f'{perfil_id}.json', base / 'perfiles' / f'{perfil_id}.json')
        copiados.append(base / 'perfiles' / f'{perfil_id}.json')
    return copiados


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('raiz')
    ap.add_argument('--destino', default='_automatizacion')
    a = ap.parse_args()
    for ruta in copiar(Path(a.raiz).resolve(), a.destino):
        print('copiado:', ruta)
    return 0


if __name__ == '__main__':
    sys.exit(main())
