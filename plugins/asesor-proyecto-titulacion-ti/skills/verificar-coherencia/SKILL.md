---
name: verificar-coherencia
description: 'Control de calidad de un avance de TI: citas↔referencias, cifras contra artefactos, páginas, trazabilidad y arquitectura. Usar al preguntar si el avance está listo o «¿cuadran las cifras?».'
---

# Verificación de coherencia (etapa 10)

Una tesis coherente cumple tres condiciones:
- dice lo que el código hace;
- cita lo que la literatura dice;
- cumple lo que la universidad pide.

Este control lo comprueba con un script (objetivo) y dos revisores (criterio).

## 1. Configurar (una vez por avance)
`_automatizacion/coherencia.json`, creado por `iniciar-titulacion`, debe tener:
- `avance`, `documento`, `pdf`, `estilo_referencias` (normalmente `Bibliography`) y `prefijo_resumen` (el inicio del párrafo del Resumen, si la detección automática falla);
- `cifras`: cada cifra clave con `archivo` (se admite glob), `filtro` opcional (p. ej. solo las corridas completas), `ruta` en el JSON, `decimales`, `escala` (100 para porcentajes), `sufijo` y `en` (`resumen`, `cuerpo` o ambos). Borra los ejemplos;
- `paginas_desde`: la página donde empieza el cuerpo, si la detección del índice falla;
- `comprobar`: las rutas de `trabajos_previos`, `requerimientos`, `reglas_arquitectura`, `versiones_adr` y, opcionalmente, `matriz_literatura_codigo` (el Excel de `matrices-titulacion`).

## 2. Correr el script
Después de generar el `.docx` y el `.pdf`:
`python "${CLAUDE_PLUGIN_ROOT}/skills/verificar-coherencia/scripts/verificar_coherencia.py" --json documento/verificacion_avance<N>.json`

Revisa:
1. **Citas ↔ referencias:** control propio, más `verificar_apa.py` del plugin de investigación si está instalado (orden alfabético, DOI, «et al.», años). Sus errores hacen fallar; sus advertencias (p. ej. referencias sin cursivas) se muestran para corregir.
2. **Cifras ↔ artefactos:** en el Resumen con su sufijo, y en el cuerpo.
3. **Páginas mínimas** por sección del perfil, hasta el avance actual. Une el número y el texto de los títulos numerados automáticamente.
4. **Resumen:** palabras máximas y palabras clave máximas.
5. **Referencias** de los últimos N años, frente al mínimo del perfil.
6. **Trabajos previos:** mínimo, lectura completa, página, Arquitectura y Tecnologías, y que cada uno se cite en el texto.
7. **Trazabilidad** de requerimientos.
8. **Arquitectura:** reglas contra el código (`verificar_reglas.py`).
9. **Versiones:** lo que dicen las decisiones frente a lo fijado en `requirements.txt` o `package.json`.
10. **Matriz literatura-código** sin celdas vacías.

Si el script falla, corrige el origen (el generador, el JSON o el código) y regenera. **Nunca** parches el Word a mano para que pase.

## 3. Revisores
- Agente `asistente-investigacion-cientifica:revisor-apa` sobre el `.docx`: formato APA 7, estilo y tono. Devuelve correcciones sin tocar el documento.
- Agente `revisor-tutor` de este plugin: revisa el avance como lo haría la tutora, con la rúbrica del perfil (secciones, mínimos, elementos exigidos, coherencia con los objetivos). Devuelve observaciones priorizadas.

Aplica o justifica cada observación; las que cambian el texto van al registro de cambios.

## 4. Resultado para la usuaria
Un resumen corto:
- qué pasó el control, con la salida «Coherencia verificada: sin errores» o la lista de errores;
- las páginas por sección;
- las advertencias que ella debe decidir.

**Control:**
- `verificar_coherencia.py` termina con código 0;
- las observaciones de los dos revisores están resueltas o justificadas.
