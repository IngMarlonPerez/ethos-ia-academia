# Changelog

## 1.3.1 – 29 de octubre de 2026
- **Menos tokens por sesión:** las descripciones de las skills y los agentes se acortaron a unos 200 caracteres, conservando las frases que las activan. Así se cargan completas en cada sesión y no se recortan por falta de espacio.

## 1.3.0 · 2026-10-17
- Nueva skill `emision-certificados-verificables`: emisión automática de certificados con firma del emisor (Ed25519), QR verificable y página pública `/verificar/<código>`; progreso validado en el servidor, un certificado por cuenta, revocación, PDF con pdf-lib, tarjeta e interfaz para juegos y webs, y herramienta `extraer_firma.py` para firmas manuscritas en imagen. Incluye la implementación de referencia (certificado «Héroe del Club» de Kernel Cero) con 19 pruebas.
- `certificados-y-reconocimientos`: aclara la política de firmas (imagen solo con autorización de la persona; nunca se usan archivos de firma electrónica personal).

## 1.2.0 · 2026-10-16
- Nueva skill `certificados-y-reconocimientos`: menciones de honor, certificados de capacitación y de logro (por ejemplo, el final del reto Kernel Cero del Club de la Ingeniería), A4 horizontal a 300 ppp con marco guilloché, medalla, firma, código y QR; identidad configurable por `config.json`.

## 1.1.0 · 2026-10-16
- Nueva skill `credenciales-del-equipo` y su generador `generar_credencial.py`: carné digital vertical con QR, desde `empresa.json` y `personas.json`; probado con el caso ETHOSLAB.

## 1.0.0 · 2026-10-16
Primera versión, extraída de la creación real de ETHOSLAB S.A.S. (Cuenca, Ecuador).

- 12 skills: `asistente-creacion-empresa`, `iniciar-empresa`, `nombre-y-marca`, `logos-y-piezas`, `papeleria-membretada`, `constitucion-sas-ecuador`, `obligaciones-post-constitucion`, `balance-inicial-scvs`, `gobierno-societario`, `sitio-web-corporativo`, `equipo-y-practicantes`, `verificar-expediente`.
- Agente `auditor-expediente` y comandos `/nueva-empresa` y `/estado-empresa`.
- `empresa.json` como fuente única de datos.
- Generadores probados contra los archivos reales del caso: el TXT del balance reproduce byte a byte las plantillas oficiales; el verificador detecta los cuatro documentos que tenían el RUC equivocado; el membrete generado coincide con el original.
- Lecciones aprendidas documentadas (RUC personal vs. de la sociedad, razón social no reservable, formato de TXT, modalidad de capital, anexos del balance inicial vs. anual).
