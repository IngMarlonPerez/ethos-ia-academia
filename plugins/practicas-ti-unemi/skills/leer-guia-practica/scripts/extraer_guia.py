# -*- coding: utf-8 -*-
"""
extraer_guia.py — lee una guía de práctica UNEMI en PDF.

1. Extrae el texto de cada página (PyMuPDF).
2. Detecta las páginas que casi no tienen texto pero sí imágenes (el contenido
   viene como imagen) y las guarda como PNG para leerlas con visión.
3. Escribe un resumen `guia_resumen.md` con datos generales, objetivos, rúbrica
   y la lista de páginas que hay que mirar como imagen.

Uso:
    python -I extraer_guia.py "<guia.pdf>" "<carpeta_salida>" [--dpi 110]
"""
import argparse
import re
import sys
from pathlib import Path

import pymupdf


def limpiar(t: str) -> str:
    # Los PDF de la SGA a veces traen caracteres rotos; se conservan tal cual,
    # pero se normalizan los espacios.
    return re.sub(r'[ \t]+', ' ', t).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('salida')
    ap.add_argument('--dpi', type=int, default=110)
    a = ap.parse_args()

    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(a.pdf)
    paginas_imagen = []
    texto_total = []
    for i, p in enumerate(doc, 1):
        t = p.get_text()
        # Texto "real" = sin contar la cabecera/pie repetidos de la SGA.
        util = [l for l in t.splitlines() if l.strip() and 'unemi.edu.ec' not in l and not re.fullmatch(r'\d+ de \d+', l.strip())]
        texto_total.append(f'=== PÁGINA {i} ===\n' + t)
        if len(' '.join(util)) < 80 and p.get_images():
            png = salida / f'pagina_{i}.png'
            p.get_pixmap(dpi=a.dpi).save(png)
            paginas_imagen.append((i, png))

    (salida / 'guia_texto.txt').write_text('\n'.join(texto_total), encoding='utf-8')
    completo = '\n'.join(texto_total)

    def buscar(rx):
        m = re.search(rx, completo, re.S | re.I)
        return limpiar(m.group(1)) if m else '(no encontrado)'

    resumen = ['# Resumen de la guía de práctica', '',
               f'- PDF: `{a.pdf}`',
               f'- Páginas: {len(doc)}',
               f'- Tema/práctica: {buscar(r"NOMBRE DE LA\s*GU.A:\s*(.+?)\s*N.\. DE")}',
               f'- Docente: {buscar(r"DOCENTE DE LA PR.CTICA:\s*(.+?)\s*UNIDAD")}',
               '',
               '## Páginas en imagen (leer con visión)', '']
    if paginas_imagen:
        resumen += [f'- Página {i}: `{png}`' for i, png in paginas_imagen]
        resumen.append('\nAbre cada PNG con la herramienta Read: ahí está la estructura sugerida del trabajo, tablas de actividades e instrumentos.')
    else:
        resumen.append('- Ninguna: todo el contenido se extrajo como texto.')
    resumen += ['', '## Dónde mirar en `guia_texto.txt`',
                '- «OBJETIVOS DE LA PRÁCTICA», «PROCEDIMIENTOS», «Objetivos específicos»',
                '- «RÚBRICA DE LA PRÁCTICA» (criterios 15/10/5/0: desarrollo, redacción y ortografía, resultados, conclusiones, anexos)',
                '- «REFERENCIAS BIBLIOGRÁFICAS»']
    (salida / 'guia_resumen.md').write_text('\n'.join(resumen), encoding='utf-8')
    print(f'Texto: {salida / "guia_texto.txt"}')
    print(f'Resumen: {salida / "guia_resumen.md"}')
    print('Páginas en imagen:', [i for i, _ in paginas_imagen] or 'ninguna')


if __name__ == '__main__':
    sys.exit(main())
