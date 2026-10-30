---
name: respaldo-fuentes-oficiales
description: 'Respalda cada cifra con su fuente ORIGINAL (gobierno, organismo o artículo), no con prensa: documento, página y recálculo, en notas PDF. Usar ante «de dónde sale esta cifra», «fuente original» o «notas de respaldo».'
---

# Respaldo con fuentes oficiales

**Qué se busca:** que cada cifra que la persona diga o escriba pueda defenderse ante cualquier audiencia, con el documento original en la mano, la página exacta y el cálculo reproducible.

## 1. Regla de oro: la prensa no es fuente, es pista
- Una nota de prensa (Primicias, Expreso, El Diario, Teleamazonas, El Universo…) **solo sirve para saber qué buscar**. Nunca se cita como respaldo final.
- Por cada cifra de prensa: identifica a quién atribuye el dato (ministerio, Senescyt, CES, universidad, estudio) y ve a ese documento.
- Si no aparece el original, la cifra se marca **«Sin fuente primaria: no usar»** o se reemplaza por la cifra oficial más cercana, diciendo la diferencia (año, definición, cobertura).

## 2. Jerarquía de fuentes
1. Documento oficial del organismo que produce el dato: rendición de cuentas o LOTAIP de la institución, planes y bases del CES, MINEDEC (antes Senescyt), INEC, ministerio de economía (MDEP, antes MEF), BCE, Registro Oficial.
2. Bases de datos oficiales descargables: datosabiertos.gob.ec, SIIES, aplicativo de distribución de recursos de la DGUP.
3. Organismos internacionales con la fuente nacional declarada: UNESCO-UIS, Banco Mundial, CEPAL.
4. Artículos científicos revisados por pares (Scopus o Scielo), vía `asistente-investigacion-cientifica:revision-sistematica`; sirven para el método y la comparación, no para reemplazar un dato oficial.
5. Prensa: solo como pista (regla 1).

## 3. Portales verificados para Ecuador
Usa `referencias/portales-oficiales-ecuador.md`. Ojo con los cambios institucionales de 2025-2026:
- la **Senescyt** se integró al **Ministerio de Educación, Deporte y Cultura (MINEDEC)**, que hoy publica los datos de educación superior;
- **finanzas.gob.ec** redirige al **Ministerio de Desarrollo Económico y Productivo (MDEP)**;
- el **CONESUP** fue reemplazado por el **CES** en 2010.
Antes de citar, comprueba en el navegador que el portal y el documento sigan publicados.

## 4. Procedimiento por cifra
1. **Anota la afirmación** tal como se va a decir («la UNEMI ejecutó cerca de 43 millones en 2025»).
2. **Busca la fuente primaria:** búsqueda web dirigida (`site:gob.ec`, `site:edu.ec`, nombre exacto del informe) y navegación del portal oficial.
3. **Descarga el documento** a `Respaldos_fuentes_originales/` con prefijo numérico y nombre claro (`01_UNEMI_Informe_Rendicion_Cuentas_2025.pdf`); comprueba que empieza con `%PDF`.
4. **Ubica la página y la tabla exactas;** distingue la página del PDF de la página impresa.
5. **Copia el valor literal** y su definición (codificado, devengado, proforma, inicial; deserción de primer año o de cohorte; registros de matrícula o personas únicas).
6. **Recalcula** cualquier derivado (costo por estudiante, totales) con un script y deja la fórmula escrita.
7. **Clasifica la confianza:** Oficial verificada · Oficial con definición distinta · Estimación propia (con supuestos) · Sin fuente primaria.

## 5. Trampas frecuentes
- **Varios «presupuestos» del mismo año:** proforma inicial ≠ codificado (tras reformas) ≠ devengado (gastado). Di cuál usas.
- **Matrícula:** registros por semestre ≠ estudiantes únicos por cédula; grado ≠ posgrado ≠ nivelación.
- **Deserción:** de primer año, por cohorte o anual son indicadores distintos; usa la definición y el año del documento oficial.
- **Proyecciones propias** (por ejemplo, costo nacional del abandono): preséntalas como estimación de orden de magnitud, con la fórmula y los supuestos.
- **Recuerdos personales** («éramos 1 500 y quedamos 200»): no son dato; se verifican con la institución (solicitud LOTAIP) o con la base propia.

## 6. Entregables
- Carpeta `Respaldos_fuentes_originales/` con los PDF originales.
- **Notas de respaldo** (Word y PDF), una ficha por cifra: afirmación, valor literal, fuente (organismo, documento, año, página, tabla), enlace, archivo local, cómo se encontró, cálculo y confianza.
- Lista de **fuentes descartadas** (prensa u otras) con el motivo.
- Si la cifra se usa en la tesis: referencia APA 7 con `asistente-investigacion-cientifica:redaccion-apa7`.

## 7. Reglas
- Nunca inventes una cifra, una página ni un enlace; si no lo verificaste, dilo.
- No uses credenciales ni formularios de la persona en los portales; las solicitudes LOTAIP las envía ella.
- Redondea para hablar en público («cerca de 43 millones»), pero conserva el valor exacto en las notas.
