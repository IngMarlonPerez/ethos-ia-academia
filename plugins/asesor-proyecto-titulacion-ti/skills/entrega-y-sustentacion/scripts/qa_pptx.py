# -*- coding: utf-8 -*-
"""
qa_pptx.py — control de calidad de un .pptx (diapositivas o póster).

    python qa_pptx.py archivo.pptx [--salida qa] [--min-pt 18] [--sin-pdf]

Revisa: texto que no cabe en su caja (medición real con métricas de Arial), marcadores de plantilla sin reemplazar,
fuentes distintas de Arial/Calibri y letra por debajo del mínimo. Además genera el PDF y una hoja de miniaturas
para la revisión visual (con LibreOffice o PowerPoint; `--sin-pdf` omite este paso).
Código de salida: 0 sin problemas · 1 con problemas.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts_comunes'))
from pptx import Presentation  # noqa: E402
from pptx.util import Emu  # noqa: E402
from presentaciones import render  # noqa: E402
from presentaciones.pptx_kit import INTERLINEADO, PT_CM, envolver  # noqa: E402

PH = re.compile(r'\b(x{3,}|lorem|ipsum|TITULO|Subtítulo|Nombre del|Click to|Haga clic|\[insert)', re.I)
A_NS = '{http://schemas.openxmlformats.org/drawingml/2006/main}'


def revisar(pptx: str, min_pt: float = 0) -> list[str]:
    problemas: list[str] = []
    prs = Presentation(pptx)
    for n, sl in enumerate(prs.slides, 1):
        for sh in sl.shapes:
            if not sh.has_text_frame or not sh.text_frame.text.strip():
                continue
            tf = sh.text_frame
            if PH.search(tf.text):
                problemas.append(f'[diap. {n}] marcador de plantilla: «{tf.text[:60]}»')
            ancho = Emu(sh.width - (tf.margin_left or 0) - (tf.margin_right or 0)).cm
            alto_disp = Emu(sh.height - (tf.margin_top or 0) - (tf.margin_bottom or 0)).cm
            necesario = 0.0
            for p in tf.paragraphs:
                runs = [r for r in p.runs if r.text]
                if not runs:
                    continue
                tam = max((r.font.size.pt for r in runs if r.font.size), default=18)
                neg = any(r.font.bold for r in runs)
                for r in runs:
                    if r.font.name and r.font.name not in ('Arial', 'Calibri'):
                        problemas.append(f'[diap. {n}] fuente {r.font.name}: «{r.text[:40]}»')
                    if min_pt and r.font.size and r.font.size.pt < min_pt:
                        problemas.append(f'[diap. {n}] letra de {r.font.size.pt} pt (< {min_pt}): «{r.text[:40]}»')
                sang = 0.35 * tam / 10 if p._p.pPr is not None and p._p.pPr.get('marL') else 0
                lineas = envolver(''.join(r.text for r in runs), (ancho - sang) / PT_CM, tam, neg)
                necesario += len(lineas) * tam * INTERLINEADO * PT_CM
            if sh.rotation in (90, 270) or tf._txBody.find('.//' + A_NS + 'spAutoFit') is not None:
                continue   # girado o con autoajuste (la caja crece con el texto)
            if necesario > alto_disp * 1.06 + 0.05:
                problemas.append(f'[diap. {n}] el texto no cabe ({necesario:.1f} cm de {alto_disp:.1f} cm): «{tf.text[:60]}»')
    return problemas


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pptx')
    ap.add_argument('--salida', default='qa_pptx')
    ap.add_argument('--min-pt', type=float, default=0)
    ap.add_argument('--sin-pdf', action='store_true')
    a = ap.parse_args()
    problemas = revisar(a.pptx, a.min_pt)
    for p in problemas:
        print(p)
    if not a.sin_pdf:
        os.makedirs(a.salida, exist_ok=True)
        try:
            pdf = render.pptx_a_pdf(a.pptx, a.salida)
            print('PDF:', pdf, '| miniaturas:', render.hoja_contactos(pdf, os.path.join(a.salida, 'miniaturas.png'), columnas=4, dpi=25))
        except (RuntimeError, OSError) as e:
            print(f'No se pudo generar el PDF para la revisión visual: {e}')
    print(f'Problemas detectados: {len(problemas)}. Revisa también las miniaturas con ojos frescos.')
    return 1 if problemas else 0


if __name__ == '__main__':
    sys.exit(main())
