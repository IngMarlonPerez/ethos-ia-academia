---
name: equipo-y-practicantes
description: 'Parte humana de la empresa: convenio y cartas para practicantes, cesión de propiedad intelectual, perfiles por rol, certificados y fichas del equipo. Usar al recibir practicantes o certificar prácticas.'
---

# Equipo y practicantes

Los practicantes producen código, documentación y análisis reales que alimentan los sistemas de la empresa (ERP, CRM, académico). Por eso todo se hace con **contenido verdadero y rastreable**, y con los derechos de propiedad intelectual bien cedidos.

## 1. Relación con la universidad
- **Qué suele pedir el sistema de gestión académica:** resolución de inscripción de la SCVS, RUC y nombramiento del representante legal, dentro de un plazo (en el caso real, 30 días). **Confirma la lista exacta con la coordinación de prácticas**: no la supongas. Anota el contacto.
- **Convenio:** si menciona una razón social o RUC, verifica si hace falta una adenda cuando la empresa quede inscrita.
- **Cartas de vinculación y solicitudes** llegan desde el sistema de la universidad a un enlace personal del representante legal: **la aceptación la hace él o ella con su propia sesión**, no se automatiza.
- **Revisa el RUC** que la universidad tiene registrado: si es el personal del gerente (cédula + 001), pide que lo corrijan en su sistema; no puedes editar documentos de terceros. `verificar-expediente` lo detecta.
- **IESS de los practicantes:** depende del tipo de convenio (pasantía preprofesional o relación laboral); lo define la universidad. Si hay pagos o becas, consulta con el contador por las retenciones.
- Mientras se legaliza: registro documentado de las prácticas (asistencia, informes, evidencias de los proyectos).

## 2. Propiedad intelectual
- Por defecto, la obra es de quien la crea: sin cesión por escrito, el código del practicante **no** es de la empresa.
- Firma de `plantillas/acta_cesion_pi.md` por cada practicante, **sin esperar** a que termine la constitución. Se ratifica después a favor de la razón social.
- Preserva el **derecho moral de autoría** (irrenunciable) y agrega confidencialidad.
- Contratos con clientes externos: cláusula de quién es dueño del código final (caso por caso).
- Generación: `plantilla_a_docx.py` con `datos.json` por practicante (lista de firmas en un anexo si son varios).

## 3. Perfiles de práctica
Cada practicante se asigna a un perfil que define producto por actividad, fuentes reales y verificaciones permitidas (`referencias/perfiles.md`): ciberseguridad, soporte y mesa de ayuda, redes e infraestructura, desarrollo del ERP, CRM comercial, sistema académico inteligente. Si el practicante no encaja, se crea un perfil nuevo con la misma estructura.

**Caso de referencia completo (Ethos IA):** la skill personal `practicas-ethoslab` (en `~/.claude/skills/`) trae el flujo íntegro con ejemplos reales: lectura del cronograma del SGA, productos por actividad, carpeta de evidencias de 7 subcarpetas, informe técnico, laboratorios Docker, certificados y el PDF de la tarea con carátula. Para una empresa nueva, copia esa skill y cambia `datos_empresa.md`, el membrete y la tutora; los motores (`mdoc.py`, `xl.py`, `flow.py`, `pdf_word.py`) son los mismos que usa este plugin.

## 4. Reglas de veracidad (no negociables)
1. **Nunca fabricar evidencia**: ni fotos, ni capturas, ni actas, ni mensajes, ni resultados que no se ejecutaron. Lo que solo puede aportar el estudiante queda como pendiente explícito.
2. Cada afirmación técnica tiene fuente (archivo y línea, salida de un comando guardada con fecha, documento oficial). Rotula **«Verificado / Por confirmar»**.
3. Solo verificaciones **pasivas** sobre activos propios de la empresa; nada de escaneo de puertos, fuerza bruta ni pruebas de intrusión sin autorización escrita de Gerencia.
4. **Secretos**: nunca abrir ni citar valores de `.env`, claves o tokens; solo nombres de variables. Nunca pedir ni escribir contraseñas del sistema académico.
5. **Datos personales**: nada de cédulas, teléfonos ni correos personales en lo que se comparte.
6. **Fechas honestas**: no retrofechar.
7. **El estudiante revisa, entiende y firma su autoría**; declara el uso de IA según la norma de su universidad.
8. Compartir en Drive, enviar correos o publicar: preparar en local y **preguntar antes**. El enlace de la carpeta queda como marcador hasta verificarlo en una ventana de incógnito.

## 5. Certificado de prácticas
`python "${CLAUDE_PLUGIN_ROOT}/skills/equipo-y-practicantes/scripts/certificado_practicas.py" --empresa empresa.json --membrete "<membrete>.docx" --datos practicante.json --salida "11_Equipo_y_Practicantes/Certificado_<Nombre>.docx" --pdf`
Redacción neutra; **no se firma aquí**: el representante firma con firma electrónica solo al confirmar que se cumplieron las horas. La fecha no es anterior al fin de la práctica.

## 6. Equipo en el sitio web
- Una ficha por persona (foto aprobada por ella, cargo inscrito, trayectoria verificable, enlaces). El equipo vive solo en la página de equipo.
- **Fotos generadas con IA:** solo con la aprobación de la persona retratada, y dejando constancia.
- Datos coherentes entre el sitio, su portafolio y su hoja de vida (nivel, años, cifras).
- Responsable de talento humano o tutor profesional: indícalo en las fichas y en los documentos a la universidad.

## Control
Acta de cesión firmada por cada practicante; lista de documentos de la universidad confirmada y entregada; cada producto con su fuente; certificados con datos reales; `verificar-expediente --carpeta-compartida` sobre lo que se comparte. Marca la etapa 9.
