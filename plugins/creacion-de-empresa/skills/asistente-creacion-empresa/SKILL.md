---
name: asistente-creacion-empresa
description: 'Puerta de entrada para crear una empresa: ubica la etapa (marca, constitución S.A.S., RUC, balance, gobierno, web, equipo) y deriva. Usar al crear o formalizar una empresa, o con «qué sigue».'
---

# Asistente de creación de empresa

Este plugin nació de la creación real de **ETHOSLAB S.A.S.** (nombre comercial Ethos IA, Cuenca, Ecuador): del nombre y el logo hasta la inscripción en la Superintendencia de Compañías, el balance inicial, el sitio web y el equipo de practicantes. Todo lo que funcionó está en una skill; todo lo que salió mal está en `referencias/lecciones_aprendidas.md`. Léelo antes de empezar: ahorra días.

## Regla de oro
Los datos de la empresa viven en **un solo archivo, `empresa.json`**. Ningún documento, membrete ni página web se escribe con datos copiados a mano: se generan desde ese archivo. Así el RUC, la razón social y el nombre del representante no pueden quedar distintos en cada documento (el error más caro del caso real).

## Pipeline
| Etapa | Skill | Qué debe quedar | Control para cerrarla |
|---|---|---|---|
| 0 Inicio | `iniciar-empresa` | Carpeta del expediente y `empresa.json` | Datos mínimos completos; la carpeta no se comparte ni se sube a GitHub |
| 1 Nombre y marca | `nombre-y-marca` | Razón social, nombre comercial, paleta y guía de marca | Disponibilidad revisada en SCVS, SENADI, dominio y redes |
| 2 Logos y piezas | `logos-y-piezas` | Logotipo oficial exportado para web, redes, sello e impresión | Se ve bien en fondo claro y oscuro; PNG con transparencia |
| 3 Papelería | `papeleria-membretada` | Membrete Word/PDF y plantillas de documentos | RUC y razón social del membrete = `empresa.json` |
| 4 Constitución | `constitucion-sas-ecuador` | Empresa inscrita (acto constitutivo, nombramiento, RUC) | Inscripción y RUC confirmados con documento, no de memoria |
| 5 Obligaciones | `obligaciones-post-constitucion` | Calendario de plazos, RUC, SRI, patente, banco, contador, IESS | Calendario generado y cada plazo con responsable |
| 6 Balance inicial | `balance-inicial-scvs` | TXT, anexos firmados y envío al portal | «CUADRADO» en el portal y comprobante de envío guardado |
| 7 Gobierno | `gobierno-societario` | Acuerdo de accionistas, cesiones, actas, nombramientos | Revisión de abogado; notificaciones a la SCVS hechas |
| 8 Sitio web | `sitio-web-corporativo` | Sitio terminado, seguro y con SEO | Sin textos de «próximamente»; pruebas y build en verde |
| 9 Equipo | `equipo-y-practicantes` | Convenio, cesión de propiedad intelectual, perfiles, certificados | Cada documento rastreable a un hecho real |
| 9b Credenciales | `credenciales-del-equipo` | Carné digital (PNG y PDF) de socios, equipo y practicantes, con QR de verificación | Cargo real, sin datos sensibles, QR probado |
| 9d Emisión verificable | `emision-certificados-verificables` | Certificados automáticos con firma del emisor, QR y página pública de verificación (Next.js + Supabase) | Servidor valida, un certificado por cuenta, QR decodificado, claves fuera del repo |
| 9c Certificados | `certificados-y-reconocimientos` | Menciones de honor, certificados de capacitación y de logro (A4, PNG y PDF) con código y QR | Hecho real comprobado, código único, página de verificación lista |
| 10 Verificación | `verificar-expediente` | Informe sin hallazgos | `verificar_expediente.py` en 0 hallazgos |

Las etapas 1–3 y 8 pueden avanzar en paralelo con 4. Las etapas 5 y 6 dependen de que 4 esté cerrada. La 10 se repite antes de entregar cualquier documento hacia afuera.

## Qué hacer al empezar una sesión
1. Busca `empresa.json` en la carpeta de trabajo. Si no existe, invoca `iniciar-empresa`.
2. Muestra el tablero: `python "${CLAUDE_PLUGIN_ROOT}/skills/asistente-creacion-empresa/scripts/tablero.py" ver --empresa empresa.json`.
3. Propón **la siguiente etapa abierta** y la skill que la resuelve. No pidas datos que ya estén en `empresa.json`.
4. Al cerrar una etapa: `tablero.py marcar <n> cerrada --empresa empresa.json --nota "<evidencia>"`. La nota cita el documento que lo prueba (número de inscripción, nombre del PDF), no «listo».

## Reglas que valen en todas las etapas
1. **Veracidad.** Nada de datos, firmas, sellos, fechas ni evidencias inventadas. Lo que falte se rotula `[[por completar]]` (resaltado en amarillo) y se le dice a la usuaria quién debe aportarlo.
2. **Acciones hacia afuera, con confirmación.** Enviar un balance, firmar, pagar, publicar un sitio, subir a GitHub o a Drive, escribir a un contador o a la universidad: se prepara todo y se pregunta antes. Un envío a la Superintendencia no se corrige.
3. **Datos personales.** Cédulas, firmas electrónicas (.p12), claves y correos personales no van a GitHub, ni a carpetas compartidas, ni a un chat con terceros. `empresa.json` queda en la carpeta privada.
4. **No es asesoría legal ni contable.** El plugin ordena, redacta borradores y calcula; un abogado societario y un contador matriculado revisan antes de firmar. Dilo en una línea cuando entregues un documento legal.
5. **Fuentes antes que memoria.** Plazos, tasas y códigos (CIIU, plan de cuentas) se confirman en el portal o la norma. Marca «Verificado / Por confirmar».
6. **Tono empresarial.** Español formal, impersonal y claro, sin relleno. Los documentos se usan de verdad: alimentan el ERP, el CRM, la contabilidad y la web.
7. **El contenido es de la empresa.** No mezcles proyectos personales de los socios ni líneas de negocio que la dueña no pidió. Si un borrador pegado desde otra herramienta los trae, retíralos y avisa en una línea.
8. **Sin lenguaje de obra en curso** en el sitio ni en piezas públicas: se entregan terminadas.

## Otros países
Las etapas 1, 2, 3, 7, 8 y 9 sirven en cualquier país. Las etapas 4, 5 y 6 son de **Ecuador (S.A.S. ante la SCVS, SRI, IESS, municipios)**. Para otro país, conserva el tablero y reemplaza esas tres skills; pide primero los manuales oficiales de la autoridad societaria y la tributaria y arma el equivalente con el mismo método: leer el manual, listar prerrequisitos y plazos, generar los documentos desde `empresa.json`, probar en el portal sin enviar.

## Referencias
- `referencias/lecciones_aprendidas.md`: errores reales y cómo se evitan.
- `referencias/mapa_de_fuentes.md`: dónde se confirma cada dato (portales, manuales, normas).
