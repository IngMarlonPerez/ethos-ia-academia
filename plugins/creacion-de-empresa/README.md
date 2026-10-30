# Creación de Empresa

Plugin de Claude (Claude Code, app de escritorio) que lleva la **creación de una empresa de punta a punta**. Funciona como un **pipeline con controles de calidad**: cada etapa tiene una skill y un control, y ninguna se cierra con el control pendiente.

Nació de la creación real de **ETHOSLAB S.A.S.** (nombre comercial *Ethos IA*, Cuenca, Ecuador, 2026) y deja reutilizable todo lo que funcionó: el método, los scripts y los documentos. Lo que salió mal está en [`lecciones_aprendidas.md`](skills/asistente-creacion-empresa/referencias/lecciones_aprendidas.md); léelo antes de empezar.

Autoría: Ethos IA (ETHOSLAB S.A.S.). Versión 1.0.0.

## La idea central
Los datos de la empresa viven en **un solo archivo, `empresa.json`**. El membrete, el balance inicial, las actas y la web se **generan** desde él. Así el RUC, la razón social o el nombre del representante no pueden quedar distintos en cada documento (el error más caro del caso real: el RUC personal del gerente quedó en documentos firmados).

## El pipeline
| Etapa | Skill | Qué deja |
|---|---|---|
| 0 Inicio | `iniciar-empresa` | Expediente con 14 carpetas, `empresa.json`, tablero |
| 1 Nombre y marca | `nombre-y-marca` | Nombre disponible (SCVS, SENADI, dominio), paleta, brief del logo |
| 2 Logos | `logos-y-piezas` | Logo en color/negro/blanco, isotipo, favicons, foto de perfil, portadas, sello |
| 3 Papelería | `papeleria-membretada` | Membrete Word/PDF, plantillas Markdown → Word, firma electrónica |
| 4 Constitución | `constitucion-sas-ecuador` | Ruta de la S.A.S. en la Superintendencia, formulario de 7 secciones, checklist |
| 5 Obligaciones | `obligaciones-post-constitucion` | Calendario de plazos, RUC, SRI, patente, banco, contador, IESS |
| 6 Balance inicial | `balance-inicial-scvs` | TXT desde las plantillas oficiales + documentos con membrete para firmar |
| 7 Gobierno | `gobierno-societario` | Acuerdo de accionistas, cesión de acciones, acta y nombramiento |
| 8 Sitio web | `sitio-web-corporativo` | Next.js + Supabase, seguridad, SEO, CI, perfil de GitHub |
| 9 Equipo | `equipo-y-practicantes` | Convenio, cesión de propiedad intelectual, perfiles, certificados |
| 9b Credenciales | `credenciales-del-equipo` | Carné digital con foto, cargo y QR de verificación (PNG y PDF) |
| 9d Emisión verificable | `emision-certificados-verificables` | Certificados automáticos con QR verificable y firma del emisor |
| 9c Certificados | `certificados-y-reconocimientos` | Menciones de honor y certificados de capacitación o logro, A4 horizontal con QR |
| 10 Verificación | `verificar-expediente` | Control de coherencia (RUC, nombres, textos prohibidos, datos personales) |

Punto de entrada: **`asistente-creacion-empresa`** (ubica la etapa, muestra el tablero y deriva a la skill). También `/creacion-de-empresa:nueva-empresa` y `/creacion-de-empresa:estado-empresa`.

## Scripts (todos probados con los datos reales del caso)
| Script | Qué hace |
|---|---|
| `iniciar_empresa.py` | Crea el expediente, `empresa.json` y el tablero |
| `tablero.py` | Ver y marcar el estado de cada etapa |
| `crear_membrete.py` | Genera la hoja membretada .docx desde `empresa.json` y el logo (colores de marca, marca de agua, pie con íconos, «Página X de Y») |
| `plantilla_a_docx.py` | Convierte una plantilla Markdown con `{{datos}}` en un Word con membrete; lo que falta queda en amarillo |
| `mdoc.py` | Motor de documentos Word sobre el membrete (tablas, figuras, firmas) |
| `pdf_word.py` | PDF con Word instalado (rutas largas, tiempo límite, reintento) |
| `exportar_logo.py` | Del logo (PDF, .ai o PNG) a favicons, redes, portadas, íconos y variantes monocromas |
| `calendario_plazos.py` | Plazos desde la fecha de inscripción, con días restantes |
| `generar_txt_scvs.py` | TXT del balance **idénticos a las plantillas oficiales** (376 y 246 cuentas), padres calculados y control de cuadre |
| `generar_documentos_balance.py` | Asiento, comprobante o declaración y estados financieros, en una página cada uno, para firma del contador |
| `certificado_practicas.py` | Certificado de prácticas para firma del representante |
| `verificar_expediente.py` | Busca RUC equivocados, nombres anteriores, textos prohibidos y cédulas ajenas |

Requisitos: Python 3.10+, `python-docx`, `Pillow`, `numpy` y `pymupdf`; **Microsoft Word** (Windows) para exportar a PDF.

## Reglas que el plugin impone
1. **Veracidad**: nada inventado; lo que falta queda en amarillo y se dice quién lo aporta.
2. **Acciones hacia afuera con confirmación**: enviar a la Superintendencia, firmar, pagar, publicar, subir a GitHub o a Drive.
3. **Datos personales** (cédulas, `.p12`, claves) fuera de GitHub y de carpetas compartidas.
4. **No es asesoría legal ni contable**: un abogado societario y un contador matriculado revisan antes de firmar.
5. **Fuentes antes que memoria**: plazos, tasas y códigos se confirman en el portal o la norma.

## Alcance geográfico
Las etapas 4, 5 y 6 son de **Ecuador** (S.A.S., SCVS, SRI, IESS, municipios). Las demás sirven en cualquier país; para otro país se conserva el tablero y se reemplazan esas tres skills con el mismo método.

## Instalación
El plugin está en el catálogo local `ethos-ia-academia` (directorio `claude-plugins`). Desde Claude Code: `/plugin` → catálogo `ethos-ia-academia` → `creacion-de-empresa`, o `/plugin install creacion-de-empresa@ethos-ia-academia`. Luego reinicia la sesión o recarga los plugins.
