# Checklist de lanzamiento del sitio

## Contenido
- [ ] Datos de contacto, razón social y RUC tomados de `empresa.json`
- [ ] Sin «próximamente», «en construcción», «nueva fase» ni metas aspiracionales (`verificar_expediente.py` sobre el repositorio)
- [ ] Solo las líneas de negocio y personas que la dueña confirmó
- [ ] Cada persona aprobó su foto y su texto; cargos = nombramientos inscritos
- [ ] Cifras demostrables; ninguna certificación inexistente
- [ ] Política de privacidad publicada y enlazada en el formulario
- [ ] Crédito del diseñador del logo

## Técnica
- [ ] `npm run lint`, `npm test` y `npm run build` en verde en local y en CI
- [ ] `.env*` fuera del repositorio; `.env.local.example` solo con nombres
- [ ] Cabeceras de seguridad y CSP report-only; sin avisos de CSP tras navegar todo el sitio
- [ ] Límite de solicitudes en `/api/*`; formulario probado con datos de prueba
- [ ] Revisión en móvil y escritorio; contraste WCAG AA
- [ ] Favicons, `apple-touch-icon`, `site.webmanifest` y tarjeta 1200×630

## SEO
- [ ] `sitemap.xml` con todas las páginas y `robots.txt` (bloquea `/api/`)
- [ ] Título y descripción únicos por página, URL canónica, Open Graph y Twitter
- [ ] Datos estructurados `Organization`, `WebSite` y `Person`; validados en <https://search.google.com/test/rich-results> y <https://validator.schema.org>
- [ ] Search Console: propiedad verificada (DNS o etiqueta), sitemap enviado, indexación solicitada para portada, equipo y marca
- [ ] Bing Webmaster (importa desde Search Console)
- [ ] Google Business Profile de la empresa
- [ ] Señales cruzadas: mismo nombre y cargo en LinkedIn, GitHub y redes, con enlace al sitio
- [ ] Datos coherentes entre el sitio, el portafolio y la hoja de vida de cada persona (nivel, años, cifras)

## Publicación (con confirmación de la dueña)
- [ ] La empresa está inscrita y el RUC es el correcto
- [ ] Dominio apuntando, variables de entorno cargadas en el proveedor
- [ ] Despliegue desde `main`; prueba de humo en producción (portada, formulario, chat)
- [ ] Perfil de la organización en GitHub con banner claro/oscuro y enlace al sitio
- [ ] Correo de contacto y WhatsApp probados desde un teléfono
