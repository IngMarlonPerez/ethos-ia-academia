---
name: algebra-lineal-vectores
description: 'Tareas de Álgebra Lineal de Economía (vectores en R³, producto punto, ángulo, axiomas de espacio vectorial) con el Editor de Ecuaciones de Word, verificadas en Python. Usar con vectores o espacios vectoriales.'
---

# Álgebra Lineal: vectores y espacios vectoriales con ecuaciones nativas

Ejemplo completo y probado: un ejemplo interno (no incluido en la versión pública) (S9-Tarea 2, 6 ejercicios, 89 ecuaciones OMML, 5 páginas) y su PDF `salida_ejemplo.pdf`. Librería: `scripts/mathlib.py` (mini-LaTeX → OMML).

## Regla de oro de la usuaria
**Todo cálculo y toda notación algebraica va en el Editor de ecuaciones de Word (OMML)**, no como texto con símbolos. Un PDF hecho con reportlab/texto plano se ve mal (fracciones con «/», raíces sin barra, vectores sin flecha, ℝ como «R»): ya pasó, no repetir. Si la tarea pide «a mano», se entrega esta guía en Word/PDF para que ella la copie a mano.

## Flujo
1. **Leer el PDF de la tarea completo** (`leer-consigna-rubrica`): extraer con PyMuPDF (`python -I`, `sys.stdout.reconfigure(encoding='utf-8')`). Si el texto de una página sale vacío o raro, renderizar la página y mirarla. Hacer checklist de cada ejercicio y literal (a, b, c). Anotar la fecha de entrega, el formato (PDF por Moodle), si es individual y si exige «a mano».
2. **Resolver y recalcular con otro método** (NumPy): `np.array`, `@` para el producto punto, `np.linalg.norm`, `np.degrees(np.arccos(...))`. Los resultados de Python deben coincidir con los manuales; esa comprobación se cita en el documento (rúbrica: manejo de herramientas/software).
3. **Estructura del documento** (cubre la rúbrica típica: calidad y profundidad, análisis y justificación, claridad y estructura, software, fecha):
   - Carátula con los datos del PDF (nombre en blanco para la usuaria, docente, fecha de entrega, periodo). No inventar la universidad: usar la que dice el PDF o avisarle.
   - **Objetivo** y **fundamento teórico** con las fórmulas usadas (suma, escalar, producto punto, norma, coseno del ángulo, `(ka)·(kb)=k²(a·b)`).
   - Por ejercicio: **datos → procedimiento paso a paso (una ecuación por paso) → resultado → verificación (si aplica) → análisis** (qué significa: combinación lineal y clausura; signo del producto punto = ángulo agudo/recto/obtuso; vectores paralelos si el resultado es el nulo; no ortogonales ni paralelos si `0<cosθ<1`).
   - **Espacio vectorial**: los 10 axiomas (5 de la suma, 5 del escalar), cada uno con su demostración en ecuación y una conclusión explícita («cumple los 10 ⇒ es espacio vectorial»); si falla uno, dar el contraejemplo numérico y decir cuál.
   - **Verificación con herramienta tecnológica** (Python/NumPy, GeoGebra o Excel, lo que haya usado la clase), **conclusiones** y **referencia** (texto estándar de Álgebra Lineal; avisar a la usuaria que lo cambie si la docente usa otro).
3b. **Figuras (opcionales, suman a «análisis» y «software»):** un ejemplo interno (no incluido en la versión pública) dibuja el ángulo entre dos vectores de R³ en el plano que generan (Gram-Schmidt, sin textos superpuestos) y vectores paralelos sobre una recta. Se incrustan con `pic()` de `build_tarea2.py` con pie «Figura n.» y se numeran en orden de aparición. Si la docente usa GeoGebra 3D, ofrecer también que la usuaria haga una captura (`Vector(u)`, `Ángulo(u,v)`) y la inserte.
4. **Generar con `scripts/mathlib.py`** (escribir el `.py` con Write; las barras invertidas se escriben normales en cadenas `'...\\frac{}{}'`). Soporta además de lo básico: `\vec{u}` (flecha), `\sqrt{}`, `^` y `_`, `\left\|…\right\|` (norma), `\mathbb{R}`, `\alpha \beta \theta`, `\oplus \odot \in \neq \ge \le`, funciones `\cos \arccos`, `\cdot`. Coma decimal en las cifras. Interlineado 1,3 (la plantilla de 2,0 alarga demasiado). Copiar el patrón del ejemplo: `H1/H2/T/E` + carátula + `sectPr` A4.
5. **Verificar con Word real** (PowerShell): `$doc.OMaths.Count`, `ComputeStatistics(2)` (páginas) y `ExportAsFixedFormat(pdf,17)`. Rasterizar con PyMuPDF y **mirar** las páginas: flechas sobre la letra (no tachadas), raíces con barra, `ℝ` de doble trazo, fracciones apiladas.
6. **Entregar** `.docx` + `.pdf` junto al enunciado, con resumen honesto: qué se resolvió, qué comprobó el software, qué debe hacer ella (nombre en carátula, copiar a mano con letra legible, escanear, subir PDF a Moodle antes de la fecha, referencia/universidad a confirmar).

## Trampas técnicas (aprendidas)
- **Flecha del vector:** el carácter de acento debe ser `U+20D7` (combinante), no `→`; con `→` Word lo dibuja encima de la letra y parece tachada.
- **ℝ:** en OMML se escribe `R` con `<m:scr m:val="double-struck"/>` (`\mathbb{R}`); el carácter `ℝ` sale como «R» normal con Cambria Math en algunos PDF.
- **Norma:** `\left\|` y `\right\|` (la librería los convierte en `‖`); no escribir `\left‖` a mano.
- **reportlab/Arial no tienen** subíndices Unicode, ℝ, ⊕, ⊙ ni ✓: por eso el PDF de texto plano falló. Usar siempre Word → PDF.
- Heredocs de bash corrompen `\`; usar Write. `python -I` ignora `PYTHONIOENCODING`: `sys.stdout.reconfigure(encoding='utf-8')`.
- Un `sed` con rangos de líneas sobre un script generado puede duplicar bloques; reconstruir el script completo con Write en vez de parchear a ciegas.

## Resultados de referencia (S9-Tarea 2) para autoverificar
`4u−v+2w=(−3,−17,14)`; `2u−3v+3w=(−16,−13,3)`; `2r·2s=204`; `m+n=(1,6,−2)`, `2m+p=(0,0,0)`, `2n·p=52`; `cosθ=17/√406≈0,8437`, `θ≈32,5°`; `(ℝ³,⊕,⊙)` es espacio vectorial.
