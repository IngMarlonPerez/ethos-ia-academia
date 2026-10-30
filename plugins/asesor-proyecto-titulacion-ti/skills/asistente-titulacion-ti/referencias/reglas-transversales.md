# Reglas transversales del Asesor

Salen de lo que pasó en los Avances 1 y 2 de la tesis VicMar Data AI (UNEMI, 2026). Cada regla tiene su razón.

## 1. Solo fuentes académicas verificables
Toda cifra o antecedente del documento sale de una fuente con DOI o indexada en Scopus, verificada en el **texto completo** del PDF (con su página). Nunca prensa, blogs, Wikipedia ni sitios secundarios.
- **Por qué:** la usuaria rechazó una cifra de SENESCYT citada por un diario («ESA CITA NO PUEDE IR… PARA ESO ES SCOPUS»), y las tutoras revisan con ese criterio.
- **Excepción acotada:** para datos de una tecnología (versión, licencia, ciclo de soporte) se admite su documentación oficial o su repositorio oficial, citados en APA como página web o software, con la fecha de consulta.
- Una fuente que no reporta una tasa poblacional (por ejemplo, con muestra balanceada) no sirve como referente de esa tasa.

## 2. Leer antes de seleccionar
Un artículo cuenta como trabajo previo solo si:
- se leyó completo, con el agente `lector-critico` del plugin de investigación;
- tiene evidencia textual con la **página de la revista**.

No se cita nada leído solo en el resumen.

## 3. La arquitectura se evalúa siempre, en tres lugares
- **En la literatura:** la tabla de trabajos previos tiene las columnas **Arquitectura** y **Tecnologías**, obligatorias; si el artículo no las describe, se escribe «no reporta».
- **En el diseño:** se comparan al menos 3 estilos con una matriz ponderada y se registra un ADR.
- **En el código:** el agente `auditor-arquitectura` y `verificar_reglas.py` comprueban que lo implementado es lo declarado.

## 4. Una sola fuente de verdad
Ninguna cifra del documento se escribe a mano:
- el generador del Word lee los artefactos del código (`metrics.json`, resultados de evaluación) y los JSON del proyecto (requerimientos, trabajos previos, decisiones);
- el código que se muestra se extrae del repositorio al generar;
- el verificador falla si el texto y los artefactos no coinciden.

**Por qué:** al reentrenar, las cifras cambian. Un documento editado a mano queda desactualizado sin que nadie lo note.

## 5. No se modifica lo oficial
- La plantilla de la universidad y los documentos ya entregados no se editan: se copian y el generador inserta.
- Antes de regenerar un documento, compara la huella de su texto. Si la usuaria lo editó a mano, integra sus cambios en el generador (`diff_versiones.py` muestra qué cambió).
- **Cada versión se conserva**: el generador archiva la salida anterior en `documento/versiones/` antes de sobrescribir.
- **La portada, los encabezados, los pies y el logo no se tocan**: `huella.py verificar` lo comprueba después de cada lote, y `huella.py restaurar` los recupera desde la plantilla.
- **Las correcciones no se revierten en silencio**: se registran en `documento/aserciones.json` y `aserciones.py verificar` avisa si un guardado desde un Word viejo las deshizo.
- Detalle de los incidentes reales en `lecciones-aprendidas.md`.

## 6. Resultados honestos
Si una meta no se cumple (por ejemplo, un AUC de 0,75 cuando la meta era 0,90), se reporta tal cual y se discute como hallazgo. Nunca se ajustan los datos ni la meta para que cuadre.

## 7. Seguridad y privacidad
- Claude **no escribe contraseñas**: la usuaria inicia sesión ella misma en Scopus, en la demo o en cualquier sistema.
- No se envían datos personales a proveedores externos de IA (skill `proteccion-datos`).
- Los datos reales con identificadores se seudonimizan. Los originales se **mueven** fuera del repositorio, con confirmación de la usuaria; nunca se borran.
- Commits solo con autorización, y push solo si la usuaria lo pide.

## 8. La IA no es autora
- La herramienta de IA no se nombra en el código, los comentarios, los documentos, los metadatos ni los commits. Los commits no llevan líneas de coautoría de un asistente, aunque la herramienta las sugiera.
- Su uso se declara con transparencia en un anexo aparte, en una carpeta local que no se publica (skill `uso-etico-ia`). Toda la responsabilidad es de los autores.
- **Por qué:** los autores lo pidieron expresamente («la IA no tiene responsabilidad y no tiene autoría»), y las revistas no aceptan a la IA como autora (Thorp, 2023).

## 9. Mover, no borrar; respaldar antes de reorganizar
- Lo que ya no se usa se mueve a `_POR_REVISAR_ELIMINAR/` con su motivo y su evidencia; los autores deciden qué borrar.
- Antes de reorganizar o publicar se hace un bundle del historial y una copia de las carpetas.
- **Por qué:** al reorganizar la tesis VicMar, un cliente gráfico de git cambió de rama con cambios sin confirmar y los guardó en un *stash*. Sin el respaldo y el stash, se habrían perdido 262 archivos.

## 10. Decisiones de la usuaria
Pregunta solo lo que es de ella: tema, alcance, universidad, qué decisión tomar entre opciones con costos distintos. Todo lo demás se deduce de los archivos o se resuelve con un valor por defecto razonable, que se informa.
