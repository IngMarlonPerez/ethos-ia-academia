# Tabla comparativa de trabajos previos

## Columnas (literatura/trabajos_previos.json)
| Campo | Qué va | De dónde sale |
|---|---|---|
| cita | «Apellido et al. (año)» | referencia |
| referencia_apa, doi, titulo, revista, anio | referencia completa | Scopus o Crossref |
| problema | qué problema resolvió | ficha del lector crítico (Q técnica) |
| tecnica | modelo, algoritmo o método | ficha |
| **tecnologias** | lenguaje; frameworks; base de datos; otras (o «no reporta») | ficha (Q tecnologías) |
| **arquitectura** | monolito, capas, cliente-servidor, microservicios, eventos, serverless, pipeline por lotes… (o «no reporta») | ficha (Q arquitectura) |
| datos_muestra | tamaño, país, periodo | ficha |
| validacion_metricas | esquema de validación y métricas con cifras | ficha (Q validación) |
| resultado | hallazgo principal con cifra | ficha |
| limitacion | declarada por el autor o señalada por ti (dilo) | ficha (Q limitación) |
| relacion_con_este_trabajo | qué decisión del proyecto respalda o qué vacío muestra | tu análisis |
| evidencia | cita textual + **página de la revista** | ficha |
| texto_completo_leido | true solo si se leyó el PDF completo | lector crítico |
| puntajes | 0–2 por pregunta | ficha |
| decision | Incluido / Elegible – no seleccionado / No recuperado | selección |

## Para el Word
`tabla_trabajos_previos.py --tabla t.json` produce 6 columnas resumidas:

| Autor (año) | Problema y técnica | Tecnologías | Arquitectura | Validación y resultado | Limitación / relación |

- Va en letra de 8 a 9 pt, con encabezado repetido y título APA («Tabla N. Comparación de trabajos previos»).
- Si el tutor pide la comparación solo en prosa (como la UNEMI), la tabla completa va en la hoja «Extracción bibliográfica» de las matrices y en el anexo.

## Ejemplo ilustrativo (autor ficticio: el contenido real sale siempre de la ficha)
| Autor (año) | Problema y técnica | Tecnologías | Arquitectura | Validación y resultado | Limitación / relación |
|---|---|---|---|---|---|
| Autora et al. (2025) | Predicción de abandono con datos del LMS. *Técnica:* random forest y XGBoost | Python; scikit-learn; no reporta la base de datos | no reporta | Validación temporal por cohorte; ROC-AUC 0,84 (p. 9) | El modelo no se integra en un sistema de consulta → respalda usar la actividad del LMS como predictor y muestra el vacío de integración |
