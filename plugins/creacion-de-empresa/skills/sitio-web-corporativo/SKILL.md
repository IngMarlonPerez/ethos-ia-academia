---
name: sitio-web-corporativo
description: 'Sitio web corporativo con Next.js + Supabase: landing, equipo, contacto, seguridad, SEO, CI y despliegue en Vercel. Usar al pedir la página web, landing, SEO o publicar el sitio.'
---

# Sitio web corporativo

El sitio es la cara pública y el canal principal de contacto comercial. Se construye **terminado** y se publica cuando la empresa esté inscrita y el contenido verificado.

## 0. Antes de escribir una línea
1. Lee `empresa.json` (razón social, nombre comercial, contactos, colores y tipografía en `marca`). El sitio no repite datos a mano: los toma de ahí.
2. Confirma con la dueña **qué entra y qué no**: líneas de negocio, qué marcas, qué personas. No mezcles proyectos personales de los socios ni líneas que no pidió. Si un brief pegado desde otra herramienta trae secciones ajenas (otra marca, una comunidad, un negocio futuro), retíralas y avisa en una línea.
3. Reúne los activos: logo exportado (`logos-y-piezas`), fotos aprobadas por cada persona, textos de servicios, enlaces a redes.

## 1. Stack (el que funcionó)
| Capa | Tecnología |
|---|---|
| Framework | Next.js (Pages Router) + React; TypeScript donde convenga |
| Datos | Supabase (PostgreSQL) con migraciones versionadas en `supabase/migrations/` |
| Validación | Zod |
| Tipografía | Autohospedada con `next/font` (sin pedir a un CDN en cada visita) |
| Calidad | ESLint, Vitest, GitHub Actions (`lint`, `test`, `build`) |
| Infraestructura | Vercel (producción desde `main`) y Docker (`output: 'standalone'` solo con `DOCKER_BUILD=1`: en Vercel rompe el build) |

Estructura, variables de entorno, API y seguridad: `referencias/arquitectura_sitio.md`.

## 2. Contenido y estructura
- **Portada centrada en el cliente**: problema → solución → impacto; 2–4 líneas de servicio; trayectoria real; misión, visión y compromiso; **cómo trabajamos**; preguntas frecuentes; contacto. No lleva biografías de fundadores.
- **Página de equipo** (`/equipo`): el único lugar con nombres, cargos y trayectorias. Foto por persona **aprobada por ella**. Si una foto se generó con IA, la persona la ve y la aprueba antes de publicarla. El cargo que se muestra es el **inscrito** (si un nombramiento está en trámite, no lo anticipes).
- **Página de marca** (`/marca`): logo, colores, usos correctos.
- **Contacto**: formulario validado con Zod que escribe en Supabase vía `/api/join`; enlaces directos a correo y WhatsApp.
- **Política de privacidad** publicada antes de recoger datos personales (Ley de Protección de Datos Personales: consentimiento, responsable del tratamiento).
- **Cifras y afirmaciones**: solo las que se pueden demostrar. Nada de «líderes», «los mejores», certificaciones que no existen ni «meta de superar X».
- **Sin lenguaje de obra en curso**: ni «próximamente», ni «en construcción», ni «nueva fase». Lo que aún no existe se omite o se redacta como capacidad presente.

## 3. Asistente con IA (opcional)
Un chat que responde sobre la empresa. Orquestación en cadena con respaldo: cada proveedor tiene cuota diaria persistida en Supabase y, si uno falla o la agota, se pasa al siguiente. Reglas: límite de solicitudes por IP, respuestas solo sobre la empresa (prompt de sistema acotado), nunca claves en el cliente, y aviso visible de que es un asistente automático.

## 4. Seguridad por defecto
Cabeceras `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, HSTS; **CSP en modo report-only** primero y bloqueante después de navegar todo el sitio sin avisos; límite de solicitudes en endpoints de IA y formularios; credenciales fuera del repositorio (`.env*` ignorado, solo `.env.local.example`); autenticación por clave en endpoints internos. Antes de publicar, revisa con la skill `verificar-expediente` y con la revisión de seguridad del repositorio.

## 5. Identidad visual
- Íconos y manifest: `exportar_logo.py` (favicons, `apple-touch-icon`, `icon-192/512`, `og-1200x630`); `site.webmanifest`.
- Colores y tipografía desde `empresa.json → marca`; contraste verificado WCAG AA; fondo oscuro por defecto en lo digital.
- Crédito del diseñador del logo en el README y en la página de marca.

## 6. SEO y descubrimiento
`referencias/checklist_lanzamiento.md`: sitemap automático, `robots.txt` (bloquea `/api/`), metadatos únicos por página con URL canónica, Open Graph y Twitter, datos estructurados (`Organization`, `WebSite`, `Person`), Search Console y Bing Webmaster, Google Business Profile, señales cruzadas (mismo nombre y cargo en LinkedIn, GitHub y redes) y datos unificados entre el sitio, el portafolio y la hoja de vida de cada persona. Cada página nueva se suma a la lista de rutas del sitemap.

## 7. GitHub
- Organización de la empresa con su propio perfil (README con banner claro/oscuro, qué hace la empresa y enlaces) y el repositorio del sitio con CI.
- Antes de subir: `.gitignore` con `.env*`, `node_modules`, `.next`; **nada de datos personales, cédulas ni claves**; rastros de herramientas de IA fuera de commits y de metadatos (la IA no es autora).
- El push lo hace la usuaria desde la cuenta que ella indique, o tú con su confirmación. Verifica que la cuenta activa de `gh` es la de la organización.

## 8. Despliegue (con confirmación)
Vercel desde `main`, dominio propio, variables de entorno cargadas en Vercel (no en el repositorio), `NEXT_PUBLIC_SITE_URL` correcta, verificación de Search Console por etiqueta o DNS. Publicar es una acción hacia afuera: confirma con la dueña la fecha y que la empresa ya está inscrita.

## Control de la etapa
`npm run lint`, `npm test` y `npm run build` en verde; revisión visual en móvil y escritorio; búsqueda de textos prohibidos (`verificar_expediente.py` sobre el repositorio) sin hallazgos; formulario probado con envío real a un entorno de prueba; fotos aprobadas. Marca la etapa 8.
