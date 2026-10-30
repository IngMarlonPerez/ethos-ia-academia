---
name: comparar-plataformas-comercio
description: 'Compara Amazon, Mercado Libre, Shopify u otras en seguridad, usabilidad y modelo de negocio, sin comprar y con fuentes. Usar para «simulación de compra» o «comercio electrónico».'
---

# Comparación de plataformas de comercio electrónico

## Límites (no negociables)
- **No comprar, no pagar, no crear cuentas, no iniciar sesión.** La simulación llega hasta el listado de resultados, la ficha del producto, las condiciones de envío a Ecuador y el carrito vacío. Si una página exige cuenta, eso **es un dato** de usabilidad: se anota y se sigue; no se esquiva.
- No se resuelven CAPTCHA ni verificaciones de robot.

## Pasos
1. **Elegir un mismo producto de prueba** barato y neutro (p. ej., una memoria USB de 64 GB) y la misma ubicación de envío (Ecuador).
2. **Navegar con el navegador integrado** (herramientas `mcp__Claude_Browser__*`): abre el listado en cada plataforma, lee el texto con `get_page_text` y anota por plataforma:
   - **Seguridad:** ¿pide cuenta?, avisos de cookies, «compra protegida»/devoluciones, métodos de pago visibles, protocolo HTTPS.
   - **Usabilidad:** buscador y filtros, orden, información de precio y entrega a Ecuador, costo de envío o envío gratis con mínimo, pasos antes de ver resultados.
   - **Modelo de negocio:** ver paso 3.
3. **Modelo de negocio con fuente** (no de memoria):
   - **Amazon:** mercado híbrido (comisiones a vendedores externos y margen de productos propios): Etro (2024), *Journal of Economic Surveys*, https://doi.org/10.1111/joes.12594. Uso de IA de extremo a extremo: Papastamoulou y Antonopoulos (2025), *Systems*, https://doi.org/10.3390/systems13090746.
   - **Mercado Libre:** informe anual Form 10-K ante la SEC (los vendedores externos generan la mayor parte del volumen; las ventas propias son menos del 10 %; ecosistema con Mercado Pago, Mercado Envíos, Mercado Ads). Búscalo en sec.gov y verifica con `WebFetch` antes de citar.
   - **Shopify:** software como servicio por suscripción; los planes y las comisiones por pagos externos están en https://www.shopify.com/pricing (cita como página web con «Recuperado el …» porque cambia, y anota que los precios varían por país).
   - Vuelve a comprobar las cifras cada vez: los precios y las condiciones cambian.
4. **Capturas:** con el navegador integrado se lee, pero no guarda PNG. Para archivos usa `evidencias-capturas/scripts/html_a_png.ps1` sobre la URL. Si el sitio lo bloquea (Amazon lo hizo), **pide a la usuaria su captura** (Win+Shift+S) e insértala; no la dejes sin evidencia ni la inventes.
5. **Cuadro comparativo** con criterios en filas (modelo de negocio, uso de IA, seguridad, usabilidad y entrega) y una nota que diga la fecha, el país de la consulta y que no se completó compra ni pago.

## Qué no afirmar
Nada sobre una plataforma que no se vio o no tiene fuente. Si falta, déjalo resaltado como «verificar en la documentación oficial».
