"""Arma una carpeta de evidencias lista para subir a Google Drive (u otro repositorio compartido).

Lee la carpeta de literatura del proyecto, con una subcarpeta por búsqueda o parte del trabajo:
    literatura/
      B1_Tema/            PDF citados, scopus_*.csv, *_seleccionados.ris, Matriz*.xlsx, *_PRISMA_2020.png
        _leidos_no_seleccionados/   PDF leídos que no se citaron
      por_descargar.json  (opcional) artículos no recuperados: [{"prioridad", "referencia", "enlace", "nota"}]

y crea (copia, no mueve):
    <destino>/
      Articulos_PDF/<subcarpeta>/
      Articulos_leidos_no_seleccionados/<subcarpeta>/
      Metadatos_RIS/<subcarpeta>.ris + Referencias_consolidadas.ris (sin duplicados, para Zotero)
      Matrices_Revision_Bibliografica/ (+ Resultados_busqueda_Scopus/ con los CSV, + diagramas PRISMA)
      Anexos/ (archivos pasados con --extra, p. ej. un Excel con gráficos)
      LEEME.txt · Articulos_por_descargar_manualmente.txt

Uso:
    python armar_paquete.py <carpeta_literatura> <destino> [--titulo "Grupo J · Sistemas de Costeo"] [--extra archivo ...]
Se puede volver a ejecutar: reemplaza la carpeta que el propio script generó (la reconoce por su LEEME.txt).
"""
import argparse
import glob
import json
import os
import re
import shutil

MARCA = "Carpeta generada por armar_paquete.py (Asistente de Investigación Científica)"


def _copiar(origen, destino):
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.copy2(origen, destino)


def _registros_ris(ruta):
    texto = open(ruta, encoding="utf-8-sig").read()
    return [r.strip() + "\nER  - \n" for r in re.split(r"^ER  -.*$", texto, flags=re.M) if r.strip()]


def _clave_ris(registro):
    m = re.search(r"^DO  - (.+)$", registro, re.M) or re.search(r"^TI  - (.+)$", registro, re.M)
    return m.group(1).strip().lower() if m else registro[:200]


def armar(literatura, destino, titulo="", extra=()):
    if os.path.exists(destino):
        leeme = os.path.join(destino, "LEEME.txt")
        if not (os.path.exists(leeme) and MARCA in open(leeme, encoding="utf-8-sig").read()):
            raise SystemExit(f"{destino} ya existe y no la generó este script; no se toca. Elige otro destino.")
        shutil.rmtree(destino)
    n_pdf = n_no_sel = 0
    ris_todos, vistos, partes = [], set(), []
    subcarpetas = sorted(d for d in os.listdir(literatura)
                         if os.path.isdir(os.path.join(literatura, d)) and not d.startswith(("_", ".")))
    for sub in subcarpetas:
        base = os.path.join(literatura, sub)
        pdfs = sorted(glob.glob(os.path.join(base, "*.pdf")))
        no_sel = sorted(glob.glob(os.path.join(base, "_leidos_no_seleccionados", "*.pdf")))
        for pdf in pdfs:
            _copiar(pdf, os.path.join(destino, "Articulos_PDF", sub, os.path.basename(pdf)))
        for pdf in no_sel:
            _copiar(pdf, os.path.join(destino, "Articulos_leidos_no_seleccionados", sub, os.path.basename(pdf)))
        n_pdf += len(pdfs)
        n_no_sel += len(no_sel)
        n_ris_parte = 0
        for ris in sorted(glob.glob(os.path.join(base, "*seleccionados*.ris"))):
            _copiar(ris, os.path.join(destino, "Metadatos_RIS", f"{sub}.ris" if n_ris_parte == 0 else os.path.basename(ris)))
            for reg in _registros_ris(ris):
                n_ris_parte += 1
                if _clave_ris(reg) not in vistos:
                    vistos.add(_clave_ris(reg))
                    ris_todos.append(reg)
        for patron, carpeta in (("Matri*.xlsx", "Matrices_Revision_Bibliografica"), ("*PRISMA*.png", "Matrices_Revision_Bibliografica"),
                                ("scopus_*.csv", os.path.join("Matrices_Revision_Bibliografica", "Resultados_busqueda_Scopus"))):
            for f in glob.glob(os.path.join(base, patron)):
                _copiar(f, os.path.join(destino, carpeta, os.path.basename(f)))
        partes.append((sub, len(pdfs), len(no_sel), n_ris_parte))
    if ris_todos:
        os.makedirs(os.path.join(destino, "Metadatos_RIS"), exist_ok=True)
        with open(os.path.join(destino, "Metadatos_RIS", "Referencias_consolidadas.ris"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(ris_todos))
    for f in extra:
        _copiar(f, os.path.join(destino, "Anexos", os.path.basename(f)))

    pendientes = []
    ruta_json = os.path.join(literatura, "por_descargar.json")
    if os.path.exists(ruta_json):
        pendientes = json.load(open(ruta_json, encoding="utf-8"))
    os.makedirs(destino, exist_ok=True)
    with open(os.path.join(destino, "Articulos_por_descargar_manualmente.txt"), "w", encoding="utf-8-sig") as f:
        f.write("ARTÍCULOS POR DESCARGAR MANUALMENTE\n" + "=" * 36 + "\n\n")
        if not pendientes:
            f.write("No hay artículos pendientes de descarga.\n")
        else:
            f.write("Pasaron el cribado, pero no se pudieron descargar automáticamente (CAPTCHA, verificación anti-robots o\n"
                    "acceso restringido). Si no están citados en el trabajo, son opcionales.\n\n"
                    "Cómo descargarlos: abrir el enlace en Chrome o Edge con la sesión institucional iniciada, resolver la\n"
                    "verificación si aparece y usar el botón «Download PDF» del editor.\n\n")
            for i, p in enumerate(pendientes, 1):
                f.write(f"{i}. [{p.get('prioridad', 'Opcional')}]\n   {p['referencia']}\n   Enlace: {p.get('enlace', '')}\n"
                        f"   Nota: {p.get('nota', '')}\n\n")

    with open(os.path.join(destino, "LEEME.txt"), "w", encoding="utf-8-sig") as f:
        f.write(f"CARPETA DE EVIDENCIAS{(' – ' + titulo) if titulo else ''}\n{'=' * 70}\n\n")
        f.write(f"Articulos_PDF/                      {n_pdf} artículos citados en el trabajo, por búsqueda o parte:\n")
        for sub, n, _, _ in partes:
            f.write(f"  {sub}/  ({n})\n")
        f.write(f"Metadatos_RIS/                      Un .ris por búsqueda y Referencias_consolidadas.ris ({len(ris_todos)}\n"
                f"                                    referencias sin duplicados) para Zotero, Mendeley o EndNote.\n"
                f"Matrices_Revision_Bibliografica/    Matrices PRISMA en Excel (M1 búsqueda, M2 cribado, M3 extracción,\n"
                f"                                    M4 temática) y diagramas PRISMA 2020.\n"
                f"  Resultados_busqueda_Scopus/       Registros completos de cada búsqueda (CSV).\n")
        if extra:
            f.write("Anexos/                             " + ", ".join(os.path.basename(e) for e in extra) + "\n")
        f.write(f"Articulos_leidos_no_seleccionados/  {n_no_sel} artículos leídos completos que no se citaron (motivo en las matrices).\n"
                f"Articulos_por_descargar_manualmente.txt   {len(pendientes)} artículo(s) no recuperado(s).\n\n"
                "Importar en Zotero: Archivo → Importar → Metadatos_RIS/Referencias_consolidadas.ris.\n"
                "Compartir en Drive: subir la carpeta completa → Compartir → «Cualquier persona con el enlace» (Lector) →\n"
                "Copiar enlace → pegarlo en el documento donde lo pida la guía.\n\n"
                f"{MARCA}\n")
    return {"destino": destino, "pdf_citados": n_pdf, "leidos_no_seleccionados": n_no_sel,
            "referencias_ris": len(ris_todos), "pendientes": len(pendientes), "partes": partes}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("literatura")
    ap.add_argument("destino")
    ap.add_argument("--titulo", default="")
    ap.add_argument("--extra", nargs="*", default=[])
    a = ap.parse_args()
    r = armar(a.literatura, a.destino, a.titulo, a.extra)
    print(f"OK {r['destino']}")
    print(f"   {r['pdf_citados']} PDF citados · {r['leidos_no_seleccionados']} leídos no seleccionados · "
          f"{r['referencias_ris']} referencias en el RIS consolidado · {r['pendientes']} pendientes")
    for sub, n, ns, nris in r["partes"]:
        aviso = "" if n == nris else f"  ← ¡{n} PDF pero {nris} registros RIS!"
        print(f"   {sub}: {n} PDF, {ns} no seleccionados, {nris} RIS{aviso}")


if __name__ == "__main__":
    main()
