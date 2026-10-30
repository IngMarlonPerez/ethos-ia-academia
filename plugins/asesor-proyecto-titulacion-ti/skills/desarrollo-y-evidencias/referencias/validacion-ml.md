# Validación honesta de modelos de machine learning en una tesis

Lecciones de la tesis VicMar Data AI (predicción de abandono, 2026). Cada punto evitó una cifra inflada o una crítica de las tutoras.

## 1. Unidad de análisis sin fuga
- Si la tesis promete **anticipar** un evento («predecir antes de que ocurra»), cada fila usa solo información disponible **hasta t**, y la etiqueta es lo que pasa en **t+1**. Un modelo con una fila por entidad y el estado final como etiqueta **detecta**; no anticipa.
- Revisa variables que son consecuencia del evento: por ejemplo, la asistencia del mismo semestre del retiro.
- Si los datos son sintéticos y una sola variable separa las clases casi perfectamente (AUC ≈ 1), el resultado prueba que la arquitectura funciona, **no** que el modelo sea bueno. Se dice así, y se contrasta con un dataset real (en esa tesis, OULAD, CC BY 4.0).

## 2. Esquemas de validación
- **Validación cruzada agrupada** (`StratifiedGroupKFold` por entidad): una misma persona nunca queda a la vez en entrenamiento y en prueba.
- **Holdout temporal:** entrenar con los periodos hasta A y probar con los posteriores (p. ej. el último 25 %). Se usa **una vez**, al final.
- **Evaluación prospectiva** (si se puede): cortar el conjunto a mitad de periodo y comparar con lo que pasó después.
- Reporta la **media ± desviación** por pliegue, no solo la media.

## 3. Comparación de modelos
Al menos 3 candidatos, en la misma validación cruzada. Por ejemplo:
- línea base interpretable (regresión logística);
- random forest con `class_weight`;
- random forest + SMOTE;
- gradient boosting.

Búsqueda de hiperparámetros (`RandomizedSearchCV`) dentro de la validación cruzada, sin mirar el holdout.

## 4. Desbalance
- El sobremuestreo (SMOTE) va **dentro** de cada pliegue de entrenamiento, con `imblearn.Pipeline`. Aplicarlo antes de dividir los datos infla las métricas.
- Reporta **PR-AUC** además de ROC-AUC. Con una clase del 5 %, un ROC-AUC de 0,75 puede venir con una precisión muy baja.
- El **umbral operativo** se elige en validación para la métrica prioritaria (p. ej. recall ≥ 0,80) y se declara. No se usa el 0,5 por defecto.

## 5. Explicabilidad
- Importancia **por permutación** sobre el conjunto de prueba. La importancia por impureza está sesgada con variables continuas y con desbalance.
- **SHAP** por caso: los 3 factores principales de cada predicción, visibles en el panel.

## 6. Clustering
- Barrido de k (2–6) con silhouette, Davies-Bouldin y Calinski-Harabasz.
- Estabilidad por bootstrap (ARI medio).
- Comparación con otro algoritmo (Ward, HDBSCAN).
- **Prueba estadística** de que los grupos difieren en la variable de interés (Kruskal-Wallis).
- Una variante sin la variable que viene del propio modelo, para descartar circularidad.

## 7. Reporte
Tabla por modelo (media ± desviación) → modelo elegido y por qué → tabla temporal con umbral, recall, precisión y PR-AUC → figuras → discusión con los trabajos previos, **incluidas las metas no alcanzadas**.
