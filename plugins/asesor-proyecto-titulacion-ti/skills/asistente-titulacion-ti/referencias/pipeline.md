# Pipeline del proyecto de titulación de TI

Cada etapa produce **archivos del proyecto**, no solo texto: los archivos alimentan el Word, las matrices y el verificador.

| Etapa | Qué produce | Archivo(s) | Control de salida |
|---|---|---|---|
| 0 Inicio | Estructura, perfil y plantilla intacta | `titulacion.json`, `00_Control_Titulacion.md`, `_automatizacion/Plantilla_ORIGINAL.docx` | md5 de la plantilla registrado; perfil confirmado |
| 1 Planteamiento | Título, problema, justificación, objetivos, alcance, Resumen | `requerimientos/requerimientos.json` → `objetivos`; `_automatizacion/datos_matrices.json` → `consistencia` | Verbos de Bloom; qué/cómo/para qué; cifras con DOI |
| 2 Literatura | Búsquedas, PRISMA, fichas, tabla de trabajos previos, 1.3 | `literatura/B*/`, `literatura/trabajos_previos.json` | `tabla_trabajos_previos.py` sin errores |
| 3 Requerimientos | Alternativas, actores, HU, RF, RNF, métricas, trazabilidad | `requerimientos/requerimientos.json` | `trazabilidad.py` sin errores |
| 4 Tecnologías | Una matriz por decisión + ADR | `decisiones/DT-NN_*.json`, `decisiones/adr/ADR-NNN-*.md` | `matriz_decision.py --todas` sin errores; ganadoras estables o desempate declarado |
| 5 Arquitectura | Matriz de estilos + ADR + reglas verificables | `decisiones/DT-NN_arquitectura.json`, `decisiones/arquitectura_reglas.json` | `verificar_reglas.py` sin violaciones (o excepciones justificadas) |
| 6 Metodología | Fases con entregables del repo | texto de 3.1 + figura | Cada entregable existe en el repo |
| 7 Diseño | UML exigidos + modelo de datos + diccionario | `diagramas/uml_*.mmd/.png`, `diccionario_datos.json/.md` | `renderizar_diagramas.py --perfil` sin faltantes; diccionario sin columnas sin descripción |
| 8 Desarrollo | Código con resultados reales | artefactos JSON del código, `figuras/`, pruebas | pytest en verde; cada métrica de 2.1 con valor |
| 9 Conclusiones | Una conclusión por objetivo | texto de 4 | Todas las conclusiones con cifra medida |
| 10 Documento | Word, PDF, matrices, verificación | `documento/Avance_N.docx/.pdf`, `documento/Matrices_*.xlsx` | `verificar_coherencia.py` código 0 |
| 11 Retroalimentación | Observaciones atendidas | `retroalimentacion/Observaciones_AvanceN.md`, `documento/Registro_cambios_AvanceN.md` | Ninguna observación sin atender o justificar |
| 12 Entrega | Demo, capturas, guiones, videos, carpeta | `figuras/demo_*.png`, `entregables/` | `armar_entrega.py --revisar` sin faltantes |

## Qué entra en cada avance (perfil UNEMI)
- **Avance 1:** Resumen/Abstract, 1.1, 1.2 y 1.3 (con al menos 10 trabajos previos), más Referencias y Anexos. Etapas 0 a 2 y 10 a 11.
- **Avance 2:** 2.1, 3.1, 3.2 y 3.3. Etapas 3 a 8 y 10 a 11.
- **Avance 3 / documento final:** 4, más la revisión completa. Etapas 9 a 12.

## Orden recomendado dentro del Avance 2
3 → 4 → 5 → 6 → 7 → 8 → 10.

Las decisiones (etapas 4 y 5) van antes del diseño detallado. Si el código ya existe, se documentan igual, y la verificación de la etapa 5 contrasta lo declarado con lo implementado.
