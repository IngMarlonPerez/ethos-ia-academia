# -*- coding: utf-8 -*-
"""Inserta un cuerpo WordprocessingML después de la portada de una plantilla UNEMI (docx) sin tocar la portada
(salvo reemplazos de texto explícitos). Conserva encabezado, pie, logo y estilos de la plantilla.

Uso desde un script de contenido:
    from ooxml import *
    from ensamblar_plantilla import ensamblar
    ensamblar(plantilla_intacta, salida, ''.join(bloques),
              reemplazos={"CARRERA DE INGENIERÍA DE SOFTWARE": "CARRERA DE INGENIERÍA EN TECNOLOGÍAS DE LA INFORMACIÓN"},
              quitar_vacio_antes="MILAGRO-ECUADOR")
La portada termina en el párrafo que contiene el primer <w:sectPr>. La plantilla se copia siempre intacta antes de
cada corrida (nunca se reescribe a mano).
"""
import os, re, shutil, tempfile, zipfile

BULLET = ('<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="hybridMultilevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/>'
          '<w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="360" w:hanging="360"/></w:pPr>'
          '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/></w:rPr></w:lvl></w:abstractNum>'
          '<w:num w:numId="1"><w:abstractNumId w:val="1"/></w:num>')


def ensamblar(plantilla, salida, cuerpo_xml, reemplazos=None, quitar_vacio_antes=None, margen_twips=1417):
    tmp = tempfile.mkdtemp(prefix="plantilla_")
    with zipfile.ZipFile(plantilla) as z:
        z.extractall(tmp)
    dp = os.path.join(tmp, "word", "document.xml")
    x = open(dp, encoding="utf8").read()
    i = x.find("<w:body>")
    j = x.find("</w:sectPr>", i)                      # sectPr de la portada (dentro de su último párrafo)
    k = x.find("</w:p>", j) + len("</w:p>")
    portada = x[:k]
    for a, b in (reemplazos or {}).items():
        assert a in portada, f"no está en la portada: {a!r}"
        portada = portada.replace(a, b)
    if quitar_vacio_antes:                              # evita que la portada desborde a una 2.ª hoja
        mi = portada.find(quitar_vacio_antes)
        ps = portada.rfind("<w:p ", 0, mi)
        pe = portada.rfind("<w:p ", 0, ps)
        assert "<w:t" not in portada[pe:ps] and "<w:sectPr" not in portada[pe:ps], "el párrafo previo no está vacío"
        portada = portada[:pe] + portada[ps:]
    m = margen_twips
    sect = (f'<w:sectPr><w:type w:val="nextPage"/><w:pgSz w:w="11906" w:h="16838" w:orient="portrait"/>'
            f'<w:pgMar w:top="{m}" w:right="{m}" w:bottom="{m}" w:left="{m}" w:header="708" w:footer="708"/></w:sectPr>')
    open(dp, "w", encoding="utf8").write(portada + cuerpo_xml + sect + "</w:body></w:document>")
    npath = os.path.join(tmp, "word", "numbering.xml")
    n = open(npath, encoding="utf8").read()
    n = re.sub(r'/>\s*$', '>' + BULLET + '</w:numbering>', n) if n.rstrip().endswith('/>') else n.replace('</w:numbering>', BULLET + '</w:numbering>')
    open(npath, "w", encoding="utf8").write(n)
    if os.path.exists(salida):
        os.remove(salida)
    with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(tmp, "[Content_Types].xml"), "[Content_Types].xml")
        for root, _, files in os.walk(tmp):
            for f in files:
                full = os.path.join(root, f)
                arc = os.path.relpath(full, tmp).replace("\\", "/")
                if arc != "[Content_Types].xml":
                    z.write(full, arc)
    shutil.rmtree(tmp, ignore_errors=True)
    return salida
