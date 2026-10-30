---
name: nombre-y-marca
description: 'Nombre y marca de una empresa: alternativas, disponibilidad (Superintendencia, SENADI, dominio), paleta y guía de marca. Usar al elegir o validar el nombre, la paleta o el encargo del logo.'
---

# Nombre y marca

## 1. Estructura de nombres
Define tres niveles, cada uno con su función:
| Nivel | Qué es | Dónde va |
|---|---|---|
| **Razón social** | Nombre legal, termina en S.A.S. | Constitución, RUC, facturas, contratos, balance |
| **Nombre comercial** | Nombre con el que se presenta al público; se declara en el formulario de constitución (campo opcional) y en el RUC | Logo, web, redes, pie del membrete |
| **Marca** | Signo registrado en el SENADI (en Ecuador las marcas no se «patentan») | Exclusividad por 10 años renovables |

La razón social no protege la marca ni al revés: son trámites distintos.

## 2. Generar alternativas (10, no 3)
Cuando la usuaria no tiene nombre, propón 10 con una lógica visible, y descarta las que fallen la prueba del punto 3. Funcionó agrupar por inspiración: 3 de origen clásico, 3 modernos, 3 contemporáneos y 1 personal/familiar. Los nombres son **palabras originales inspiradas en un concepto**, no el apellido de una persona (evita problemas de derechos de imagen). Presenta una tabla: nombre · inspiración · por qué encaja · riesgo. Detalle del método en `referencias/metodo_nombres.md`.

## 3. Verificar disponibilidad antes de invertir en diseño
Hazlo en este orden y registra el resultado en `01_Nombre_y_Marca/guia/disponibilidad.md`:
1. **Denominación** en el buscador de la SCVS (para la razón social). Si no está disponible, prueba variantes. **La reserva dura 30 días**: no la pidas hasta tener listo el resto del expediente.
2. **SENADI**: filtro gratuito (buscador de solicitudes y Gaceta de la Propiedad Intelectual); si el nombre pasa, la **búsqueda fonética oficial** detecta parecidos de sonido; si sale limpia, el registro formal. Un mismo nombre puede estar libre en tu rubro aunque exista en otro (Clasificación de Niza). Confirma las tasas vigentes antes de decir cifras.
3. **Dominio** (.com, .ec, .tech…) y **usuarios de redes**.
4. **Búsqueda de choque**: ¿existe un programa estatal, una empresa conocida o un producto con ese nombre? Un nombre muy asociado a un programa público se descartó por riesgo de confusión.

**Control:** no empieces logo, sello ni papelería hasta tener la denominación reservada o la empresa inscrita. En el caso real, el nombre planeado no se pudo reservar y se rehízo toda la marca.

## 4. Paleta corporativa
Si ya existe un sitio o un logo, **extrae** los colores de ahí; no inventes otros. Define y documenta:
- Fondo oscuro digital, color de marca principal (acento), color secundario, neutros de texto.
- **Versión de impresión** de cada color (más sobria): los tonos brillantes están calibrados para pantalla y se ven lavados en papel o tela.
- Reglas: fondo oscuro por defecto en lo digital; un color manda y el otro acentúa; el monograma no lleva más de 2 colores; contraste mínimo de texto (WCAG AA); sobre fondo claro el texto va en el tono profundo o en negro.
- Guarda los colores en `empresa.json → marca` (RRGGBB): de ahí los toman el membrete, los documentos y el sitio.

## 5. Guía de marca de una página
Qué archivo usar dónde: camiseta clara y oscura, gorra (bordado: trazo grueso), sello físico, foto de perfil, portadas de redes (tamaños oficiales), favicon. Se arma con la skill `logos-y-piezas` una vez que existe el logo.

## 6. Encargo del logo
- **Diseñador**: usa `plantillas/brief_disenador.md` (empresa, tono, qué no se quiere, paleta obligatoria, entregables y usos). Pide siempre el vector (.ai o .svg), PNG con transparencia, versión negra, blanca y compacta, y la **cesión escrita de derechos**.
- **Generador de imágenes con IA** como exploración: `referencias/prompts_logo_ia.md`. No son el logo final: revisa cada letra (los textos salen con errores) y pide siempre un vector limpio al diseñador o vectoriza con criterio.

## Control de la etapa
Nombre disponible en SCVS, SENADI, dominio y redes; paleta en `empresa.json`; brief enviado o logo aprobado. Marca la etapa 1 con la nota «denominación reservada/inscrita el …».
