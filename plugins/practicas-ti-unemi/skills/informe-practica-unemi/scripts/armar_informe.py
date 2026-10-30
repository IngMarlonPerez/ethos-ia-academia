# -*- coding: utf-8 -*-
"""
armar_informe.py — arma el informe de la práctica en Word SOBRE la plantilla oficial UNEMI
(portada intacta) a partir de un JSON de contenido. Usa word_apa.py del plugin
asistente-investigacion-cientifica (tablas, figuras y referencias en APA 7).

Uso:
    python -I armar_informe.py contenido.json

contenido.json:
{
  "plantilla": "C:/.../formato_para_actividades_de_aprendizaje_UNEMI.docx",
  "salida": "C:/.../Actividad_Practica_X.docx",
  "portada": {"tema": "...", "autores": "...", "asignatura": "...", "docente": "...",
              "fecha": "...", "periodo": "...", "carrera": "CARRERA DE ...", "compactar": 2},  # sin dato: queda resaltado; "" = en blanco
  "contenido": [
    {"tipo": "titulo", "texto": "I. INTRODUCCIÓN", "nivel": 1},
    {"tipo": "parrafo", "texto": "Texto con *cursiva*, **negrita** y ==resaltado==."},
    {"tipo": "tabla", "numero": 1, "titulo": "...", "encabezados": ["A","B"], "filas": [["a","b"]],
     "nota": "...", "anchos": [5, 8], "tam": 10},
    {"tipo": "figura", "numero": 1, "titulo": "...", "ruta": "...png", "nota": "...", "ancho_cm": 15},
    {"tipo": "imagen", "ruta": "...png", "pie": "...", "ancho_cm": 13}
  ],
  "referencias": ["Autor, A. (2026). Título. *Revista*, *1*(1), 1–10. https://doi.org/..."],
  "anexos": [{"texto": "**Anexo A.** ...", "imagenes": [{"ruta": "...png", "pie": "..."}]},
             {"bloques": [{"tipo": "titulo", "texto": "Anexo B. ...", "nivel": 2}, {"tipo": "parrafo", "texto": "..."}, {"tipo": "imagen", "ruta": "...", "pie": "..."}]}]
}

Reglas:
- La portada no se reescribe: solo se cambia el texto de los campos TEMA, AUTORES, ASIGNATURA,
  DOCENTE, FECHA DE ENTREGA y PERIODO. Si la carrera de la plantilla no coincide con la de la
  usuaria, se avisa, no se corrige por cuenta propia.
- Si Word tiene abierto el archivo de salida y no se puede guardar, se guarda una copia
  `_v2`, `_v3`… y se avisa.
"""
import json
import sys
from pathlib import Path

SC = Path(__file__).resolve().parents[2]  # carpeta del plugin → scripts_comunes
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts_comunes'))
from localizar_plugin import INVESTIGACION, ruta_en_plugin  # noqa: E402

ruta_apa = ruta_en_plugin(INVESTIGACION, 'skills/redaccion-apa7/scripts')
if ruta_apa is None:
    sys.exit('Falta el plugin asistente-investigacion-cientifica (word_apa.py). Instálalo: '
             'claude plugin install asistente-investigacion-cientifica@ethos-ia-academia --scope user')
sys.path.insert(0, str(ruta_apa))

import docx  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Cm, Pt  # noqa: E402
from word_apa import Cursor, abrir, referencias, usar_perfil  # noqa: E402

CAMPOS = [('TEMA:', 'tema'), ('AUTORES:', 'autores'), ('ASIGNATURA:', 'asignatura'),
          ('DOCENTE:', 'docente'), ('FECHA DE ENTREGA:', 'fecha'), ('PERIODO:', 'periodo')]


def llenar_portada(doc, datos):
    for p in doc.paragraphs:
        for etiqueta, clave in CAMPOS:
            if p.text.startswith(etiqueta) and len(p.runs) >= 3:
                valor = datos.get(clave)  # None = sin dato (queda resaltado); '' = campo en blanco a propósito
                for r in p.runs[2:-1]:
                    r.text = ''
                ult = p.runs[-1]
                if valor is None:
                    ult.text = f'[{clave} por completar]'
                    ult.font.highlight_color = WD_COLOR_INDEX.YELLOW
                else:
                    ult.text = valor
    carrera = datos.get('carrera')
    for p in doc.paragraphs:
        if p.text.startswith('CARRERA DE'):
            if carrera and p.runs:
                for r in p.runs[1:]:
                    r.text = ''
                p.runs[0].text = carrera
            print('Carrera en el documento:', p.text)


def pie(cur, texto, tam=11):
    par = cur._nuevo_parrafo()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.first_line_indent = Cm(0)
    r = par.add_run(texto)
    r.italic = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(tam)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    spec = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    usar_perfil('unemi')
    doc = abrir(spec['plantilla'])
    llenar_portada(doc, spec.get('portada', {}))
    idx = next(i for i, p in enumerate(doc.paragraphs) if p.text.strip().startswith('MILAGRO-ECUADOR'))
    # Con varios autores la portada puede desbordar a una 2.ª página: se quitan párrafos VACÍOS
    # (sin texto ni imagen) justo antes de «MILAGRO-ECUADOR». No se toca ningún texto de la plantilla.
    quitar = int(spec.get('portada', {}).get('compactar', 0))
    if quitar:
        vacios = [p for p in doc.paragraphs[:idx]
                  if not p.text.strip() and not p._p.findall('.//' + qn('w:drawing')) and not p._p.findall('.//' + qn('w:sectPr'))]
        for p in vacios[-quitar:]:
            p._p.getparent().remove(p._p)
        idx = next(i for i, p in enumerate(doc.paragraphs) if p.text.strip().startswith('MILAGRO-ECUADOR'))
    cur = Cursor(doc, doc.paragraphs[idx + 1])

    def emitir(b):
        tp = b['tipo']
        if tp == 'titulo':
            cur.titulo(b['texto'], b.get('nivel', 1))
        elif tp == 'parrafo':
            cur.parrafo(b['texto'])
        elif tp == 'tabla':
            cur.tabla(b['numero'], b['titulo'], b['encabezados'], b['filas'], b['nota'], anchos=b.get('anchos'), tam=b.get('tam'))
        elif tp == 'figura':
            cur.figura(b['numero'], b['titulo'], b['ruta'], b['nota'], ancho_cm=b.get('ancho_cm', 15.5))
        elif tp == 'imagen':
            cur.imagen(b['ruta'], b.get('ancho_cm', 13)).paragraph_format.keep_with_next = True
            if b.get('pie'):
                pie(cur, b['pie'])
        else:
            sys.exit(f'Tipo de bloque desconocido: {tp}')

    for b in spec['contenido']:
        emitir(b)
    if spec.get('referencias'):
        cur.titulo('REFERENCIAS', 1)
        referencias(cur, spec['referencias'])
    if spec.get('anexos'):
        cur.titulo('ANEXOS', 1)
        for a in spec['anexos']:
            if 'bloques' in a:          # anexo con bloques descriptivos (títulos, párrafos, imágenes con pie)
                for b in a['bloques']:
                    emitir(b)
            else:                        # forma simple: un párrafo y sus imágenes
                cur.parrafo(a['texto'])
                for im in a.get('imagenes', []):
                    emitir({'tipo': 'imagen', **im})

    salida = Path(spec['salida'])
    destino = salida
    n = 2
    while True:
        try:
            doc.save(str(destino))
            break
        except PermissionError:
            destino = salida.with_name(f'{salida.stem}_v{n}{salida.suffix}')
            n += 1
    if destino != salida:
        print(f'AVISO: {salida.name} estaba abierto en Word; se guardó una copia: {destino.name}')
    print('Guardado:', destino)
    return 0


if __name__ == '__main__':
    sys.exit(main())
