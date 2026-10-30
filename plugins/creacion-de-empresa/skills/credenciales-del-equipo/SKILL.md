---
name: credenciales-del-equipo
description: 'Credencial o carné digital del equipo con foto, cargo y QR de verificación, en PNG y PDF, desde empresa.json. Usar al pedir «credencial», «carné» o cuando entra alguien nuevo.'
---

# Credenciales del equipo

Modelo: el carné digital de una universidad (cabecera de color, foto circular, nombre, etiqueta, tabla de datos, QR, pie). Una persona = una credencial en PNG (pantalla) y PDF (impresión).

## 1. Reúne los datos
- **Empresa:** `empresa.json` aporta `razon_social`, `nombre_comercial`, `ciudad`, `sitio_web` y los colores `marca.color_primario` y `marca.color_acento`. Si falta algo, el script usa valores por defecto y lo avisa.
- **Personas:** crea `personas.json` (ver `ejemplo_personas.json`): `id`, `nombre` (hasta dos líneas), `foto`, `cargo`, `etiqueta`, `filas` (pares campo/valor) y `url` de verificación.
- **Logo:** el isotipo en PNG con transparencia que dejó `logos-y-piezas` (`isotipo-blanco.png` si la cabecera es oscura).

## 2. Decisiones de privacidad (por defecto)
- **No incluir cédula, teléfono, correo personal ni dirección.** El QR ya cumple la función de verificar.
- **La URL del QR debe ser una página pública que la persona aprobó** (perfil del sitio, página de equipo). Nunca un enlace con datos personales en la dirección.
- **Sin fecha de vencimiento inventada:** solo «Emitida: mes y año». Si la empresa define vigencia (practicantes: la del convenio), agrégala como fila con su fuente.
- **El cargo es el real y vigente** (acta, nombramiento, convenio). Lo no confirmado se pregunta; no se inventa.
- Foto con consentimiento de la persona.

## 3. Genera
`python "${CLAUDE_PLUGIN_ROOT}/skills/credenciales-del-equipo/scripts/generar_credencial.py" --empresa empresa.json --personas personas.json --logo isotipo-blanco.png --salida credenciales/`

Requiere `Pillow` y `qrcode` (`pip install pillow qrcode`). Fuente: Segoe UI si existe (Windows); usa `--fuente ruta.ttf` para la tipografía de la marca.

## 4. Revisa a ojo (obligatorio)
Abre cada PNG y comprueba: nombre completo sin cortar, cargo exacto, foto centrada en el rostro, QR que escanea con el celular y lleva a la página correcta, textos legibles. Los nombres largos pasan a dos líneas; una fila muy larga puede desbordar: acórtala.

## 5. Practicantes y equipo nuevo
Etiqueta «PRACTICANTE <MARCA>», fila de **Universidad/Carrera** y **Periodo** del convenio, y una URL pública solo si la persona y la empresa la aprueban. La credencial no sustituye al convenio ni al carné de la universidad.

## 6. Entrega
Guarda en la carpeta de equipo del expediente (por ejemplo `09_Equipo/credenciales/`), registra en el tablero de la etapa 9 y entrega PNG + PDF. Para tarjeta física de PVC (CR80), pide una versión horizontal: se adapta el lienzo a 1011×638 px.

## Control
Datos = `empresa.json` y `personas.json`; sin datos personales sensibles; QR probado; revisión visual hecha.
