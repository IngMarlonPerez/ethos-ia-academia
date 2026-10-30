---
name: iniciar-empresa
description: 'Crea el expediente de una empresa nueva: carpetas, empresa.json (fuente única de datos) y tablero de etapas. Usar al empezar a crear una empresa o si falta empresa.json.'
---

# Iniciar el expediente de una empresa

1. **Lee antes de preguntar.** Si la carpeta ya tiene documentos (cédulas, correos de la Superintendencia, un acto constitutivo, un membrete), léelos primero: dan la razón social, el RUC y las fechas. Pregunta solo lo que falte:
   - razón social tentativa y 2–3 alternativas, y nombre comercial;
   - tipo societario (S.A.S. por defecto en Ecuador), ciudad y provincia;
   - quién será representante legal y qué cargo tendrá;
   - socios y porcentaje de cada uno;
   - a qué se dedicará (en una frase) y las líneas de negocio;
   - si ya hay logo, dominio o redes.

2. **Crea el expediente.** No sobrescribe nada.
   `python "${CLAUDE_PLUGIN_ROOT}/skills/iniciar-empresa/scripts/iniciar_empresa.py" "<carpeta de la empresa>" --razon-social "..." --nombre-comercial "..." --ciudad "..." --provincia "..." --representante "..." --cargo "Gerente General"`

   Deja:
   - `empresa.json`: la **fuente única de datos** (campos en `referencias/campos_empresa.md`; ejemplo ficticio en `plantillas/empresa.ejemplo.json`);
   - 14 carpetas numeradas: `01_Nombre_y_Marca`, `03_SCVS_Constitucion`, `04_SRI`, `09_Balance_Inicial_SCVS`, etc.;
   - `00_Resumen_y_Cronograma/00_Control_Empresa.md`: el tablero de etapas;
   - `.gitignore` que excluye `empresa.json`, la carpeta de firma electrónica, `*.p12`, `*.pfx` y `.env*`.

3. **Completa `empresa.json` con la usuaria**, solo con datos que ella confirme. Lo que aún no existe se deja vacío: el RUC, el expediente y el número de inscripción se llenan **cuando la Superintendencia los entrega**, nunca antes ni de memoria. Cédulas y datos personales quedan solo en este archivo local.

4. **Cierra la etapa 0 y sigue.**
   `python "${CLAUDE_PLUGIN_ROOT}/skills/asistente-creacion-empresa/scripts/tablero.py" marcar 0 cerrada --empresa empresa.json --nota "expediente creado"`
   Siguiente: `nombre-y-marca` (si aún no hay nombre definitivo) o `constitucion-sas-ecuador`.

## Control
- `empresa.json` existe, es JSON válido y tiene razón social, ciudad y representante.
- La carpeta **no** está dentro de un repositorio público ni de una carpeta compartida.
- Ningún dato inventado: lo desconocido está vacío.

## Si ya hay una empresa en marcha
Corre el mismo script sobre su carpeta: no toca lo que existe. Después reconstruye `empresa.json` desde los documentos oficiales (razón de inscripción, correo de la SCVS, consulta de RUC) y marca como cerradas las etapas ya cumplidas con su evidencia en la nota. Termina con `verificar-expediente`.
