"""Genera los recorridos guiados de CodeTour (.tours/*.tour) desde un JSON y los valida contra el código.

Cada paso se ubica por patrón (expresión regular sin «^»), no por número de línea: los recorridos siguen
funcionando aunque el código cambie. El script falla si un patrón no existe, y avisa si la primera
coincidencia sin anclar no es la misma línea que la coincidencia anclada.

JSON de entrada (lista de recorridos, en orden):
    [{"id": "01-arquitectura", "titulo": "1 · Arquitectura", "descripcion": "…",
      "pasos": [{"archivo": "docker-compose.yml", "patron": "^  gateway:", "titulo": "API Gateway",
                 "nota": "Nginx es el único punto de entrada…"}]}]

    python gen_codetour.py recorridos.json --repo ruta/del/repositorio
"""
import argparse
import json
import re
import sys
from pathlib import Path


def linea(texto: str, pos: int) -> int:
    return texto[:pos].count("\n") + 1


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()
    repo = Path(args.repo)
    tours = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    (repo / ".tours").mkdir(exist_ok=True)
    errores = 0
    for i, t in enumerate(tours):
        pasos = []
        for p in t["pasos"]:
            ruta = repo / p["archivo"]
            if not ruta.exists():
                print(f"ERROR {t['id']}: no existe {p['archivo']}"); errores += 1; continue
            texto = ruta.read_text(encoding="utf-8")
            anclado = re.search(p["patron"], texto, re.M)
            if not anclado:
                print(f"ERROR {t['id']}: el patrón {p['patron']!r} no aparece en {p['archivo']}"); errores += 1; continue
            libre = p["patron"].lstrip("^")
            if linea(texto, re.search(libre, texto).start()) != linea(texto, anclado.start()):
                print(f"ERROR {t['id']}: sin «^», {libre!r} coincide antes en {p['archivo']}; haga el patrón más específico")
                errores += 1; continue
            pasos.append({"file": p["archivo"], "pattern": libre, "title": p["titulo"], "description": p["nota"]})
        tour = {"$schema": "https://aka.ms/codetour-schema", "title": t["titulo"], "description": t.get("descripcion", ""),
                "isPrimary": i == 0, "steps": pasos}
        if i + 1 < len(tours):
            tour["nextTour"] = tours[i + 1]["titulo"]
        (repo / ".tours" / f"{t['id']}.tour").write_text(json.dumps(tour, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{t['id']}: {len(pasos)} pasos")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
