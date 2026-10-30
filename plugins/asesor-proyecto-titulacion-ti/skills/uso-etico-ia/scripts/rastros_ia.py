# -*- coding: utf-8 -*-
"""
rastros_ia.py — busca rastros de herramientas de IA generativa en lo que se
va a entregar o publicar, y revisa la autoría de los archivos de Office.

La IA no es autora: el nombre de la herramienta, las líneas de coautoría
automáticas y las frases en voz de asistente no deben quedar en el código, los
comentarios, los documentos, los metadatos ni los commits. Lo único que las
nombra es el anexo de uso ético (carpeta local que se excluye con --excluir).

Busca:
  - nombres de herramientas (por defecto: Claude, Anthropic, ChatGPT, Copilot;
    se cambian con --nombres). Gemini, Groq u otros proveedores que el PRODUCTO
    usa como componente no se buscan por defecto;
  - líneas de coautoría o firma automática (Co-Authored-By de un asistente,
    «Generated with», enlaces de sesión);
  - frases en voz de asistente («a pedido del usuario», «como asistente»…);
  - autor y último modificador de .docx/.xlsx/.pptx que no estén en --autores.

Con --fijar-autoria reescribe esos metadatos con los autores (solo en archivos
propios; nunca en la plantilla oficial, que se pasa con --excluir).

Uso:
    python rastros_ia.py <raíz> [--lista archivos.txt] [--autores "A; B"]
                          [--excluir ANEXO_USO_ETICO_IA] [--fijar-autoria]
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

NOMBRES = ['Claude', 'Anthropic', 'ChatGPT', 'Copilot']
FIRMAS = [r'co-authored-by:\s*[^\n]*(?:noreply@anthropic\.com|copilot|chatgpt|claude)', r'generated with \[?(?:claude|chatgpt|copilot)',
          r'claude[-_ ]session', r'🤖']
VOZ_ASISTENTE = [r'a pedido del usuario', r'regla del usuario', r'pidi[óo] el usuario', r'como asistente',
                 r'como modelo de lenguaje', r'lo confirm[ée] prob[áa]ndolo']
EXCLUIR_DIRS = {'.git', 'node_modules', 'venv', '.venv', '__pycache__', 'dist', 'build', '.pytest_cache', 'site-packages'}
TEXTO = {'.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.md', '.txt', '.sql', '.ps1', '.sh', '.css', '.html', '.yml',
         '.yaml', '.toml', '.ini', '.cfg', '.ris', '.mmd', '.csv', '.example', '.gitignore', '.env'}
OFFICE = {'.docx', '.xlsx', '.pptx'}


def archivos(raiz: Path, lista: Path | None, excluir: list[str]) -> list[Path]:
    excl = [e.strip('/\\').replace('\\', '/') for e in excluir]
    if lista:
        rutas = [raiz / l.strip() for l in lista.read_text(encoding='utf-8').splitlines() if l.strip()]
    else:
        rutas = [p for p in raiz.rglob('*') if p.is_file() and not (set(p.relative_to(raiz).parts) & EXCLUIR_DIRS)]
    salida = []
    for p in rutas:
        if not p.is_file():
            continue
        rel = p.relative_to(raiz).as_posix()
        if any(rel == e or rel.startswith(e + '/') for e in excl):
            continue
        salida.append(p)
    return salida


def patron(nombres: list[str]) -> re.Pattern:
    partes = [rf'\b{re.escape(n)}\b' for n in nombres] + FIRMAS + VOZ_ASISTENTE
    return re.compile('(?i)(' + '|'.join(partes) + ')')


def leer_core(ruta: Path) -> str | None:
    try:
        with zipfile.ZipFile(ruta) as z:
            return z.read('docProps/core.xml').decode('utf-8')
    except (KeyError, zipfile.BadZipFile):
        return None


def autores_core(xml: str) -> tuple[str, str]:
    c = re.search(r'<dc:creator>(.*?)</dc:creator>', xml or '')
    m = re.search(r'<cp:lastModifiedBy>(.*?)</cp:lastModifiedBy>', xml or '')
    return (c.group(1) if c else ''), (m.group(1) if m else '')


def fijar_autoria(ruta: Path, autores: list[str]) -> None:
    """Reescribe creator y lastModifiedBy dentro del zip sin tocar el resto."""
    creador, ultimo = '; '.join(autores), autores[0]
    with zipfile.ZipFile(ruta) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    fd, nombre_tmp = tempfile.mkstemp(suffix=ruta.suffix)
    os.close(fd)
    tmp = Path(nombre_tmp)
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for info, datos in items:
            if info.filename == 'docProps/core.xml':
                xml = datos.decode('utf-8')
                for etiqueta, valor in (('dc:creator', creador), ('cp:lastModifiedBy', ultimo)):
                    if f'<{etiqueta}>' in xml:
                        xml = re.sub(rf'<{etiqueta}>.*?</{etiqueta}>', f'<{etiqueta}>{valor}</{etiqueta}>', xml)
                    elif f'<{etiqueta}/>' in xml:
                        xml = xml.replace(f'<{etiqueta}/>', f'<{etiqueta}>{valor}</{etiqueta}>')
                    else:
                        xml = xml.replace('</cp:coreProperties>', f'<{etiqueta}>{valor}</{etiqueta}></cp:coreProperties>')
                datos = xml.encode('utf-8')
            z.writestr(info, datos)
    shutil.move(str(tmp), str(ruta))


def revisar(raiz: Path, rutas: list[Path], nombres: list[str], autores: list[str], fijar: bool) -> tuple[list, list]:
    pat = patron(nombres)
    texto, office = [], []
    permitidos = {a.strip().lower() for a in autores}
    for p in rutas:
        rel = p.relative_to(raiz).as_posix()
        suf = p.suffix.lower() if p.suffix else p.name.lower()
        if suf in OFFICE:
            xml = leer_core(p)
            if xml is None:
                continue
            c, m = autores_core(xml)
            nombres_doc = {x.strip().lower() for x in re.split(r'[;,]', c) if x.strip()} | ({m.strip().lower()} if m.strip() else set())
            ajenos = nombres_doc - permitidos if permitidos else set()
            if pat.search(c + ' ' + m) or ajenos:
                office.append(f'{rel}: autor «{c}», último cambio «{m}»')
                if fijar and autores:
                    fijar_autoria(p, autores)
            continue
        if suf not in TEXTO and not p.name.endswith('.example'):
            continue
        try:
            contenido = p.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        for i, linea in enumerate(contenido.splitlines(), 1):
            m = pat.search(linea)
            if m:
                texto.append(f'{rel}:{i}: «{m.group(0)}» … {linea.strip()[:100]}')
    return texto, office


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('raiz')
    ap.add_argument('--lista', help='archivo con las rutas a revisar (p. ej. salida de git ls-files)')
    ap.add_argument('--nombres', help='nombres a buscar separados por coma (por defecto: ' + ', '.join(NOMBRES) + ')')
    ap.add_argument('--autores', default='', help='autores permitidos en los metadatos, separados por ;')
    ap.add_argument('--excluir', action='append', default=[], help='carpeta o archivo a omitir (relativo a la raíz)')
    ap.add_argument('--fijar-autoria', action='store_true')
    a = ap.parse_args()
    raiz = Path(a.raiz).resolve()
    nombres = [x.strip() for x in a.nombres.split(',')] if a.nombres else NOMBRES
    autores = [x.strip() for x in a.autores.split(';') if x.strip()]
    rutas = archivos(raiz, Path(a.lista) if a.lista else None, a.excluir)
    texto, office = revisar(raiz, rutas, nombres, autores, a.fijar_autoria)
    print(f'Archivos revisados: {len(rutas)}')
    for x in texto:
        print('  RASTRO:', x)
    for x in office:
        print('  METADATOS:', x + (' → corregido' if a.fijar_autoria and autores else ''))
    if not texto and not office:
        print('Sin rastros de herramientas de IA ni autores ajenos.')
    pendientes = len(texto) + (0 if a.fijar_autoria and autores else len(office))
    return 1 if pendientes else 0


if __name__ == '__main__':
    sys.exit(main())
