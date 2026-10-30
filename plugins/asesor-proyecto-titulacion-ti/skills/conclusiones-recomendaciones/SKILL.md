---
name: conclusiones-recomendaciones
description: 'Redacta las conclusiones y recomendaciones de la tesis de TI (sección 4): una conclusión por objetivo con la cifra medida, metas no alcanzadas como hallazgos y trabajo futuro. Usar al pedir conclusiones, recomendaciones, trabajo futuro o el cierre.'
---

# Conclusiones y recomendaciones (etapa 9)

La plantilla UNEMI dice que las conclusiones deben:
- «guardar correspondencia con los objetivos propuestos»;
- ser «breves, precisas y convincentes»;
- ser una «consecuencia lógica de los resultados».

Mínimo: 1 página.

## 1. Una conclusión por objetivo
- Lee los objetivos de `requerimientos.json` → `objetivos` y sus métricas.
- Para cada objetivo, un párrafo de 3 a 5 oraciones:
  1. **qué se hizo** (verbo en pasado, el del objetivo);
  2. **resultado medido**, con la cifra leída del artefacto (nunca escrita a mano) y la meta: «alcanzó un ROC-AUC de 0,997 en la validación temporal (meta ≥ 0,90)»;
  3. **contraste** con uno o dos trabajos previos: coincide, supera o se queda corto, y por qué;
  4. **alcance del hallazgo** (datos sintéticos frente a reales, una institución frente a varias).
- **Meta no alcanzada:** se concluye igual, con honestidad. Por ejemplo: «en datos reales, el ROC-AUC fue de 0,752, por debajo de la meta; el predictor dominante fue el rendimiento académico, lo que coincide con Kok et al. (2024)».
- Una conclusión general final: cómo el conjunto responde al objetivo general y cuál es el aporte frente al vacío de 1.3.

## 2. Recomendaciones
Numeradas, accionables y dirigidas a alguien:
- a la institución (adopción, datos reales, gobierno de datos, capacitación);
- técnicas (proveedor de IA de pago para producción, monitoreo del modelo, reentrenamiento periódico);
- de privacidad (autorizaciones antes de usar datos reales).

## 3. Trabajo futuro
Sale de las **limitaciones declaradas** y de lo que sugieren los trabajos previos. Por ejemplo:
- arranque en frío (alumnos sin historial) → modelo previo a la matrícula;
- validación multiinstitucional;
- pruebas con más usuarios.

**Control:**
- cada objetivo específico tiene su conclusión con la cifra medida y su meta;
- no se afirma nada que no esté medido o citado;
- las metas no alcanzadas están discutidas;
- la sección cumple el mínimo de páginas del perfil.
