# -*- coding: utf-8 -*-
"""
mover_a_revision.py — mueve (NUNCA borra) archivos o carpetas que el proyecto ya
no usa a una carpeta de revisión, conservando su ruta original, y registra
cada uno en INDICE.md con el motivo y la evidencia. Los autores revisan el
índice y deciden qué borrar.

La carpeta de revisión va en .gitignore y en .git/info/exclude: no se publica.

Uso:
    python mover_a_revision.py <raíz> <ruta> [<ruta> …] --categoria "Código heredado"
        --motivo "Prototipo anterior en Node" --evidencia "Ningún import lo alcanza desde main.py"
        [--carpeta _POR_REVISAR_ELIMINAR] [--secretos]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import date
from pathlib import Path

ENCABEZADO = """# Archivos por revisar antes de eliminar

Esta carpeta NO se publica (está en .gitignore y en .git/info/exclude). Contiene lo que el proyecto ya no usa.
Nada se borró: cada elemento conserva su ruta original debajo de esta carpeta.
Revisen cada fila y eliminen solo lo que confirmen; si algo se necesita, devuélvanlo a su ruta original.
Los elementos marcados «CONTIENE SECRETOS» tienen contraseñas o claves reales: al borrarlos, cambien esas credenciales.

| Ruta original | Categoría | Motivo | Evidencia de que no se usa | Fecha |
|---|---|---|---|---|
"""


def mover(raiz: Path, rutas: list[str], categoria: str, motivo: str, evidencia: str, carpeta: str = '_POR_REVISAR_ELIMINAR',
          secretos: bool = False) -> list[str]:
    destino_base = raiz / carpeta
    destino_base.mkdir(exist_ok=True)
    indice = destino_base / 'INDICE.md'
    if not indice.exists():
        indice.write_text(ENCABEZADO, encoding='utf-8')
    movidos = []
    for r in rutas:
        origen = (raiz / r).resolve()
        if not origen.exists():
            print(f'  no existe, se omite: {r}')
            continue
        rel = origen.relative_to(raiz.resolve())
        if rel.parts and rel.parts[0] == carpeta:
            print(f'  ya está en la carpeta de revisión: {r}')
            continue
        destino = destino_base / rel
        if destino.exists():
            raise SystemExit(f'Ya existe {destino}: revísalo antes de mover {r} (no se sobrescribe nada).')
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(origen), str(destino))
        marca = ' CONTIENE SECRETOS.' if secretos else ''
        fila = f'| `{rel.as_posix()}` | {categoria} | {motivo}{marca} | {evidencia} | {date.today().isoformat()} |\n'
        with indice.open('a', encoding='utf-8') as f:
            f.write(fila)
        movidos.append(rel.as_posix())
    return movidos


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('raiz')
    ap.add_argument('rutas', nargs='+')
    ap.add_argument('--categoria', required=True)
    ap.add_argument('--motivo', required=True)
    ap.add_argument('--evidencia', required=True)
    ap.add_argument('--carpeta', default='_POR_REVISAR_ELIMINAR')
    ap.add_argument('--secretos', action='store_true', help='marca que el elemento contiene credenciales reales')
    a = ap.parse_args()
    movidos = mover(Path(a.raiz).resolve(), a.rutas, a.categoria, a.motivo, a.evidencia, a.carpeta, a.secretos)
    for m in movidos:
        print('  movido:', m)
    print(f'{len(movidos)} elementos movidos; ver {a.carpeta}/INDICE.md')
    return 0


if __name__ == '__main__':
    sys.exit(main())
