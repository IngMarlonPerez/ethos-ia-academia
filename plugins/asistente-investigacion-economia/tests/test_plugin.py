# -*- coding: utf-8 -*-
"""Pruebas del plugin de Economía: estructura, manifiesto, frontmatter de skills y agentes, y smoke tests de las librerías."""
import importlib.util, json, os, re, sys, zipfile
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(RAIZ, "scripts")
sys.path.insert(0, SCRIPTS)


def frontmatter(ruta):
    t = open(ruta, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    assert m, f"sin frontmatter: {ruta}"
    campos = dict(re.findall(r"^(name|description|tools):\s*(.+)$", m.group(1), re.M))
    return campos


def test_manifiesto():
    j = json.load(open(os.path.join(RAIZ, ".claude-plugin", "plugin.json"), encoding="utf-8"))
    assert j["name"] == "asistente-investigacion-economia" and j["version"]
    assert {"elsevier_api_key", "elsevier_insttoken", "correo_contacto"} <= set(j["userConfig"])
    mcp = json.load(open(os.path.join(RAIZ, ".mcp.json"), encoding="utf-8"))
    assert "literatura" in mcp["mcpServers"]


@pytest.mark.parametrize("nombre", sorted(os.listdir(os.path.join(RAIZ, "skills"))))
def test_skills(nombre):
    ruta = os.path.join(RAIZ, "skills", nombre, "SKILL.md")
    c = frontmatter(ruta)
    assert c["name"] == nombre and len(c["description"]) > 80


@pytest.mark.parametrize("archivo", sorted(os.listdir(os.path.join(RAIZ, "agents"))))
def test_agentes(archivo):
    c = frontmatter(os.path.join(RAIZ, "agents", archivo))
    assert c["name"] + ".md" == archivo and c["tools"]


def test_referencias_de_las_skills_existen():
    """Toda ruta ${CLAUDE_PLUGIN_ROOT}/... citada en skills y agentes debe existir."""
    faltan = []
    for base, _, files in os.walk(RAIZ):
        for f in files:
            if f.endswith(".md") and ("skills" in base or "agents" in base):
                t = open(os.path.join(base, f), encoding="utf-8").read()
                for ruta in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./\-]+\.(?:py|md|ps1|js|json))", t):
                    if not os.path.exists(os.path.join(RAIZ, ruta)):
                        faltan.append((f, ruta))
    assert not faltan, faltan


def test_lib_docx_y_mathlib():
    import lib_docx as L
    xml = L.P("Texto *cursiva* y $$c+v+p$$") + L.EQ(r"s'=\frac{p}{v}") + L.TABLE([["a", "b"], ["c", "d"]], [1000, 1000]) + L.CAPT("Tabla 1", "t") + L.NOTE("x")
    from lxml import etree
    etree.fromstring(('<w:root xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">' + xml + "</w:root>").encode("utf8"))
    assert "m:oMath" in xml


def test_ensamblar_no_toca_plantilla(tmp_path):
    """Crea una plantilla mínima, ensambla y comprueba que la plantilla queda intacta."""
    import hashlib, lib_docx as L
    doc = ('<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
           'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
           'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body><w:p w14:paraId="AAAA0001"><w:r><w:t>Intro</w:t></w:r></w:p>'
           '<w:sectPr><w:pgMar w:top="1320" w:right="1700" w:bottom="280" w:left="1559"/></w:sectPr></w:body></w:document>')
    plantilla = tmp_path / "plantilla.docx"
    with zipfile.ZipFile(plantilla, "w") as z:
        z.writestr("word/document.xml", doc)
        z.writestr("word/_rels/document.xml.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>')
    h0 = hashlib.md5(plantilla.read_bytes()).hexdigest()
    salida = tmp_path / "salida.docx"
    L.set_figuras(str(tmp_path))
    L.ensamblar(str(plantilla), str(salida), {"AAAA0001": lambda x: x + L.P("Contenido nuevo")})
    assert hashlib.md5(plantilla.read_bytes()).hexdigest() == h0
    assert b"Contenido nuevo" in zipfile.ZipFile(salida).read("word/document.xml")
    assert b'w:bottom="1300"' in zipfile.ZipFile(salida).read("word/document.xml")


def test_matriz_y_ris_de_extremo_a_extremo(tmp_path):
    """Proyecto sintético: 3 registros, 2 candidatos -> matriz, PRISMA y RIS coherentes."""
    import csv, textwrap
    ev = tmp_path / "Evidencias_Drive"
    for s in ("01_Busquedas_Scopus", "04_Scripts_Python", "05_Base_datos"):
        (ev / s).mkdir(parents=True)
    cols = ["Busqueda", "Authors", "Title", "Year", "Source title", "Volume", "Issue", "Art. No.", "Page start", "Page end", "Cited by", "DOI", "Abstract",
            "Author Keywords", "Publisher", "Document Type", "Publication Stage", "Open Access", "Subject", "EID"]
    filas = [("B1", "Uno A.", "Mercantilism and trade", "2022", "Rev A", "1", "1", "", "1", "10", "5", "10.1/aaa", "", "mercantilism; trade", "", "Article", "", "Free to read", "", "e1"),
             ("B1", "Dos B.", "Physiocracy net product", "2021", "Rev B", "2", "2", "", "5", "20", "3", "10.1/bbb", "", "", "", "Article", "", "", "", "e2"),
             ("B1", "Tres C.", "Health care costs", "2020", "Rev C", "3", "3", "", "7", "9", "1", "10.1/ccc", "", "", "", "Article", "", "", "", "e3")]
    with open(ev / "01_Busquedas_Scopus" / "scopus_B1_t.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(cols); w.writerows(filas)
    (ev / "04_Scripts_Python" / "config_trabajo.py").write_text(textwrap.dedent('''
        TEMA="Prueba"; FECHA="13-oct-2026"; AUTORA="Grupo X"
        PREGUNTAS={"Q1":"Mercantilismo","Q2":"Fisiocracia"}
        CRITERIOS=[("Inclusión","x")]
        CSVS={"B1":"scopus_B1_t.csv"}
        BUSQUEDAS=[{"id":"B1","base":"Scopus","ecuacion":"X","filtros":"ar","fecha":FECHA,"metodo":"API","sin_filtros":10,"con_filtros":3,"rol":"p"}]
        REGLAS=[(r"health","E1 · salud")]
        CAND={"10.1/aaa":dict(cita="Uno (2022)",sc=(2,0),dec="I",acc="RES",mot="m",obj="o",hall="h",aportes={"Q1":"a"}),
              "10.1/bbb":dict(cita="Dos (2021)",sc=(0,2),dec="I",acc="MET",mot="m",obj="o",hall="",aportes={"Q2":"b"})}
        LIBROS=[("Marx, Karl",1867,"Das Kapital","Meissner")]
        TITULOS_APA={}; IDIOMA={}; PDFS={}
        PERIODOS=["a","b","c"]; CONTEOS_PERIODO={"B1":[1,2,3]}; CORPUS={"B1":"scopus_B1_t.csv"}
    '''), encoding="utf-8")
    import matriz_consistencia as M, ris_zotero as R, json as J
    cfg = str(ev / "04_Scripts_Python" / "config_trabajo.py")
    M.main(cfg)
    P = J.load(open(ev / "05_Base_datos" / "prisma_conteos.json", encoding="utf-8"))
    assert P["n_unicos"] == 3 and P["n_inc"] == 2 and P["motivos_titulo"].get("E1") == 1
    R.main(cfg)
    ris = (ev / "01_Busquedas_Scopus" / "referencias_incluidas_zotero.ris").read_text(encoding="utf-8")
    assert ris.count("ER  - ") == 3 and "TY  - BOOK" in ris and "DO  - 10.1/aaa" in ris


def test_graficos_busqueda_genera_figuras(tmp_path):
    """Reutiliza el proyecto sintético: debe crear el flujo y la evidencia bibliométrica."""
    test_matriz_y_ris_de_extremo_a_extremo(tmp_path)
    import graficos_busqueda as G
    G.main(str(tmp_path / "Evidencias_Drive" / "04_Scripts_Python" / "config_trabajo.py"))
    assert (tmp_path / "Evidencias_Drive" / "03_Graficos" / "fig_flujo_seleccion.png").stat().st_size > 5000
    assert (tmp_path / "Evidencias_Drive" / "03_Graficos" / "fig_evidencia_bibliometrica.png").stat().st_size > 5000


def test_iniciar_trabajo_crea_estructura(tmp_path):
    import iniciar_trabajo as I
    plantilla = tmp_path / "p.docx"; plantilla.write_bytes(b"PK")
    I.main([str(tmp_path / "trabajo"), "--tema", "T", "--autora", "G", "--plantilla", str(plantilla)])
    t = tmp_path / "trabajo"
    assert (t / "00_Control_Trabajo.md").exists() and (t / "_respaldo" / "p_respaldo_original.docx").exists()
    assert (t / "Evidencias_Drive" / "04_Scripts_Python" / "config_trabajo.py").exists()
    for lib in ("lib_docx.py", "matriz_consistencia.py", "ris_zotero.py", "matrices.py"):
        assert (t / "Evidencias_Drive" / "04_Scripts_Python" / lib).exists()
