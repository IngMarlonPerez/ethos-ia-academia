---
name: constitucion-sas-ecuador
description: 'Guía la constitución electrónica de una S.A.S. en la Superintendencia de Compañías: prerrequisitos, denominación, formulario, CIIU, capital y firma. Usar al constituir o llenar el formulario.'
---

# Constitución de una S.A.S. en Ecuador (SCVS)

La constitución electrónica de una S.A.S. **no tiene costo** y se hace en línea. Lo que la retrasa es lo previo: firma electrónica, multas, nombre y datos. Esta skill prepara todo para que el formulario se llene en una sola sesión. La usuaria (o los socios) firman y envían; **tú no firmas, no pagas ni presentas nada**.

> Una S.A.S. se constituye llenando un **formulario de 7 secciones**; no existe «minuta estándar o propia» (eso es de las compañías anónimas y de responsabilidad limitada). El sistema genera el acto constitutivo con **texto fijo** de la SCVS: no admite cláusulas propias.

## Fase 0 · Prerrequisitos (lo que más tarda: empezar ya)
Para **cada socio** y para el representante:
1. **Multas del CNE** pagadas (certificado de votación vigente). Un adeudo bloquea trámites de identidad.
2. **Firma electrónica en archivo (.p12)**, vigente. El sistema solo acepta archivo: no token, HSM ni roaming. Emisores: Registro Civil, Security Data, Uanataca, ANF o Banco Central. Costo de referencia: USD 10–30 + IVA por persona (verificar). Plan B si no hay cupo ese día: otro emisor el mismo día.
3. **Usuario solicitante registrado** en el portal de la SCVS con esa firma.
4. **Correo corporativo real** (el sistema notifica por ahí) y un teléfono fijo y un celular de contacto (el formulario pide ambos).
5. **Cédulas escaneadas a color**, resolución máxima 200 dpi, hasta 20 MB en total.
6. **Estado civil** de cada socio (campo obligatorio): confírmalo, no lo asumas. Si es casado o en unión de hecho, puede haber sociedad de bienes que afecte el aporte (Código Civil arts. 139 y 222: verificar con abogado).

Si un socio no tendrá su firma a tiempo, la alternativa real fue constituir con quien sí la tiene y sumar al otro por **cesión de acciones** (ver `gobierno-societario`). Decide esto **antes**, no a mitad del trámite.

## Fase 1 · Reservar la identidad
- Busca la disponibilidad de la razón social y **reserva** (vigencia 30 días: reserva solo cuando el resto del expediente esté listo). Si no está disponible, usa la alternativa preparada en `nombre-y-marca`.
- El nombre comercial se ingresa **en el mismo formulario** (campo opcional): no hace falta esperar al RUC.

## Fase 2 · Formulario (preparar las respuestas en `03_SCVS_Constitucion/respuestas_formulario.md`)
1. **Cuestionario previo de legalidad (8 preguntas):** capacidad legal y licitud de fondos = SÍ; no habrá actividades de seguros, mercado de valores ni lavado de activos = NO. (La S.A.S. tiene prohibidas las operaciones financieras, bursátiles y de seguros.)
2. **Sección 1 · Datos de la compañía:** razón social, nombre comercial, domicilio (provincia, cantón, calle e intersección), plazo de duración de la compañía (indefinido) y **plazo de los representantes legales en su cargo**: verifica en pantalla si acepta «indefinido» o exige 1–5 años; si exige número, elige el máximo y anota que es un límite del campo. Contactos: correo, teléfono fijo y celular.
3. **Sección 2 · Accionistas:** nombres, identificación, domicilio, estado civil y porcentaje.
4. **Sección 3 · Cuadro de suscripciones y pago del capital:** capital suscrito, valor nominal (USD 1 o múltiplos), acciones por socio. **No hay capital mínimo.** Las acciones se pagan en numerario o con bienes (nunca con trabajo). El capital por pagar se deposita en la cuenta de la compañía en un plazo máximo de **24 meses**.
5. **Sección 4 · Representantes legales / administradores:** cargo y tipo de representación (individual o conjunta).
6. **Actividades económicas (CIIU):** 1 principal + hasta 5 complementarias, **del catálogo del propio portal**. El **objeto social se construye solo** a partir de ellas: revisa el texto resultante y que cubra todas las líneas de negocio. Marca la casilla «y cualquier actividad mercantil o civil lícita» para no reformar el estatuto al agregar una línea. Los códigos de memoria se equivocan (en el caso real había dudas entre versiones): búscalos por descripción.
7. **Sección 5 · Contrato/acto unilateral y nombramientos:** lo genera el sistema. **Léelo completo** antes de firmar; no se edita. Lo que no cabe aquí (voto dirimente, no competencia, recompra) va en el **acuerdo de accionistas** privado (`gobierno-societario`).
8. **Sección 6 · Anexos de legalidad:** cédulas y documentos habilitantes.
9. **Sección 7 · Generación de inscripciones:** revisión final; elegir al accionista que figura para la facturación (costo USD 0).

## Fase 3 · Firma y seguimiento
1. Firma electrónica del expediente por cada socio y por el representante.
2. Envío a revisión. Revisa el portal y el correo **cada 1–2 días**; responde cualquier observación del analista en menos de 48 horas.
3. Aprobación e **inscripción automática** en el Registro de Sociedades.

## Fase 4 · Qué guardar al final (y dónde)
En `03_SCVS_Constitucion/` guarda, y copia sus datos a `empresa.json → constitucion`:
- acto constitutivo firmado, **nombramiento** del representante, anexo legal y razón de inscripción (número y fecha de inscripción, número de nombramiento);
- el comprobante de inicio del trámite (número de trámite) y el **correo «Compañía Constituida»** (trae RUC y expediente).

**Confirma el RUC en dos fuentes** (ese correo y la «Consulta de RUC» del SRI) y escríbelo en `empresa.json`. **No es la cédula del representante + 001.** Luego corre `verificar-expediente`.

Inmediatamente después empiezan los plazos: genera el calendario con `obligaciones-post-constitucion`.

## Reglas
- No presentes nada por la usuaria ni uses su firma. Prepara respuestas, revisa textos y explica cada pantalla.
- Plazos y tasas: «Verificado / Por confirmar» contra el manual vigente de la SCVS; las normas cambian.
- Deja dicho que un **abogado societario** debe revisar el acuerdo de accionistas y los documentos que derivan del trámite.

## Control
Inscripción y nombramiento con número; RUC confirmado en dos fuentes; `empresa.json → constitucion` completo; calendario de plazos generado. Marca la etapa 4.

Detalle de cada pantalla y checklist imprimible: `referencias/checklist_portal.md`.
