# Campos de `empresa.json`

Es el único archivo de datos de la empresa. Los scripts del plugin lo leen; no lo copies a mano en documentos.

| Campo | Para qué se usa | Quién lo confirma |
|---|---|---|
| `razon_social` | Membrete, documentos, pie de página, contratos | Razón de inscripción de la SCVS |
| `nombre_comercial` | Pie del membrete, sitio web, redes | Formulario de constitución / RUC |
| `ruc` | Membrete y documentos. **RUC de la compañía, no el personal del gerente** | Correo «Compañía Constituida» + consulta de RUC del SRI |
| `clave_archivos` | Sufijo de los nombres de archivo (p. ej. `ETHOSLAB`) | La dueña |
| `nombres_anteriores` | Nombres que ya no valen (la razón social que no se pudo reservar): `verificar_expediente.py` los busca | La dueña |
| `textos_prohibidos` | Frases que no pueden aparecer en la web ni en piezas públicas | Reglas de la dueña |
| `domicilio.*` | Ciudad, provincia, país, dirección; `direccion_membrete` es la línea corta del pie | Acto constitutivo |
| `contacto.*` | Teléfono, correo y web que salen en el membrete y el sitio | La dueña |
| `representante.*` | Nombre, cargo e identificación; firma de documentos | Nombramiento inscrito |
| `socios[]` | Nombre, identificación y acciones de cada socio | Acto constitutivo / libro de acciones |
| `capital.*` | Suscrito, pagado, acciones, valor nominal y plazo de pago en meses | Acto constitutivo (cláusulas cuarta y quinta) |
| `constitucion.*` | Expediente, trámite, N.º de inscripción y fecha, N.º de nombramiento | Razón de inscripción |
| `actividades_ciiu.*` | Actividad principal y complementarias | Formulario de constitución |
| `marca.*` | Colores `color_primario`, `color_acento`, `color_secundario`, `color_texto`, `color_fondo_digital` (RRGGBB) y tipografía web | Guía de marca |
| `redes` | Enlaces a redes y organización en GitHub | La dueña |
| `etapas` | Estado de cada etapa del pipeline (lo gestiona `tablero.py`) | — |

## Privacidad
`empresa.json` contiene cédulas. No lo subas a GitHub ni lo mandes a terceros. Para compartir datos con un contador o con la universidad, entrega solo los campos que necesitan.
