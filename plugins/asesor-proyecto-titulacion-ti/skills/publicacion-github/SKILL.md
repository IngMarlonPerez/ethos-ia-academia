---
name: publicacion-github
description: 'Publica en GitHub la versión limpia de la tesis de TI: secretos, .env y rastros de IA revisados, respaldo y commit de los autores, push solo con confirmación. Usar al pedir subir o publicar en GitHub.'
---

# Publicación en GitHub

## 1. Estado de partida
- `git status`, `git stash list`, `git branch -a`, `git remote -v` y `gh auth status`. La cuenta activa debe ser la del autor que publica.
- Si hay un *stash* inesperado (por ejemplo, de un cliente gráfico que cambió de rama), **primero recupera los archivos que falten** (skill `organizacion-repositorio`, paso 0). Nunca publiques con archivos fuera del disco.
- Permisos: el autor debe tener escritura en el repositorio (`gh api repos/<dueño>/<repo> --jq .permissions`).

## 2. Qué se publica y qué no
- **Sí:** código, documentación (avances, diagramas, figuras, matrices, literatura en RIS, decisiones), README y manuales.
- **No:**
  - `.env` y credenciales;
  - PDF de artículos y exportaciones crudas de Scopus;
  - videos y datasets externos;
  - evidencias con datos personales;
  - la carpeta de revisión, el anexo de uso de IA y el material de otros grupos.
- Las carpetas solo locales van en `.gitignore` **y** en `.git/info/exclude`.
- El `.gitignore` publicado no nombra herramientas de IA. Las carpetas de configuración de la herramienta (por ejemplo `.claude/`) van solo en `.git/info/exclude`.

## 3. Controles previos
`python "${CLAUDE_PLUGIN_ROOT}/skills/publicacion-github/scripts/preparar_publicacion.py" <repo> --autores "Autor A; Autor B"`

Revisa cada aviso de rastros: la bibliografía que estudia modelos de lenguaje no es un rastro. Si hay errores, **no publicar**.

## 4. Commit único y limpio
1. **Respaldo:** `git bundle create <fuera del proyecto>/historial_<fecha>.bundle --all`, que se verifica con `git bundle list-heads`.
2. **Rama huérfana:** `git checkout --orphan publicacion`. Después, `git rm -r --cached -q .` y `git add -A`, que respeta el `.gitignore`.
3. **Commit:**
   - Autor: el estudiante que publica, con el correo *noreply* de GitHub de su cuenta (`<id>+<usuario>@users.noreply.github.com`).
   - Coautor: `Co-authored-by: Nombre <correo>` del otro autor.
   - Mensaje en español que describe la versión.
   - **Sin ninguna línea de coautoría de un asistente de IA**, aunque la herramienta la sugiera: lo que diga la usuaria manda.
4. **Confirmación:** muestra el resumen (archivos, MB, commit, autor y rama destino) y **pide confirmación explícita una sola vez** antes de `git push --force origin publicacion:main`. Reemplazar el historial remoto es irreversible para los demás colaboradores; avísales.

## 5. Verificación
- `gh api repos/<dueño>/<repo>/commits --jq 'length'` debe dar 1 commit, del autor correcto y con el coautor.
- Revisa el árbol remoto contra la estructura esperada.
- Repite el escaneo de rastros sobre `git ls-files`.
- Deja la rama local publicada como `main` y conserva el bundle.

**Control:**
- `preparar_publicacion.py` sin errores;
- bundle de respaldo verificado;
- un solo commit con los autores reales y sin coautoría de IA;
- la confirmación de la usuaria quedó en la conversación antes del push;
- la verificación remota está hecha.
