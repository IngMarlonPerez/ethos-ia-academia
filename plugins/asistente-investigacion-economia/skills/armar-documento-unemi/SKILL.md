---
name: armar-documento-unemi
description: 'Ensambla el Word final de un trabajo de Economía sobre la plantilla del grupo (tablas APA, ecuaciones nativas, referencias) y exporta el PDF con Word. Usar al armar, consolidar o «llenar la plantilla».'
---

# Armar el Word sobre la plantilla del grupo

Librerías: `${CLAUDE_PLUGIN_ROOT}/scripts/lib_docx.py` (P, SEC, H1, H2, EQ, CAPT, TABLE, IMG, NOTE, REF, `listar_parrafos`, `ensamblar`) y `mathlib.py` (ecuaciones). Ejemplo completo: un ejemplo interno (no incluido en la versión pública) + bloques.

## Pasos
1. **Plantilla**: la que indique la usuaria. Copia intacta en `_respaldo/…_respaldo_original.docx` (md5 anotado). El resultado va con el nombre del archivo maestro (o `_FINAL.docx`); el original nunca se sobrescribe.
2. **Edición a mano**: guardar el md5 del último build (`00_Control_Trabajo.md`); si el Word actual no coincide, ella lo editó: integrar sus cambios al script antes de regenerar.
3. **Ubicar dónde insertar**: `listar_parrafos(plantilla)` imprime los `paraId` de «Introducción», «Desarrollo», «Conclusiones», «Referencias» y sus saltos de página. Sustituir los saltos por el contenido (`ensamblar(plantilla, salida, {paraId: función_o_texto})`); poner la metodología tras la introducción, anexos tras las referencias.
4. **Contenido**: escribir el script de construcción con la herramienta Write; texto con `*cursiva*` y `$$ecuación$$`; tablas con anchos en twips (área útil ≈ 8650); interlineado 1,15 en el desarrollo si la consigna pide dos hojas por sección (APA doble espacio solo si la consigna lo exige); rótulo y nota APA en cada tabla y figura; renumerar figuras y tablas por orden de aparición y actualizar las referencias cruzadas del texto.
5. **Referencias**: una sola lista `referencias_apa.py` usada por el documento, la matriz y el RIS; orden alfabético sin acentos; DOI como URL; sangría francesa.
6. **PDF con Word real**: `python -I "${CLAUDE_PLUGIN_ROOT}/scripts/exportar_pdf_word.py" "<docx>" "<pdf>" --miniaturas` (copia a una ruta corta, exporta por COM, cuenta páginas totales, ecuaciones, imágenes y las páginas del cuerpo de «Introducción» a «Referencias»).
7. **Mirar el PDF página por página** (miniaturas): tablas sin palabras partidas, figuras sin huecos ni cortes, títulos no huérfanos, nada de restos de plantilla, comentarios o cambios.
8. **Verificar citas**: `python -I "${CLAUDE_PLUGIN_ROOT}/scripts/verificar_citas.py" "<docx>"` (referencias sin cita = error) y `verificar_apa.py` para formato; `similitud.py` si hay Turnitin.
9. Si el pie de página es gráfico, avisar que la numeración debe revisarse; si el docente pide páginas exactas, ajustar y volver a medir.
10. Copiar Word + PDF finales a `Evidencias_Drive/06_Documento_final/`; guardar el md5. Siguiente: `revision-final-honesta`.
