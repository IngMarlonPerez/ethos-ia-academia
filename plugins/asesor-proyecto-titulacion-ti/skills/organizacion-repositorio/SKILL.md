---
name: organizacion-repositorio
description: 'Audita y reorganiza el repositorio de la tesis de TI: respaldo, inventario, código sin uso movido (nunca borrado) y capas. Usar al organizar el proyecto, limpiar archivos o antes de publicar.'
---

# Organización del repositorio

## 0. Respaldo antes de tocar nada
- `git fetch --all --unshallow` (si aplica) y `git bundle create <fuera del proyecto>/historial.bundle --all`. El bundle se verifica con `git bundle list-heads`.
- Copia de las carpetas de trabajo, sin `node_modules` ni `venv`, fuera del proyecto (con robocopy en Windows).
- **No dejes cambios sin confirmar si alguien va a cambiar de rama.** Un cliente gráfico de git (por ejemplo, GitHub Desktop con «dejar mis cambios en la rama») guarda los cambios en un *stash*. Así desaparecen del disco los archivos movidos con `git mv`, y en la raíz reaparecen los archivos de la otra rama.
  - Si pasa, los archivos están en `stash@{0}`.
  - Se recuperan solo los que faltan, sin sobrescribir nada: `git restore --source='stash@{0}' --worktree --pathspec-from-file=<lista>`.

## 1. Inventario
`python "${CLAUDE_PLUGIN_ROOT}/skills/organizacion-repositorio/scripts/inventario.py" <raíz> --json inventario.json`

Muestra el tamaño por carpeta, los archivos de 50 MB o más y los candidatos a revisar:
- videos, comprimidos, PDF de artículos;
- `.env`, respaldos, temporales de Office;
- `.bat` de otros productos;
- entornos duplicados.

## 2. Qué código se usa
- Alcanzabilidad desde los puntos de entrada (`main.py`, `src/main.jsx`): `detectar_arquitectura.py` de la skill `decision-arquitectura` da el grafo de imports. Complétalo con `grep` de los nombres de archivo en scripts, pipeline y documentación.
- Se mueve **solo** lo que no se alcanza.
  - Si algo heredado todavía se importa (endpoints, componentes), queda listado como «pendiente de decisión», con la razón, y no se toca.
  - Los scripts que reescriben el historial o hacen `push` sin revisión son **peligrosos**: van a la carpeta de revisión.

## 3. Mover sin borrar
`python "${CLAUDE_PLUGIN_ROOT}/skills/organizacion-repositorio/scripts/mover_a_revision.py" <raíz> <rutas…> --categoria "…" --motivo "…" --evidencia "…" [--secretos]`

- Conserva la ruta original y agrega una fila a `_POR_REVISAR_ELIMINAR/INDICE.md`.
- No sobrescribe nada.
- La carpeta va en `.gitignore` **y** en `.git/info/exclude`, para que no se publique aunque cambie el `.gitignore`.

## 4. Estructura por capas, justificada
- Todo el código en `codigo_fuente/`, organizado según la arquitectura elegida (ADR de `decision-arquitectura`). La documentación va en `documentacion/` y los datos externos, que no se versionan, en `datos/`. Usa la plantilla de `referencias/estructura-por-capas.md`.
- **ADR-000 de estructura:**
  - al menos 3 artículos leídos en texto completo (los de la referencia sirven de punto de partida; busca más con `asistente-investigacion-cientifica:revision-sistematica`);
  - 3 repositorios de referencia verificados con `gh api`;
  - una matriz ponderada con sensibilidad.
- `codigo_fuente/README.md` explica la correspondencia carpeta → capa y las reglas de dependencia.

## 5. Rutas y verificación
- Actualiza todas las rutas:
  - `package.json`, proxy de Vite, scripts del pipeline;
  - generadores del documento, rutas de figuras y diccionarios;
  - pruebas.
- Usa rutas relativas al archivo (`Path(__file__).resolve().parents[n]`), nunca absolutas de una máquina.
- **Control:** pasan las pruebas del backend, el *build* del frontend y el pipeline. El documento se regenera y `verificar-coherencia` termina sin errores.
- Escribe `documentacion/auditoria/AUDITORIA_<fecha>.md` en tono neutro: hallazgos, acciones, estado verificado, código heredado pendiente y riesgos, **sin valores de secretos**.

**Control:**
- respaldo verificado;
- `INDICE.md` con motivo y evidencia por fila;
- todo el código en una carpeta por capas;
- ADR-000 con artículos y repositorios;
- pruebas, *build* y documento en verde.
