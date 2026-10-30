# -*- coding: utf-8 -*-
"""
preparar_publicacion.py — controles antes de publicar un proyecto de titulación
en GitHub. Solo lee; no hace commit ni push.

Sobre exactamente lo que se publicaría (git ls-files -co --exclude-standard):
  1. Estado de git: cambios en stash (posibles archivos fuera del disco) y rama actual.
  2. Tamaño: ERROR si un archivo supera --max-mb (GitHub rechaza > 100 MB; por
     defecto 50); AVISO si supera la mitad.
  3. Material que no se publica: .env, PDF dentro de literatura/ (derechos de
     autor), videos, comprimidos y carpetas solo locales (_POR_REVISAR_ELIMINAR,
     ANEXO_USO_ETICO_IA, _MATERIAL_EXTERNO_NO_SUBIR).
  4. Secretos: buscar_secretos.py (skill proteccion-datos).
  5. Rastros de herramientas de IA y autoría de Office: rastros_ia.py (skill uso-etico-ia).

Escribe la lista en --lista para revisarla y termina con 1 si hay errores.

Uso:
    python preparar_publicacion.py <repo> [--autores "A; B"] [--max-mb 50] [--lista publicar.txt]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[3]
SOLO_LOCAL = ('_POR_REVISAR_ELIMINAR/', 'ANEXO_USO_ETICO_IA/', '_MATERIAL_EXTERNO_NO_SUBIR/')
NO_PUBLICAR = [
    ('archivo .env con secretos', re.compile(r'(^|/)\.env$|(^|/)\.env\.(?!example$)[^/]+$')),
    ('PDF de artículo (derechos de autor)', re.compile(r'(?i)(^|/)literatura/.*\.pdf$')),
    ('video', re.compile(r'(?i)\.(mp4|mov|avi|mkv)$')),
    ('comprimido', re.compile(r'(?i)\.(zip|rar|7z)$')),
]


def git(repo: Path, *args) -> str:
    r = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.stdout


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('repo')
    ap.add_argument('--autores', default='')
    ap.add_argument('--max-mb', type=float, default=50)
    ap.add_argument('--lista', default='publicar.txt')
    ap.add_argument('--excluir-rastros', action='append', default=[], help='rutas a omitir en el escaneo de rastros')
    a = ap.parse_args()
    repo = Path(a.repo).resolve()
    errores, avisos = [], []

    stash = git(repo, 'stash', 'list').strip()
    if stash:
        avisos.append(f'Hay cambios guardados en stash ({len(stash.splitlines())}): revisa que no falten archivos en el disco '
                      '(git stash show --name-status stash@{0}).')
    print('Rama actual:', git(repo, 'rev-parse', '--abbrev-ref', 'HEAD').strip() or '(sin commits)')

    archivos = [x for x in git(repo, 'ls-files', '-co', '--exclude-standard').splitlines() if x.strip()]
    Path(a.lista).write_text('\n'.join(archivos) + '\n', encoding='utf-8')
    total = 0
    for rel in archivos:
        p = repo / rel
        if not p.exists():
            continue
        mb = p.stat().st_size / 1e6
        total += mb
        if mb > a.max_mb:
            errores.append(f'{rel}: {mb:.1f} MB (máximo {a.max_mb:g} MB)')
        elif mb > a.max_mb / 2:
            avisos.append(f'{rel}: {mb:.1f} MB')
        if rel.startswith(SOLO_LOCAL):
            errores.append(f'{rel}: carpeta solo local; agrégala a .gitignore y a .git/info/exclude')
        for motivo, rx in NO_PUBLICAR:
            if rx.search(rel):
                errores.append(f'{rel}: {motivo}')
    print(f'Se publicarían {len(archivos)} archivos ({total:.1f} MB). Lista en {a.lista}')

    sec = subprocess.run([sys.executable, str(PLUGIN / 'skills/proteccion-datos/scripts/buscar_secretos.py'), str(repo)],
                         capture_output=True, text=True, encoding='utf-8', errors='replace')
    print('\n— Secretos —\n' + sec.stdout.strip())
    if sec.returncode:
        errores.append('buscar_secretos.py encontró secretos (ver arriba).')

    rastros = [sys.executable, str(PLUGIN / 'skills/uso-etico-ia/scripts/rastros_ia.py'), str(repo), '--lista', a.lista]
    if a.autores:
        rastros += ['--autores', a.autores]
    for e in a.excluir_rastros:
        rastros += ['--excluir', e]
    ra = subprocess.run(rastros, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print('\n— Rastros de IA y autoría —\n' + ra.stdout.strip())
    if ra.returncode:
        avisos.append('rastros_ia.py reportó hallazgos: revisa cada uno (la bibliografía sobre IA no es un rastro).')

    if avisos:
        print('\nAVISOS:')
        for x in avisos:
            print('  !', x)
    if errores:
        print('\nERRORES (no publicar todavía):')
        for x in errores:
            print('  ✗', x)
        return 1
    print('\nListo para publicar: confirma con la usuaria antes del push.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
