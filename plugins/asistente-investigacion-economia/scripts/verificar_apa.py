"""Verifica un documento contra las reglas de citación y referencias de APA 7.ª edición.

Uso:
    python verificar_apa.py documento.docx [--desde 2022] [--hasta 2026] [--titulo-referencias "Referencias"]
    python verificar_apa.py documento.md   (también .txt)

Revisa:
  ERRORES (deben corregirse)
    - referencia de la lista que no se cita en el texto
    - cita en el texto cuyo autor tiene referencia pero con otro año
    - referencias duplicadas
    - lista de referencias fuera de orden alfabético
    - DOI escrito sin el formato https://doi.org/...
  ADVERTENCIAS (revisar)
    - posible cita sin referencia (heurística: puede ser una falsa alarma)
    - «et al.» con 1–2 autores, o nombres completos con 3+ autores (APA 7 usa et al. desde la primera cita)
    - «&» dentro del texto en español (en el texto se escribe «y»)
    - años fuera del rango pedido; «Recuperado de» delante de un DOI
    - en .docx: referencias sin sangría francesa o sin ninguna cursiva (revista, volumen o libro)
Sale con código 1 si hay errores.
"""
import argparse
import re
import sys
import unicodedata

TITULOS_REF = ("referencias", "referencias bibliográficas", "referencias bibliograficas", "bibliografía", "bibliografia",
               "references", "lista de referencias")
TITULOS_FIN = ("anexo", "anexos", "apéndice", "apendice", "apéndices", "appendix", "anexos y transparencia")
AÑO = r"(?:1[89]\d\d|20\d\d)[a-z]?"
NO_AUTORES = {"tabla", "figura", "nota", "parte", "actividad", "pregunta", "escenario", "anexo", "enero", "febrero", "marzo",
              "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre", "q", "n", "p",
              "periodo", "período", "año", "desde", "hasta", "entre", "total", "prisma", "scopus", "versión", "version"}


def normal(texto):
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(c for c in t if not unicodedata.combining(c)).replace("ø", "o")
    return re.sub(r"[^a-z0-9 ]", "", t).strip()


def clave_orden(ref_texto):
    """Orden APA 7 (9.44–9.46): letra por letra dentro del apellido del primer autor, sin espacios ni signos
    («da Silva» se ordena como «dasilva»); «nada precede a algo» (Loft antes que Loftus); luego el resto."""
    apellido, _, resto = ref_texto.partition(",")
    return (normal(apellido).replace(" ", ""), normal(resto).replace(" ", ""))


# ------------------------------------------------------------------ lectura
def leer_docx(ruta):
    import docx
    d = docx.Document(ruta)
    parrafos = []
    for p in d.paragraphs:
        indent = p.paragraph_format.first_line_indent
        parrafos.append({"texto": p.text, "francesa": bool(indent is not None and indent < 0),
                         "cursiva": any(r.italic for r in p.runs if r.text.strip())})
    tablas = [" ".join(c.text for c in fila.cells) for t in d.tables for fila in t.rows]
    return parrafos, tablas


def leer_texto(ruta):
    texto = open(ruta, encoding="utf-8").read()
    parrafos = [{"texto": re.sub(r"^#+\s*", "", l), "francesa": None, "cursiva": None} for l in texto.splitlines()]
    return parrafos, []


def separar(parrafos, titulo_ref=None):
    """Devuelve (cuerpo, referencias) según el título de la lista de referencias."""
    titulos = (titulo_ref.lower(),) if titulo_ref else TITULOS_REF
    inicio = None
    for i, p in enumerate(parrafos):
        if p["texto"].strip().lower().rstrip(":") in titulos:
            inicio = i
    if inicio is None:
        return parrafos, []
    fin = len(parrafos)
    for j in range(inicio + 1, len(parrafos)):
        t = p = parrafos[j]["texto"].strip().lower()
        if any(t.startswith(x) for x in TITULOS_FIN) and len(t) < 60:
            fin = j
            break
    return parrafos[:inicio] + parrafos[fin:], parrafos[inicio + 1:fin]


# ------------------------------------------------------------------ referencias
def analizar_referencia(texto):
    m = re.match(rf"^(.+?)\s\(({AÑO}|s\.\s?f\.|n\.\s?d\.|en prensa|in press)(?:,[^)]*)?\)\.", texto.strip())
    if not m:
        return None
    autores_txt, anio = m.group(1), m.group(2)
    pares = re.findall(r"([^,&]+?),\s((?:[A-ZÁÉÍÓÚÑ][a-záéíóú]?\.[\s-]?)+)", autores_txt.replace(" & ", ", "))
    apellidos = [a.strip() for a, _ in pares] or [autores_txt.split(",")[0].strip()]
    n_autores = len(pares) if pares else 1
    if "..." in autores_txt or "…" in autores_txt:
        n_autores = max(n_autores, 21)
    return {"texto": texto.strip(), "apellidos": apellidos, "primer": apellidos[0], "anio": anio, "n_autores": n_autores}


# ------------------------------------------------------------------ citas
def extraer_citas(cuerpo):
    """Citas parentéticas y narrativas: lista de dicts con autor principal, año, forma y texto."""
    citas = []
    for m in re.finditer(r"\(([^()]*?\d{4}[a-z]?[^()]*)\)", cuerpo):
        for item in m.group(1).split(";"):
            item = item.strip()
            mm = re.match(rf"^(?:véase\s+|ver\s+|como se citó en\s+)?(.+?),\s*({AÑO}(?:,\s*{AÑO})*|s\.\s?f\.|en prensa)(?:,.*)?$", item)
            if mm:
                for anio in re.findall(AÑO + r"|s\.\s?f\.|en prensa", mm.group(2)):
                    citas.append({"autores": mm.group(1).strip(), "anio": anio, "forma": "parentética", "texto": f"({item})"})
    for m in re.finditer(PATRON_NARRATIVA, cuerpo):
        autores = _sin_palabras_iniciales(m.group(1))
        if autores:
            citas.append({"autores": autores, "anio": m.group(2), "forma": "narrativa", "texto": f"{autores} ({m.group(2)})"})
    return citas


NOMBRE = r"[A-ZÁÉÍÓÚÑØ][\w'’\-]+(?: [A-ZÁÉÍÓÚÑØ][\w'’\-]+)*"
AUTOR = r"(?:(?:[Dd][ae]|[Dd]el|[Vv]an|[Vv]on|[Dd][iu]) )?" + NOMBRE
PATRON_NARRATIVA = (rf"({AUTOR}(?:, {AUTOR})*(?:,? (?:y|&) {AUTOR})?(?: et al\.)?) "
                    rf"\(({AÑO}|s\.\s?f\.|en prensa)(?:, p{{1,2}}\. ?[\d–\-]+)?\)")
PALABRAS_INICIALES = {"segun", "tambien", "para", "como", "en", "por", "con", "sin", "los", "las", "el", "la", "lo", "al",
                      "del", "de", "ademas", "asi", "asimismo", "mientras", "aunque", "ya", "y", "e", "que", "cuando", "donde",
                      "igualmente", "finalmente", "luego", "despues", "antes", "un", "una", "este", "esta", "estos", "estas",
                      "dicho", "dicha", "su", "sus", "si", "no", "mas", "entre", "sobre", "tras", "hacia", "porque", "pues",
                      "and", "the", "of", "in", "by", "as", "while", "although", "according", "to"}


def _sin_palabras_iniciales(autores):
    """Quita palabras comunes que el patrón toma por apellidos al inicio de la oración («Según Pérez» → «Pérez»)."""
    tokens = autores.split(" ")
    while tokens and normal(tokens[0]) in PALABRAS_INICIALES:
        tokens.pop(0)
    return " ".join(tokens).strip(" ,")


def _coincide(cita_autores, ref):
    ca = normal(cita_autores)
    return any(normal(a) and (normal(a) in ca or ca.startswith(normal(a).split()[-1])) for a in ref["apellidos"][:1]) or \
        normal(ref["primer"]).split()[-1] in ca.split()


# ------------------------------------------------------------------ verificación
def verificar(parrafos, tablas, desde=None, hasta=None, titulo_ref=None):
    cuerpo_p, refs_p = separar(parrafos, titulo_ref)
    cuerpo = "\n".join(p["texto"] for p in cuerpo_p) + "\n" + "\n".join(tablas)
    errores, avisos, info = [], [], []

    refs, otros = [], []
    for p in refs_p:
        if not p["texto"].strip():
            continue
        r = analizar_referencia(p["texto"])
        if r:
            r.update({"francesa": p["francesa"], "cursiva": p["cursiva"]})
            refs.append(r)
        else:
            otros.append(p["texto"].strip()[:120])
    if not refs_p:
        errores.append("No se encontró el título de la lista de referencias (Referencias / Bibliografía).")
    info.append(f"{len(refs)} referencias en la lista")
    for o in otros:
        info.append(f"Párrafo en la sección de referencias que no parece una referencia: «{o}»")

    # duplicados y orden
    vistas = {}
    for r in refs:
        clave = normal(r["texto"])[:120]
        if clave in vistas:
            errores.append(f"Referencia duplicada: {r['texto'][:90]}")
        vistas[clave] = True
    claves = [clave_orden(r["texto"]) for r in refs]
    for a, b, r in zip(claves, claves[1:], refs[1:]):
        if b < a:
            errores.append(f"Orden alfabético: «{r['texto'][:60]}…» debería ir antes de la referencia anterior")

    for r in refs:
        if re.search(r"\b(?:doi:\s*10\.|dx\.doi\.org|http://doi\.org)", r["texto"], re.I):
            errores.append(f"DOI con formato antiguo (usar https://doi.org/...): {r['texto'][:80]}")
        if re.search(r"(Recuperado de|Retrieved from)\s+https?://doi", r["texto"], re.I):
            avisos.append(f"«Recuperado de» delante de un DOI (APA 7 no lo usa): {r['texto'][:80]}")
        anio = re.match(r"\d{4}", r["anio"])
        if anio and ((desde and int(anio.group()) < desde) or (hasta and int(anio.group()) > hasta)):
            avisos.append(f"Año fuera del rango {desde}–{hasta}: {r['texto'][:80]}")
        if r["francesa"] is False:
            avisos.append(f"Sin sangría francesa: {r['texto'][:70]}")
        if r["cursiva"] is False:
            avisos.append(f"Sin cursivas (revista y volumen, o título del libro): {r['texto'][:70]}")

    # citas ↔ referencias
    citas = [c for c in extraer_citas(cuerpo) if normal(c["autores"]).split()[:1] and
             normal(c["autores"]).split()[0] not in NO_AUTORES and not c["autores"].isupper()]
    citadas = set()
    for c in citas:
        candidatas = [r for r in refs if _coincide(c["autores"], r)]
        mismas = [r for r in candidatas if r["anio"].rstrip("abcdefgh") == c["anio"].rstrip("abcdefgh") and
                  (r["anio"] == c["anio"] or not c["anio"][-1:].isalpha())]
        if mismas:
            r = mismas[0]
            citadas.add(r["texto"])
            if "et al" in c["autores"] and r["n_autores"] <= 2:
                avisos.append(f"«et al.» con {r['n_autores']} autor(es): {c['texto']} → nombra a todos")
            if "et al" not in c["autores"] and r["n_autores"] >= 3:
                avisos.append(f"{r['n_autores']} autores: usa «et al.» desde la primera cita → {c['texto']}")
            if r["n_autores"] == 2 and "et al" not in c["autores"] and not re.search(r"\s(y|&)\s", c["autores"]):
                avisos.append(f"Dos autores: nombra a ambos → {c['texto']}")
        elif candidatas:
            errores.append(f"Año distinto al de la referencia: {c['texto']} (en la lista: {candidatas[0]['anio']})")
        else:
            avisos.append(f"Posible cita sin referencia: {c['texto']}")
        if re.search(r"\s&\s", c["autores"]) and c["forma"] == "narrativa":
            avisos.append(f"En el texto en español se escribe «y», no «&»: {c['texto']}")
    for r in refs:
        if r["texto"] not in citadas:
            errores.append(f"Referencia sin cita en el texto: {r['texto'][:90]}")
    info.append(f"{len(citas)} citas encontradas en el texto; {len(citadas)} referencias citadas")
    return errores, list(dict.fromkeys(avisos)), info


def main():
    # En consolas de Windows (cp1252) un nombre como «Fındık» rompía la impresión.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("documento")
    ap.add_argument("--desde", type=int)
    ap.add_argument("--hasta", type=int)
    ap.add_argument("--titulo-referencias")
    a = ap.parse_args()
    if a.documento.lower().endswith(".docx"):
        parrafos, tablas = leer_docx(a.documento)
    else:
        parrafos, tablas = leer_texto(a.documento)
    errores, avisos, info = verificar(parrafos, tablas, a.desde, a.hasta, a.titulo_referencias)
    print("=== Verificación APA 7 ===")
    for i in info:
        print("·", i)
    print(f"\nERRORES ({len(errores)})")
    for e in errores:
        print("  ✗", e)
    print(f"\nADVERTENCIAS ({len(avisos)})")
    for w in avisos:
        print("  !", w)
    print("\nResultado:", "APROBADO (sin errores)" if not errores else "CORREGIR LOS ERRORES")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
