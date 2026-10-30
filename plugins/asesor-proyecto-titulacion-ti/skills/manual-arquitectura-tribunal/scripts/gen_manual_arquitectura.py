"""Genera en Word el manual de arquitectura para el tribunal a partir de un JSON.

Uso: python gen_manual_arquitectura.py manual.json [salida.docx]

El JSON describe la portada y una lista de bloques en orden. Cada bloque tiene un
«tipo» y sus campos:
  h1, h2, h3   {"texto"}
  p            {"texto"}                  **negrita** dentro del texto
  vineta       {"texto"}
  codigo       {"texto"}                  bloque monoespaciado, respeta saltos de línea
  tabla        {"encabezado", "filas", "anchos"?}   `código` dentro de una celda
  demo         {"texto"}                  recuadro «Para la demostración»
  imagen       {"ruta", "ancho"?, "pie"}  ruta relativa a «raiz»
  salto        {}                         salto de página
Las rutas de imágenes y del logo son relativas a «raiz» (la raíz del repositorio del
proyecto). La autoría del archivo son los autores del JSON; el PDF se obtiene después
con Microsoft Word (docx_a_pdf.ps1).
"""
import json
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


def _rgb(hexa: str) -> RGBColor:
    return RGBColor.from_string(hexa.lstrip('#').upper())


class Manual:
    def __init__(self, datos: dict):
        self.d = datos
        self.raiz = Path(datos['raiz'])
        self.azul = _rgb(datos.get('color_principal', '002E45'))
        self.acento = _rgb(datos.get('color_acento', 'FF6900'))
        self.fondo_demo = datos.get('fondo_demo', 'FFF1E6').lstrip('#')
        self.doc = Document()
        for s in self.doc.sections:
            s.left_margin = s.right_margin = Cm(2.2)
            s.top_margin = s.bottom_margin = Cm(2)
        self.doc.styles['Normal'].font.name = 'Calibri'
        self.doc.styles['Normal'].font.size = Pt(10.5)
        for nombre, tam in (('Heading 1', 16), ('Heading 2', 13), ('Heading 3', 11.5)):
            st = self.doc.styles[nombre]
            st.font.name = 'Calibri'
            st.font.size = Pt(tam)
            st.font.color.rgb = self.azul
        autores = datos.get('autores', [])
        props = self.doc.core_properties
        props.author = props.last_modified_by = '; '.join(autores)
        props.title = datos['portada']['titulo']

    # ── utilidades ────────────────────────────────────────────────────────
    @staticmethod
    def _sombrear(celda, color: str) -> None:
        tc = celda._tc.get_or_add_tcPr()
        sh = OxmlElement('w:shd')
        sh.set(qn('w:val'), 'clear')
        sh.set(qn('w:color'), 'auto')
        sh.set(qn('w:fill'), color)
        tc.append(sh)

    @staticmethod
    def _runs(par, texto: str, tam: float | None = None, marca: str = '**', mono: bool = False) -> None:
        """Agrega el texto alternando normal y resaltado según la marca (** negrita, ` código)."""
        for i, trozo in enumerate(texto.split(marca)):
            r = par.add_run(trozo)
            if i % 2 == 1:
                if mono:
                    r.font.name = 'Consolas'
                else:
                    r.bold = True
            if tam:
                r.font.size = Pt(tam - (1 if mono and i % 2 == 1 else 0))

    def _texto_celda(self, par, texto: str, tam: float) -> None:
        # Primero separa `código`; dentro de cada trozo normal, **negrita**.
        for i, trozo in enumerate(str(texto).split('`')):
            if i % 2 == 1:
                r = par.add_run(trozo)
                r.font.name = 'Consolas'
                r.font.size = Pt(tam - 0.5)
            else:
                self._runs(par, trozo, tam)

    # ── bloques ───────────────────────────────────────────────────────────
    def portada(self) -> None:
        pt = self.d['portada']
        if pt.get('logo'):
            self.doc.add_picture(str(self.raiz / pt['logo']), width=Cm(3))
            self.doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        for texto, tam, color, negrita in ((pt['titulo'], 24, self.azul, True),
                                           (pt.get('subtitulo', ''), 13, self.acento, False)):
            if not texto:
                continue
            par = self.doc.add_paragraph()
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = par.add_run(texto)
            r.bold, r.font.size, r.font.color.rgb = negrita, Pt(tam), color
        for linea in pt.get('lineas', []):
            self.doc.add_paragraph(linea).alignment = WD_ALIGN_PARAGRAPH.CENTER
        if pt.get('nota'):
            par = self.doc.add_paragraph()
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = par.add_run(pt['nota'])
            r.italic, r.font.size = True, Pt(9)
        self.doc.add_page_break()

    def bloque(self, b: dict) -> None:
        tipo = b['tipo']
        if tipo in ('h1', 'h2', 'h3'):
            self.doc.add_heading(b['texto'], int(tipo[1]))
        elif tipo == 'p':
            par = self.doc.add_paragraph()
            self._runs(par, b['texto'])
            par.paragraph_format.space_after = Pt(4)
        elif tipo == 'vineta':
            par = self.doc.add_paragraph(style='List Bullet')
            self._runs(par, b['texto'])
            par.paragraph_format.space_after = Pt(1)
        elif tipo == 'codigo':
            for linea in b['texto'].strip('\n').split('\n'):
                par = self.doc.add_paragraph()
                r = par.add_run(linea or ' ')
                r.font.name, r.font.size = 'Consolas', Pt(8.5)
                par.paragraph_format.space_after = Pt(0)
                par.paragraph_format.left_indent = Cm(0.4)
            self.doc.add_paragraph().paragraph_format.space_after = Pt(2)
        elif tipo == 'tabla':
            self._tabla(b)
        elif tipo == 'demo':
            t = self.doc.add_table(rows=1, cols=1)
            celda = t.rows[0].cells[0]
            self._sombrear(celda, self.fondo_demo)
            celda.text = ''
            par = celda.paragraphs[0]
            r = par.add_run(b.get('etiqueta', 'Para la demostración: '))
            r.bold, r.font.size, r.font.color.rgb = True, Pt(9.5), self.acento
            self._texto_celda(par, b['texto'], 9.5)
            self.doc.add_paragraph().paragraph_format.space_after = Pt(2)
        elif tipo == 'imagen':
            ruta = self.raiz / b['ruta']
            if not ruta.exists():
                raise FileNotFoundError(f'No existe la figura {ruta}')
            self.doc.add_picture(str(ruta), width=Cm(b.get('ancho', 15)))
            self.doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            par = self.doc.add_paragraph()
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = par.add_run(b.get('pie', ''))
            r.italic, r.font.size = True, Pt(9)
        elif tipo == 'salto':
            self.doc.add_page_break()
        else:
            raise ValueError(f'Tipo de bloque desconocido: {tipo}')

    def _tabla(self, b: dict) -> None:
        encabezado = b['encabezado']
        t = self.doc.add_table(rows=1, cols=len(encabezado))
        t.style = 'Table Grid'
        for i, h in enumerate(encabezado):
            c = t.rows[0].cells[i]
            c.text = ''
            r = c.paragraphs[0].add_run(h)
            r.bold, r.font.size, r.font.color.rgb = True, Pt(9), RGBColor(255, 255, 255)
            self._sombrear(c, str(self.azul))
        for fila in b['filas']:
            celdas = t.add_row().cells
            for i, valor in enumerate(fila):
                celdas[i].text = ''
                self._texto_celda(celdas[i].paragraphs[0], valor, 9)
        if b.get('anchos'):
            for fila in t.rows:
                for i, ancho in enumerate(b['anchos']):
                    fila.cells[i].width = Cm(ancho)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def generar(self, salida: Path) -> Path:
        self.portada()
        for b in self.d['bloques']:
            self.bloque(b)
        salida.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(salida)
        return salida


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    datos = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    salida = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(datos['salida'])
    print('Generado:', Manual(datos).generar(salida))
    return 0


if __name__ == '__main__':
    sys.exit(main())
