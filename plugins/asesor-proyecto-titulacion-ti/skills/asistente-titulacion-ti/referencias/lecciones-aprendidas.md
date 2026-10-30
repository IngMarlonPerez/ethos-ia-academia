# Lecciones aprendidas

Cada regla del Asesor nace de un problema real. Léela al empezar un proyecto y antes de cada entrega. Las filas marcadas **(VicMar)** salen de la tesis VicMar Data AI; las marcadas **(Académicos)** vienen del plugin «proyectos-academicos» de V. M. Lluilema Pisco, que las vivió en una tesis de otra carrera, y aplican igual a TI.

## Del Word y de las versiones
| Qué pasó | Consecuencia | Regla que lo evita |
|---|---|---|
| **(Académicos)** La usuaria guardó desde una ventana de Word abierta con una versión anterior | Se revirtieron correcciones ya hechas (una cifra, una fuente, un párrafo) | Registrar cada corrección en `documento/aserciones.json` (`aserciones.py registrar`) y correr `aserciones.py verificar` antes de editar o regenerar. Si alguna fue revertida, **informar y preguntar** antes de reaplicarla |
| **(Académicos)** Word abierto durante la edición | El archivo no se pudo guardar de vuelta | Pedir que cierre Word antes de cada lote; si el guardado falla por archivo en uso, esperar |
| **(Académicos)** El documento de trabajo perdió el encabezado y el fondo de la portada | Páginas sin logo y portada sin diseño | Trabajar siempre sobre copias; `huella.py plantilla` en cada revisión; `huella.py restaurar` si faltan |
| **(Académicos)** Se pidió «no mover nada» y había que añadir figuras | Riesgo de alterar el trabajo manual de la usuaria | Solo inserciones y comprobación con `diff_versiones.py --solo-inserciones` |
| **(Académicos)** Un título quedó con otra lista de numeración (se veía «1.1.1» donde correspondía «1.2.1») | Numeración de títulos alterada | Revisar la numeración de títulos hermanos en el PDF; `huella.py verificar` avisa si cambió `numbering.xml` |
| **(VicMar)** Cambios a mano perdidos al regenerar el Word | Trabajo de la usuaria sobrescrito | El generador compara la **huella del texto** y se detiene; ahora además archiva cada versión previa en `documento/versiones/` |
| **(VicMar)** El generador creyó que el Word se había editado a mano justo después de exportar el PDF | Word vuelve a guardar el `.docx` al actualizar el índice, y el md5 cambia | Comparar la huella del texto (párrafos y tablas, sin el índice), no el md5 |
| **(VicMar)** Referencias y Anexos aparecían numerados | Numeración automática del estilo Heading 1 | `quitar_numeracion` en Referencias y Anexos; el verificador falla si llevan número |
| **(VicMar)** Texto de instrucciones de la plantilla visible en el entregado | Documento con frases como «Se refiere a…» | Borrar esos párrafos en el generador y revisar el PDF |

## De las fuentes y del texto
| Qué pasó | Consecuencia | Regla que lo evita |
|---|---|---|
| **(VicMar)** Se citó una cifra de un diario | La usuaria la rechazó: las tutoras revisan con criterio de fuente académica | Solo fuentes con DOI o Scopus, leídas en el texto completo con su página |
| **(Académicos)** Referencia en la lista que nunca se citaba | Incumplimiento de APA 7 | Cruce automático cita↔referencia (`verificar_apa.py`) en cada revisión |
| **(Académicos)** Referencias fuera de la ventana de 5 años sin explicación | Incumplimiento de la guía | Reemplazarlas o justificarlas por escrito |
| **(Académicos)** Párrafos que empezaban siempre con «Autor (año) señala…» | Texto con aspecto de copia, poco propio | Idea propia primero y la cita entre paréntesis; revisar el «desfile de autores» |
| **(Académicos)** Texto demasiado cercano a las fuentes | Riesgo de similitud en Turnitin o Compilatio | Correr `similitud.py` (investigación científica, `redaccion-apa7`) antes de entregar |
| **(Académicos)** Nombres de autores y tutor escritos de memoria en el póster | Nombres equivocados | Tomar autores, tutor y carrera de `titulacion.json` o de la portada |
| **(Académicos)** La guía del tutor traía ejemplos con errores de APA | Tiempo perdido discutiendo formato | La guía manda en **contenido y estructura**; APA 7 manda en **formato**. Anotar la discrepancia y seguir |
| **(VicMar)** Cifras distintas entre Resumen y cuerpo | Incoherencia | Ambas salen del mismo artefacto; `verificar_coherencia.py` las compara |
| **(VicMar)** «Tres corridas» en el texto cuando había cuatro | Un conteo escrito a mano | Contar desde los archivos |

## Del proyecto y del repositorio
| Qué pasó | Consecuencia | Regla que lo evita |
|---|---|---|
| **(Académicos)** La conversación se quedó sin contexto varias veces | Se perdió el hilo y hubo que reconstruir decisiones | Estado persistente en `titulacion.json`, el tablero y el registro de cambios; reanudar con `tablero.py estado` |
| **(Académicos)** Figuras de terceros sugeridas para ilustrar | Riesgo de derechos de autor y baja calidad | Figuras propias y editables, con «Elaboración propia a partir de…» |
| **(Académicos)** Figuras nuevas que no quedaron en la carpeta del proyecto | La usuaria no tenía los archivos | Toda figura se guarda en `figuras/` con su PNG y su fuente editable |
| **(VicMar)** Un cliente gráfico de git cambió de rama con cambios sin confirmar | Casi se pierden 262 archivos | Respaldo y bundle antes de reorganizar; mover, no borrar |
| **(VicMar)** El generador importaba su biblioteca desde la carpeta de la herramienta | El repositorio no se podía regenerar sin esa herramienta | `copiar_biblioteca.py` deja el repositorio autocontenido |
| **(VicMar)** La herramienta sugería líneas de coautoría de un asistente en los commits | La IA habría figurado como autora | Regla 8: la IA no es autora; `uso-etico-ia` limpia y genera el anexo local |
