# Ethos IA Academia

**Metodologías académicas listas para cualquier modelo de IA.** Revisión sistemática PRISMA 2020, redacción en APA 7, proyecto de titulación de TI, trabajos de Economía, prácticas de laboratorio y creación de empresa, con herramientas que verifican cada dato.

Aporte abierto de **Ethos IA (ETHOSLAB S.A.S.)** a la comunidad académica. Licencia MIT. [English below](#english).

## Qué incluye

| Plugin | Para qué sirve |
|---|---|
| `asistente-investigacion-cientifica` | Revisión sistemática PRISMA 2020 con Scopus, OpenAlex y Unpaywall; las 4 matrices de revisión y redacción en APA 7 |
| `asistente-investigacion-economia` | Trabajos de Economía: consigna y rúbrica, literatura por áreas JEL, matriz de consistencia y ejercicios con ecuaciones de Word |
| `asesor-proyecto-titulacion-ti` | Tesis de TI de punta a punta: trabajos previos, requerimientos, decisiones de arquitectura, UML, documento, video técnico y sustentación |
| `practicas-ti-unemi` | Prácticas de laboratorio de TI con evidencias e informe |
| `creacion-de-empresa` | Constitución de una S.A.S. en Ecuador, marca, balance inicial, gobierno societario y equipo |

Son **75 metodologías** y un **servidor MCP** con herramientas de búsqueda de literatura.

## Funciona con cualquier modelo

Ethos IA Academia se apoya en dos estándares abiertos:

- **MCP (Model Context Protocol).** El servidor `servidor/ethos_academia_mcp.py` expone cada metodología como *prompt* y como recurso, junto con las herramientas de Scopus, OpenAlex, Unpaywall y descarga de PDF. Sirve en cualquier cliente MCP: Claude Code, Claude Desktop, Goose, Cline, Continue, OpenCode, etc. Por tanto, también sirve con el modelo que ese cliente use: Claude, GPT, Gemini o un modelo local con Ollama.
- **Skills (`SKILL.md`).** Cada metodología es un archivo Markdown legible por personas y por agentes.

## Instalación en Windows

Requisitos:
- Windows 10 u 11;
- un cliente de IA compatible con MCP.

El instalador pone Python si hace falta.

```powershell
git clone https://github.com/IngMarlonPerez/ethos-ia-academia
cd ethos-ia-academia
powershell -ExecutionPolicy Bypass -File instalar.ps1
```

El instalador:
1. Instala Python y las bibliotecas de Word, Excel y PDF.
2. Te pide, de forma opcional, tu clave de Scopus y tu correo de contacto, y los guarda solo en tu equipo.
3. Registra Ethos IA Academia en el cliente que elijas.

### Instalación directa en Claude Code

```
/plugin marketplace add IngMarlonPerez/ethos-ia-academia
/plugin install asistente-investigacion-cientifica@ethos-ia-academia
```

### Otro cliente MCP (cualquier modelo)

```json
{ "ethos-academia": { "command": "python", "args": ["<ruta>/servidor/ethos_academia_mcp.py"] } }
```

## Principios

- **Solo fuentes académicas** con DOI, leídas en texto completo; cada cifra se verifica en su fuente.
- **La IA no es autora.** La autoría es de quien escribe el trabajo; el plugin de titulación incluye una revisión de rastros de IA y un anexo de declaración de uso.
- **Privacidad.** Las claves no salen del equipo y no hay telemetría.

## Contribuir

Puedes abrir *issues* y *pull requests*. Los perfiles de cada universidad (plantillas y rúbricas) son bienvenidos.

## Créditos

- Desarrollado por **Ethos IA (ETHOSLAB S.A.S.)**, Cuenca, Ecuador. Gerente General: Marlon David Pérez Almachi.
- Partes adaptadas del plugin «proyectos-academicos» de Victor Manuel Lluilema Pisco.
- Íconos de [Lucide](https://lucide.dev) (ISC).

---

## English

**Ethos IA Academia** packages research and thesis methodologies so that any AI model can use them: PRISMA 2020 systematic reviews, APA 7 writing, IT capstone projects, Economics coursework, lab reports and company formation in Ecuador.

- It ships **75 methodologies** as Agent Skills (`SKILL.md`).
- It also ships an **MCP server** with literature tools (Scopus, OpenAlex, Unpaywall).
- It works with any MCP client and therefore with any model, including local models through Ollama.
- On Windows, install it with `instalar.ps1`.
- Released by Ethos IA (ETHOSLAB S.A.S.) under the MIT license.
