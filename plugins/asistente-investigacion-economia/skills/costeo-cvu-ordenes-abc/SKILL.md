---
name: costeo-cvu-ordenes-abc
description: 'Investigaciones de Sistema de Costeo sobre empresas de Ecuador: punto de equilibrio, CVU, costeo por órdenes y ABC, con cuadro comparativo. Usar con «punto de equilibrio», «CVU», «costeo por órdenes» o «ABC».'
---

# Sistemas de costeo: CVU, órdenes de producción y ABC en empresas del Ecuador

Probado con «S9-Tarea 2 Sistema de Costeo, Grupo J» (2026-10-23): 16 páginas, 4 puntos de la consigna, 6 figuras en Python, 4 ecuaciones OMML, 26 referencias (19 de Scopus 2021–2026). Scripts completos en un ejemplo interno (no incluido en la versión pública).

## Flujo
1. **Consigna, rúbrica y plan del grupo** (`leer-consigna-rubrica`). Leer también el PDF de repartición: fija qué empresa y qué punto le toca a cada integrante. Debajo de cada sección poner «Responsables: …» (la docente exige que todos cumplan su parte). Si la rúbrica habla de «idea central, ramas y subramas», incluir un **mapa mental** (Figura 1).
2. **Búsqueda Scopus** (`buscar-literatura-economia`), artículos 2021–2026, exportar todo:
   - B1 `TITLE-ABS-KEY(("cost-volume-profit" OR "break-even analysis" OR "breakeven point") AND (decision* OR planning OR "profit planning"))` → 133
   - B2 `TITLE-ABS-KEY("activity-based costing" OR "time-driven activity-based costing")` → 817
   - B3 `TITLE-ABS-KEY(("job order costing" OR "job costing" OR "cost accounting" OR "costing system*" OR "management accounting") AND (Ecuador OR "Latin America" OR SME* OR "small and medium"))` → 143
   B1 está dominada por salud (break-even de procedimientos): filtrar por título y quedarse con lo de decisión empresarial o capacidad de servicios.
3. **Resúmenes por OpenAlex** (la API sin red UNEMI da STANDARD: solo primer autor y sin resumen). Completar la lista de autores para APA con OpenAlex; si no se puede (sin DOI), **descartar** la fuente y decirlo.
4. **Empresas ecuatorianas** (por defecto, si el plan no dice otra cosa): manufactura PRONACA, servicios Banco Pichincha, órdenes Imprenta Mariscal, ABC Corporación Favorita. **Las empresas no publican sus costos**: los números son *ilustrativos* y se rotulan así en cada tabla y figura; para el cuadro comparativo se dicen «empresas idóneas por la naturaleza de su operación», nunca «usan oficialmente».
5. **Cálculos** (ecuaciones nativas con `ejercicios-con-ecuaciones`):
   - `MCu = P − CVu`, `Q_PE = CF/MCu`, `Ventas_PE = CF/(1 − CVu/P)`, margen de seguridad, `GAO = MC total / utilidad operativa`.
   - Meta con utilidad neta en Ecuador: `UAI = Utilidad neta / ((1 − 0,15)(1 − 0,25))` (participación laboral 15 %, IR 25 %), luego `Q_meta = (CF + UAI)/MCu`.
   - Sensibilidad: CVu ±, CF +10 %, precio ±5 %; comparar manufactura (margen estrecho → muy sensible al CVu) con servicios (costo casi todo fijo → sensible al volumen y a CF).
   - Órdenes: hoja de costos MPD + MOD + CIF con tasa predeterminada (`CIF presupuestados / base`); mostrar el error de cotizar sin CIF.
   - ABC: tabla actividad → inductor → tasa → consumo por objeto, contra reparto tradicional por ventas; mostrar el % de subcosteo.
6. **Figuras** (`graficos-economia`): mapa mental, gráfica CVU con zonas de pérdida/utilidad, barras de sensibilidad del punto de equilibrio, flujo de órdenes, flujo ABC (recursos → actividades → inductores → objetos), barras por año de B1–B3 (avisar que el año en curso está incompleto).
7. **Redacción** por literal, en el orden y con los títulos de la consigna; cada cita acompañada de criterio propio. Punto 4 (Ecuador): «necesarios pero no suficientes» — dolarización (sin devaluación, competir por costos), predominio de MIPYMES (INEC), crisis eléctrica 2024, IVA 15 % (Ley Orgánica para Enfrentar el Conflicto Armado Interno…, 2024), complementos (TDABC + teoría de restricciones, kaizen costing, IA en contabilidad de gestión).
8. **Word** (`armar-documento-unemi`): el TEMA va en el párrafo vacío de la carátula; la Figura 1 al inicio del desarrollo (si se pone en la introducción deja media página en blanco por el salto de la plantilla); verificar páginas por sección con Word COM.
9. **Cierre** (`revision-final-honesta`): cifras hipotéticas, fuentes leídas solo por resumen o título, fuentes descartadas, conclusiones personales como borrador que cada integrante debe reescribir, enlace de Drive vacío en la carátula.

## Artículos útiles ya verificados (DOI)
Rojas 2021 (10.25115/eea.v39i8.4787, CVU corto plazo) · Balami et al. 2024 (10.1186/s12913-024-11290-8, punto de equilibrio de capacidad de un servicio) · Guimarães et al. 2025 (10.3390/en18092198) · Rodríguez-García et al. 2023 (10.4995/ijpme.2023.18442, TDABC en supermercados) · Al-Mashkoor y Hadi 2024 (10.55214/25768484.v8i6.3801) · Al-Mekhlafi y Othman 2023 (10.24874/IJQR17.02-19) · Neamah et al. 2024 (10.1371/journal.pone.0301440, ABC a pedido) · Kefe y Tanış 2023 (10.6018/rcsar.413411) · Tandiono 2024 (10.33736/ijbs.6914.2024) · Molela et al. 2024 (10.1142/S021987702450010X) · Roffia et al. 2024 (10.1007/s11365-023-00938-2) · Záu Barreto y Brás 2023 (10.22201/fca.24488410e.2023.4663) · Porporato y Werbin 2024 (10.1080/10978526.2024.2343478) · Mustafa et al. 2022 (10.3390/en15114155) · Biadacz 2022 y 2024 · Getzin et al. 2026 · Daowadueng 2024 · Alrawashedh 2023.
