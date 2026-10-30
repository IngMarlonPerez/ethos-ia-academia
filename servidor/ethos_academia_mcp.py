#!/usr/bin/env python3
"""Servidor MCP «ethos-academia»: las metodologías y herramientas de Ethos IA Academia para cualquier modelo.

Funciona con cualquier cliente MCP (Claude Code o Desktop, Goose, Cline, Continue, OpenCode…) y, por lo
tanto, con el modelo que ese cliente use: Claude, GPT, Gemini o uno local con Ollama.

Expone:
  - herramientas de literatura (Scopus, OpenAlex, Unpaywall y descarga de PDF), reutilizadas del
    servidor «literatura» del plugin asistente-investigacion-cientifica;
  - `metodologias_listar` y `metodologia_leer`, para que el modelo consulte cada skill (SKILL.md);
  - cada skill como **prompt** MCP (aparece en el menú de prompts del cliente) y como **recurso**
    `skill://<plugin>/<skill>`.

Solo usa la biblioteca estándar de Python. Habla MCP por stdio, un mensaje JSON-RPC por línea.
Las claves (ELSEVIER_API_KEY, CORREO_CONTACTO) se leen del entorno y nunca se escriben en disco.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

VERSION = '1.0.0'
RAIZ = Path(__file__).resolve().parent.parent
PLUGINS = RAIZ / 'plugins'

_spec = importlib.util.spec_from_file_location(
    'literatura_mcp', PLUGINS / 'asistente-investigacion-cientifica' / 'servers' / 'literatura_mcp.py')
lit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lit)


# ── catálogo de skills ────────────────────────────────────────────────────
def _frontmatter(texto: str) -> tuple[dict, str]:
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', texto, re.S)
    if not m:
        return {}, texto
    datos = {}
    for linea in m.group(1).splitlines():
        if ':' in linea:
            k, v = linea.split(':', 1)
            datos[k.strip()] = v.strip().strip('\'"')
    return datos, texto[m.end():]


def catalogo() -> dict[str, dict]:
    """{'plugin/skill': {plugin, skill, descripcion, ruta}} de todos los SKILL.md."""
    skills = {}
    for f in sorted(PLUGINS.glob('*/skills/*/SKILL.md')):
        meta, _ = _frontmatter(f.read_text(encoding='utf-8'))
        plugin, skill = f.parents[2].name, f.parent.name
        skills[f'{plugin}/{skill}'] = {'plugin': plugin, 'skill': meta.get('name', skill),
                                       'descripcion': meta.get('description', ''), 'ruta': f}
    return skills


def _leer(clave: str) -> str:
    s = catalogo().get(clave)
    if not s:
        raise lit.ErrorHerramienta(f'No existe la metodología {clave}. Usa metodologias_listar.')
    _, cuerpo = _frontmatter(s['ruta'].read_text(encoding='utf-8'))
    # Los scripts de la skill se citan con rutas relativas: se da la carpeta base para ejecutarlos.
    return f'Carpeta base de la skill (scripts y plantillas): {s["ruta"].parent}\n\n{cuerpo}'


def h_listar(args):
    plugin = (args or {}).get('plugin')
    return [{'id': k, 'descripcion': v['descripcion']} for k, v in catalogo().items()
            if not plugin or v['plugin'] == plugin]


def h_leer(args):
    return {'id': args['id'], 'contenido': _leer(args['id'])}


HERRAMIENTAS = dict(lit.HERRAMIENTAS)
HERRAMIENTAS['metodologias_listar'] = (h_listar, lit._herramienta(
    'metodologias_listar', 'Listar metodologías académicas',
    'Lista las metodologías (skills) de Ethos IA Academia: revisión sistemática PRISMA, APA 7, matrices, '
    'titulación de TI, economía, prácticas y creación de empresa. Úsala para elegir cuál seguir.',
    {'plugin': {'type': 'string', 'description': 'Filtra por plugin, p. ej. asistente-investigacion-cientifica'}}, []))
HERRAMIENTAS['metodologia_leer'] = (h_leer, lit._herramienta(
    'metodologia_leer', 'Leer una metodología',
    'Devuelve las instrucciones completas de una metodología (id plugin/skill). Léela entera y síguela paso a paso '
    'antes de producir el entregable.',
    {'id': {'type': 'string', 'description': 'Id devuelto por metodologias_listar, p. ej. '
                                             'asistente-investigacion-cientifica/revision-sistematica'}}, ['id']))

INSTRUCCIONES = (
    'Ethos IA Academia: metodologías de investigación y titulación con herramientas verificables. Antes de una tarea '
    'académica, llama a metodologias_listar, elige la metodología y léela con metodologia_leer. Reglas: solo fuentes '
    'académicas con DOI leídas en texto completo; cada cifra se verifica en su fuente; la IA no figura como autora. '
    + lit.INSTRUCCIONES)


# ── protocolo ─────────────────────────────────────────────────────────────
def _prompts():
    return [{'name': k.replace('/', '__'), 'title': v['skill'], 'description': v['descripcion'],
             'arguments': [{'name': 'tarea', 'description': 'Qué se quiere lograr', 'required': False}]}
            for k, v in catalogo().items()]


def _atender(msg):
    metodo, id_ = msg.get('method'), msg.get('id')
    if id_ is None:
        return
    p = msg.get('params') or {}
    responder = lit._responder
    if metodo == 'initialize':
        pedida = p.get('protocolVersion')
        responder(id_, {'protocolVersion': pedida if pedida in lit.PROTOCOLOS else lit.PROTOCOLOS[0],
                        'capabilities': {'tools': {'listChanged': False}, 'prompts': {'listChanged': False},
                                         'resources': {'listChanged': False}},
                        'serverInfo': {'name': 'ethos-academia', 'title': 'Ethos IA Academia', 'version': VERSION},
                        'instructions': INSTRUCCIONES})
    elif metodo == 'prompts/list':
        responder(id_, {'prompts': _prompts()})
    elif metodo == 'prompts/get':
        clave = p.get('name', '').replace('__', '/')
        try:
            texto = _leer(clave)
        except lit.ErrorHerramienta as e:
            responder(id_, error={'code': -32602, 'message': str(e)})
            return
        tarea = (p.get('arguments') or {}).get('tarea')
        if tarea:
            texto += f'\n\n---\nTarea de la persona usuaria: {tarea}'
        responder(id_, {'description': catalogo()[clave]['descripcion'],
                        'messages': [{'role': 'user', 'content': {'type': 'text', 'text': texto}}]})
    elif metodo == 'resources/list':
        responder(id_, {'resources': [{'uri': f'skill://{k}', 'name': k, 'description': v['descripcion'],
                                       'mimeType': 'text/markdown'} for k, v in catalogo().items()]})
    elif metodo == 'resources/read':
        uri = p.get('uri', '')
        try:
            texto = _leer(uri.removeprefix('skill://'))
        except lit.ErrorHerramienta as e:
            responder(id_, error={'code': -32602, 'message': str(e)})
            return
        responder(id_, {'contents': [{'uri': uri, 'mimeType': 'text/markdown', 'text': texto}]})
    else:
        # tools/list, tools/call y ping: mismo manejo que «literatura», con el catálogo ampliado.
        lit.HERRAMIENTAS = HERRAMIENTAS
        lit._atender(msg)


def main():
    lit._log(f'ethos-academia iniciado (v{VERSION}, {len(catalogo())} metodologías)')
    for linea in iter(sys.stdin.buffer.readline, b''):
        linea = linea.strip()
        if not linea:
            continue
        try:
            msg = json.loads(linea.decode('utf-8'))
        except json.JSONDecodeError:
            lit._responder(None, error={'code': -32700, 'message': 'JSON no válido'})
            continue
        for m in (msg if isinstance(msg, list) else [msg]):
            _atender(m)


if __name__ == '__main__':
    main()
