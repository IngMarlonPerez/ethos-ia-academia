---
name: balance-inicial-scvs
description: 'Balance inicial de una S.A.S. para la Superintendencia: TXT de situación financiera y documentos con membrete para el contador. Usar con balance inicial, asiento de apertura o error al cuadrar.'
---

# Balance inicial en el portal de la SCVS

Vence **30 días después de la inscripción** (calcula la fecha con `obligaciones-post-constitucion`). Lo presenta en el portal el **representante legal registrado**, con la clave de la compañía; los documentos los firma electrónicamente un **contador** con registro profesional.

## Qué se presenta
| Pieza | Dónde va | Cómo se hace |
|---|---|---|
| `situacionFinanciera.txt` | «Estado de Situación Financiera NIIF» | `generar_txt_scvs.py` |
| `resultadoIntegral.txt` | «Estado de Resultado Integral NIIF» | `generar_txt_scvs.py` |
| Anexo **RUC** | Anexos | PDF de la Consulta de RUC del SRI (o el certificado) |
| Anexo **Comprobante de depósito** | Anexos | Capital pagado: comprobante de ingreso (doc. 02). Capital por pagar: declaración (doc. 02) |
| Anexo **Asiento de diario** | Anexos | Doc. 01, firmado por el contador y el representante |
| Nóminas de socios y de administradores | — | El sistema las emite solo |

El documento 03 (estados financieros) **no se sube**: es para el contador y el archivo de la compañía. Las **notas, el informe del representante, el acta de junta y el informe de comisario** son del balance **anual**, no de este.

## Paso 1 · Decidir la modalidad con el contador (antes de generar nada)
| Modalidad | Asiento | Estado de situación | Anexo «comprobante» |
|---|---|---|---|
| **Capital por pagar** | Debe 30102 (−) capital suscrito no pagado / Haber 30101 capital suscrito | Activo 0 · Patrimonio 0 (30101 = capital; 30102 = −capital) | Declaración del representante que reemplaza al comprobante de depósito |
| **Capital pagado** | Debe 1010101 Caja / Haber 30101 | Activo = capital · Patrimonio = capital | Comprobante de ingreso (recibo) |

Base: el capital suscrito no pagado **resta del patrimonio** (NIIF para las PYMES, sección 22, párr. 22.7 a). En el caso real ambos criterios se usaron: cambiar la modalidad después obliga a regenerar todo. Si es «pagado», el dinero debe haberse **recibido de verdad** y luego depositarse en la cuenta de la compañía. No son excluyentes con el plazo de 24 meses: es una decisión contable que toma el contador.

Dato legal a mencionar: el art. 54 del Reglamento de las S.A.S. habla de 30 días posteriores al plazo de pago; el correo de la SCVS, de 30 días desde la inscripción. Presenta dentro de los 30 días del correo.

## Paso 2 · Reunir datos
- `empresa.json` completo (razón social, **RUC de la compañía**, representante, domicilio, `constitucion`, `capital`).
- Del contador: nombre, C.C./RUC, **registro profesional**. Si aún no se sabe, quedan líneas en blanco; no inventes.
- `balance.json` (modelo en `referencias/balance_ejemplo.json`): fechas, modalidad, capital, accionistas, número de comprobante.
- Plantillas oficiales del portal (Estados Financieros → «Formatos»): `ESTADO_SITUACION_FINANCIERA.txt`, `ESTADO_RESULTADO_INTEGRAL.txt`, y `PLAN_CUENTAS`. Los otros dos formatos (cambios en el patrimonio, flujo de efectivo) son del balance anual.

## Paso 3 · Generar los TXT
`python "${CLAUDE_PLUGIN_ROOT}/skills/balance-inicial-scvs/scripts/generar_txt_scvs.py" --situacion-plantilla "FORMATOS/ESTADO_SITUACION_FINANCIERA.txt" --resultados-plantilla "FORMATOS/ESTADO_RESULTADO_INTEGRAL.txt" --caso pagado --capital 200 --salida "09_Balance_Inicial_SCVS"`   (o `--caso por_pagar`, o `--valores valores.json` para otros saldos)

- Copia **la plantilla oficial tal cual** (376 cuentas en situación y 246 en resultados en la versión del caso real; mismo orden, CRLF) y cambia solo los valores. Las cuentas padre se calculan como suma de sus hijas. Verifica el formato y que Activo = Pasivo + Patrimonio.
- Un TXT con solo las cuentas usadas **falla**: el portal exige todas.

## Paso 4 · Generar los documentos con membrete
`python "${CLAUDE_PLUGIN_ROOT}/skills/balance-inicial-scvs/scripts/generar_documentos_balance.py" --empresa empresa.json --balance balance.json --membrete "08_Papeleria_Membretada/Membrete_<CLAVE>.docx" --salida "09_Balance_Inicial_SCVS" --pdf`

Produce `01_Asiento_Diario_Apertura`, `02_Comprobante_Ingreso_Capital` **o** `02_Declaracion_Capital_Suscrito_por_Pagar`, y `03_Estados_Financieros_Iniciales` (.docx y .pdf, **una página cada uno**, ~130 KB). Asiento, glosa y notas salen coherentes con la modalidad. Mira los PDF antes de enviarlos al contador.

## Paso 5 · Firmas
1. El contador revisa, corrige si hace falta y **firma electrónicamente** los PDF (sello FirmaEC u otro). Si hay cambios, edita el `.docx`/`balance.json`, regenera y vuelve a pedir la firma.
2. Firma el representante legal.
3. Guarda los firmados con sufijo `-signed` sin pisar los originales.

## Paso 6 · Portal (lo hace el representante legal)
1. www.supercias.gob.ec → Portal de Trámites en Línea → Sector Societario → Estados Financieros → **Ingresar Balance Inicial**.
2. Adjuntar los dos TXT → **«Auditar y cuadrar»**. Esto **no envía nada**. Debe decir **CUADRADO**.
3. Pestaña **Anexos**: «Adjuntar / Modificar» en RUC, Comprobante de Depósito y Asiento de Diario; revisar cada uno con «Ver PDF» (completo y legible).
4. **«Enviar información»** solo con todo adjunto: después de enviar no se puede rectificar. Antes de enviar se puede corregir desde el menú principal → «Corrección de información».
5. Guarda el comprobante de envío que llega al correo de la compañía.

## Si «Auditar y cuadrar» da error
- «El número total de cuentas no es el correcto» / «No consta la cuenta…»: el TXT no es copia de la plantilla. Descarga la plantilla del portal y regenera con ese archivo.
- Error de signo en la cuenta 30102: prueba con el valor positivo.
- No cuadra: revisa que Activo = Pasivo + Patrimonio (el script lo comprueba).
- Mientras no salga CUADRADO no se envía nada: puede corregirse y reintentarse.

## Control
TXT generados desde la plantilla oficial; «CUADRADO» en el portal (captura guardada); tres anexos firmados y revisados con «Ver PDF»; comprobante de envío archivado. Marca la etapa 6 con «enviado el AAAA-MM-DD».

Guía imprimible para el representante: `plantillas/leeme_portal.txt`.
