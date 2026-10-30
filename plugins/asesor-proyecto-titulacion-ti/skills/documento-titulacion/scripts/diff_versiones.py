# -*- coding: utf-8 -*-
"""
diff_versiones.py — compara dos versiones del Word.

    python diff_versiones.py ANTES.docx DESPUES.docx
        qué párrafos cambió, añadió o quitó la usuaria (útil antes de regenerar: descubre ediciones a mano)
    python diff_versiones.py ANTES.docx DESPUES.docx --solo-inserciones
        verifica que un lote propio NO alteró ningún párrafo existente (sale 1 si alteró alguno)
"""
from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts_comunes'))
import docx  # noqa: E402
import versionado_docx as vd  # noqa: E402


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('antes')
    ap.add_argument('despues')
    ap.add_argument('--solo-inserciones', action='store_true')
    ap.add_argument('--max', type=int, default=60, help='máximo de diferencias a mostrar')
    a = ap.parse_args()

    if a.solo_inserciones:
        alterados = vd.solo_inserciones(a.antes, a.despues)
        for t in alterados:
            print('ALTERADO/ELIMINADO:', t)
        print('OK: solo inserciones, ningún párrafo existente cambió' if not alterados
              else f'{len(alterados)} párrafos existentes cambiaron')
        return 1 if alterados else 0

    A = [p.text for p in docx.Document(a.antes).paragraphs]
    B = [p.text for p in docx.Document(a.despues).paragraphs]
    cont = {'replace': 0, 'insert': 0, 'delete': 0}
    mostradas = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=A, b=B, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        cont[op] += max(i2 - i1, j2 - j1)
        if mostradas >= a.max:
            continue
        if op == 'replace':
            for x, y in zip(A[i1:i2], B[j1:j2]):
                if x != y:
                    mostradas += 1
                    print(f'~ [{i1}->{j1}] ANTES: {x[:140]}\n              AHORA: {y[:140]}')
        elif op == 'insert':
            for k, y in enumerate(B[j1:j2]):
                mostradas += 1
                print(f'+ [{j1 + k}] {y[:160]}')
        else:
            for k, x in enumerate(A[i1:i2]):
                mostradas += 1
                print(f'- [{i1 + k}] {x[:160]}')
    print(f"\nResumen: {cont['replace']} modificados, {cont['insert']} añadidos, {cont['delete']} eliminados "
          f"({len(A)} -> {len(B)} párrafos).")
    return 0


if __name__ == '__main__':
    sys.exit(main())
