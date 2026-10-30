---
name: emision-certificados-verificables
description: 'Emisión automática de certificados con firma digital y QR verificable (Next.js + Supabase, página /verificar, revocación). Usar con «certificado con QR verificable» o «certificados del juego».'
---

# Emisión de certificados verificables (firma del emisor + QR)

Convierte un certificado bonito en un **sistema**: solo lo recibe quien cumplió, es único por cuenta, lleva un **QR que cualquiera puede escanear** y una página pública confirma que es auténtico. Implementación de referencia probada: `plantillas/` (31 pruebas, compilación y PDF verificados; el QR se decodificó desde el PDF real).

## Reglas que no se negocian
1. **La IA no tiene autoría.** Commits, PR, documentos y metadatos van solo a nombre de la persona responsable (en este equipo: la cuenta GitHub dueña del repo). Sin «Co-Authored-By» ni «Generated with» de ningún asistente. La responsabilidad legal es de quien firma.
2. **Nunca abrir, copiar ni usar archivos de firma electrónica personal** (`.p12`, `.pfx`, tokens) ni sus contraseñas, aunque la usuaria comparta la ruta. En Ecuador la firma electrónica equivale a la manuscrita y el titular debe custodiarla en exclusiva; automatizarla en un servidor puede violar las condiciones de la entidad certificadora. Se firma con **una clave propia del emisor** (Ed25519). Si más adelante se quiere validez legal por PDF, se usa un certificado de sello o de persona jurídica dedicado y se agrega un paso PAdES, sin tocar el resto.
3. **Firma manuscrita en imagen**: solo la que entregue la propia persona y con su autorización (`scripts/extraer_firma.py` quita el fondo del papel). Es una firma **visual**, no electrónica; dilo.
4. **Hecho real y validado en el servidor.** El progreso nace en el navegador; el servidor exige orden, tiempos plausibles y un certificado por cuenta. **No es infalible**: dilo, y deja la revocación lista.
5. **Antes de publicar:** no hacer merge a `main` ni desplegar a producción sin que la usuaria lo pida; verificar con qué cuenta de GitHub se hace el push (`gh auth status`; el repo puede pertenecer a otra cuenta) y **devolver la cuenta activa original** al terminar.
6. Las claves privadas nunca van al repo ni al chat: solo a variables de entorno. Respaldarlas fuera del repo.

## Qué incluye `plantillas/` (copiar al proyecto Next.js)
| Pieza | Archivo |
|---|---|
| Núcleo: validación de nombre, progreso, firma Ed25519, huella | `lib/certificado/core.js` (+ pruebas) |
| Acceso a Supabase (emisión idempotente, verificación pública) | `lib/certificado/store.js` (+ pruebas con BD simulada) |
| PDF con pdf-lib + QR (`qrcode`) | `lib/certificado/pdf.js` |
| API: progreso, estado/emisión, PDF (solo dueño), verificación pública | `pages/api/kc/*.js` |
| Página pública de verificación | `pages/verificar/[codigo].js` |
| Base de datos y RLS (solo el servidor escribe) | `supabase/migrations/0006_*.sql` |
| Arte del certificado y claves | `scripts/generar-arte-certificado.py`, `scripts/generar-clave-certificados.js` |
| Interfaz en el juego/web (tarjeta, reclamo, login Google/GitHub, descarga) | `public/kc-cert.js`, `public/kc-cert.css` |
| Guía de activación para el proyecto | `docs/certificado-kernel-cero.md` |

## Flujo de trabajo
1. **Datos:** emisor, nombre del reconocimiento, prefijo de código (`CLUB-CERT`), sitio, cuántos niveles/requisitos, firmante y cargo, logo, colores. Pide la **firma en imagen** si la persona la quiere (`python scripts/extraer_firma.py foto.png firma.png`) y un **nombre de ejemplo** para la vista previa.
2. **Arte:** adapta `generar-arte-certificado.py` (textos, colores, logo, firma en `lib/certificado/assets/firma-*.png`) y ejecútalo. Revisa el PNG a ojo. La imagen pública de ejemplo va **limpia** (sin marca de agua): el nombre y la fecha se superponen en HTML; la etiqueta «ejemplo ilustrativo» va fuera del diseño.
3. **Código:** copia `plantillas/` al repo; ajusta constantes (`TOTAL_NIVELES`, tiempos mínimos, prefijo `CODIGO_RE`, textos del PDF y de la página, URLs). `npm i pdf-lib qrcode`; añade en `next.config.js` `outputFileTracingIncludes` para `lib/certificado/assets/**`.
4. **Pruebas:** `npm test` (firma válida/alterada, orden de niveles, idempotencia, revocación, tiempos imposibles) y `next build`. Genera un PDF de prueba, míralo, y **decodifica el QR** (p. ej. `opencv-python-headless` `QRCodeDetector`) para confirmar que lleva a `/verificar/<código>`.
5. **Interfaz:** inserta la tarjeta en la pantalla de inicio y el bloque «Reclamar certificado» al final; estados: invitado (invitar a registrarse con Google/GitHub), con sesión y progreso, 31/31 con nombre confirmable (**queda fijo al emitir**), emitido (descargar PDF + enlace de verificación). Sin la clave de firma configurada debe decir «estamos activando» y no romper nada.
6. **Activación (la hace la persona, tú la guías):** migración SQL en Supabase; `node scripts/generar-clave-certificados.js` y pegar las claves en las variables de entorno del hosting; añadir la URL de redirección del OAuth en Supabase; redeplegar. Revocar: `update certificados set revocado = true …`.
7. **Entrega:** commit con la identidad de la persona (regla 1), push, PR y vista previa; resumen honesto de límites y pasos pendientes. Pregunta antes de unir a `main`.

## Control de calidad
Nombre con tildes y largos sin cortar · código único y correlativo · QR decodifica a la URL correcta · firma verificable y alteración detectada · PDF solo para el dueño y solo si cumplió · página de verificación sin correo ni ids internos · aviso «reconocimiento educativo y simbólico, no sustituye una certificación profesional» · sin secretos en el repo · autoría sin IA.
