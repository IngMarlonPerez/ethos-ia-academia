# Lecciones aprendidas de una creación real (ETHOSLAB S.A.S., Cuenca, 2026)

Cada punto es algo que pasó. Está ordenado por el daño que causó.

## 1. Datos de identidad
- **El RUC de la sociedad no es la cédula del gerente + «001».** Ese número es el RUC de la persona natural. El RUC de la compañía lo asigna el SRI al inscribirse y llega en el correo «Compañía Constituida» de la SCVS. Por no confirmarlo, el RUC personal quedó en el membrete, en tres documentos firmados y en las cartas de vinculación de la universidad.
  → Confirmar el RUC en **dos fuentes**: el correo/razón de inscripción de la SCVS y la «Consulta de RUC» pública del SRI. Guardarlo en `empresa.json` y correr `verificar_expediente.py` antes de entregar.
- **El nombre planeado no siempre se puede reservar.** La razón social del plan original no estaba disponible; la empresa se constituyó con otra y el nombre querido quedó como nombre comercial. Todo el trabajo de marca hecho con el nombre viejo (logos, sello, guía) hubo que rehacerlo.
  → No diseñar logo ni sello hasta tener la denominación **reservada o inscrita**. Tener 2–3 nombres de respaldo.

## 2. Constitución
- **En una S.A.S. no hay «minuta estándar o propia».** Esa elección es de las compañías anónimas y de responsabilidad limitada. El acto constitutivo de la S.A.S. lo genera el sistema con texto fijo y no admite cláusulas propias.
  → Lo que el estatuto no permite (voto dirimente, no competencia, recompra) va en un **acuerdo de accionistas privado**.
- **El objeto social se arma solo, a partir de los CIIU.** Elegir bien los códigos es el paso técnico más importante. Máximo 1 principal + 5 complementarias, y la casilla «cualquier actividad mercantil o civil lícita» evita reformar el estatuto después. Los códigos se buscan en el catálogo del portal, no de memoria (hubo discrepancias entre versiones).
- **Firma electrónica solo en archivo (.p12).** No sirve token, HSM ni roaming. Si un socio no la tiene a tiempo, se puede constituir con quien sí la tiene y sumar al otro luego por cesión de acciones; pero entonces el socio que firma es el único con clave de la compañía ante la SCVS.
- **Un socio con bloqueos bancarios o mal buró no puede abrir la cuenta corriente.** Eso retrasó el depósito del capital. Definir desde el inicio quién será titular de la cuenta.
- **El capital no pagado tiene 24 meses**, pero el balance inicial vence en 30 días. No se confunden: el balance no exige depositar nada si el capital queda por pagar.

## 3. Balance inicial
- **Los TXT de ejemplo no sirven.** El portal exige **todas** las cuentas del plan, en el orden de su plantilla (376 en situación financiera, 246 en resultados). Un TXT con 10 líneas falla.
  → Partir siempre de las plantillas oficiales (carpeta «Formatos» del portal) y cambiar solo valores: `generar_txt_scvs.py`.
- **Dos criterios para el capital.** Capital suscrito **por pagar** (30101 = 200 y 30102 = −200, patrimonio 0) o **pagado** (Caja = 200, patrimonio 200). La contadora consultada prefirió «pagado en caja» y cambió su asiento. Se perdió un día regenerando documentos.
  → Decidir la modalidad **con el contador antes** de generar nada, y comprobar que el asiento, la glosa y el comprobante digan lo mismo. Un asiento firmado con «Capital pagado 200» en la tabla y «íntegramente pendiente de pago» en la glosa se contradice.
- **El plazo no es el mismo en dos fuentes.** El correo de la SCVS dice 30 días desde la inscripción; el art. 54 del Reglamento de las S.A.S. habla de 30 días posteriores al plazo de pago del capital. Ante la duda se presenta dentro de los 30 días del correo. El traslado al lunes del Código Tributario no aplica a la SCVS.
- **La lista de anexos del balance anual no es la del balance inicial.** Una herramienta de IA mostró «notas, informe del representante, acta de junta, comisario»: eso es del balance anual. El inicial pide RUC, comprobante de depósito y asiento de diario; el portal lo muestra en su propia pantalla de anexos.
- **El contador debe tener firma electrónica vigente** y poner nombre, C.C./RUC y número de registro profesional. Un familiar sin RUC activo ni firma electrónica no puede firmar. Los contadores independientes cobran poco por una firma puntual; los planes mensuales de contabilidad en línea parten de unos USD 50.
- **Word, no LibreOffice, para el PDF.** En esa máquina LibreOffice ya no estaba instalado; se exportó con Word (COM). Cada PDF debe pesar poco por página (el portal limita el tamaño): se redujeron las imágenes del membrete.

## 4. Marca y logos
- Los generadores de imágenes con IA **escriben mal** los textos de los letreros (por ejemplo «SOLUCIONES AVANGABAS»). Revisar cada letra antes de usarlos y no tomarlos como fuente del logo.
- El archivo `.ai` del diseñador era compatible con PDF: se abrió con PyMuPDF y trae un tablero por variante. Usar el de «color sobre blanco» para impresión y membrete; los tableros con fondo oscuro son solo para pantalla.
- Pedir al diseñador la **cesión escrita de los derechos** del logo y dejar su crédito donde corresponda.

## 5. Sitio web
- El sitio se construye **terminado**: nada de «próximamente» ni «en construcción». Se despliega cuando la empresa esté inscrita.
- Los briefs pegados desde otras IA suelen colar líneas de negocio ajenas o proyectos personales de los socios. Quitarlos por defecto y avisar.
- Las páginas de equipo llevan nombres y trayectorias; la portada habla del cliente. Las fotos generadas con IA solo se publican con la aprobación de la persona retratada.
- `.env*` fuera del repositorio; solo la plantilla `.env.local.example` se publica.

## 6. Gobierno
- Si entra un socio después de constituida la sociedad, la vía rápida es la **cesión de acciones** (documento privado + notificación a la SCVS dentro de 8 días), no un aumento de capital. Nombrar un segundo gerente con representación individual puede exigir antes una reforma del artículo del estatuto que habla de «el Gerente General» en singular: confirmarlo en el portal o con un abogado.
- Solo el **representante legal registrado** obtiene la clave de la compañía y presenta el balance inicial. Un cambio de representante bloquea la clave. Presentar el balance inicial **antes** de registrar un nuevo nombramiento.
- Las acciones de una S.A.S. se pagan solo en numerario o con bienes; **el trabajo no se aporta como capital**. Para un colaborador con expectativa de participación: contrato de trabajo o de servicios más una promesa escrita de cesión de acciones con plazos de consolidación (vesting).

## 7. Práctica de trabajo
- Pedir el logo y el contador **en paralelo** con la constitución; son lo que más tarda.
- Un solo archivo de datos y scripts que generan los documentos: cuando cambió el criterio del capital, regenerar tardó minutos, no horas.
- Guardar siempre la versión anterior (`_version_anterior`) cuando se reemplaza un membrete o un TXT.
