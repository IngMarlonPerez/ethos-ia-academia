# Evaluar un componente de IA generativa (NL2SQL, chatbot, clasificador con LLM)

Lecciones de la evaluación NL2SQL de la tesis VicMar Data AI: 40 preguntas y 8 adversariales, cuatro corridas, de 67,5 % a 92,5 % de exactitud.

## 1. Conjunto dorado
- Entre 30 y 50 casos **derivados de las historias de usuario**, cada uno con su `historia` y su `categoria` (conteo, agregación, ranking, filtro temporal…).
- La referencia se **calcula** (SQL de referencia ejecutado sobre los mismos datos), no se escribe de memoria.
- De 5 a 10 **adversariales**:
  - escritura (DELETE, DROP);
  - tablas físicas no autorizadas;
  - datos de otra organización;
  - extracción de datos personales;
  - inyección en el texto.

## 2. Métricas
- **Exactitud por ejecución:**
  - estricta: el mismo multiconjunto de filas;
  - relajada: las columnas de la referencia están contenidas en la respuesta, con tolerancia de redondeo y de escala (×100).
- Exactitud **por categoría**.
- Adversariales bloqueadas (meta 100 %), base sin cambios después de ellas, **violaciones de aislamiento** (meta 0).
- Latencia p50 y p95; proveedor que respondió.
- **Fallas técnicas del proveedor** (cuota agotada, error 5xx, salida vacía) reportadas aparte: exactitud con y sin ellas.

## 3. Cómo correrla sin engañarse
- Llama al sistema como lo haría el usuario: el mismo endpoint, el mismo rol, en proceso (TestClient) con un token generado localmente. Claude nunca escribe contraseñas.
- **Desactiva o intercepta la caché semántica y el aprendizaje** durante la evaluación: si no, la evaluación contamina el sistema y la segunda corrida se evalúa contra sí misma.
- Los proveedores gratuitos limitan solicitudes y tokens por minuto: deja una **pausa entre preguntas** (p. ej. 30 s) y decláralo.
- Guarda cada corrida con fecha y conserva las intermedias con nombre, para la tabla de evolución.

## 4. Robustez del LLM
- Cascada de proveedores con respaldo automático.
- Detectar salidas degeneradas (vacías, «!!!!», placeholders) y reintentar una vez.
- Límite de tokens suficiente para los modelos que «razonan», o razonamiento desactivado.
- Verificar que las cifras de la explicación estén en las filas; si no, rehacer la narración o usar un resumen determinista.

## 5. Reporte
Tabla por categoría, tabla de corridas (qué defecto se corrigió entre una y otra), adversariales, latencia y la frase honesta sobre las limitaciones de los proveedores gratuitos.
