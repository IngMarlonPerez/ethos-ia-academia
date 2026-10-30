# -*- coding: utf-8 -*-
"""
buscar_secretos.py — busca en el repositorio contraseñas, claves de API y
tokens escritos en el código, y cédulas ecuatorianas VÁLIDAS (posibles datos
personales reales) en archivos de datos.

Revisa además que `.env` esté en .gitignore y que git no lo esté siguiendo.
Muestra cada hallazgo ENMASCARADO (nunca imprime el secreto completo).

Los valores en carpetas o archivos de prueba se listan aparte como aviso
(deben ser ficticios); no hacen fallar. Para permitir un falso positivo, agrega en esa línea el comentario
`secreto-permitido` o pasa --ignorar con una expresión regular de rutas.

Uso:
    python buscar_secretos.py <repo> [--ignorar "tests/fixtures/.*"] [--sin-cedulas]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

EXCLUIR = {'node_modules', '.git', 'venv', '.venv', '__pycache__', 'dist', 'build', '.next', 'site-packages', 'coverage',
           '.pytest_cache', 'target', 'bin', 'obj'}
BINARIOS = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.docx', '.xlsx', '.pptx', '.zip', '.mp4', '.ico', '.woff', '.woff2',
            '.ttf', '.joblib', '.pkl', '.parquet', '.db', '.sqlite', '.exe', '.dll', '.pyc', '.lock'}
PATRONES = [
    ('contraseña en el código', re.compile(r'''(?i)\b(?:password|passwd|pwd|contrase(?:ñ|n)a)\b["']?\s*[:=]\s*["']([^"'\s]{4,})["']''')),
    # Dentro de una cadena de conexión («…;PWD=valor;…»), no un argumento de función (password=variable).
    ('contraseña en cadena de conexión', re.compile(r'(?i)(?:^|[;"\'])\s*(?:pwd|password)\s*=\s*([^;"\'\s{}(),]{4,})(?=[;"\'\s]|$)')),
    ('clave de API', re.compile(r'''(?i)\b(?:api[_-]?key|secret|token|access[_-]?key)\b["']?\s*[:=]\s*["']([A-Za-z0-9_\-./+]{16,})["']''')),
    ('clave de AWS', re.compile(r'\b(AKIA[0-9A-Z]{16})\b')),
    ('clave de OpenAI/Anthropic', re.compile(r'\b(sk-(?:ant-)?[A-Za-z0-9_\-]{20,})')),
    ('token de GitHub', re.compile(r'\b(gh[pousr]_[A-Za-z0-9]{36,})')),
    ('clave de Google', re.compile(r'\b(AIza[0-9A-Za-z\-_]{35})')),
    ('token de Slack', re.compile(r'\b(xox[baprs]-[A-Za-z0-9-]{10,})')),
    ('clave privada', re.compile(r'(-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----)')),
    ('URL con usuario y contraseña', re.compile(r'\b[a-z+]+://[^/\s:@]+:([^@\s/]{4,})@')),
]
VALORES_INOCUOS = re.compile(r'(?i)^(?:\*+|x+|changeme|cambiar|tu_?clave|your_?password|password|contraseña|<.*>|'
                             r'os\.environ.*|process\.env.*|settings\..*|none|null|true|false)$'
                             r'|[{}%$]|fake|dummy|ejemplo|example|placeholder|^(?:tu|your|su)_\w+$')
CONEXION = re.compile(r'(?i)(?:server|uid|user id|database|data source|host|driver)\s*=')   # contexto de cadena de conexión
CONSTANTE = re.compile(r'^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$')   # DEFAULT_PASSWORD: nombre de variable, no un valor
PRUEBAS = re.compile(r'(^|/)(tests?|__tests__|spec|fixtures?)/|\.(test|spec)\.|(^|/)test_[^/]*$')
DATOS = {'.csv', '.json', '.sql', '.txt', '.tsv', '.xml', '.ris'}
CEDULA = re.compile(r'(?<!\d)(\d{10})(?!\d)')


def digito(nueve: str) -> int:
    t = 0
    for i, d in enumerate(nueve):
        v = int(d) * (2 if i % 2 == 0 else 1)
        t += v - 9 if v > 9 else v
    return (10 - t % 10) % 10


def cedula_real(c: str) -> bool:
    return 1 <= int(c[:2]) <= 24 and int(c[2]) < 6 and digito(c[:9]) == int(c[9])


def enmascarar(s: str) -> str:
    return s[:2] + '*' * max(len(s) - 4, 3) + s[-2:] if len(s) > 6 else '****'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('repo')
    ap.add_argument('--ignorar', action='append', default=[])
    ap.add_argument('--sin-cedulas', action='store_true')
    ap.add_argument('--umbral-cedulas', type=int, default=5, help='cédulas válidas por archivo para reportarlo')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    repo = Path(a.repo).resolve()
    ignorar = [re.compile(x) for x in a.ignorar]
    hallazgos, avisos_prueba, cedulas = [], [], {}
    for p in repo.rglob('*'):
        partes = p.relative_to(repo).parts
        if set(partes) & EXCLUIR or any(x.startswith(('venv', '.venv')) for x in partes) or not p.is_file():
            continue
        rel = p.relative_to(repo).as_posix()
        if p.suffix.lower() in BINARIOS or any(x.search(rel) for x in ignorar) or p.name.startswith('.env'):
            continue
        try:
            if p.stat().st_size > 5_000_000:
                continue
            texto = p.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        for n, linea in enumerate(texto.splitlines(), 1):
            if 'secreto-permitido' in linea:
                continue
            for nombre, patron in PATRONES:
                if nombre == 'contraseña en cadena de conexión' and not CONEXION.search(linea):
                    continue
                for m in patron.finditer(linea):
                    valor = m.group(1)
                    if VALORES_INOCUOS.search(valor.strip()) or CONSTANTE.match(valor.strip()):
                        continue
                    destino = avisos_prueba if PRUEBAS.search(rel) else hallazgos
                    destino.append(f'{rel}:{n}  {nombre}: {enmascarar(valor)}')
            if not a.sin_cedulas and p.suffix.lower() in DATOS and not PRUEBAS.search(rel):
                for m in CEDULA.finditer(linea):
                    if cedula_real(m.group(1)):
                        cedulas[rel] = cedulas.get(rel, 0) + 1
    gitignore = repo / '.gitignore'
    avisos = []
    if (repo / '.env').exists() or list(repo.glob('*/.env')):
        if not gitignore.exists() or '.env' not in gitignore.read_text(encoding='utf-8', errors='ignore'):
            avisos.append('.env existe pero no está en .gitignore.')
        r = subprocess.run(['git', '-C', str(repo), 'ls-files', '--', '*.env', '.env', '*/.env'], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            hallazgos.append(f'git está siguiendo archivos .env: {r.stdout.strip()}')
    # Archivos ignorados por git (p. ej. env.yaml local): no se suben al repositorio,
    # pero sí viajan si se comparte la carpeta en un .zip → aviso, no error.
    ignorados = []
    for h in list(hallazgos):
        ruta = h.split(':', 1)[0]
        r = subprocess.run(['git', '-C', str(repo), 'check-ignore', '-q', ruta], capture_output=True)
        if r.returncode == 0:
            hallazgos.remove(h)
            ignorados.append(h)
    for h in hallazgos:
        print('  SECRETO:', h)
    for h in ignorados:
        print('  IGNORADO POR GIT (no compartir la carpeta sin excluirlo):', h)
    for h in avisos_prueba:
        print('  EN PRUEBAS (revisar que sea un valor ficticio):', h)
    # Un número suelto puede pasar el dígito verificador por azar (≈1 %): solo se
    # reportan archivos con varias cédulas válidas.
    cedulas = {k: v for k, v in cedulas.items() if v >= a.umbral_cedulas}
    for rel, k in sorted(cedulas.items(), key=lambda kv: -kv[1]):
        print(f'  DATO PERSONAL: {rel}: {k} cédulas ecuatorianas con formato y dígito verificador válidos')
    for x in avisos:
        print('  AVISO:', x)
    total = len(hallazgos) + len(cedulas)
    print('Sin secretos ni cédulas válidas en el repositorio.' if not total else
          f'{len(hallazgos)} secretos y {len(cedulas)} archivos con posibles cédulas reales. Muévelos a variables de entorno '
          'o fuera del repositorio; seudonimiza los datos con anonimizar.py.')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
