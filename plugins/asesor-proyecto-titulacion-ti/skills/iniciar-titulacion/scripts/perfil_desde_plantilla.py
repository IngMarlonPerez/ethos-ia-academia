# -*- coding: utf-8 -*-
"""
perfil_desde_plantilla.py — propone el perfil institucional a partir de la
plantilla en blanco (.docx) del trabajo de titulación de una universidad.

Lee:
  - los títulos (Heading 1/2 o Título 1/2) → secciones numeradas 1, 1.1, 2 …;
  - los párrafos de guía debajo de cada título y los mínimos de páginas
    («mínimo de N páginas»). Si una sección tiene varios mínimos, cada uno
    es una PARTE (p. ej. 3.2 Diseño = arquitectura 2 + UML 2 + modelo ER 2);
  - los límites del Resumen («máximo de 150 palabras», «máximo cinco palabras»);
  - «al menos N trabajos», «mínimo N referencias de los últimos N años»;
  - las tablas de preguntas («¿Qué aporta de nuevo…?») y del anexo de actividades;
  - márgenes, papel y tamaños de los títulos.

El resultado es un BORRADOR: la lista "_revisar" dice qué confirmar con la
usuaria antes de usarlo. Los campos que la plantilla no trae (avance de cada
sección, skill que la atiende, UML exigidos, carpeta de entrega) se proponen
con los valores del perfil UNEMI cuando el título coincide.

Uso:
    python perfil_desde_plantilla.py "<plantilla.docx>" --id <id> --institucion "<nombre>" [--salida perfil.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

import docx

NUMEROS = {'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5, 'seis': 6, 'siete': 7, 'ocho': 8,
           'nueve': 9, 'diez': 10, 'veinte': 20, 'treinta': 30}
ESPECIALES = {'resumen': 'resumen', 'abstract': 'abstract', 'referencias': 'referencias',
              'bibliografia': 'referencias', 'anexos': 'anexos'}

# Qué skill y qué avance corresponden a cada sección, cuando el título se parece
# a los de la plantilla UNEMI (se usan solo como propuesta).
SUGERENCIAS = [
    (r'^descripci', 'planteamiento-y-objetivos', 1),
    (r'^prop[oó]sito', 'planteamiento-y-objetivos', 1),
    (r'^base conceptual|^marco te[oó]rico|^estado del arte', 'trabajos-previos', 1),
    (r'^requerimientos|^an[aá]lisis', 'analisis-requerimientos', 2),
    (r'^metodolog', 'metodologia-desarrollo', 2),
    (r'^dise[nñ]o', 'decision-arquitectura', 2),
    (r'^desarrollo', 'desarrollo-y-evidencias', 2),
    (r'^conclusiones', 'conclusiones-recomendaciones', 3),
    (r'^introducci', 'planteamiento-y-objetivos', 1),
]


def sin_tildes(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower().strip()


def numero(texto: str) -> int | None:
    t = sin_tildes(texto)
    return int(t) if t.isdigit() else NUMEROS.get(t)


def nivel_titulo(p) -> int | None:
    nombre = sin_tildes(p.style.name if p.style is not None else '')
    m = re.match(r'(heading|titulo)\s*(\d)', nombre)
    return int(m.group(2)) if m and p.text.strip() else None


def sugerir(titulo: str) -> tuple[str | None, int | None]:
    t = sin_tildes(titulo)
    for patron, skill, avance in SUGERENCIAS:
        if re.search(patron, t):
            return skill, avance
    return None, None


def extraer(ruta: Path, ident: str, institucion: str) -> dict:
    d = docx.Document(str(ruta))
    revisar: list[str] = []
    secciones: list[dict] = []
    requisitos: dict = {}
    actual: dict | None = None
    guia: list[str] = []
    n1 = n2 = 0

    def cerrar_parte(minimo: int | None):
        nonlocal guia
        if actual is None:
            return
        texto = ' '.join(guia).strip()
        if minimo is not None:
            actual.setdefault('partes', []).append({'guia': texto, 'min_paginas': minimo})
        elif texto:
            actual['guia'] = (actual.get('guia', '') + ' ' + texto).strip()
        guia = []

    for p in d.paragraphs:
        texto = p.text.strip()
        nivel = nivel_titulo(p)
        if nivel in (1, 2):
            cerrar_parte(None)
            limpio = re.sub(r'^\d+(\.\d+)*\.?\s+', '', texto)
            clave = sin_tildes(limpio).rstrip('.')
            if nivel == 1 and clave in ESPECIALES:
                ident_s, titulo_num = ESPECIALES[clave], limpio
            elif nivel == 1 and clave.startswith('anexo'):
                ident_s, titulo_num = ('anexo_academico' if 'academ' in clave else 'anexos'), limpio
            elif nivel == 1:
                n1, n2 = n1 + 1, 0
                ident_s, titulo_num = str(n1), f'{n1}. {limpio}'
            else:
                n2 += 1
                ident_s, titulo_num = f'{n1}.{n2}', f'{n1}.{n2} {limpio}'
            skill, avance = sugerir(limpio)
            actual = {'id': ident_s, 'titulo': limpio, 'marca_pdf': titulo_num, 'nivel': nivel}
            if skill:
                actual['skill'], actual['avance'] = skill, avance
            secciones.append(actual)
            continue
        if not texto or actual is None:
            continue
        t = sin_tildes(texto)
        m = re.search(r'minimo de (\w+) paginas?', t)
        if m:
            cerrar_parte(numero(m.group(1)))
            continue
        m = re.search(r'maximo de (\w+) palabras', t)
        if m and actual['id'] == 'resumen':
            actual.setdefault('reglas', {})['max_palabras'] = numero(m.group(1))
        m = re.search(r'palabras clave\w*:?\s*maximo (\w+)', t)
        if m and actual['id'] == 'resumen':
            actual.setdefault('reglas', {})['max_palabras_clave'] = numero(m.group(1))
            continue
        m = re.search(r'al menos (\w+) trabajos', t)
        if m:
            requisitos['min_trabajos_previos'] = numero(m.group(1))
        m = re.search(r'minimo (\w+) referencias(?: de los ultimos (\w+) anos)?', t)
        if m:
            requisitos['min_referencias'] = numero(m.group(1))
            if m.group(2):
                requisitos['anios_referencias'] = numero(m.group(2))
            if 'ieee' in t:
                requisitos['estilos_citas_admitidos'] = ['APA 7', 'IEEE']
        guia.append(texto)
    cerrar_parte(None)

    for s in secciones:
        partes = s.get('partes', [])
        if len(partes) == 1:
            s['min_paginas'] = partes[0]['min_paginas']
            s['guia'] = (s.get('guia', '') + ' ' + partes[0]['guia']).strip()
            del s['partes']
        elif partes:
            s['min_paginas'] = sum(pt['min_paginas'] for pt in partes)
            for i, pt in enumerate(partes):
                pt['id'] = f"{s['id']}{'abcdefgh'[i]}"

    for t in d.tables:
        primera = sin_tildes(t.rows[0].cells[0].text)
        if primera.startswith('¿que aporta') or primera.startswith('que aporta'):
            requisitos['preguntas_esta_relacionado'] = [r.cells[0].text.strip() for r in t.rows if r.cells[0].text.strip()]
        elif primera == 'fecha':
            texto = sin_tildes(' '.join(c.text for r in t.rows for c in r.cells))
            m1 = re.search(r'minimo (\w+) actividades', texto)
            m2 = re.search(r'al menos (\w+) interacciones', texto)
            requisitos['anexo'] = {'columnas': [c.text.strip() for c in t.rows[0].cells],
                                   'min_actividades': numero(m1.group(1)) if m1 else None,
                                   'min_interacciones_tutor': numero(m2.group(1)) if m2 else None}
        elif primera.startswith('no.') and len(t.columns) == 2:
            requisitos.setdefault('anexo', {})['tabla_videos'] = [c.text.strip() for c in t.rows[0].cells]
            revisar.append('Anexo: la plantilla trae una tabla de videos vacía; confirmar qué videos se piden.')
        elif primera.startswith('areas'):
            # Las casillas de verificación son símbolos de la fuente Wingdings (área privada U+F000–U+F0FF).
            areas = re.split(r'[-]|\s{2,}', t.rows[1].cells[0].text.strip())
            requisitos['anexo_academico_areas'] = [a.strip() for a in areas if a.strip()]

    sec = d.sections[0]
    estilos = d.styles

    def pt(nombre):
        try:
            f = estilos[nombre].font.size
            return f.pt if f else None
        except KeyError:
            return None

    formato = {
        'papel_cm': [round(sec.page_width.cm, 1), round(sec.page_height.cm, 1)],
        'margenes_cm': {'izquierdo': round(sec.left_margin.cm, 2), 'derecho': round(sec.right_margin.cm, 2),
                        'superior': round(sec.top_margin.cm, 2), 'inferior': round(sec.bottom_margin.cm, 2)},
        'titulo1_pt': pt('Heading 1'), 'titulo2_pt': pt('Heading 2'),
    }
    revisar += [
        'Fuente, tamaño e interlineado del cuerpo: la plantilla no los fija en el estilo Normal; confirmar con la guía.',
        'Avance al que pertenece cada sección y skill que la atiende (propuestas por coincidencia de título).',
        'Diagramas UML exigidos y estructura de la carpeta de entrega (no están en la plantilla).',
    ]
    for s in secciones:
        if s['id'][0].isdigit() and 'avance' not in s:
            revisar.append(f"Sección {s['marca_pdf']}: sin avance ni skill sugeridos.")
    return {'id': ident, 'institucion': institucion, 'plantilla': {'archivo': ruta.name},
            'formato': formato, 'secciones': secciones, 'requisitos': requisitos, '_revisar': revisar}


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('plantilla')
    ap.add_argument('--id', required=True, help='identificador corto del perfil, p. ej. unemi')
    ap.add_argument('--institucion', required=True)
    ap.add_argument('--salida', help='JSON de salida (por defecto, se imprime)')
    a = ap.parse_args()
    perfil = extraer(Path(a.plantilla), a.id, a.institucion)
    texto = json.dumps(perfil, indent=2, ensure_ascii=False)
    if a.salida:
        Path(a.salida).write_text(texto + '\n', encoding='utf-8')
        mins = [(s['id'], s.get('min_paginas')) for s in perfil['secciones'] if s.get('min_paginas')]
        print(f'Perfil borrador en {a.salida}. Mínimos de páginas: {mins}')
        print('Por revisar:', *perfil['_revisar'], sep='\n  - ')
    else:
        sys.stdout.reconfigure(encoding='utf-8')
        print(texto)
    return 0


if __name__ == '__main__':
    sys.exit(main())
