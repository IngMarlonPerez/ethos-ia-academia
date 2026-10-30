# -*- coding: utf-8 -*-
"""
pipeline.py — las etapas del proyecto de titulación de TI y su tablero.

El estado vive en titulacion.json → "etapas"; 00_Control_Titulacion.md se
regenera desde ahí (no se edita a mano).
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

ETAPAS = [
    {'n': 0, 'nombre': 'Inicio', 'skills': ['iniciar-titulacion'], 'seccion': '—', 'avance': '—',
     'control': 'Perfil confirmado; estructura creada; plantilla oficial copiada intacta (md5 igual).'},
    {'n': 1, 'nombre': 'Planteamiento y objetivos', 'skills': ['planteamiento-y-objetivos'], 'seccion': '1.1, 1.2', 'avance': '1',
     'control': 'Objetivos con verbo de Bloom y qué/cómo/para qué; matriz de consistencia; cifras del problema con DOI.'},
    {'n': 2, 'nombre': 'Literatura y trabajos previos',
     'skills': ['asistente-investigacion-cientifica:revision-sistematica', 'trabajos-previos'], 'seccion': '1.3', 'avance': '1',
     'control': '≥ mínimo de trabajos previos leídos completos, con ficha y página; columnas Arquitectura y Tecnologías llenas; vacío redactado.'},
    {'n': 3, 'nombre': 'Análisis y requerimientos', 'skills': ['analisis-requerimientos', 'proteccion-datos'], 'seccion': '2.1', 'avance': '2',
     'control': '≥ 3 alternativas; cada objetivo con HU, RF y métrica; ningún RF sin prueba; RNF de privacidad.'},
    {'n': 4, 'nombre': 'Selección tecnológica', 'skills': ['seleccion-tecnologica'], 'seccion': '3.3 (a)', 'avance': '2',
     'control': '≥ 3 candidatas por decisión con fuente por celda; ganadora estable en la sensibilidad; ADR.'},
    {'n': 5, 'nombre': 'Arquitectura', 'skills': ['decision-arquitectura'], 'seccion': '3.2 (a)', 'avance': '2',
     'control': '≥ 3 estilos comparados con evidencia; ADR; el código cumple las reglas de arquitectura.'},
    {'n': 6, 'nombre': 'Metodología', 'skills': ['metodologia-desarrollo'], 'seccion': '3.1', 'avance': '2',
     'control': 'Cada fase con entregable (archivo existente del repo) y resultado verificable.'},
    {'n': 7, 'nombre': 'Diseño (UML y datos)', 'skills': ['diseno-uml-datos'], 'seccion': '3.2 (b), (c)', 'avance': '2',
     'control': 'Todos los UML exigidos por el perfil; diccionario generado del esquema real sin columnas sin descripción.'},
    {'n': 8, 'nombre': 'Desarrollo y evidencias', 'skills': ['desarrollo-y-evidencias', 'proteccion-datos'], 'seccion': '3.3 (b), (c)', 'avance': '2',
     'control': 'Pruebas en verde; cada métrica de 2.1 con valor en un artefacto JSON; código extraído en vivo.'},
    {'n': 9, 'nombre': 'Conclusiones', 'skills': ['conclusiones-recomendaciones'], 'seccion': '4', 'avance': '3',
     'control': 'Una conclusión por objetivo con su cifra medida; nada sin medir.'},
    {'n': 10, 'nombre': 'Documento y control de calidad',
     'skills': ['documento-titulacion', 'matrices-titulacion', 'verificar-coherencia', 'asistente-investigacion-cientifica:redaccion-apa7'],
     'seccion': 'todas', 'avance': 'cada avance',
     'control': 'verificar_coherencia.py sin errores; PDF con páginas mínimas; revisores APA y tutor atendidos; huella.py verificar sin alteraciones y aserciones.py vigentes.'},
    {'n': 11, 'nombre': 'Retroalimentación del tutor', 'skills': ['retroalimentacion-tutor'], 'seccion': '—', 'avance': 'tras cada avance',
     'control': 'Cada observación con su cambio, lugar y evidencia; registro de cambios.'},
    {'n': 12, 'nombre': 'Sustentación y entrega', 'skills': ['entrega-y-sustentacion', 'asistente-investigacion-cientifica:paquete-evidencias'],
     'seccion': 'Anexos', 'avance': 'final',
     'control': 'Demo reproducible; capturas; guion; diapositivas y póster con qa_pptx.py sin problemas; simulacro con revisor-tribunal; videos; carpeta de entrega completa; RIS = referencias.'},
]

ESTADOS = {'pendiente': '⬜', 'en_curso': '🟨', 'cerrada': '✅', 'no_aplica': '➖'}


def estado_inicial() -> dict:
    return {str(e['n']): {'estado': 'pendiente', 'fecha': None, 'nota': ''} for e in ETAPAS}


def render_tablero(proyecto: dict) -> str:
    etapas = proyecto.get('etapas') or estado_inicial()
    lineas = [
        f"# Tablero del proyecto de titulación — {proyecto.get('tema', '(sin tema)')}",
        '',
        f"Institución: {proyecto.get('institucion', '')} · Perfil: `{proyecto.get('perfil', 'unemi')}` · "
        f"Avance actual: {proyecto.get('avance_actual', 1)}",
        f"Autores: {', '.join(proyecto.get('autores', [])) or '—'} · Tutores: {', '.join(proyecto.get('tutores', [])) or '—'}",
        '',
        'Generado desde `titulacion.json` por el Asesor de Proyecto de Titulación de TI. No editar a mano: '
        'pide «marca la etapa N como cerrada».',
        '',
        '| | Etapa | Skill(s) | Sección | Avance | Control de salida | Fecha | Nota |',
        '|---|---|---|---|---|---|---|---|',
    ]
    for e in ETAPAS:
        st = etapas.get(str(e['n']), {})
        icono = ESTADOS.get(st.get('estado', 'pendiente'), '⬜')
        skills = ', '.join(f'`{s}`' for s in e['skills'])
        lineas.append(f"| {icono} | {e['n']} · {e['nombre']} | {skills} | {e['seccion']} | {e['avance']} | "
                      f"{e['control']} | {st.get('fecha') or ''} | {st.get('nota', '')} |")
    lineas += ['', 'Leyenda: ⬜ pendiente · 🟨 en curso · ✅ cerrada (control cumplido) · ➖ no aplica.', '']
    return '\n'.join(lineas)


def etapa_actual(proyecto: dict) -> dict:
    etapas = proyecto.get('etapas') or estado_inicial()
    for e in ETAPAS:
        if etapas.get(str(e['n']), {}).get('estado') in ('pendiente', 'en_curso'):
            return e
    return ETAPAS[-1]


def marcar(proyecto: dict, n: int, estado: str, nota: str = '') -> None:
    if estado not in ESTADOS:
        raise ValueError(f'Estado inválido: {estado}. Usa {list(ESTADOS)}')
    etapas = proyecto.setdefault('etapas', estado_inicial())
    etapas[str(n)] = {'estado': estado, 'fecha': date.today().isoformat(), 'nota': nota}


def escribir_tablero(raiz: Path, proyecto: dict) -> Path:
    ruta = raiz / '00_Control_Titulacion.md'
    ruta.write_text(render_tablero(proyecto), encoding='utf-8')
    return ruta
