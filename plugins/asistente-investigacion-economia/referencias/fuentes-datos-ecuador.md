# Fuentes oficiales y trampas (Ecuador, macro)

## Dónde está cada dato (probado oct-2026)
| Dato | Fuente | Cómo obtenerlo |
|---|---|---|
| Crecimiento PIB real anual 2000–2025 | Banco Mundial NY.GDP.MKTP.KD.ZG | `scripts/obtener_datos_wb.py ECU 1999 2025 NY.GDP.MKTP.KD.ZG` (coincide con BCE 2021–2025, base 2018) |
| Participación del gasto (C, G, I, X, M) | Banco Mundial NE.CON.PRVT.ZS, NE.CON.GOVT.ZS, NE.GDI.TOTL.ZS, NE.EXP.GNFS.ZS, NE.IMP.GNFS.ZS | mismo script |
| Informe de evolución 2025 y perspectivas 2026 (PIB, componentes reales, VAB 20 industrias, inflación, sector externo, servicios, previsión 2026) | BCE | `curl -sL https://contenido.bce.fin.ec/documentos/Administracion/EvolEconEcu_2025pers2026.pdf` (≈4 MB). Para el año siguiente buscar el equivalente |
| IPC mensual, incidencias, serie histórica de diciembres | INEC | `https://www.ecuadorencifras.gob.ec/documentos/web-inec/Inflacion/<AÑO>/<Mes con mayúscula>/01_ipc_Presentacion_IPC_<mes><año>.pdf` (probar mayúsculas/minúsculas: 2025 funcionó con `Diciembre`) |
| Inflación promedio anual | Banco Mundial FP.CPI.TOTL.ZG | mismo script |
| Balanza comercial por productos | BCE `.../balanzaComercial/ebc2026MM.html` (página dinámica; WebFetch no la lee) → usar tablas del informe |

## Cómo leer los PDF del BCE
- `pdftotext -layout` revuelve las columnas de las tablas y gráficos. Usar `pymupdf` `get_text()` (orden de lectura) o `get_text('words')` y asignar cada valor a su año por coordenada x.
- Localizar páginas buscando el título de la tabla ("Tabla 34", "Figura 8") con pymupdf.

## Errores reales encontrados en borradores (revisar siempre)
1. Dato mensual (p. ej. febrero) presentado como si fuera el anual: la división "alojamiento y electricidad" figuraba como −15,16 % cuando en diciembre fue +16,97 % (efecto de la compensación eléctrica).
2. Promedio anual confundido con variación diciembre-diciembre (2019: promedio 0,27 %, diciembre −0,07 %).
3. Fuente equivocada (boletín de pobreza ENEMDU citado como fuente del IPC) y restos de la guía pegados ("Fuente Principal 1…").
4. DOI inventado o mal copiado (Yaselga y Pilacuán: `10.47550/34.2.2`, no `.../RCE/34.2.2`): verificar con Crossref.
5. Fuente citada que no es la de la serie (se citaba Datosmacro; la serie coincidía con Banco Mundial).
6. Cifras sin respaldo en la fuente (p. ej. "volumen exportado −0,2 %"): quitarlas o reemplazarlas.
7. Tablas cuyas categorías no suman el total (importaciones: 30.750,5 vs 30.925,2): agregar fila de ajustes.
8. Saldo "de bienes y servicios" calculado solo con bienes: agregar la balanza de servicios (BCE tabla 13) y discutir el valor real (volumen vs precio, términos de intercambio).
9. Introducción/conclusiones que mencionan secciones inexistentes (VAB) o "el documento reporta…".
10. Cuadro de términos de intercambio del BCE: el texto rotula distinto que la tabla; usar la tabla (promedio −6,9 %, diciembre −10,9 % en 2025).

## Hechos 2025 ya verificados (para contrastar el próximo año)
PIB real +3,7 % (2024: −1,9 %); inflación dic 1,91 % (prom. 0,71 %); bal. comercial bienes USD 6.226,7 M; exportaciones 37.152,0 M (no petroleras 79,14 %); importaciones 30.925,2 M; servicios déficit 2.081 M; previsión BCE 2026: 2,5 %.

## Literatura Scopus 2021–2026 útil (Ecuador macro; ya verificada por DOI)
Cachanosky et al. 2025 (10.1111/sjpe.12397); Connolly 2025 (10.1007/s10479-024-06365-y); Orellana et al. 2023 (10.1504/GBER.2023.130009); Bunce y Carrillo-Maldonado 2023 (10.1016/j.eneco.2023.106876); Ramírez-Álvarez et al. 2025 (10.1186/s40008-025-00356-3); Martin-Mayoral et al. 2026 (10.1080/01603477.2026.2677572); Camacho-Villagómez y García-Albán 2026 (10.1016/j.eneco.2026.109447); Bonilla y Villacreses 2023 (10.18356/16840348-2023-140-6); D'Espaux y Padilla 2026 (10.1080/1540496X.2026.2658128); Vázquez-deCastro et al. 2024 (10.1111/twec.13488); Quintero Montaño et al. 2026 (10.12804/revistas.urosario.edu.co/economia/a.16088); Yaselga y Pilacuán 2024 (10.47550/34.2.2). Refrescar la búsqueda cada año con `PUBYEAR >` (año−5).
