#!/usr/bin/env python3
"""Servidor MCP «literatura» del plugin Asistente de Investigación Científica.

Da a Claude herramientas para buscar literatura científica por vías autorizadas:
  - Scopus Search API y Abstract Retrieval API de Elsevier (clave personal de la usuaria)
  - OpenAlex (datos abiertos CC0)
  - Unpaywall (enlaces legales a PDF de acceso abierto)

Solo usa la biblioteca estándar de Python (no hay nada que instalar). Habla MCP por
stdio: un mensaje JSON-RPC por línea. Los mensajes de diagnóstico van a stderr.

Credenciales: llegan como variables de entorno desde el userConfig del plugin
(ELSEVIER_API_KEY, ELSEVIER_INSTTOKEN, CORREO_CONTACTO). Nunca se escriben en
disco ni se devuelven en las respuestas.
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = "1.0.0"
PROTOCOLOS = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"]
UA = "AsistenteInvestigacionCientifica/1.0 (plugin de Claude; uso academico no comercial)"
SCOPUS_BUSQUEDA = "https://api.elsevier.com/content/search/scopus"
SCOPUS_RESUMEN = "https://api.elsevier.com/content/abstract"
COLUMNAS_CSV = ["Busqueda", "Authors", "Title", "Year", "Source title", "Volume", "Issue", "Art. No.", "Page start",
                "Page end", "Cited by", "DOI", "Abstract", "Author Keywords", "Publisher", "Document Type",
                "Publication Stage", "Open Access", "Subject", "EID"]


# --------------------------------------------------------------------- utilidades
RESPALDO_ENTORNO = {"ELSEVIER_API_KEY": "SCOPUS_API_KEY", "ELSEVIER_INSTTOKEN": "SCOPUS_INSTTOKEN", "CORREO_CONTACTO": "CORREO_CONTACTO_INVESTIGACION"}


def _cfg(nombre):
    """Lee una credencial: primero la del userConfig del plugin (llega en `nombre`); si está vacía, la variable de
    entorno de respaldo que la usuaria haya creado en Windows (p. ej. SCOPUS_API_KEY). Para uso personal; antes de
    publicar el plugin en el directorio de Anthropic, quitar el respaldo (su revisión lo retiene)."""
    for clave in (nombre, RESPALDO_ENTORNO.get(nombre)):
        valor = (os.environ.get(clave or "") or "").strip()
        if valor and not valor.startswith("${"):
            return valor
    # Windows: leer la variable de usuario del registro (la app pudo abrirse antes de crearla)
    if os.name == "nt" and RESPALDO_ENTORNO.get(nombre):
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                return str(winreg.QueryValueEx(k, RESPALDO_ENTORNO[nombre])[0]).strip()
        except OSError:
            pass
    return ""


def _log(*partes):
    print("[literatura]", *partes, file=sys.stderr, flush=True)


class ErrorHerramienta(Exception):
    """Error que se devuelve a Claude como resultado de la herramienta (isError)."""


def _http_json(url, cabeceras=None, reintentos=3):
    cab = {"User-Agent": UA, "Accept": "application/json"}
    cab.update(cabeceras or {})
    for intento in range(reintentos):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=cab), timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            cuerpo = e.read().decode("utf-8", "replace")[:600]
            if e.code == 429 and intento < reintentos - 1:
                time.sleep(2 * (intento + 1))
                continue
            raise ErrorHerramienta(f"HTTP {e.code} en {urllib.parse.urlsplit(url).netloc}: {cuerpo}")
        except urllib.error.URLError as e:
            if intento < reintentos - 1:
                time.sleep(1.5)
                continue
            raise ErrorHerramienta(f"Sin conexión con {urllib.parse.urlsplit(url).netloc}: {e.reason}")


def _cabeceras_elsevier():
    clave = _cfg("ELSEVIER_API_KEY")
    if not clave:
        raise ErrorHerramienta(
            "No hay clave de la API de Elsevier configurada. Opciones: (1) la usuaria registra una clave gratuita en "
            "https://dev.elsevier.com con su correo institucional y la escribe en la configuración del plugin "
            "(/plugin → asistente-investigacion-cientifica → Configurar); (2) mientras tanto, usar el método del "
            "navegador descrito en la skill revision-sistematica (scopus_api.js).")
    cab = {"X-ELS-APIKey": clave}
    token = _cfg("ELSEVIER_INSTTOKEN")
    if token:
        cab["X-ELS-Insttoken"] = token
    return cab


def _pagina_scopus(ecuacion, vista, cursor="0", cantidad=25):
    # Paginación con start (el parámetro cursor está restringido para claves sin licencia especial; máx. 5.000 registros)
    params = {"query": ecuacion, "view": vista, "count": str(cantidad), "start": str(cursor)}
    return _http_json(f"{SCOPUS_BUSQUEDA}?{urllib.parse.urlencode(params)}", _cabeceras_elsevier())


def _fila_scopus(e, etiqueta):
    autores = e.get("author") or []
    if autores:
        nombres = "; ".join(a.get("authname") or a.get("ce:indexed-name") or "" for a in autores)
    else:
        nombres = e.get("dc:creator", "")
    paginas = (e.get("prism:pageRange") or "").split("-")
    return {
        "Busqueda": etiqueta,
        "Authors": nombres,
        "Title": e.get("dc:title", ""),
        "Year": (e.get("prism:coverDate") or "")[:4],
        "Source title": e.get("prism:publicationName", ""),
        "Volume": e.get("prism:volume", ""),
        "Issue": e.get("prism:issueIdentifier", ""),
        "Art. No.": e.get("article-number", ""),
        "Page start": paginas[0] if paginas and paginas[0] else "",
        "Page end": paginas[1] if len(paginas) > 1 else "",
        "Cited by": e.get("citedby-count", ""),
        "DOI": e.get("prism:doi", ""),
        "Abstract": e.get("dc:description", ""),
        "Author Keywords": e.get("authkeywords", ""),
        "Publisher": "",
        "Document Type": e.get("subtypeDescription", ""),
        "Publication Stage": "",
        "Open Access": "Free to read" if str(e.get("openaccess", "0")) == "1" or e.get("openaccessFlag") is True else "",
        "Subject": "",
        "EID": e.get("eid", ""),
    }


def _abstract_openalex(indice):
    if not indice:
        return ""
    posiciones = [(p, palabra) for palabra, lista in indice.items() for p in lista]
    return " ".join(palabra for _, palabra in sorted(posiciones))


def _doi_limpio(doi):
    doi = (doi or "").strip()
    for prefijo in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.lower().startswith(prefijo):
            doi = doi[len(prefijo):]
    if not doi.startswith("10."):
        raise ErrorHerramienta(f"DOI no válido: «{doi}». Debe empezar con 10.")
    return doi


# --------------------------------------------------------------------- herramientas
def h_scopus_estado(_args):
    estado = {
        "clave_elsevier": "configurada" if _cfg("ELSEVIER_API_KEY") else "FALTA",
        "insttoken": "configurado" if _cfg("ELSEVIER_INSTTOKEN") else "no configurado (solo necesario fuera de la red de la universidad)",
        "correo_contacto": "configurado" if _cfg("CORREO_CONTACTO") else "no configurado (Unpaywall lo requiere)",
    }
    if _cfg("ELSEVIER_API_KEY"):
        try:
            d = _pagina_scopus("TITLE-ABS-KEY(\"cost accounting\") AND PUBYEAR > 2024", "STANDARD", cantidad=1)
            estado["prueba_busqueda"] = f"OK ({d['search-results']['opensearch:totalResults']} resultados de prueba)"
        except ErrorHerramienta as e:
            estado["prueba_busqueda"] = f"FALLÓ: {e}"
        try:
            _pagina_scopus("TITLE-ABS-KEY(\"cost accounting\") AND PUBYEAR > 2024", "COMPLETE", cantidad=1)
            estado["vista_COMPLETE_con_resumenes"] = "disponible"
        except ErrorHerramienta as e:
            estado["vista_COMPLETE_con_resumenes"] = f"no disponible ({str(e)[:160]}); usar scopus_resumen o el navegador"
    return estado


def h_scopus_contar(args):
    ecuacion = args["ecuacion"]
    d = _pagina_scopus(ecuacion, "STANDARD", cantidad=1)
    total = int(d["search-results"].get("opensearch:totalResults", 0))
    return {"ecuacion": ecuacion, "total": total, "fecha_consulta": time.strftime("%Y-%m-%d")}


def h_scopus_exportar(args):
    ecuacion, ruta = args["ecuacion"], args["ruta_csv"]
    maximo = int(args.get("max_registros", 500))
    etiqueta = args.get("etiqueta_busqueda", "B1")
    vista = "COMPLETE"
    try:
        d = _pagina_scopus(ecuacion, vista)
    except ErrorHerramienta as e:
        if "401" in str(e) or "403" in str(e) or "AUTHORIZATION" in str(e).upper():
            vista = "STANDARD"
            d = _pagina_scopus(ecuacion, vista)
        else:
            raise
    total = int(d["search-results"].get("opensearch:totalResults", 0))
    filas = []
    while True:
        entradas = d["search-results"].get("entry", [])
        if entradas and "error" in entradas[0]:
            break
        filas += [_fila_scopus(e, etiqueta) for e in entradas]
        siguiente = len(filas)
        if len(filas) >= min(total, maximo, 5000) or not entradas:
            break
        time.sleep(0.15)
        d = _pagina_scopus(ecuacion, vista, cursor=siguiente)
    filas = filas[:maximo]
    os.makedirs(os.path.dirname(os.path.abspath(ruta)) or ".", exist_ok=True)
    with open(ruta, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS_CSV)
        w.writeheader()
        w.writerows(filas)
    con_resumen = sum(1 for r in filas if r["Abstract"])
    return {"ecuacion": ecuacion, "total_en_scopus": total, "exportados": len(filas), "ruta_csv": os.path.abspath(ruta),
            "vista": vista, "registros_con_resumen": con_resumen, "fecha_consulta": time.strftime("%Y-%m-%d"),
            "nota": "" if con_resumen else "Sin resúmenes: pedir cada uno con scopus_resumen u obtenerlos con el método del navegador."}


def h_scopus_resumen(args):
    if args.get("eid"):
        url = f"{SCOPUS_RESUMEN}/eid/{urllib.parse.quote(args['eid'])}"
    elif args.get("doi"):
        url = f"{SCOPUS_RESUMEN}/doi/{urllib.parse.quote(_doi_limpio(args['doi']))}"
    else:
        raise ErrorHerramienta("Indica eid o doi.")
    d = _http_json(f"{url}?view=META_ABS", _cabeceras_elsevier())
    r = d.get("abstracts-retrieval-response", {})
    core = r.get("coredata", {})
    claves = (r.get("authkeywords") or {}).get("author-keyword") or []
    if isinstance(claves, dict):
        claves = [claves]
    return {"titulo": core.get("dc:title", ""), "doi": core.get("prism:doi", ""), "anio": (core.get("prism:coverDate") or "")[:4],
            "revista": core.get("prism:publicationName", ""), "resumen": core.get("dc:description", ""),
            "palabras_clave": [k.get("$", "") for k in claves]}


def h_openalex_doi(args):
    doi = _doi_limpio(args["doi"])
    params = {"mailto": _cfg("CORREO_CONTACTO")} if _cfg("CORREO_CONTACTO") else {}
    url = f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(doi)}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    w = _http_json(url)
    oa = w.get("open_access") or {}
    ubicaciones = [{"pdf": l.get("pdf_url"), "pagina": l.get("landing_page_url"), "fuente": (l.get("source") or {}).get("display_name"),
                    "version": l.get("version"), "licencia": l.get("license")}
                   for l in (w.get("locations") or []) if l.get("is_oa")]
    return {"titulo": w.get("title"), "anio": w.get("publication_year"), "tipo": w.get("type"), "idioma": w.get("language"),
            "autores": [a["author"]["display_name"] for a in w.get("authorships", [])],
            "revista": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
            "citas": w.get("cited_by_count"), "acceso_abierto": oa.get("is_oa"), "estado_oa": oa.get("oa_status"),
            "url_oa": oa.get("oa_url"), "ubicaciones_oa": ubicaciones, "resumen": _abstract_openalex(w.get("abstract_inverted_index"))}


def h_unpaywall_pdf(args):
    doi = _doi_limpio(args["doi"])
    correo = _cfg("CORREO_CONTACTO")
    if not correo:
        raise ErrorHerramienta("Unpaywall exige un correo de contacto. La usuaria puede escribirlo en la configuración del plugin "
                               "(campo «Correo de contacto»). Mientras tanto, usa openalex_doi, que da los mismos enlaces en la mayoría de casos.")
    d = _http_json(f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?{urllib.parse.urlencode({'email': correo})}")
    mejor = d.get("best_oa_location") or {}
    return {"doi": doi, "titulo": d.get("title"), "acceso_abierto": d.get("is_oa"), "estado_oa": d.get("oa_status"),
            "pdf": mejor.get("url_for_pdf"), "pagina": mejor.get("url"), "version": mejor.get("version"), "licencia": mejor.get("license"),
            "otras_ubicaciones": [l.get("url_for_pdf") or l.get("url") for l in d.get("oa_locations", [])][:6]}


def h_descargar_pdf(args):
    url, ruta = args["url"], args["ruta_pdf"]
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                                             "(KHTML, like Gecko) Chrome/130.0 Safari/537.36",
                                               "Accept": "application/pdf,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            datos = r.read()
    except urllib.error.HTTPError as e:
        raise ErrorHerramienta(f"HTTP {e.code}: el sitio bloqueó la descarga directa. Prueba desde el navegador de la app "
                               "(fetch en la página del artículo) o regístralo como «no recuperado».")
    if datos[:4] != b"%PDF":
        raise ErrorHerramienta("La respuesta no es un PDF (probablemente una página HTML o un CAPTCHA). No se guardó nada.")
    os.makedirs(os.path.dirname(os.path.abspath(ruta)) or ".", exist_ok=True)
    with open(ruta, "wb") as f:
        f.write(datos)
    return {"ruta_pdf": os.path.abspath(ruta), "bytes": len(datos), "verificado": "empieza con %PDF"}


# --------------------------------------------------------------------- catálogo
def _herramienta(nombre, titulo, descripcion, propiedades, requeridos, solo_lectura=True):
    return {"name": nombre, "title": titulo, "description": descripcion,
            "inputSchema": {"type": "object", "properties": propiedades, "required": requeridos, "additionalProperties": False},
            "annotations": {"title": titulo, "readOnlyHint": solo_lectura, "destructiveHint": False, "openWorldHint": True}}


ECUACION = {"type": "string", "description": "Ecuación en sintaxis de búsqueda avanzada de Scopus, p. ej. "
            "TITLE-ABS-KEY((\"cost volume profit\") AND (\"decision making\")) AND PUBYEAR > 2021 AND PUBYEAR < 2027 "
            "AND DOCTYPE(ar) AND LANGUAGE(english) AND PUBSTAGE(final). Referencia: https://dev.elsevier.com/sc_search_tips.html"}
DOI = {"type": "string", "description": "DOI del artículo, con o sin el prefijo https://doi.org/"}

HERRAMIENTAS = {
    "scopus_estado": (h_scopus_estado, _herramienta(
        "scopus_estado", "Estado de la conexión con Scopus",
        "Indica si la clave de la API de Elsevier y el correo de contacto están configurados, y prueba una búsqueda mínima. "
        "Úsala al empezar una revisión para saber si se busca por la API o por el navegador.", {}, [])),
    "scopus_contar": (h_scopus_contar, _herramienta(
        "scopus_contar", "Contar resultados en Scopus",
        "Devuelve cuántos documentos encuentra una ecuación en Scopus (Scopus Search API). Sirve para la fase de "
        "identificación de PRISMA: conteo sin filtros y con filtros.", {"ecuacion": ECUACION}, ["ecuacion"])),
    "scopus_exportar": (h_scopus_exportar, _herramienta(
        "scopus_exportar", "Exportar resultados de Scopus a CSV",
        "Descarga los registros de una ecuación (autores, título, año, revista, DOI, resumen, palabras clave, acceso "
        "abierto, EID) y los guarda en un CSV en disco. Devuelve solo un resumen. Intenta la vista COMPLETE (con "
        "resúmenes) y, si la suscripción no la permite, usa STANDARD.",
        {"ecuacion": ECUACION, "ruta_csv": {"type": "string", "description": "Ruta del CSV a crear (se sobrescribe si existe)"},
         "max_registros": {"type": "integer", "description": "Máximo de registros (por defecto 500)", "minimum": 1, "maximum": 5000},
         "etiqueta_busqueda": {"type": "string", "description": "Etiqueta de la ecuación en la matriz, p. ej. B1"}},
        ["ecuacion", "ruta_csv"], solo_lectura=False)),
    "scopus_resumen": (h_scopus_resumen, _herramienta(
        "scopus_resumen", "Resumen de un artículo en Scopus",
        "Devuelve el título, el resumen y las palabras clave de un artículo por su EID o DOI (Abstract Retrieval API).",
        {"eid": {"type": "string", "description": "EID de Scopus, p. ej. 2-s2.0-85160032031"}, "doi": DOI}, [])),
    "openalex_doi": (h_openalex_doi, _herramienta(
        "openalex_doi", "Metadatos abiertos de un DOI (OpenAlex)",
        "Consulta OpenAlex (datos abiertos CC0): autores, revista, año, idioma, citas, resumen y ubicaciones de acceso "
        "abierto con enlace al PDF cuando existe.", {"doi": DOI}, ["doi"])),
    "unpaywall_pdf": (h_unpaywall_pdf, _herramienta(
        "unpaywall_pdf", "PDF legal de acceso abierto (Unpaywall)",
        "Busca en Unpaywall la mejor copia legal de acceso abierto de un DOI (versión del editor o del autor).",
        {"doi": DOI}, ["doi"])),
    "descargar_pdf": (h_descargar_pdf, _herramienta(
        "descargar_pdf", "Descargar un PDF de acceso abierto",
        "Descarga un PDF desde una URL de acceso abierto y lo guarda solo si el archivo empieza con %PDF. No resuelve "
        "CAPTCHA ni evita bloqueos: si el sitio bloquea, informa el error para registrar el artículo como no recuperado.",
        {"url": {"type": "string", "description": "URL directa del PDF"},
         "ruta_pdf": {"type": "string", "description": "Ruta donde guardar, p. ej. literatura/B1/Autor_2024_Tema.pdf"}},
        ["url", "ruta_pdf"], solo_lectura=False)),
}

INSTRUCCIONES = ("Herramientas de búsqueda de literatura científica. Empieza con scopus_estado. Para PRISMA: scopus_contar "
                 "(sin y con filtros) → scopus_exportar al CSV del proyecto → cribado → openalex_doi / unpaywall_pdf → "
                 "descargar_pdf. Si Scopus no tiene clave, sigue el método del navegador de la skill revision-sistematica.")


# --------------------------------------------------------------------- protocolo
def _responder(id_, resultado=None, error=None):
    msg = {"jsonrpc": "2.0", "id": id_}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = resultado
    sys.stdout.buffer.write((json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()


def _atender(msg):
    metodo, id_ = msg.get("method"), msg.get("id")
    if id_ is None:  # notificación (p. ej. notifications/initialized): no se responde
        return
    params = msg.get("params") or {}
    if metodo == "initialize":
        pedida = params.get("protocolVersion")
        _responder(id_, {"protocolVersion": pedida if pedida in PROTOCOLOS else PROTOCOLOS[0],
                         "capabilities": {"tools": {"listChanged": False}},
                         "serverInfo": {"name": "literatura", "title": "Literatura científica (Scopus, OpenAlex, Unpaywall)",
                                        "version": VERSION},
                         "instructions": INSTRUCCIONES})
    elif metodo == "ping":
        _responder(id_, {})
    elif metodo == "tools/list":
        _responder(id_, {"tools": [definicion for _, definicion in HERRAMIENTAS.values()]})
    elif metodo == "tools/call":
        nombre = params.get("name")
        if nombre not in HERRAMIENTAS:
            _responder(id_, error={"code": -32602, "message": f"Herramienta desconocida: {nombre}"})
            return
        try:
            datos = HERRAMIENTAS[nombre][0](params.get("arguments") or {})
            _responder(id_, {"content": [{"type": "text", "text": json.dumps(datos, ensure_ascii=False, indent=1)}], "isError": False})
        except (ErrorHerramienta, KeyError, ValueError) as e:
            texto = f"Falta el argumento {e}" if isinstance(e, KeyError) else str(e)
            _responder(id_, {"content": [{"type": "text", "text": texto}], "isError": True})
        except Exception as e:  # noqa: BLE001 - cualquier fallo inesperado se informa sin tumbar el servidor
            _log("error inesperado:", repr(e))
            _responder(id_, {"content": [{"type": "text", "text": f"Error inesperado: {e!r}"}], "isError": True})
    else:
        _responder(id_, error={"code": -32601, "message": f"Método no soportado: {metodo}"})


def main():
    _log(f"servidor iniciado (v{VERSION})")
    for linea in iter(sys.stdin.buffer.readline, b""):
        linea = linea.strip()
        if not linea:
            continue
        try:
            msg = json.loads(linea.decode("utf-8"))
        except json.JSONDecodeError:
            _responder(None, error={"code": -32700, "message": "JSON no válido"})
            continue
        for m in (msg if isinstance(msg, list) else [msg]):
            _atender(m)


if __name__ == "__main__":
    main()
