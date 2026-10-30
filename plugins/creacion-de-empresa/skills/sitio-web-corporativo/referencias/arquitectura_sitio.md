# Arquitectura del sitio corporativo (referencia)

```text
├── pages/
│   ├── index.js              Landing corporativa
│   ├── equipo.js             Perfiles directivos y equipo (único lugar con nombres y bios)
│   ├── equipo/<persona>.tsx  Perfil individual
│   ├── marca.js              Logo, colores y usos
│   ├── sitemap.xml.js        Sitemap generado
│   ├── _app.js / _document.js  Tipografía global, idioma, favicon
│   └── api/
│       ├── empresa-chat.js   Asistente con IA
│       └── join.js           Recepción del formulario de contacto
├── components/               ChatWidget, Seo, secciones de la portada, tarjetas de equipo
├── lib/
│   ├── ai/complete.js        Orquestación multiproveedor con cuota diaria por proveedor
│   ├── rateLimit.js          Control de abuso por IP
│   ├── internalAuth.js       Autenticación interna por clave
│   └── seo.js                Fuente única de metadatos, rutas del sitemap y datos estructurados
├── supabase/migrations/      Esquema versionado
├── public/                   favicon, íconos, manifest, robots, imágenes de marca y equipo
├── scripts/                  Preparación de íconos y recortes de logo
└── .github/workflows/ci.yml  lint + test + build en cada push y pull request
```

## Variables de entorno (solo nombres; los valores van en `.env.local` y en Vercel)
| Variable | Para qué |
|---|---|
| `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` | Conexión a la base de datos (la de servicio solo en el servidor) |
| `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `NVIDIA_API_KEY` | Proveedores del asistente (cualquier conjunto equivalente) |
| `GROQ_DAILY_LIMIT`, `OPENROUTER_DAILY_LIMIT`, `NVIDIA_DAILY_LIMIT` | Tope diario por proveedor |
| `INTERNAL_API_KEY` | Autenticación de endpoints internos |
| `NEXT_PUBLIC_SITE_URL` | URL canónica |
| `NEXT_PUBLIC_GA_MEASUREMENT_ID` | Analítica (opcional) |
| `NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION` | Verificación de Search Console por etiqueta (opcional) |
| `ALERT_WEBHOOK_URL` | Alertas (opcional) |

Publica solo `.env.local.example` con los nombres y sin valores.

## API
| Endpoint | Método | Descripción |
|---|---|---|
| `/api/empresa-chat` | POST | Consulta al asistente; límite por IP y cuota por proveedor |
| `/api/join` | POST | Valida con Zod y guarda el contacto en Supabase |

## Cabeceras de seguridad (next.config.js)
`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` sin cámara, micrófono ni geolocalización, `Strict-Transport-Security` de 2 años, y `Content-Security-Policy-Report-Only` restringida a recursos propios (`default-src 'self'`, `frame-ancestors 'none'`, `form-action 'self'`). Pasa a CSP bloqueante solo tras navegar todo el sitio con las devtools abiertas sin ver avisos.

## Comandos
`npm run dev`, `npm run build`, `npm start`, `npm run lint`, `npm test`. Node 22 o superior.

## Docker
`DOCKER_BUILD=1` activa `output: 'standalone'` (imagen pequeña). No lo actives en Vercel.
