---
name: certificados-y-reconocimientos
description: 'Diseña certificados, menciones y diplomas A4 con marco, firma, código y QR de verificación, en PNG y PDF, desde un config.json. Usar al pedir «certificado», «diploma» o «reconocimiento».'
---

# Certificados y reconocimientos

Tres tipos, un mismo diseño formal (inspirado en un título universitario, con identidad propia):
- `mencion`: **Mención de honor** por mérito (motivo en una frase).
- `capacitacion`: **Certificado de capacitación** (curso, horas, nota).
- `logro`: **Certificado de logro** (completar un reto, juego o programa; por ejemplo Kernel Cero, 31 niveles).

## 1. Qué es y qué no es (decirlo siempre)
- Es un certificado **de quien lo emite** (la empresa, el club). **No es un título académico ni una certificación oficial** de otra entidad; el pie lo dice y no se quita sin decisión expresa.
- **No usar logos, sellos ni firmas de terceros** (universidades, certificadoras) sin autorización escrita. Cuando haya convenios, la certificadora entrega su propio certificado; el nuestro es complemento («en alianza con…», solo con permiso).
- **Cada certificado nace de un hecho real**: curso dictado, nota registrada, reto completado, mérito documentado. Nada se emite «por si acaso».
- **La firma no se inventa ni se dibuja**: queda una línea para firma manuscrita o electrónica del firmante real. Solo se incorpora una imagen de firma si **la propia persona la entrega y lo autoriza** (es una firma visual, no electrónica). Nunca se abren ni usan sus archivos de firma electrónica (`.p12`, tokens).
- **¿Quieres que se emitan solos y sean verificables?** Usa la skill `emision-certificados-verificables` (progreso validado en el servidor, firma del emisor, QR y página `/verificar`).

## 2. Prepara los datos
- `config.json` (quién emite): `marca`, `razon_social`, `ciudad`, `logo` (PNG con transparencia), `color_primario`, `color_acento`, `firmante`, `cargo_firmante`, `url_verificacion`, y opcionalmente `quien_otorga`, `autoridad`, `aviso_pie`. Ejemplo: `ejemplos/config_ethos_ia.json`.
- `lista.json` (a quién): una entrada por certificado con `tipo`, `codigo`, `nombre`, `fecha` y los campos del tipo. Ejemplo: `ejemplos/lista_ejemplo.json`.
- **Códigos únicos y correlativos** (`ETHOS-CERT-2026-0001`, `CLUB-KC-0001`): no se repiten ni se reasignan. Llevar el registro en una hoja de cálculo.
- **El Club de la Ingeniería:** usa su propio `config.json` (marca «El Club de la Ingeniería», su logo, y como firmante a quien dirige el club con su cargo real). Es una organización distinta de ETHOSLAB: el certificado no debe decir que lo emite la empresa.

## 3. Genera
`python "${CLAUDE_PLUGIN_ROOT}/skills/certificados-y-reconocimientos/scripts/generar_certificado.py" --config config.json --lista lista.json --salida emitidos/`

Plantillas sin datos reales: `--plantillas --salida plantillas/`. Requiere `Pillow` y `qrcode`. Fuentes: Georgia y Segoe UI (Windows); si no existen, cambia `FUENTES_DIR` o instala equivalentes.

**Tamaño estándar:** A4 horizontal, 3508 × 2480 px a 300 ppp; el PDF mide exactamente 297 × 210 mm. Comprueba con `pymupdf` si cambias algo.

## 4. Revisa a ojo (obligatorio)
Abre cada PNG: nombre completo sin cortar, fecha y código correctos, textos que no choquen con la cinta de la medalla, QR visible. Nombres muy largos reducen el tamaño solos; un motivo o curso muy largo pasa a más líneas: acórtalo.

## 5. Antes de emitir de verdad: la página de verificación
El QR lleva a `url_verificacion/<código>`. **Esa página debe existir antes de entregar certificados**: muestra nombre, curso o logro y fecha de quien tenga ese código. Implica una lista pública mínima; pide el consentimiento de cada persona y publica solo lo necesario (nunca cédula ni correo). Si aún no existe, dilo al entregar o usa solo la versión impresa sin promesas de verificación.

## 6. Entrega y registro
Guarda PNG y PDF en `emitidos/`, anota cada código en el registro (persona, fecha, tipo, quién aprobó) y entrega el PDF para imprimir en papel de 120–160 g (mate o con textura). La tinta dorada real o la lámina requieren una versión de imprenta aparte: el dorado del archivo es un degradado digital.

## Control
Hecho real comprobado, código único registrado, firmante real, aviso al pie, tamaño A4 comprobado, revisión visual hecha, página de verificación lista (o aviso).
