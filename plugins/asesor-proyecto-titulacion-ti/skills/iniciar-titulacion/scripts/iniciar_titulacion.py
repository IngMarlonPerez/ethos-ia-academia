# -*- coding: utf-8 -*-
"""
iniciar_titulacion.py — crea la estructura de un proyecto de titulación de TI.

NUNCA sobrescribe: si un archivo o carpeta ya existe, lo deja como está y lo
informa. Crea:

  titulacion.json                 datos del proyecto + estado de las etapas
  00_Control_Titulacion.md        tablero del pipeline (se regenera desde el JSON)
  _automatizacion/                generadores del documento y archivos de control
      Plantilla_ORIGINAL.docx     copia INTACTA de la plantilla oficial (md5 en titulacion.json)
      coherencia.json             cifras clave y reglas que revisa verificar_coherencia.py
      datos_matrices.json         consistencia, PRISMA y coherencia literatura-código (matrices_titulacion.py)
  literatura/                     búsquedas (B1_…) del plugin de investigación + trabajos_previos.json
  requerimientos/requerimientos.json
  decisiones/  decisiones/adr/    matrices de decisión (DT-…json) y ADR
  diagramas/  figuras/            Mermaid (.mmd → .png) y figuras de resultados
  documento/                      avances generados (.docx/.pdf) y registros de cambios
  retroalimentacion/              observaciones de los tutores y su atención
  entregables/                    estructura de la carpeta de entrega del perfil

Uso:
    python iniciar_titulacion.py "<carpeta>" --tema "<tema>" --carrera "<carrera>"
        --autores "A; B" [--tutores "T1; T2"] [--perfil unemi | ruta/perfil.json]
        [--plantilla "<plantilla oficial.docx>"] [--repo "<ruta del código>"]
        [--tipo software datos_ml ia_llm redes seguridad]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLUGIN / 'scripts_comunes'))
from perfil import cargar_perfil, escribir_json, md5  # noqa: E402
from pipeline import escribir_tablero, estado_inicial  # noqa: E402

TIPOS = ['software', 'datos_ml', 'ia_llm', 'redes', 'seguridad']


def crear_carpeta(ruta: Path, creados: list, existentes: list):
    if ruta.exists():
        existentes.append(ruta)
    else:
        ruta.mkdir(parents=True)
        creados.append(ruta)


def crear_archivo(ruta: Path, contenido: str | dict, creados: list, existentes: list):
    if ruta.exists():
        existentes.append(ruta)
        return
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(contenido, dict):
        escribir_json(ruta, contenido)
    else:
        ruta.write_text(contenido, encoding='utf-8')
    creados.append(ruta)


def plantilla(nombre: str) -> dict:
    """Plantillas JSON que traen las skills (se copian al proyecto)."""
    rutas = {
        'coherencia': PLUGIN / 'skills/verificar-coherencia/plantillas/coherencia.json',
        'trabajos_previos': PLUGIN / 'skills/trabajos-previos/plantillas/trabajos_previos.json',
        'requerimientos': PLUGIN / 'skills/analisis-requerimientos/plantillas/requerimientos.json',
        'matrices': PLUGIN / 'skills/matrices-titulacion/plantillas/datos_matrices.json',
    }
    return json.loads(rutas[nombre].read_text(encoding='utf-8'))


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('carpeta')
    ap.add_argument('--tema', required=True)
    ap.add_argument('--carrera', default='Ingeniería en Tecnologías de la Información')
    ap.add_argument('--autores', required=True, help='separados por punto y coma')
    ap.add_argument('--tutores', default='')
    ap.add_argument('--perfil', default='unemi')
    ap.add_argument('--plantilla', help='plantilla oficial (.docx) de la universidad')
    ap.add_argument('--repo', default='', help='ruta del repositorio de código (relativa a la carpeta o absoluta)')
    ap.add_argument('--tipo', nargs='*', default=['software'], choices=TIPOS)
    a = ap.parse_args()

    raiz = Path(a.carpeta).resolve()
    raiz.mkdir(parents=True, exist_ok=True)
    perfil = cargar_perfil(a.perfil, raiz)
    creados: list[Path] = []
    existentes: list[Path] = []

    for sub in ['_automatizacion', 'literatura', 'requerimientos', 'decisiones/adr', 'diagramas', 'figuras',
                'documento', 'retroalimentacion']:
        crear_carpeta(raiz / sub, creados, existentes)
    ent = perfil.get('entrega', {})
    for c in ent.get('carpetas', []):
        crear_carpeta(raiz / ent.get('carpeta_raiz', 'entregables') / c['ruta'], creados, existentes)

    md5_plantilla = None
    if a.plantilla:
        origen = Path(a.plantilla)
        destino = raiz / '_automatizacion' / 'Plantilla_ORIGINAL.docx'
        if destino.exists():
            existentes.append(destino)
        else:
            shutil.copy2(origen, destino)
            creados.append(destino)
        md5_plantilla = md5(destino)
        if md5_plantilla != md5(origen):
            print('AVISO: la copia de la plantilla no coincide con el original (ya existía una distinta).')

    proyecto = {
        'version': 1,
        'tema': a.tema,
        'titulo': '',
        'carrera': a.carrera,
        'institucion': perfil.get('institucion', ''),
        'perfil': a.perfil,
        'autores': [x.strip() for x in a.autores.split(';') if x.strip()],
        'tutores': [x.strip() for x in a.tutores.split(';') if x.strip()],
        'tipo_proyecto': a.tipo,
        'repositorio_codigo': a.repo,
        'avance_actual': 1,
        'plantilla_original': '_automatizacion/Plantilla_ORIGINAL.docx' if a.plantilla else '',
        'plantilla_md5': md5_plantilla,
        'documentos': {},
        'etapas': estado_inicial(),
    }
    ruta_proy = raiz / 'titulacion.json'
    if ruta_proy.exists():
        existentes.append(ruta_proy)
        proyecto = json.loads(ruta_proy.read_text(encoding='utf-8'))
        if md5_plantilla and not proyecto.get('plantilla_md5'):
            proyecto['plantilla_original'] = '_automatizacion/Plantilla_ORIGINAL.docx'
            proyecto['plantilla_md5'] = md5_plantilla
            escribir_json(ruta_proy, proyecto)
            print('titulacion.json: se registró la plantilla oficial y su md5.')
    else:
        escribir_json(ruta_proy, proyecto)
        creados.append(ruta_proy)
    tablero = raiz / '00_Control_Titulacion.md'
    if tablero.exists():
        existentes.append(tablero)
    else:
        escribir_tablero(raiz, proyecto)
        creados.append(tablero)

    crear_archivo(raiz / '_automatizacion/coherencia.json', plantilla('coherencia'), creados, existentes)
    crear_archivo(raiz / 'literatura/trabajos_previos.json', plantilla('trabajos_previos'), creados, existentes)
    crear_archivo(raiz / 'requerimientos/requerimientos.json', plantilla('requerimientos'), creados, existentes)
    crear_archivo(raiz / '_automatizacion/datos_matrices.json', plantilla('matrices'), creados, existentes)

    print(f'Proyecto de titulación en {raiz} (perfil {a.perfil}).')
    print(f'Creados ({len(creados)}):', *[f'  + {p.relative_to(raiz)}' for p in creados], sep='\n')
    if existentes:
        print(f'Ya existían, sin cambios ({len(existentes)}):', *[f'  = {p.relative_to(raiz)}' for p in existentes], sep='\n')
    if not a.plantilla and not proyecto.get('plantilla_md5'):
        print('Falta la plantilla oficial: vuelve a correr con --plantilla "<archivo.docx>" cuando la tengas.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
