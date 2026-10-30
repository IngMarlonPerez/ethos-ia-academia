# -*- coding: utf-8 -*-
"""
detectar_arquitectura.py — describe la arquitectura REAL de un repositorio a
partir de su código (heurístico: el agente auditor-arquitectura confirma
leyendo los puntos de entrada).

Detecta:
  - lenguajes (por extensión) y frameworks REALMENTE USADOS: declarados en el
    manifiesto (package.json, requirements*.txt, pyproject.toml, pom.xml,
    build.gradle, *.csproj, go.mod, composer.json) Y importados en el código.
    Los declarados sin uso se listan aparte (dependencias muertas);
  - aplicaciones y desplegables (manifiesto con framework de frontend/backend,
    o Dockerfile) y servicios de docker-compose;
  - bases de datos y mensajería (dependencias usadas, imágenes de docker-compose);
  - rutas de API (FastAPI/Flask, Django, Express, NestJS, Spring, ASP.NET);
  - grafo de dependencias entre componentes (carpetas de segundo nivel) según
    los imports de Python y JavaScript/TypeScript;
  - acceso a base de datos desde el frontend (acoplamiento indebido);
  - estilo inferido con su evidencia: monolito, backend en capas,
    cliente-servidor desacoplado (SPA + API), microservicios, orientada a
    eventos, serverless.

Uso:
    python detectar_arquitectura.py <repo> [--json salida.json] [--md salida.md]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

EXCLUIR = {'node_modules', '.git', 'venv', '.venv', 'env', '__pycache__', 'dist', 'build', '.next', 'site-packages',
           'coverage', '.pytest_cache', '.mypy_cache', 'target', 'bin', 'obj', '.idea', '.vscode', 'vendor', '.claude'}
EXTENSIONES = {'.py': 'Python', '.js': 'JavaScript', '.jsx': 'JavaScript (JSX)', '.ts': 'TypeScript', '.tsx': 'TypeScript (TSX)',
               '.java': 'Java', '.cs': 'C#', '.go': 'Go', '.php': 'PHP', '.rb': 'Ruby', '.kt': 'Kotlin', '.dart': 'Dart',
               '.sql': 'SQL', '.vue': 'Vue', '.svelte': 'Svelte', '.rs': 'Rust'}
JS = ('.js', '.jsx', '.ts', '.tsx', '.vue', '.mjs', '.cjs', '.svelte')
# dependencia → (nombre, rol, módulo que se importa en el código)
FRAMEWORKS = {
    'react': ('React', 'frontend', 'react'), 'vue': ('Vue', 'frontend', 'vue'), '@angular/core': ('Angular', 'frontend', '@angular/core'),
    'svelte': ('Svelte', 'frontend', 'svelte'), 'next': ('Next.js', 'fullstack', 'next'), 'nuxt': ('Nuxt', 'fullstack', 'nuxt'),
    'express': ('Express', 'backend', 'express'), '@nestjs/core': ('NestJS', 'backend', '@nestjs/core'), 'fastify': ('Fastify', 'backend', 'fastify'),
    'fastapi': ('FastAPI', 'backend', 'fastapi'), 'flask': ('Flask', 'backend', 'flask'), 'django': ('Django', 'backend', 'django'),
    'streamlit': ('Streamlit', 'fullstack', 'streamlit'),
    'scikit-learn': ('scikit-learn', 'ml', 'sklearn'), 'tensorflow': ('TensorFlow', 'ml', 'tensorflow'), 'torch': ('PyTorch', 'ml', 'torch'),
    'xgboost': ('XGBoost', 'ml', 'xgboost'), 'langchain': ('LangChain', 'ia', 'langchain'), 'openai': ('OpenAI SDK', 'ia', 'openai'),
    'anthropic': ('Anthropic SDK', 'ia', 'anthropic'), 'sqlalchemy': ('SQLAlchemy', 'datos', 'sqlalchemy'),
    'prisma': ('Prisma', 'datos', '@prisma/client'), 'sequelize': ('Sequelize', 'datos', 'sequelize'), 'mongoose': ('Mongoose', 'datos', 'mongoose'),
}
# Frameworks de manifiestos sin imports comparables (se aceptan con solo declararse).
FRAMEWORKS_SIN_IMPORT = {'spring-boot': ('Spring Boot', 'backend'), 'microsoft.aspnetcore': ('ASP.NET Core', 'backend'),
                         'laravel/framework': ('Laravel', 'backend'), 'gin-gonic/gin': ('Gin', 'backend')}
# dependencia → (motor, módulo importado)
BASES = {'pyodbc': ('SQL Server (ODBC)', 'pyodbc'), 'pymssql': ('SQL Server', 'pymssql'), 'mssql': ('SQL Server', 'mssql'),
         'msnodesqlv8': ('SQL Server', 'msnodesqlv8'), 'tedious': ('SQL Server', 'tedious'), 'psycopg': ('PostgreSQL', 'psycopg'),
         'psycopg2': ('PostgreSQL', 'psycopg2'), 'psycopg2-binary': ('PostgreSQL', 'psycopg2'), 'pg': ('PostgreSQL', 'pg'),
         'asyncpg': ('PostgreSQL', 'asyncpg'), 'mysqlclient': ('MySQL', 'MySQLdb'), 'pymysql': ('MySQL', 'pymysql'),
         'mysql2': ('MySQL', 'mysql2'), 'pymongo': ('MongoDB', 'pymongo'), 'mongodb': ('MongoDB', 'mongodb'), 'mongoose': ('MongoDB', 'mongoose'),
         'redis': ('Redis', 'redis'), 'firebase': ('Firebase', 'firebase'), 'firebase-admin': ('Firebase', 'firebase_admin'),
         '@supabase/supabase-js': ('Supabase', '@supabase/supabase-js'), 'supabase': ('Supabase', 'supabase'),
         'oracledb': ('Oracle', 'oracledb')}
MENSAJERIA = {'kafka-python': ('Kafka', 'kafka'), 'confluent-kafka': ('Kafka', 'confluent_kafka'), 'kafkajs': ('Kafka', 'kafkajs'),
              'pika': ('RabbitMQ', 'pika'), 'amqplib': ('RabbitMQ', 'amqplib'), 'aio-pika': ('RabbitMQ', 'aio_pika'),
              'celery': ('Celery', 'celery'), 'bullmq': ('BullMQ', 'bullmq'), 'nats': ('NATS', 'nats')}
IMAGENES = {'mssql': 'SQL Server', 'postgres': 'PostgreSQL', 'mysql': 'MySQL', 'mariadb': 'MariaDB', 'mongo': 'MongoDB',
            'redis': 'Redis', 'rabbitmq': 'RabbitMQ', 'kafka': 'Kafka', 'elasticsearch': 'Elasticsearch', 'nginx': 'Nginx'}
RUTAS = [
    (('.py',), re.compile(r'@\w+\.(?:get|post|put|patch|delete|route|api_route)\(\s*[\'"]'), 'FastAPI/Flask'),
    (('.py',), re.compile(r'\b(?:re_)?path\(\s*r?[\'"][^\'"]*[\'"]\s*,'), 'Django'),
    (JS, re.compile(r'\b(?:app|router|server)\.(?:get|post|put|patch|delete)\(\s*[\'"`]/'), 'Express/Fastify'),
    (JS, re.compile(r'@(?:Get|Post|Put|Patch|Delete)\('), 'NestJS'),
    (('.java', '.kt'), re.compile(r'@(?:Get|Post|Put|Patch|Delete|Request)Mapping'), 'Spring'),
    (('.cs',), re.compile(r'\[Http(?:Get|Post|Put|Patch|Delete)'), 'ASP.NET'),
]
DRIVERS_BD = {'mssql', 'msnodesqlv8', 'tedious', 'pg', 'mysql', 'mysql2', 'mongoose', 'mongodb', 'oracledb', 'sqlite3', 'knex',
              'sequelize', '@prisma/client', 'pyodbc', 'psycopg2', 'sqlalchemy'}
IMPORT_PY = re.compile(r'^\s*(?:from\s+(\.*[\w.]*)\s+import|import\s+([\w.]+))', re.MULTILINE)
IMPORT_JS = re.compile(r'''(?:import\s[^'"]*?from\s*|import\s*\(\s*|require\(\s*|export\s[^'"]*?from\s*|^\s*import\s*)['"]([^'"]+)['"]''',
                       re.MULTILINE)
MANIFIESTOS = ('package.json', 'requirements.txt', 'pyproject.toml', 'pom.xml', 'build.gradle', 'go.mod', 'composer.json',
               'Dockerfile', 'serverless.yml', 'manage.py')
CAPAS = {'api', 'routes', 'routers', 'controllers', 'core', 'services', 'domain', 'models', 'repositories', 'db', 'data', 'dal',
         'persistence', 'infrastructure', 'application', 'handlers', 'views'}


CARPETAS_CLIENTE = {'src', 'client', 'app', 'pages', 'components', 'public', 'frontend', 'web'}


def es_prueba(rel: Path) -> bool:
    s = rel.as_posix().lower()
    return bool(re.search(r'(^|/)(tests?|__tests__|spec)/|\.(test|spec)\.|(^|/)test_[^/]*\.py$', s))


def archivos(repo: Path):
    for p in repo.rglob('*'):
        partes = p.relative_to(repo).parts
        if set(partes) & EXCLUIR or any(x.startswith(('venv', '.venv')) for x in partes):
            continue
        if p.is_file():
            yield p


def leer(p: Path, limite: int = 400_000) -> str:
    try:
        return '' if p.stat().st_size > limite else p.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return ''


def dependencias(p: Path) -> list[str]:
    t = leer(p)
    if p.name == 'package.json':
        try:
            pj = json.loads(t)
        except ValueError:
            return []
        return [k.lower() for s in ('dependencies', 'devDependencies') for k in pj.get(s, {})]
    if p.name.startswith('requirements') and p.suffix == '.txt':
        return [re.split(r'[<>=~!\[;\s]', l.strip(), maxsplit=1)[0].lower() for l in t.splitlines()
                if l.strip() and not l.strip().startswith(('#', '-'))]
    if p.name == 'pyproject.toml':
        return [m.lower() for m in re.findall(r'["\']([A-Za-z0-9_.\-]+)\s*[<>=~!\[]', t)]
    if p.name in ('pom.xml', 'build.gradle'):
        return [m.lower() for m in re.findall(r'(spring-boot[\w-]*)', t)]
    if p.suffix == '.csproj':
        return [m.lower() for m in re.findall(r'Include="([\w.]+)"', t)]
    if p.name in ('go.mod', 'composer.json'):
        return [m.lower() for m in re.findall(r'([\w.-]+/[\w.-]+)', t)]
    return []


def servicios_compose(repo: Path) -> dict[str, dict]:
    servicios = {}
    for p in list(repo.glob('docker-compose*.y*ml')) + list(repo.glob('compose*.y*ml')):
        dentro, actual = False, None
        for linea in leer(p).splitlines():
            if re.match(r'^services:\s*$', linea):
                dentro = True
                continue
            if dentro and re.match(r'^\S', linea):
                dentro = False
            if not dentro:
                continue
            m = re.match(r'^  ([\w.-]+):\s*$', linea)
            if m:
                actual = m.group(1)
                servicios[actual] = {'archivo': p.name}
                continue
            m = re.match(r'^\s{4}(image|build):\s*(.+)$', linea)
            if m and actual:
                servicios[actual][m.group(1)] = m.group(2).strip().strip('"\'')
    return servicios


def componente_de(rel: Path, es_dir: bool = False) -> str:
    """Componente = carpeta de segundo nivel (backend/core, src/components).
    Un archivo directo de una carpeta de primer nivel pertenece a esa carpeta."""
    partes = rel.parts
    if es_dir:
        return '/'.join(partes[:2]) if partes else '(raíz)'
    if len(partes) >= 3:
        return f'{partes[0]}/{partes[1]}'
    return partes[0] if len(partes) == 2 else '(raíz)'


def resolver_import_py(origen: Path, modulo: str, repo: Path) -> Path | None:
    if modulo.startswith('.'):
        puntos = len(modulo) - len(modulo.lstrip('.'))
        base = origen.parent
        for _ in range(puntos - 1):
            base = base.parent
        resto = modulo.lstrip('.').split('.')[0]
        destino = base / resto if resto else base
        return destino if destino.exists() or destino.with_suffix('.py').exists() else None
    primera = modulo.split('.')[0]
    for ancestro in [origen.parent, *origen.parents]:
        if ancestro != repo and repo not in ancestro.parents:
            break
        destino = ancestro / primera
        if destino.is_dir():
            return destino
        if destino.with_suffix('.py').exists():
            return destino.with_suffix('.py')
    return None


def resolver_import_js(origen: Path, esp: str, repo: Path) -> Path | None:
    if esp.startswith('.'):
        base = (origen.parent / esp).resolve()
    elif esp.startswith('@/'):
        base = (repo / 'src' / esp[2:]).resolve()
    else:
        return None
    for cand in [base, *[base.with_suffix(s) for s in JS], base / 'index.js', base / 'index.ts', base / 'index.jsx']:
        if cand.exists():
            return cand
    return base


def paquete_js(esp: str) -> str:
    partes = esp.split('/')
    return '/'.join(partes[:2]) if esp.startswith('@') else partes[0]


def app_de(rel: Path, apps: set[str]) -> str | None:
    for ancestro in [rel.parent, *rel.parents]:
        clave = '(raíz)' if str(ancestro) == '.' else ancestro.as_posix()
        if clave in apps:
            return clave
    return None


def analizar(repo: Path) -> dict:
    repo = repo.resolve()
    lenguajes = Counter()
    deps: dict[str, set[str]] = defaultdict(set)
    manifiestos: list[Path] = []
    fuentes: list[Path] = []
    for p in archivos(repo):
        rel = p.relative_to(repo)
        if p.suffix in EXTENSIONES:
            lenguajes[EXTENSIONES[p.suffix]] += 1
            fuentes.append(p)
        if p.name in MANIFIESTOS or p.suffix == '.csproj' or (p.name.startswith('requirements') and p.suffix == '.txt'):
            manifiestos.append(rel)
            d = dependencias(p)
            app = '(raíz)' if str(rel.parent) == '.' else rel.parent.as_posix()
            deps[app].update(d)
    apps = set(deps)

    # Segunda pasada: imports por aplicación, rutas, grafo y acceso a BD desde el cliente.
    importados: dict[str, set[str]] = defaultdict(set)
    rutas = Counter()
    ejemplos_rutas: list[str] = []
    grafo: dict[tuple[str, str], list[str]] = defaultdict(list)
    imports_bd: list[tuple[Path, int, str]] = []
    for p in fuentes:
        rel = p.relative_to(repo)
        texto = leer(p)
        if not texto:
            continue
        app = app_de(rel, apps)
        origen = componente_de(rel)
        if 'test' not in rel.as_posix().lower():
            for exts, patron, marco in RUTAS:
                if p.suffix in exts:
                    k = len(patron.findall(texto))
                    if k:
                        rutas[marco] += k
                        if len(ejemplos_rutas) < 12:
                            ejemplos_rutas.append(f'{rel.as_posix()}: {marco} ×{k}')
        if p.suffix == '.py':
            for m in IMPORT_PY.finditer(texto):
                modulo = m.group(1) or m.group(2)
                if app:
                    importados[app].add(modulo.lstrip('.').split('.')[0].lower())
                linea = texto[:m.start()].count('\n') + 1
                if modulo.split('.')[0].lower() in DRIVERS_BD:
                    imports_bd.append((rel, linea, modulo.split('.')[0]))
                destino = resolver_import_py(p, modulo, repo)
                if destino is not None and destino != repo:
                    d = componente_de(destino.relative_to(repo), destino.is_dir())
                    if d != origen:
                        grafo[(origen, d)].append(f'{rel.as_posix()}:{linea}')
        elif p.suffix in JS:
            for m in IMPORT_JS.finditer(texto):
                esp = m.group(1)
                linea = texto[:m.start()].count('\n') + 1
                if not esp.startswith(('.', '@/')):
                    pkg = paquete_js(esp).lower()
                    if app:
                        importados[app].add(pkg)
                    if pkg in DRIVERS_BD:
                        imports_bd.append((rel, linea, pkg))
                    continue
                destino = resolver_import_js(p, esp, repo)
                if destino is not None and repo in destino.parents:
                    d = componente_de(destino.relative_to(repo))
                    if d != origen:
                        grafo[(origen, d)].append(f'{rel.as_posix()}:{linea}')

    frameworks: dict[str, dict[str, str]] = {}
    sin_uso: dict[str, list[str]] = {}
    bases, mensajes = set(), set()
    for app, ds in deps.items():
        usados = importados.get(app, set())
        for d in ds:
            if d in FRAMEWORKS:
                nombre, rol, modulo = FRAMEWORKS[d]
                if modulo.lower() in usados or modulo.split('/')[0].lower() in usados:
                    frameworks.setdefault(app, {})[nombre] = rol
                else:
                    sin_uso.setdefault(app, []).append(d)
            for clave, (nombre, rol) in FRAMEWORKS_SIN_IMPORT.items():
                if d.startswith(clave):
                    frameworks.setdefault(app, {})[nombre] = rol
            if d in BASES:
                motor, modulo = BASES[d]
                if modulo.lower() in usados:
                    bases.add(motor)
                else:
                    sin_uso.setdefault(app, []).append(d)
            if d in MENSAJERIA:
                motor, modulo = MENSAJERIA[d]
                if modulo.lower() in usados:
                    mensajes.add(motor)
    compose = servicios_compose(repo)
    for s in compose.values():
        img = s.get('image', '').lower()
        for clave, nombre in IMAGENES.items():
            if clave in img and nombre != 'Nginx':
                (mensajes if nombre in ('RabbitMQ', 'Kafka') else bases).add(nombre)

    def roles(app):
        return set(frameworks.get(app, {}).values())

    frontends = sorted(a for a in frameworks if 'frontend' in roles(a))
    backends = sorted(a for a in frameworks if roles(a) & {'backend', 'fullstack'})
    dockerfiles = {('(raíz)' if str(m.parent) == '.' else m.parent.as_posix()) for m in manifiestos if m.name == 'Dockerfile'}
    desplegables = sorted(set(frontends) | set(backends) | dockerfiles)

    def es_cliente(rel: Path) -> bool:
        """El archivo pertenece a una aplicación de frontend; si esa aplicación
        también tiene backend (Express + React en el mismo package.json), solo
        cuentan las carpetas típicas del cliente."""
        app = app_de(rel, apps)
        if app not in frontends or rel.suffix not in JS or es_prueba(rel):
            return False
        # En la raíz del repo suele haber también scripts y herramientas: ahí
        # (o si la app también tiene backend) solo cuentan las carpetas del cliente.
        if app != '(raíz)' and not roles(app) & {'backend', 'fullstack'}:
            return True
        resto = rel.parts if app == '(raíz)' else rel.relative_to(app).parts
        return len(resto) > 1 and resto[0] in CARPETAS_CLIENTE

    bd_front = [f'{rel.as_posix()}:{linea} importa {drv}' for rel, linea, drv in imports_bd if es_cliente(rel)]

    apps_servicio = [s for s, v in compose.items() if 'build' in v or not any(k in v.get('image', '').lower() for k in IMAGENES)]
    estilos = []
    if any(m.name == 'serverless.yml' for m in manifiestos) or (repo / 'netlify' / 'functions').exists() or (repo / 'api').is_dir() and (repo / 'vercel.json').exists():
        estilos.append(('serverless', 'configuración serverless (serverless.yml, funciones de Netlify o Vercel)'))
    if len(apps_servicio) >= 3 or len(backends) >= 3:
        estilos.append(('microservicios', f'{len(apps_servicio)} servicios de aplicación en docker-compose; {len(backends)} backends: '
                                          f"{', '.join(backends)}"))
    if mensajes:
        estilos.append(('orientada a eventos (componente)', f"mensajería en uso: {', '.join(sorted(mensajes))}"))
    if frontends and backends and set(frontends) != set(backends) and len(backends) < 3:
        estilos.append(('cliente-servidor desacoplado (SPA + API)',
                        f"cliente en {', '.join(frontends)}; API en {', '.join(b for b in backends if b not in frontends) or ', '.join(backends)}"
                        f"; {sum(rutas.values())} rutas de API"))
    if len(backends) == 1 and not (set(frontends) - set(backends)):
        estilos.append(('monolito', f'una sola aplicación desplegable ({backends[0]}) que sirve interfaz y lógica'))
    for b in backends:
        base = repo if b == '(raíz)' else repo / b
        sub = {x.name.lower() for x in base.iterdir() if x.is_dir()} if base.is_dir() else set()
        if len(sub & CAPAS) >= 2:
            estilos.append(('backend en capas', f"{b}: carpetas {', '.join(sorted(sub & CAPAS))}"))
    return {
        'repositorio': str(repo),
        'lenguajes': dict(lenguajes.most_common()),
        'frameworks_por_aplicacion': frameworks,
        'dependencias_declaradas_sin_uso': sin_uso,
        'desplegables': desplegables,
        'servicios_docker_compose': compose,
        'bases_de_datos': sorted(bases),
        'mensajeria': sorted(mensajes),
        'rutas_api': dict(rutas),
        'ejemplos_rutas': ejemplos_rutas,
        'dependencias_entre_componentes': {f'{a} -> {b}': {'n': len(v), 'ejemplos': v[:3]}
                                           for (a, b), v in sorted(grafo.items(), key=lambda kv: -len(kv[1]))},
        'bd_desde_frontend': bd_front,
        'estilo_inferido': [{'estilo': e, 'evidencia': ev} for e, ev in estilos],
    }


def a_markdown(r: dict) -> str:
    l = [f"# Arquitectura detectada en `{r['repositorio']}`", '', '## Estilo inferido (heurístico)', '']
    l += [f"- **{e['estilo']}** — {e['evidencia']}" for e in r['estilo_inferido']] or ['- (sin señales claras)']
    l += ['', '## Lenguajes', ''] + [f'- {k}: {v} archivos' for k, v in r['lenguajes'].items()]
    l += ['', '## Frameworks en uso por aplicación', '']
    for app, fws in r['frameworks_por_aplicacion'].items():
        l.append(f"- `{app}`: " + ', '.join(f'{n} ({rol})' for n, rol in fws.items()))
    if r['dependencias_declaradas_sin_uso']:
        l += ['', '## Dependencias declaradas que el código no importa', '']
        l += [f"- `{app}`: {', '.join(sorted(set(v)))}" for app, v in r['dependencias_declaradas_sin_uso'].items()]
    l += ['', f"## Desplegables ({len(r['desplegables'])})", ''] + [f'- `{d}`' for d in r['desplegables']]
    if r['servicios_docker_compose']:
        l += ['', '## Servicios de docker-compose', ''] + [f'- `{k}`: {v}' for k, v in r['servicios_docker_compose'].items()]
    l += ['', f"## Bases de datos: {', '.join(r['bases_de_datos']) or '—'} · Mensajería: {', '.join(r['mensajeria']) or '—'}", '']
    l += ['## Rutas de API', ''] + ([f'- {k}: {v}' for k, v in r['rutas_api'].items()] or ['- (ninguna)'])
    l += ['', '## Dependencias entre componentes (imports)', '', '| Origen → destino | Imports | Ejemplos |', '|---|---|---|']
    l += [f"| {k} | {v['n']} | {'; '.join(v['ejemplos'])} |" for k, v in r['dependencias_entre_componentes'].items()]
    if r['bd_desde_frontend']:
        l += ['', '## ⚠ Acceso a base de datos desde el frontend', ''] + [f'- {x}' for x in r['bd_desde_frontend']]
    return '\n'.join(l) + '\n'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('repo')
    ap.add_argument('--json')
    ap.add_argument('--md')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    r = analizar(Path(a.repo))
    if a.json:
        Path(a.json).write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding='utf-8')
    if a.md:
        Path(a.md).write_text(a_markdown(r), encoding='utf-8')
    print(a_markdown(r))
    return 0


if __name__ == '__main__':
    sys.exit(main())
