---
name: verificar-expediente
description: 'Control de calidad del expediente: RUC distintos del oficial, nombres viejos, «próximamente» y datos personales. Usar antes de entregar o publicar, o al preguntar si todo es coherente.'
---

# Verificar el expediente

Nació del error más caro del caso real: el RUC personal del gerente quedó en el membrete, en tres documentos firmados y en las cartas de vinculación de la universidad, y nadie lo vio hasta que ya estaban firmados.

## 1. Corre el control
`python "${CLAUDE_PLUGIN_ROOT}/skills/verificar-expediente/scripts/verificar_expediente.py" --empresa empresa.json --carpeta "<carpeta del expediente>" [--carpeta-compartida] [--json 99_Auditoria/hallazgos.json]`

Revisa `.docx` (cuerpo, **encabezados y pies**, donde suele estar el RUC), `.pdf`, `.xlsx`, `.txt`, `.md`, `.json`, `.html` y código (`.ts`, `.js`, `.tsx`). Ignora `node_modules`, `.git` y compilados. Busca:
1. **RUC distinto del oficial** (cualquier número de 13 dígitos que termine en 001). Si coincide con «cédula del representante o de un socio + 001», lo dice: es su RUC personal.
2. **Nombres anteriores** de la empresa (`nombres_anteriores` en `empresa.json`), p. ej. la razón social que no se pudo reservar.
3. **Textos prohibidos** (`textos_prohibidos`): «próximamente», «en construcción», etc.
4. Con `--carpeta-compartida`: **posibles cédulas** de personas ajenas, en material que se va a compartir o publicar.

Sale con código 1 si hay hallazgos. Prerrequisito: `empresa.json` con el **RUC confirmado** en dos fuentes y las cédulas de representante y socios (solo para esta comparación).

## 2. Qué hacer con los hallazgos
- Un `.docx` o un PDF **no firmado**: corrígelo en origen (membrete, plantilla o `empresa.json`) y regenéralo.
- Un PDF **ya firmado** electrónicamente: no se edita (rompe la firma). Se emite uno nuevo y se firma de nuevo, o se aclara por escrito con la entidad.
- Documentos de **terceros** (cartas de vinculación de la universidad, certificados): no los edites; pide a quien los emitió que corrija su sistema.
- Si la usuaria dijo que corrige ella a mano esos documentos, **no los toques**: solo regístralos en `99_Auditoria/hallazgos.json` y déjalo dicho.

## 3. Revisiones manuales que el script no hace
- Fechas coherentes: la de firma no es anterior a la del hecho; plazos calculados con `calendario_plazos.py`.
- Cifras: el capital, el número de acciones y los porcentajes son los mismos en el acto constitutivo, el asiento, el balance, el acuerdo y la web.
- Datos del contador y del representante escritos igual en todos los documentos.
- Metadatos de Office: creador = razón social, no el nombre de una herramienta ni de una persona.
- Nada de contraseñas, claves, `.p12` ni `.env` en carpetas compartidas ni en el repositorio.

## 4. Cuándo correrlo
Antes de entregar cualquier documento hacia afuera, tras cambiar el RUC, el nombre o el membrete, y al cerrar el expediente. Si quieres una revisión que no modifique nada, delega en el agente `auditor-expediente`.

## Control
0 hallazgos o hallazgos justificados y registrados. Marca la etapa 10 con la fecha de la corrida.
