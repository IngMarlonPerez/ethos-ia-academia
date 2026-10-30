# -*- coding: utf-8 -*-
"""
anexo_uso_ia.py — genera el anexo «Declaración de uso ético y responsable de
herramientas de inteligencia artificial» de un proyecto de titulación.

Lee los autores y el título de titulacion.json y las herramientas y tareas de
un JSON (plantilla: plantillas/uso_ia.json). Escribe el .docx en una carpeta
LOCAL que no se publica (por defecto ANEXO_USO_ETICO_IA/), que es el único
lugar del proyecto donde se nombran las herramientas de IA.

Uso:
    python anexo_uso_ia.py <raíz del proyecto> --datos uso_ia.json [--salida ANEXO_USO_ETICO_IA/Declaracion.docx]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

REFERENCIAS = [
    'Nature. (2023). Tools such as ChatGPT threaten transparent science; here are our ground rules for their use '
    '[Editorial]. Nature, 613, 612. https://doi.org/10.1038/d41586-023-00191-1',
    'Thorp, H. H. (2023). ChatGPT is fun, but not an author. Science, 379(6630), 313. https://doi.org/10.1126/science.adg7879',
]


def generar(raiz: Path, datos: dict, salida: Path) -> Path:
    proyecto = json.loads((raiz / 'titulacion.json').read_text(encoding='utf-8')) if (raiz / 'titulacion.json').exists() else {}
    autores = datos.get('autores') or proyecto.get('autores', [])
    if not autores:
        raise SystemExit('Faltan los autores (titulacion.json → autores o "autores" en el JSON).')
    d = docx.Document()
    d.styles['Normal'].font.name = 'Arial'
    d.styles['Normal'].font.size = Pt(11)

    def p(texto, negrita=False, centro=False):
        par = d.add_paragraph()
        par.add_run(texto).bold = negrita
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER if centro else WD_ALIGN_PARAGRAPH.JUSTIFY

    p(datos.get('universidad', proyecto.get('universidad', '')).upper(), True, True)
    p('Anexo. Declaración de uso ético y responsable de herramientas de inteligencia artificial', True, True)
    p(f"Proyecto: «{datos.get('titulo') or proyecto.get('titulo', '')}»", centro=True)
    p(f"Autores: {' y '.join(autores)} · Fecha: {datos.get('fecha', '')}", centro=True)
    d.add_heading('1. Herramientas utilizadas', level=2)
    t = d.add_table(rows=1, cols=4)
    t.style = 'Table Grid'
    for c, txt in zip(t.rows[0].cells, ('Herramienta', 'Proveedor y versión', 'Periodo', 'Uso')):
        c.text = txt
    for h in datos.get('herramientas', []):
        fila = t.add_row().cells
        for c, k in zip(fila, ('nombre', 'proveedor_version', 'periodo', 'uso')):
            c.text = h.get(k, '')
    d.add_heading('2. Tareas en que se usó', level=2)
    for x in datos.get('tareas', []):
        d.add_paragraph(x, style='List Bullet')
    p(datos.get('no_se_uso_para', 'La IA no definió el problema, los objetivos ni las conclusiones; las cifras del '
                                   'documento provienen del código ejecutado sobre los datos.'))
    d.add_heading('3. Verificación humana', level=2)
    for x in datos.get('verificacion', []):
        d.add_paragraph(x, style='List Bullet')
    d.add_heading('4. Protección de datos', level=2)
    p(datos.get('proteccion_datos', 'No se entregó ningún dato personal a las herramientas de IA.'))
    d.add_heading('5. Autoría y responsabilidad', level=2)
    p(f"{' y '.join(autores)} son los únicos autores de este trabajo. Las herramientas de inteligencia artificial no "
      'tienen autoría ni responsabilidad sobre él: toda la responsabilidad sobre el contenido, el código, los datos, las '
      'decisiones y cualquier error recae exclusivamente en los autores, en línea con las revistas que no aceptan a '
      'estas herramientas como autoras porque no pueden asumir responsabilidad (Thorp, 2023; Nature, 2023).')
    if datos.get('marco_institucional'):
        p(datos['marco_institucional'])
    d.add_heading('Referencias', level=2)
    for r in sorted(REFERENCIAS + datos.get('referencias_extra', [])):
        par = d.add_paragraph(r)
        par.paragraph_format.left_indent, par.paragraph_format.first_line_indent = Pt(36), Pt(-36)
    p('Firmas:', True)
    for a in autores:
        p(f'\n______________________________\n{a}')
    d.core_properties.author = '; '.join(autores)
    d.core_properties.last_modified_by = autores[0]
    salida.parent.mkdir(parents=True, exist_ok=True)
    d.save(str(salida))
    return salida


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('raiz')
    ap.add_argument('--datos', required=True)
    ap.add_argument('--salida', default='ANEXO_USO_ETICO_IA/Declaracion_uso_etico_responsable_IA.docx')
    a = ap.parse_args()
    raiz = Path(a.raiz).resolve()
    salida = Path(a.salida) if Path(a.salida).is_absolute() else raiz / a.salida
    print('Generado:', generar(raiz, json.loads(Path(a.datos).read_text(encoding='utf-8')), salida))
    print('Recuerda: esa carpeta va en .gitignore y en .git/info/exclude; el anexo no se publica.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
