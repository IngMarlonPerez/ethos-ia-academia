---
name: gobierno-societario
description: 'Gobierno de una S.A.S.: acuerdo de accionistas, cesión de acciones, actas, segundo gerente y vesting. Usar con socios 50/50, socio nuevo, cambio de representante o acuerdo de socios.'
---

# Gobierno societario

Todo es **borrador para revisión de un abogado societario** antes de firmarse. El plugin ordena y redacta; no reemplaza esa revisión. Dilo en una línea al entregar cada documento.

## 1. Acuerdo de accionistas (privado)
**Por qué existe:** el acto constitutivo de una S.A.S. lo genera el sistema con texto fijo; no admite cláusulas propias. Con dos socios al 50 % no hay forma de poner un voto dirimente en el estatuto. El acuerdo lo recoge fuera del expediente.
- Plantilla: `plantillas/acuerdo_accionistas.md` (voto dirimente, roles operativos, derecho de preferencia de 30 días, recompra por fallecimiento o incapacidad, dedicación y no competencia, disputas por negociación → mediación → arbitraje, vigencia).
- Limitación que debes decir: es exigible **entre las partes**, no con la misma fuerza frente a terceros. Alternativas que el abogado evaluará: poder irrevocable limitado, cláusula penal por incumplimiento del voto, o reparto 51/49.
- El acuerdo debe reflejar el reparto **actual** (si cambió por una cesión, actualízalo antes de firmar).
- Redacta pensando en que una línea de negocio pueda separarse en su propia sociedad más adelante, sin comprometerlo hoy.

## 2. Entra un socio: cesión de acciones
Vía rápida cuando la sociedad ya existe y el capital sigue por pagar: **cesión de acciones** (documento privado), no aumento de capital.
- Plantilla: `plantillas/contrato_cesion_acciones.md`. Define cuántas acciones, su numeración, el precio (normalmente el valor nominal) y **quién asume el pago del capital pendiente de las acciones cedidas**.
- Se anota en el **Libro de Acciones y Accionistas** y se **notifica a la SCVS dentro de 8 días** de la anotación (revisión de unos 2 días).
- Si el capital se pagó o no, y el efecto contable y tributario del precio: lo confirma el contador.
- El nuevo socio necesita sus prerrequisitos (multas del CNE y firma electrónica en archivo) para firmar electrónicamente.

## 3. Segundo gerente o cambio de administrador: acta y nombramiento
- Plantilla: `plantillas/acta_junta_nombramiento.md` (Junta Universal con el 100 % del capital, ratificación de la cesión, designación con representación individual o conjunta, aceptación del cargo).
- **Punto abierto que debes confirmar antes de presentar:** si el estatuto describe la administración en cabeza de «el Gerente General» en singular, la SCVS puede exigir una **reforma del estatuto** antes de aceptar un segundo gerente con representación individual. Consulta en el portal o con un abogado.
- Los nombramientos se registran en el portal de la SCVS (a veces en ventanilla).
- **Orden recomendado si hay balance inicial pendiente:** primero presenta el balance inicial con el representante registrado; luego registra el nuevo nombramiento. Solo el representante legal registrado obtiene la clave de la compañía y un cambio **la bloquea** (el nuevo debe rehacer la actualización).
- Cuando el nuevo nombramiento quede inscrito, actualiza `empresa.json`, el membrete, los documentos y la página de equipo del sitio.

## 4. Colaborador que quiere participación futura
- En una S.A.S. las acciones se pagan en **numerario o con bienes**: el trabajo no se aporta como capital.
- Esquema habitual: contrato de trabajo o de servicios + bono por resultados hoy, y **promesa escrita de cesión de acciones con consolidación gradual (vesting)** después. Hay que ajustar el derecho de preferencia y el voto dirimente del acuerdo para el nuevo socio.

## 5. Régimen patrimonial de los socios
Si los socios son pareja, casados o en unión de hecho (Código Civil arts. 139 y 222), puede existir sociedad de bienes que afecte el aporte de capital y lo que pida el banco. Es un dato a **verificar con un abogado** antes del primer depósito.

## 6. Cómo se generan los documentos
1. Completa `datos.json` con lo que pide la plantilla (se ve en los `{{datos.…}}`); lo que falte queda en amarillo.
2. `python "${CLAUDE_PLUGIN_ROOT}/skills/papeleria-membretada/scripts/plantilla_a_docx.py" --plantilla "${CLAUDE_PLUGIN_ROOT}/skills/gobierno-societario/plantillas/<plantilla>.md" --empresa empresa.json --membrete "<membrete>.docx" --datos datos.json --salida "07_Gobierno_Societario/<nombre>.docx" --pdf`
3. Entrega al abogado el `.docx`; la firma electrónica se estampa en el PDF final.

## Control
Cada documento con 0 campos amarillos, revisión de abogado registrada, notificaciones a la SCVS hechas y anotadas con fecha, `empresa.json → socios` y `representante` actualizados. Marca la etapa 7.
