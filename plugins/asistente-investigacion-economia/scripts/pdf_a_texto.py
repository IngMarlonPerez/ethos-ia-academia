"""Extrae texto de un PDF a UTF-8 (y rasteriza páginas si se pide).
Uso:  python -I pdf_a_texto.py entrada.pdf salida.txt [paginas_png_dpi]
- Copiar antes el PDF a una ruta corta (p. ej. C:/w) si la ruta original es larga o tiene tildes.
- Si el PDF es escaneado (texto vacío), con dpi se generan pgN.png para leerlas con la herramienta Read.
- Para tablas con columnas revueltas (informes del BCE) usar get_text('words') y ubicar por coordenada x.
"""
import sys, pymupdf
src, dst, *dpi = sys.argv[1:]
d = pymupdf.open(src)
txt = '\n'.join(f'=====PAGE {i+1}\n' + p.get_text() for i, p in enumerate(d))
open(dst, 'w', encoding='utf-8').write(txt)
print('páginas:', len(d), '| caracteres:', len(txt))
if dpi:
    for i, p in enumerate(d):
        p.get_pixmap(dpi=int(dpi[0])).save(f'pg{i+1}.png')
    print('PNG generados')
