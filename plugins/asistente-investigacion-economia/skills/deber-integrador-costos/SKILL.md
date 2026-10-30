---
name: deber-integrador-costos
description: 'Deberes integradores de Contabilidad de Costos: orden de producción, ABC/ABM, pedido especial y precio con margen, con ecuaciones de Word e informe. Usar con «componente práctico», «deber integrador» o «pedido especial».'
---

# Deber integrador de costos: órdenes, ABC, ABM, decisiones y precio

Probado con «S15 Componente Práctico 2, Sistema de Costeo, Grupo J» (2026-10-24): 22 páginas, Partes I–X, 40 ecuaciones OMML, 5 figuras, 7 tablas, 16 referencias Scopus 2022–2026, auditoría 100 % de la consigna. Scripts completos en un ejemplo interno (no incluido en la versión pública).

## 0. Leer TODO, incluidas las imágenes
- Las tablas de datos de la consigna suelen ser **imágenes** dentro del PDF: el texto extraído dice «la siguiente:» y nada más. Ubicar la página (`'siguiente:' in page.get_text()`), renderizarla con PyMuPDF y **mirarla con Read**. Contrastar valor por valor con lo que haya pegado la usuaria.
- Leer la rúbrica al final del PDF: puede traer criterios copiados de otra materia (p. ej. «finanzas corporativas, valuación y presupuesto de capital» en un deber de costos). No ignorarlo: agregar un apartado breve que conecte los resultados con ese criterio (flujos incrementales = lógica del presupuesto de capital; margen → flujos → valor).

## 1. Cálculos (verificar con `assert` en Python antes de redactar)
`01_calculos_figuras.py` guarda `resultados.json`. Fórmulas:
- **Orden**: MPD = Σ materiales directos; MOD; CIF = Σ indirectos (mat. ind., MO ind., energía, depreciación, mantenimiento); costo primo = MPD + MOD; conversión = MOD + CIF (no se suman entre sí: comparten MOD); total = MPD + MOD + CIF; unitario = total / unidades. Participación % de cada elemento.
- **ABC**: tasa = costo de la actividad / total de inductores; asignado = tasa × consumo de la orden; CIF_ABC = Σ; costo total y unitario con ABC; diferencia y % frente a los CIF tradicionales. Si el caso no da la base tradicional, comparar con los CIF reales de la orden y **decirlo**.
- **Pedido especial**: verificar capacidad ociosa; ingreso incremental = Q × P; costo relevante = CV + costos específicos (empaque); costo incremental; utilidad incremental; precio mínimo = costo relevante; costos fijos irrelevantes; % de utilización con el pedido; 3 factores cualitativos (reacción de clientes habituales, capacidad/calidad, relación y riesgo del cliente).
- **Precio**: costo de producción = MPD + MOD + CIF; costo total = + gastos adm. y ventas; margen = costo total × %; PV = costo total × (1 + %); utilidad = margen × Q; margen sobre precio; utilidad con precios menores y unidades necesarias para mantener la utilidad.

## 2. Reglas de presentación (aprendidas en la auditoría)
- **Toda cifra calculada lleva su ecuación** en el editor de Word (`EQ`), incluidos los porcentajes de las interpretaciones; un % solo en el texto resta en «Cálculos».
- Cada literal con su propio subtítulo y numeración de la consigna (`QA(pregunta, respuesta)`); preguntas conceptuales justificadas y con al menos una cita en las clave.
- Hoja de costos como tabla con encabezado limpio (Elemento | Detalle | Valor) y fila de datos de la orden.
- ABM: tabla actividad | a) agrega / b) no agrega | justificación + figura de dos columnas. Inspección = no agrega valor (necesaria pero reducible); diseño personalizado y ensamblaje = agregan valor; retrabajo, corrección de errores, almacenamiento y transporte innecesarios = no agregan.
- Informe a la gerencia: encabezado (Para/De/Asunto/Fecha) + un párrafo por cada viñeta, con las cifras del caso; contar palabras (≥ mínimo pedido).
- Conclusiones: exactamente las pedidas, cada una con un número del ejercicio.
- Formato: interlineado 1,5 con `P(t, line=360)`; Times New Roman 12 justificado (por defecto en la plantilla UNEMI). Auditar con `04_auditar_formato.py`.
- Asteriscos de ecuaciones de búsqueda dentro de tablas: reemplazar `*` por `∗` (el `*` activa cursiva en `rich`).

## 3. Figuras sugeridas
Composición del costo de la orden (dona + barras por concepto), CIF por actividad y tradicional vs ABC, clasificación ABM, análisis incremental + sensibilidad al precio ofrecido (precio mínimo marcado), formación del precio + utilidad según precio.

## 4. Literatura (Scopus 2021–2026, verificada por DOI)
Ecuaciones: B4 `("activity-based management" OR "non-value-added activit*" OR "value-added activit*") AND cost*` (77); B5 `("relevant cost*" OR "special order" OR "short-term decision*" OR "pricing decision*" OR "cost-plus pricing") AND (accounting OR costing)` (95). Útiles: Suparmanto et al. 2024 (10.62527/joiv.8.1.2000, órdenes y precio a pedido), Cainas y Kralik 2024 (10.2308/ISSUES-2022-003, costos relevantes), Ammar et al. 2026 (10.1016/j.bar.2026.101949, precio sobre costo), Jiang et al. 2022 (10.3389/fpubh.2021.763829, TDABM), Dara et al. 2025 (10.3390/infrastructures10030055, actividades sin valor), Alghazali 2023 (10.26668/businessreview/2023.v8i4.1370, ABC y precio), Wijekoon et al. 2024 (10.1108/JAEE-10-2021-0308), más los de `costeo-cvu-ordenes-abc`.

## 5. Auditoría final («verifica que cumpla al 100 %»)
Tabla requisito → estado para cada literal de la consigna y cada criterio de la rúbrica; volver a mirar las imágenes de datos; contar ecuaciones y páginas con Word COM (`03_pdf.ps1` con `pwsh`); revisar el PDF a la vista; corregir y regenerar. Informar con honestidad lo que la usuaria debe completar (enlace de Drive) o decidir (criterios discutibles).
