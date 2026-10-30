# -*- coding: utf-8 -*-
"""
localizar_plugin.py — encuentra la carpeta instalada de un plugin de Claude.

${CLAUDE_PLUGIN_ROOT} solo apunta al plugin que se ejecuta. Para usar un script
de OTRO plugin (p. ej. word_apa.py o verificar_apa.py del Asistente de
Investigación Científica) se lee su `installPath` en
~/.claude/plugins/installed_plugins.json. La ruta cambia con cada versión: se
busca en el momento y nunca se guarda en los proyectos.

Uso:
    python localizar_plugin.py asistente-investigacion-cientifica
    python localizar_plugin.py asistente-investigacion-cientifica skills/redaccion-apa7/scripts/word_apa.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

INVESTIGACION = 'asistente-investigacion-cientifica'
PRACTICAS = 'practicas-ti-unemi'


def _registro() -> dict:
    base = Path(os.environ.get('CLAUDE_CONFIG_DIR') or Path.home() / '.claude')
    archivo = base / 'plugins' / 'installed_plugins.json'
    if not archivo.exists():
        return {}
    try:
        return json.loads(archivo.read_text(encoding='utf-8')).get('plugins', {})
    except (OSError, ValueError):
        return {}


def ruta_plugin(nombre: str) -> Path | None:
    """Carpeta instalada del plugin `nombre` (cualquier catálogo), o None."""
    var = os.environ.get(nombre.upper().replace('-', '_') + '_ROOT')
    if var and Path(var).is_dir():
        return Path(var)
    candidatas = []
    for clave, instalaciones in _registro().items():
        if clave.split('@')[0] != nombre:
            continue
        for inst in instalaciones if isinstance(instalaciones, list) else [instalaciones]:
            ruta = Path(inst.get('installPath', ''))
            if ruta.is_dir():
                candidatas.append((inst.get('lastUpdated') or inst.get('installedAt') or '', ruta))
    if candidatas:
        return sorted(candidatas)[-1][1]
    if nombre == PRACTICAS:
        return Path(__file__).resolve().parents[1]
    return None


def ruta_en_plugin(nombre: str, relativa: str) -> Path | None:
    raiz = ruta_plugin(nombre)
    if raiz is None:
        return None
    ruta = raiz / relativa
    return ruta if ruta.exists() else None


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    r = ruta_en_plugin(sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ruta_plugin(sys.argv[1])
    if r is None:
        print(f'No se encontró {" ".join(sys.argv[1:])}. ¿Está instalado el plugin?', file=sys.stderr)
        sys.exit(1)
    print(r)
