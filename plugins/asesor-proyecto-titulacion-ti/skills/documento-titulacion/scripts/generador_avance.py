# -*- coding: utf-8 -*-
"""
generador_avance.py — ESQUELETO del generador de un avance. Se copia al
proyecto como _automatizacion/build_avanceN.py y se completa allí.

Reglas del generador:
  1. Parte de una COPIA: la plantilla oficial (Avance 1) o el documento del
     avance anterior entregado (Avance 2 en adelante). Nunca modifica el original.
  2. UNA SOLA FUENTE DE VERDAD: ninguna cifra ni tabla se escribe a mano. Se
     leen de los JSON del proyecto (requerimientos, trabajos previos,
     decisiones, diccionario de datos) y de los artefactos del código
     (metrics.json, resultados de evaluación); el código se extrae en vivo.
  3. Ancla por prefijo de texto (buscar), nunca por índice de párrafo.
  4. Antes de sobrescribir la salida, compara la huella de su TEXTO con la
     registrada: si cambió, la usuaria la editó a mano → se detiene para
     integrar sus cambios. (Se usa la huella del texto y no el md5 porque Word
     vuelve a guardar el archivo al actualizar el índice en docx_a_pdf.ps1.)
  5. NUNCA PIERDE UNA VERSIÓN: antes de sobrescribir, archiva la salida anterior
     como documento/versiones/Avance_N_vNN.docx (con su huella). Al terminar,
     comprueba que la zona protegida (encabezados, pies, logo, fondo y secciones)
     sigue igual que en el origen.

Uso (desde la raíz del proyecto):
    python _automatizacion/build_avanceN.py [--forzar]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


# Biblioteca copiada al proyecto con copiar_biblioteca.py: el generador no
# depende de ninguna carpeta externa al repositorio.
LIB = Path(__file__).resolve().parent / 'lib'
if not (LIB / 'docx_titulacion.py').exists():
    sys.exit(f'Falta {LIB}. Copia la biblioteca con: python copiar_biblioteca.py <raíz del proyecto>')
sys.path.insert(0, str(LIB))
from docx_titulacion import (Insertor, abrir_copia, buscar, contar_palabras, fragmento, funcion_py,  # noqa: E402,F401
                             huella_texto, insertar_referencia, quitar_numeracion, referencia_desde_markdown,
                             reemplazar_texto)
from formato_es import miles, n, pct  # noqa: E402,F401
from perfil import cargar_proyecto, escribir_json, leer_json, md5  # noqa: E402
import versionado_docx as vd  # noqa: E402

# ── Configuración del avance ─────────────────────────────────────────────
AVANCE = 2                                               # ← número del avance
PROYECTO, PERFIL, RAIZ = cargar_proyecto(Path(__file__).resolve().parent)
ORIGEN = RAIZ / (PROYECTO['documentos'].get(str(AVANCE - 1), {}).get('entregado') or PROYECTO['plantilla_original'])
SALIDA = RAIZ / 'documento' / f'Avance_{AVANCE}.docx'
REPO = (RAIZ / PROYECTO['repositorio_codigo']).resolve() if PROYECTO.get('repositorio_codigo') else None
FIG, DIAG = RAIZ / 'figuras', RAIZ / 'diagramas'


def datos(rel: str) -> dict:
    return leer_json(RAIZ / rel)


# ── Secciones: una función por sección de la plantilla ──────────────────
def seccion_2(doc, ins: Insertor):
    """2. Análisis del caso — tablas desde requerimientos/requerimientos.json."""
    from trazabilidad import tablas
    t = tablas(datos('requerimientos/requerimientos.json'))
    a = ins.titulo(buscar(doc, 'Referencias', 'Heading 1'), '2. Análisis del caso', 1, salto_pagina=True, antes=True)
    a = ins.titulo(a, '2.1 Requerimientos', 2)
    a = ins.subtitulo(a, 'Identificación de alternativas de solución')
    a = ins.parrafo(a, 'COMPLETAR: descripción, ventajas y desventajas de cada alternativa.')
    a = ins.tabla(a, t['alternativas'], 'Matriz comparativa de alternativas de solución')
    a = ins.subtitulo(a, 'Historias de usuario')
    a = ins.tabla(a, t['historias'], 'Historias de usuario con criterios de aceptación', anchos=[0.6, 2.2, 2.8, 0.9])
    a = ins.subtitulo(a, 'Requerimientos funcionales')
    a = ins.tabla(a, t['rf'], 'Requerimientos funcionales por componente')
    a = ins.subtitulo(a, 'Requerimientos no funcionales')
    a = ins.tabla(a, t['rnf'], 'Requerimientos no funcionales (ISO/IEC 25010)')
    a = ins.subtitulo(a, 'Métricas de calidad')
    a = ins.tabla(a, t['metricas'], 'Métricas de calidad y metas')
    a = ins.subtitulo(a, 'Matriz de trazabilidad')
    return ins.tabla(a, t['trazabilidad'], 'Trazabilidad de objetivos a pruebas')


def construir(doc):
    ins = Insertor(doc, PERFIL)
    seccion_2(doc, ins)
    # seccion_3_1(doc, ins); seccion_3_2(doc, ins); seccion_3_3(doc, ins) …
    for pref in ('Referencias', 'Anexos'):
        try:
            quitar_numeracion(buscar(doc, pref))
        except KeyError:
            pass
    return ins


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser()
    ap.add_argument('--forzar', action='store_true', help='sobrescribir aunque la salida se haya editado a mano')
    a = ap.parse_args()
    if PROYECTO.get('plantilla_md5') and md5(RAIZ / PROYECTO['plantilla_original']) != PROYECTO['plantilla_md5']:
        sys.exit('La plantilla ORIGINAL cambió (md5 distinto). Restáurala: nunca se edita.')
    registro = PROYECTO['documentos'].setdefault(str(AVANCE), {})
    if SALIDA.exists() and registro.get('huella') and huella_texto(SALIDA) != registro['huella'] and not a.forzar:
        copia = SALIDA.with_name(SALIDA.stem + '_editado_a_mano.docx')
        shutil.copy2(SALIDA, copia)
        sys.exit(f'{SALIDA.name} se editó a mano después de generarse. Copia guardada en {copia.name}: integra esos '
                 'cambios en este generador y vuelve a correr con --forzar.')
    if SALIDA.exists():
        archivada, _ = vd.crear_copia_versionada(SALIDA, destino=str(SALIDA.parent / 'versiones'), desde=1)
        print(f'Versión anterior archivada: {Path(archivada).relative_to(RAIZ)}')
    doc = abrir_copia(ORIGEN)
    ins = construir(doc)
    SALIDA.parent.mkdir(exist_ok=True)
    # Autoría del documento: solo los autores del proyecto.
    autores = PROYECTO.get('autores', [])
    if autores:
        doc.core_properties.author = '; '.join(autores)
        doc.core_properties.last_modified_by = autores[0]
    doc.save(str(SALIDA))
    registro.update({'generado': str(SALIDA.relative_to(RAIZ)), 'huella': huella_texto(SALIDA)})
    escribir_json(RAIZ / 'titulacion.json', PROYECTO)
    # La portada puede completarse (títulos, autores); encabezados, pies, logo, fondo y secciones no.
    mal = [t for n, t in vd.comparar_huellas(vd.huella(str(ORIGEN)), vd.huella(str(SALIDA)),
                                              estricto_preliminares=False) if n == 'FALLA']
    if mal:
        print('ZONA PROTEGIDA ALTERADA respecto del origen:')
        for detalle in mal:
            print('  -', detalle)
        print('Restaura con: huella.py restaurar <docx> --plantilla <origen> -o <salida>')
        return 1
    print(f'Generado {SALIDA.name}: {ins.n_figura} figuras y {ins.n_tabla} tablas. Siguiente: docx_a_pdf.ps1 y verificar_coherencia.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
