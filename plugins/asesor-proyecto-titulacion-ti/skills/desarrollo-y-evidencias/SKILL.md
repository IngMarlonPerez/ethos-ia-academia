---
name: desarrollo-y-evidencias
description: 'Desarrollo y resultados de la tesis de TI (3.3): código explicado, métricas en artefactos, validación, pruebas y pipeline reproducible. Usar para explicar el código, resultados, pruebas o la demo.'
---

# Desarrollo y evidencias (etapa 8)

Las tutoras de la tesis VicMar pidieron «mostrar el código del modelo y del backend con resultados reales de validación cruzada/temporal». La respuesta que funcionó tiene tres partes:
- el código **escribe** sus resultados;
- el documento **los lee**;
- el código que se muestra se **extrae** del repositorio al generar.

## 1. Una sola fuente de verdad
Ver `referencias/fuente-unica-de-verdad.md`.
- Cada script de entrenamiento o evaluación guarda un JSON con fecha: `metrics.json`, `resultados_eval_AAAAMMDD_HHMM.json`. Incluye media ± desviación por pliegue, validación temporal, umbral y matriz de confusión.
- Las figuras (curvas ROC y PR, matriz de confusión, importancia de variables, comparación de modelos) las genera un script a partir de esos JSON.
- En `requerimientos.json` → `metricas`, cada métrica apunta a su `artefacto` y a su `ruta_json`.
- En `_automatizacion/coherencia.json` → `cifras` se registran las cifras que citan el Resumen y el cuerpo.

## 2. Validación según el tipo de proyecto
- **Machine learning** (`referencias/validacion-ml.md`):
  - la unidad de análisis correcta (panel sin fuga);
  - validación cruzada **agrupada** por entidad;
  - holdout **temporal**, usado una sola vez;
  - comparar al menos 3 modelos;
  - el balanceo **dentro** de cada pliegue;
  - umbral elegido para la métrica prioritaria (p. ej. recall ≥ 0,80);
  - PR-AUC cuando hay desbalance;
  - importancia por permutación y SHAP;
  - datos reales externos para contrastar un dataset sintético.
- **IA, LLM o NL2SQL** (`referencias/evaluacion-llm-nl2sql.md`):
  - conjunto dorado derivado de las historias de usuario (`plantillas/gold_set.json`);
  - exactitud por ejecución, estricta y relajada;
  - preguntas adversariales;
  - latencia p50 y p95;
  - fallas del proveedor separadas de los errores del sistema;
  - pausa entre preguntas si los proveedores gratuitos limitan las consultas por minuto;
  - la evaluación no debe contaminar la caché del sistema.
- **Software** (`referencias/pruebas-software.md`):
  - pruebas unitarias y de integración, incluidas las de seguridad (aislamiento, permisos, fallar cerrado);
  - tabla «Pruebas de funcionamiento» (`plantillas/pruebas_funcionamiento.md`).

## 3. Pipeline reproducible
Copia `plantillas/pipeline.ps1` a `scripts/pipeline.ps1` en el repositorio. Cada paso usa el envoltorio `Paso`, que se detiene en el primer error, y las credenciales vienen de `.env`. El pipeline reconstruye datos → modelo → evaluación → figuras → pruebas. Es la base de la demo (skill `entrega-y-sustentacion`).

## 4. Código en el documento, «a manera de manual»
- Se extrae en vivo con `docx_titulacion.funcion_py(ruta, 'nombre')` (Python, por AST) o con `docx_titulacion.fragmento(ruta, 'desde', 'hasta')` (JS, SQL, cualquier texto).
- Para ver un fragmento antes de insertarlo:
  `python "${CLAUDE_PLUGIN_ROOT}/skills/desarrollo-y-evidencias/scripts/extraer_codigo.py" <archivo> <función | desde> [hasta]`
- **Front end (3.3 b):**
  - el componente principal de la interfaz;
  - el servicio que llama a la API;
  - el manejo de la sesión y el rol.
- **Back end (3.3 c):**
  - la ruta principal;
  - la validación y seguridad;
  - el entrenamiento o proceso central;
  - la función de privacidad.
- Después de cada fragmento, un párrafo «manual»:
  - qué recibe (variables);
  - qué estructuras usa;
  - cómo funciona paso a paso;
  - por qué está hecho así, con cita si la decisión viene de la literatura.
- Fragmentos de 15 a 60 líneas; sin claves ni datos personales.

## 5. Resultados
Tablas y figuras leídas de los artefactos:
- comparación de modelos (media ± desviación);
- validación temporal;
- exactitud por categoría;
- evolución entre corridas;
- **tabla de defectos detectados y corregidos** (defecto | evidencia | corrección | archivo);
- pruebas de seguridad.

Si una meta no se cumple, se dice y se discute: en la tesis VicMar, el ROC-AUC en datos reales fue 0,752 frente a una meta de 0,90, y se presentó como hallazgo. **Nunca se ajustan datos ni metas para que cuadre.**

**Control:**
- las pruebas pasan (pytest o npm test) y el pipeline termina sin errores;
- cada métrica de 2.1 tiene su valor en un artefacto;
- el código del documento se extrae del repositorio;
- los resultados que no alcanzan la meta están discutidos.
