---
name: obligaciones-post-constitucion
description: 'Lo que sigue tras inscribir una S.A.S.: RUC, facturación SRI, patente, banco, contador, IESS y calendario de plazos. Usar con la empresa inscrita o al preguntar qué plazos tiene.'
---

# Obligaciones posteriores a la constitución

## 1. Calcula el calendario (primero)
`python "${CLAUDE_PLUGIN_ROOT}/skills/obligaciones-post-constitucion/scripts/calendario_plazos.py" --inscripcion AAAA-MM-DD --ruc <ruc> [--inicio-actividades AAAA-MM-DD] --salida "00_Resumen_y_Cronograma/calendario_plazos.md"`

Calcula, desde la fecha de inscripción: balance inicial (30 días), patente municipal (30 días desde inicio de actividades), depósito del capital (24 meses), fechas del SRI por noveno dígito del RUC, renovación del nombramiento, y lo que depende de eventos (factura electrónica, IESS, cesión de acciones). La columna «Verificar» marca los plazos que dependen de una resolución vigente: confírmalos en el portal. **Un plazo ante la SCVS no se traslada por fin de semana**; si vence en día no laborable, presenta antes.

## 2. Verificar el RUC (primer día)
- La S.A.S. recibe el RUC **automáticamente** ~24 horas después de inscribirse. Lo trae el correo «Compañía Constituida».
- Verifícalo en la **Consulta de RUC** pública del SRI (srienlinea.sri.gob.ec → RUC → Consulta). Debe mostrar: razón social, **estado ACTIVO**, representante legal, actividad principal, régimen, obligación de llevar contabilidad, fecha de inicio de actividades y el establecimiento matriz con el nombre comercial.
- **No es la cédula del representante + 001** (ese es su RUC personal). Si algún documento ya salió con el RUC equivocado, anótalo para corregirlo (`verificar-expediente` los encuentra).
- Guarda la página como PDF («Guardar como PDF» del navegador): sirve como anexo «RUC» del balance inicial. El **certificado oficial** se baja con la clave de la compañía; la SCVS suele aceptar la consulta, y si la observa se presenta el certificado.
- Revisa que las actividades económicas del RUC coincidan con el objeto social y, si falta alguna, actualiza el RUC en línea.

## 3. Clave de la compañía en el SRI y facturación electrónica
- La **clave del SRI de la compañía** la gestiona el representante legal (en línea con firma electrónica o en agencia con su cédula, el nombramiento inscrito y el acuerdo de uso de medios electrónicos). Es distinta de la clave personal y de la de la SCVS.
- **Facturación electrónica**: obligatoria para sociedades antes de la primera venta. Requiere firma electrónica de la compañía y clave del SRI. Puede ser la herramienta gratuita del SRI o un proveedor de pago.
- Obligaciones permanentes: contabilidad, IVA mensual (también en cero), retenciones si es agente de retención, impuesto a la renta anual. Fechas por noveno dígito en el calendario.

## 4. Superintendencia: actualización de datos y balance inicial
- **Actualización de información general** en el portal de la SCVS: solo el **representante legal registrado** obtiene la clave de la compañía. Al terminar llega un correo «proceso de actualización de datos ha culminado».
- **Balance inicial** (30 días): skill `balance-inicial-scvs`.
- Si luego cambia el representante legal, la clave se bloquea y el nuevo debe rehacer la actualización: presenta el balance inicial **antes**.

## 5. Municipio
Patente municipal dentro de 30 días desde el inicio de actividades. En Cuenca: formulario 106 (código de impuesto 9090; costo del formulario ~USD 2,72 más el impuesto según tabla progresiva): confirma en la ordenanza del cantón. Uso de suelo: si la actividad es de oficina/servicios profesionales suele tener menos restricciones que comercial/bodega; **verifícalo en el municipio** antes de afirmarlo.

## 6. Banco
- Cuenta corriente **a nombre de la compañía** (la mayoría de bancos la piden corriente para personas jurídicas): documentos habituales, nombramiento inscrito, RUC, acto constitutivo y cédulas.
- Decide quién la abre: un socio con bloqueos o mal buró no puede.
- Aquí se deposita el capital por pagar (plazo máximo 24 meses). No mezcles fondos personales y de la empresa: es el escenario típico donde se pretende «levantar el velo societario».

## 7. Contador
Es **bloqueante** del balance inicial: contrata uno antes. Qué necesitas de él: firma electrónica vigente, nombre completo, C.C./RUC y número de registro profesional. Cobros de referencia: planes de contabilidad en línea para S.A.S. desde unos USD 50 al mes; un servicio puntual (revisar y firmar el balance inicial) cuesta bastante menos. Pide también **centros de costo por línea de negocio** desde el primer asiento.
- **Dónde buscar** (de más accesible a más caro): docentes de contabilidad de universidades y conocidos con firma electrónica; el colegio de contadores local; contadores independientes; plataformas en línea con planes mensuales; estudios contables grandes. Verifica siempre precios y contactos en su sitio oficial el día que los uses.
- **Qué preguntar:** ¿firma con firma electrónica?, ¿cuánto cobra por un servicio único y por el plan mensual?, ¿emite factura?, ¿puede firmar esta semana?
- **Quién no sirve:** quien no tiene RUC activo ni firma electrónica no puede firmar ni cobrar a la empresa con comprobante válido.
- Mensaje listo: `plantillas/mensaje_contador.md`.

## 8. IESS
Registro patronal al contratar personal (aviso de entrada dentro de los primeros 15 días de iniciada la relación laboral: verifica). Las prácticas preprofesionales dependen del convenio con la universidad (ver `equipo-y-practicantes`).

## 9. Marca y propiedad intelectual
Registro de la marca en el SENADI (ver `nombre-y-marca`). Traspaso al patrimonio de la empresa de activos intangibles que ya existían (dominio, redes, contenido) mediante acta de aporte, **una vez exista el RUC**.

## 10. Incentivos a mencionar al contador (verificar vigencia)
Reducción del impuesto a la renta por reinversión en investigación o desarrollo tecnológico acreditado (LRTI art. 37.1) y reducción de 3 puntos por nuevas inversiones (art. 37.2). Exportación de servicios de software: tarifa 0 % de IVA.

## Control
Calendario generado y guardado; RUC verificado y archivado en PDF; contador contratado con sus datos en `balance-inicial-scvs`; banco, SRI y municipio con responsable y fecha. Marca la etapa 5.
