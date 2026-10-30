# -*- coding: utf-8 -*-
"""
huella.py — zona protegida del Word: portada, fondo, encabezados, pies, secciones y estilos.

    python huella.py crear DOC.docx -o huella.json
    python huella.py verificar DOC.docx --contra huella.json      # antes/después de CADA lote de cambios
    python huella.py plantilla DOC.docx --plantilla PLANTILLA.docx # ¿conserva encabezados, pies y fondo?
    python huella.py restaurar DOC.docx --plantilla PLANTILLA.docx -o SALIDA.docx [--reemplazar]

Códigos de salida: 0 intacta · 1 alterada o faltan elementos.
`--preliminares-libres` deja de tratar como FALLA los cambios en dedicatoria, agradecimiento o índices que la
usuaria hace a mano.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts_comunes'))
import docx  # noqa: E402
import versionado_docx as vd  # noqa: E402


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('accion', choices=['crear', 'verificar', 'plantilla', 'restaurar'])
    ap.add_argument('doc')
    ap.add_argument('-o', '--salida')
    ap.add_argument('--contra')
    ap.add_argument('--plantilla')
    ap.add_argument('--reemplazar', action='store_true')
    ap.add_argument('--preliminares-libres', action='store_true')
    a = ap.parse_args()

    if a.accion == 'crear':
        h = vd.huella(a.doc)
        Path(a.salida or 'huella.json').write_text(json.dumps(h, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f"Huella guardada: {len(h['partes'])} encabezados/pies, {len(h['secciones'])} sección(es), "
              f"{h['preliminares']['elementos']} elementos preliminares.")
        return 0
    if a.accion == 'verificar':
        if not a.contra:
            ap.error('verificar necesita --contra huella.json')
        ref = json.loads(Path(a.contra).read_text(encoding='utf-8'))
        dif = vd.comparar_huellas(ref, vd.huella(a.doc), estricto_preliminares=not a.preliminares_libres)
        for nivel, texto in dif:
            print(f'[{nivel}] {texto}')
        mal = any(n == 'FALLA' for n, _ in dif)
        print('ZONA PROTEGIDA ALTERADA' if mal else 'ZONA PROTEGIDA INTACTA')
        return 1 if mal else 0
    if not a.plantilla:
        ap.error(f'{a.accion} necesita --plantilla')
    if a.accion == 'plantilla':
        dif = vd.comparar_con_plantilla(a.doc, a.plantilla)
        for nivel, texto in dif:
            print(f'[{nivel}] {texto}')
        print('CONSERVA ENCABEZADOS, PIES Y FONDO DE LA PLANTILLA' if not dif else 'FALTAN ELEMENTOS: usar «restaurar»')
        return 1 if any(n == 'FALLA' for n, _ in dif) else 0
    if not a.salida:
        ap.error('restaurar necesita -o SALIDA.docx')
    antes = [p.text for p in docx.Document(a.doc).paragraphs]
    for accion in vd.restaurar_encabezados(a.doc, a.plantilla, a.salida, reemplazar=a.reemplazar):
        print('-', accion)
    ok = zipfile.ZipFile(a.salida).testzip() is None and [p.text for p in docx.Document(a.salida).paragraphs] == antes
    print('Texto del documento intacto y paquete válido' if ok else 'ERROR: revisar la salida')
    print('Pendiente:', vd.comparar_con_plantilla(a.salida, a.plantilla) or 'nada')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
