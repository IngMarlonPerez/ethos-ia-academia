# -*- coding: utf-8 -*-
"""
armar_entrega.py — arma y revisa la carpeta de entrega final según el perfil
institucional (en UNEMI: AVANCES_TESIS, CODIGO_FUENTE, DATA_UTILIZADA,
DIAGRAMAS, EVIDENCIAS-TUTORIAS, MATRIZ_AVANCES, PROTOTIPO_FUNCIONAL,
PROYECTO_FINAL_TESIS, VIDEOS_*).

  --revisar   solo informa qué subcarpetas faltan o están vacías (no copia nada)
  --copiar    copia lo que el proyecto ya tiene a su lugar: avances generados
              (docx/pdf), diagramas (.mmd/.png), matrices (.xlsx) y los PDF de
              literatura citados. NUNCA copia datos personales ni archivos .env,
              y NO copia el código (hazlo desde git: `git archive`).

Uso (desde la raíz del proyecto):
    python armar_entrega.py --revisar
    python armar_entrega.py --copiar
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLUGIN / 'scripts_comunes'))
from perfil import cargar_proyecto  # noqa: E402


def copiar(origenes: list[Path], destino: Path) -> int:
    destino.mkdir(parents=True, exist_ok=True)
    k = 0
    for o in origenes:
        d = destino / o.name
        if o.is_file() and not d.exists():
            shutil.copy2(o, d)
            k += 1
    return k


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--revisar', action='store_true')
    ap.add_argument('--copiar', action='store_true')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    proyecto, perfil, raiz = cargar_proyecto('.')
    ent = perfil.get('entrega', {})
    base = raiz / ent.get('carpeta_raiz', 'entregables')
    if a.copiar:
        doc = raiz / 'documento'
        for n in (1, 2, 3):
            archivos = list(doc.glob(f'Avance_{n}*.docx')) + list(doc.glob(f'Avance_{n}*.pdf'))
            archivos = [x for x in archivos if 'editado_a_mano' not in x.name]
            if archivos:
                print(f'AVANCE_{n}: {copiar(archivos, base / "AVANCES_TESIS" / f"AVANCE_{n}")} archivos')
        print(f"DIAGRAMAS: {copiar(list((raiz / 'diagramas').glob('*.mmd')) + list((raiz / 'diagramas').glob('*.png')), base / 'DIAGRAMAS')} archivos")
        print(f"MATRIZ_AVANCES: {copiar(list(doc.glob('*.xlsx')), base / 'MATRIZ_AVANCES')} archivos")
        pdfs = [p for p in (raiz / 'literatura').rglob('*.pdf') if '_leidos_no_seleccionados' not in p.parts]
        print(f"DATA_UTILIZADA: {copiar(pdfs, base / 'DATA_UTILIZADA')} PDF citados")
        print('CODIGO_FUENTE: exporta el código limpio con `git archive --format=zip -o entregables/CODIGO_FUENTE/codigo.zip HEAD` '
              '(no incluye .env ni archivos ignorados).')
    faltan, vacias = [], []
    for c in ent.get('carpetas', []):
        ruta = base / c['ruta']
        if not ruta.exists():
            faltan.append(c['ruta'])
        elif not any(ruta.iterdir()):
            vacias.append(f"{c['ruta']} — {c['contenido']}")
    print(f'\nCarpeta de entrega: {base}')
    for x in faltan:
        print('  FALTA:', x)
    for x in vacias:
        print('  VACÍA:', x)
    if not faltan and not vacias:
        print('  Todas las subcarpetas del perfil tienen contenido.')
    return 1 if faltan or vacias else 0


if __name__ == '__main__':
    sys.exit(main())
