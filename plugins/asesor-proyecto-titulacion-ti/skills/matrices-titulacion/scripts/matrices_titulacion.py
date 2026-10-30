# -*- coding: utf-8 -*-
"""
matrices_titulacion.py — genera el Excel de matrices metodológicas del
proyecto a partir de los JSON del proyecto (una sola fuente de verdad):

  1. Matriz de consistencia            ← _automatizacion/datos_matrices.json
  2. Extracción bibliográfica          ← literatura/trabajos_previos.json
  3. PRISMA (inclusión-exclusión)      ← datos_matrices.json (o enlace al Excel de matrices-revision)
  4. Decisiones tecnológicas y de arquitectura ← decisiones/DT-*.json (matriz_decision.py)
  5. Trazabilidad                      ← requerimientos/requerimientos.json
  6. Coherencia literatura-código      ← datos_matrices.json; las cifras se leen de los artefactos
  + las matrices oficiales del perfil (en UNEMI: congruencia, estado del arte,
    contexto, lectura de publicaciones); «Estado del Arte» se llena sola.

Uso (desde la raíz del proyecto):
    python matrices_titulacion.py [--datos _automatizacion/datos_matrices.json] [--salida documento/Matrices.xlsx]
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import sys
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

PLUGIN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLUGIN / 'scripts_comunes'))
from formato_es import n  # noqa: E402
from perfil import cargar_proyecto, leer_json  # noqa: E402

ENC_RELLENO = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
ENC_FUENTE = Font(bold=True, color='FFFFFF', size=10)
TITULO = Font(bold=True, size=14, color='1F4E78')
SUB = Font(italic=True, size=9, color='595959')
AJUSTE = Alignment(wrap_text=True, vertical='top', horizontal='left')
CENTRO = Alignment(wrap_text=True, vertical='center', horizontal='center')
LINEA = Side(style='thin', color='D9D9D9')
BORDE = Border(left=LINEA, right=LINEA, top=LINEA, bottom=LINEA)
ZEBRA = (PatternFill(start_color='F2F6FA', end_color='F2F6FA', fill_type='solid'),
         PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid'))


def _mod(ruta: Path, nombre: str):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def hoja(wb, titulo: str, subtitulo: str, encabezados: list[str], filas: list[list], anchos: list[int] | None = None):
    ws = wb.create_sheet(titulo[:31])
    ws['A1'] = titulo
    ws['A1'].font = TITULO
    ws['A2'] = subtitulo
    ws['A2'].font = SUB
    fila0 = 4
    for c, h in enumerate(encabezados, 1):
        celda = ws.cell(row=fila0, column=c, value=h)
        celda.fill, celda.font, celda.alignment, celda.border = ENC_RELLENO, ENC_FUENTE, CENTRO, BORDE
    for i, fila in enumerate(filas):
        for c, v in enumerate(fila, 1):
            celda = ws.cell(row=fila0 + 1 + i, column=c, value=v)
            celda.alignment, celda.border, celda.fill = AJUSTE, BORDE, ZEBRA[i % 2]
    for c, w in enumerate(anchos or [28] * len(encabezados), 1):
        ws.column_dimensions[get_column_letter(c)].width = w
    ws.freeze_panes = ws.cell(row=fila0 + 1, column=1).coordinate
    ws.sheet_view.showGridLines = False
    return ws


def _reales(lista):
    return [x for x in lista if isinstance(x, dict) and not x.get('_ejemplo')]


def valor_cifra(c: dict, raiz: Path) -> str:
    vc = _mod(PLUGIN / 'skills/verificar-coherencia/scripts/verificar_coherencia.py', 'vc')
    archivos = sorted(glob.glob(str(raiz / c['archivo'])))
    if not archivos:
        return '(artefacto no encontrado)'
    v = vc.valor_ruta(leer_json(archivos[-1]), c['ruta']) * c.get('escala', 1)
    return n(v, c.get('decimales', 3)) + c.get('sufijo', '')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--datos', default='_automatizacion/datos_matrices.json')
    ap.add_argument('--salida')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    proyecto, perfil, raiz = cargar_proyecto('.')
    d = leer_json(raiz / a.datos) if (raiz / a.datos).exists() else {}
    tema = proyecto.get('titulo') or proyecto.get('tema', '')
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    avisos = []

    hoja(wb, '1. Matriz de consistencia', tema,
         ['Problema', 'Objetivo', 'Nivel Bloom', 'Dimensión / unidad de análisis', 'Metodología / diseño', 'Resultado esperado / instrumento'],
         [[x.get('problema', ''), x.get('objetivo', ''), x.get('nivel_bloom', ''), x.get('dimension', ''), x.get('metodologia', ''),
           x.get('resultado_instrumento', '')] for x in _reales(d.get('consistencia', []))], [34, 40, 14, 30, 30, 34])

    tp = leer_json(raiz / 'literatura/trabajos_previos.json') if (raiz / 'literatura/trabajos_previos.json').exists() else {}
    trabajos = [t for t in _reales(tp.get('trabajos', [])) if t.get('decision', 'Incluido') == 'Incluido']
    tec = lambda t: '; '.join(f'{k}: {v}' for k, v in (t.get('tecnologias') or {}).items() if v) if isinstance(t.get('tecnologias'), dict) else t.get('tecnologias', '')
    hoja(wb, '2. Extracción bibliográfica', 'Trabajos previos leídos en texto completo (fuente: literatura/trabajos_previos.json)',
         ['N°', 'Autor(es) (año)', 'Título', 'Revista', 'DOI', 'Búsqueda', 'Problema / objetivo', 'Técnica o método',
          'Tecnologías', 'Arquitectura', 'Validación y métricas', 'Resultado principal', 'Limitación', 'Relación con este trabajo',
          'Evidencia (página)'],
         [[i, t.get('cita', ''), t.get('titulo', ''), t.get('revista', ''), t.get('doi', ''), t.get('busqueda', ''),
           t.get('problema', ''), t.get('tecnica', ''), tec(t), t.get('arquitectura', ''), t.get('validacion_metricas', ''),
           t.get('resultado', ''), t.get('limitacion', ''), t.get('relacion_con_este_trabajo', ''),
           ' | '.join(f"{e.get('texto', '')[:120]} ({e.get('pagina', '')})" for e in t.get('evidencia', []))]
          for i, t in enumerate(trabajos, 1)],
         [5, 22, 36, 22, 22, 9, 30, 26, 28, 24, 28, 30, 28, 30, 40])
    if len(trabajos) < perfil.get('requisitos', {}).get('min_trabajos_previos', 10):
        avisos.append(f"solo {len(trabajos)} trabajos previos incluidos.")

    pr = d.get('prisma', {})
    busq = pr.get('busquedas', [])
    fases = _reales(pr.get('fases', []))
    if fases:
        hoja(wb, '3. PRISMA', 'Flujo de identificación, cribado, elegibilidad e inclusión',
             ['Fase PRISMA', *busq, 'Criterio aplicado', 'Motivo de exclusión más frecuente'],
             [[f.get('fase', ''), *[f.get(b, '') for b in busq], f.get('criterio', ''), f.get('motivo', '')] for f in fases])
    elif pr.get('excel_revision'):
        ws = wb.create_sheet('3. PRISMA')
        ws['A1'] = 'PRISMA 2020: ver el Excel de la revisión sistemática'
        ws['A1'].font = TITULO
        ws['A3'] = pr['excel_revision']

    carpeta = raiz / 'decisiones'
    decisiones = sorted(carpeta.glob('DT-*.json')) if carpeta.is_dir() else []
    if decisiones:
        md = _mod(PLUGIN / 'skills/seleccion-tecnologica/scripts/matriz_decision.py', 'matriz_decision')
        filas = []
        for ruta in decisiones:
            dd = leer_json(ruta)
            if md.validar(dd, perfil):
                avisos.append(f'{ruta.name} no pasa la validación (corre matriz_decision.py).')
                continue
            r = md.resolver(dd)
            nombres = {k['id']: k['nombre'] for k in dd['candidatas']}
            filas.append([dd.get('id', ''), dd['decision'], dd.get('tipo', 'tecnologia'),
                          ' / '.join(f'{nombres[k]} ({n(v, 2)})' for k, v in r['ranking']),
                          ', '.join(f"{c['nombre']} {c['peso']} %" for c in dd['criterios']),
                          nombres[r['elegida']], r['estabilidad']])
        hoja(wb, '4. Decisiones', 'Decisiones tecnológicas y de arquitectura (matriz ponderada + sensibilidad; ver ADR)',
             ['ID', 'Decisión', 'Tipo', 'Opciones (puntaje sobre 5)', 'Criterios y pesos', 'Elegida', 'Estabilidad'], filas,
             [8, 28, 12, 44, 44, 20, 44])

    if (raiz / 'requerimientos/requerimientos.json').exists():
        tz = _mod(PLUGIN / 'skills/analisis-requerimientos/scripts/trazabilidad.py', 'trazabilidad')
        t = tz.tablas(leer_json(raiz / 'requerimientos/requerimientos.json'))['trazabilidad']
        hoja(wb, '5. Trazabilidad', 'Objetivo → historias → requerimientos → componente → prueba', t[0], t[1:], [40, 20, 24, 24, 24])

    filas = []
    for x in _reales(d.get('coherencia_literatura_codigo', [])):
        evid = x.get('evidencia', '')
        if x.get('cifra'):
            evid = evid.replace('{cifra}', valor_cifra(x['cifra'], raiz))
        filas.append([x.get('antecedente', ''), x.get('afirma', ''), x.get('decision_codigo', ''), x.get('archivo', ''), evid])
    hoja(wb, '6. Coherencia literatura-código', 'Cada antecedente citado → decisión verificable en el código',
         ['Antecedente', 'Qué afirma el documento', 'Decisión en el código', 'Dónde está implementada', 'Evidencia medida'],
         filas, [26, 44, 44, 34, 34])

    oficiales = d.get('oficiales', {})
    for m in perfil.get('matrices_oficiales', []):
        filas = [f for f in oficiales.get(m['hoja'], []) if isinstance(f, list)]
        if 'estado del arte' in m['hoja'].lower():
            autores = ', '.join(proyecto.get('autores', []))
            filas += [[autores, t.get('cita', ''), f"{t.get('anio', '')} / {t.get('revista', '')}", t.get('titulo', ''),
                       'Artículo científico', t.get('palabras_clave', ''), t.get('resultado', ''), t.get('relacion_con_este_trabajo', ''),
                       f"https://doi.org/{t['doi']}" if t.get('doi') else '', t.get('doi', '')] for t in trabajos]
        hoja(wb, m['hoja'], f"Matriz oficial ({perfil.get('institucion', '')})", m['columnas'], filas)

    salida = raiz / (a.salida or d.get('salida') or 'documento/Matrices_Metodologicas.xlsx')
    salida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(salida))
    print(f'Matrices: {salida} ({len(wb.sheetnames)} hojas: {", ".join(wb.sheetnames)})')
    for x in avisos:
        print('  AVISO:', x)
    return 0


if __name__ == '__main__':
    sys.exit(main())
