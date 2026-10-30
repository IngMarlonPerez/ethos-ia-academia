---
name: ejercicios-con-ecuaciones
description: 'Ejercicios numéricos de Economía (elasticidades, Slutsky, costeo, CVU) en Word con el Editor de Ecuaciones, paso a paso e interpretación. Usar con un deber o informe con cálculos o «con el editor de ecuaciones».'
---

# Ejercicios numéricos con ecuaciones nativas de Word

Ejemplo completo: un ejemplo interno (no incluido en la versión pública). Librería: `scripts/mathlib.py` (mini-LaTeX → OMML).

## Flujo
1. **Leer todo** (`leer-consigna-rubrica`): enunciado, cada literal (a, b, c, d) como checklist, rúbrica (comprensión, redacción y ortografía, estrategia, metodología, ejecución técnica: cálculos, cifras significativas, unidades).
2. **Revisar borradores**: detectar fórmulas reales (`<m:oMath>`) vs texto plano; **recalcular TODAS las cifras a mano** (método independiente). Marcar: cifras sin ecuación, falta de |ε| en la clasificación, signo perdido en elasticidad cruzada, mezcla de coma/punto decimal, ejercicios ausentes, ortografía.
3. **Reglas de cálculo**: elasticidad precio clasificada con **valor absoluto** (|ε| > 1 elástica, < 1 inelástica, = 1 unitaria); elasticidad cruzada **conserva el signo** (+ sustitutos, − complementarios); punto medio cuando el enunciado da dos precios/cantidades, cociente directo si da % ya calculados; comprobación de ingreso total como apoyo (sin afirmar rentabilidad si no hay costos); en Slutsky descomponer efecto global = sustitución + ingreso con unidades; en tablas de elasticidades cruzadas verificar si la fila es la cantidad o el precio (comprobar con simetría de Slutsky).
4. **Estructura por ejercicio**: datos → procedimiento paso a paso → resultado → clasificación → interpretación económica con palabras propias y cita. Cuadros resumen, conclusiones (una por resultado) y recomendaciones, referencias APA 7, anexo con ecuaciones de búsqueda.
5. **Literatura**: buscar casos reales para contextualizar (pollo y carne con elasticidades hicksianas y marshallianas; transporte; videojuegos) con `buscar-literatura-economia`; leer tablas con cuidado y citar solo lo que respaldan.
6. **Generar con `mathlib.py`**: `$$…$$` en línea, ecuación centrada, tablas; soporta `\frac`, `_{}`, `\left|…\right|`, `\varepsilon`, `\Delta`, `\%`, `\$`, `\times`, `\approx`, `\text{}`. Escribir el `.py` con Write (con `chr(92)` para `\` si hace falta). Cifras con coma decimal. En el documento, cada fórmula y cada cálculo es una ecuación nativa.
7. **Ensamblar** sobre el archivo maestro (`armar-documento-unemi`), contar páginas del desarrollo (p. ej. máximo 3), verificar con Word real (`OMaths.Count`), exportar PDF.
8. Entregar Word + PDF y un resumen honesto: qué estaba mal, qué se cambió, qué debe verificar ella (nombres en carátula, enlaces, indexación Scopus, tildes del nombre de la docente).
