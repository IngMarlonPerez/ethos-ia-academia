---
name: graficos-economia
description: 'Gráficos de Economía con Python sin textos superpuestos ni cortados: PRISMA, bibliometría, diagramas, ciclo del PIB y figuras de ejercicios. Usar al pedir gráficos, figuras o diagramas.'
---

# Gráficos de Economía sin textos superpuestos

Librería: `${CLAUDE_PLUGIN_ROOT}/scripts/lib_figuras.py` (`lienzo`, `caja`, `flecha`, `guardar` con verificador). Metodología: `scripts/graficos_busqueda.py`. Ciclo del PIB: `scripts/grafico_ciclo.py`.

## Reglas de diseño (aprendidas por corrección de la usuaria)
1. **Diseñar a tamaño final**: ancho útil del Word UNEMI ≈ 6,0 in (15 cm); fuente 6,5–8 pt. Una figura de 7,5 in reducida a 15 cm queda ilegible.
2. **Leyendas fuera del área de datos** (fila inferior con `constrained_layout`); ninguna etiqueta sobre una flecha o sobre el borde de una caja; márgenes en los extremos (cajas ≤ 98 % del lienzo).
3. **Paleta única y accesible** (`PALETA`), un color por escuela/serie, mismo color en todas las figuras del trabajo.
4. **Variedad exigida por la rúbrica** cuando haya datos: barras + dispersión + cajas (con datos reales de Scopus: producción por periodo, año vs citas, distribución de citas) y al menos un recurso visual conceptual por sección (tabla comparativa, diagrama de flujo, línea de tiempo, circuito).
5. Cada figura lleva rótulo APA («Figura N» en negrita, título en cursiva), nota «Elaboración propia con…» y una lectura en el texto (qué muestra y por qué importa). Valores ilustrativos se rotulan como tales.
6. **Metodología**: `python -I "${CLAUDE_PLUGIN_ROOT}/scripts/graficos_busqueda.py" <config_trabajo.py>` genera el flujo de selección y la evidencia bibliométrica desde `prisma_conteos.json` y los CSV; también escribe `resumen_estadistico.csv` (mediana, media, correlación año–citas).

## Verificación obligatoria
- `guardar()` imprime «OK» o la lista de textos que se pisan o salen del lienzo. Corregir hasta que diga OK.
- **Abrir cada PNG con Read y mirarlo**: el verificador no ve flechas que cruzan texto ni cajas que cortan palabras. Los «fuera del lienzo» de ejes ocultos son falsos positivos.
- Guardar PNG (250 dpi) en `Evidencias_Drive/03_Graficos/` junto con el script que los genera: es parte de la evidencia para Drive.
- Escribir los scripts con Write (los heredocs de bash corrompen `\n`).
