# Una sola fuente de verdad: del código al documento

```
código (entrenar, evaluar, ETL) ──escribe──► artefactos JSON + figuras PNG
                                                  │
requerimientos.json, trabajos_previos.json,       │
decisiones/DT-*.json, diccionario_datos.json ─────┤
                                                  ▼
                            build_avanceN.py (lee, formatea con coma decimal, inserta)
                                                  │
                                                  ▼
                            Avance_N.docx → docx_a_pdf.ps1 → Avance_N.pdf
                                                  │
                                                  ▼
                            verificar_coherencia.py (cifras = artefactos, citas, páginas)
```

## Reglas
1. **Ninguna cifra se escribe a mano** en el generador. Se lee el JSON: `n(m['validacion_temporal']['roc_auc'])`.
2. **Formato en español:** `formato_es.n` (coma decimal, punto de miles), `pct` (espacio antes de %), `media_de` (media ± desviación).
3. **Selección del artefacto:** si hay varias corridas (`resultados_*.json`), el generador y el verificador eligen **la misma**: la última que cumple el filtro (p. ej. 40 preguntas y 8 adversariales). Si no hay una corrida completa, el generador se detiene; no usa una parcial.
4. **Corridas guardadas:** las corridas intermedias se conservan con un nombre (`corrida1_antes_de_correcciones.json`) para la tabla «evolución entre corridas».
5. **Después de reentrenar**, regenera: pipeline → generador → PDF → verificador. Nunca parches el Word a mano.
6. **El código mostrado** se extrae con `funcion_py` o `fragmento`. Si el código cambia, el documento cambia.

## Estructura mínima de un metrics.json (ML)
```json
{
  "fecha": "2026-09-25T16:03",
  "unidad": "alumno-periodo", "n_filas": 83678, "n_entidades": 14508, "tasa_positiva": 0.10,
  "comparacion_cv": {"RF": {"roc_auc": {"media": 0.99, "desviacion": 0.003}, "recall": {...}}, "LOGISTICA": {...}},
  "modelo_final": "RF",
  "validacion_temporal": {"corte": "2024-2", "umbral_operativo": {"umbral": 0.31, "roc_auc": 0.997, "pr_auc": 0.976,
                           "recall": 0.777, "precision": 0.9, "matriz_confusion": [[...], [...]]}},
  "importancia_permutacion": [{"variable": "...", "media": 0.12, "desviacion": 0.01}]
}
```
