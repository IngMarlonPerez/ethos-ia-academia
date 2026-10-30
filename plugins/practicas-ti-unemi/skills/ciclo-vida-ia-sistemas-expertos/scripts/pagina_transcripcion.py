# -*- coding: utf-8 -*-
"""
pagina_transcripcion.py — convierte una conversación (preguntas y respuestas) en una
página HTML limpia para capturarla como evidencia (luego se pasa a PNG con
evidencias-capturas/scripts/html_a_png.ps1).

IMPORTANTE: las respuestas deben ser las que el modelo da DE VERDAD en la sesión
(Claude responde cada caso en el chat y esas mismas respuestas se copian aquí).
Nunca se inventan ni se resumen después; la página se rotula como transcripción.

Uso:
    python -I pagina_transcripcion.py conversacion.json salida.html

conversacion.json:
{
  "titulo": "Casos simulados presentados a Claude",
  "subtitulo": "Claude (Anthropic) · 22/10/2026 · Ejercicio didáctico, no es un diagnóstico médico",
  "etiqueta_modelo": "Claude",
  "items": [{"etiqueta": "Caso 1", "pregunta": "...", "respuesta": "..."}],
  "nota": "Transcripción de las respuestas generadas por Claude en esta práctica."
}
"""
import html
import json
import sys
from pathlib import Path

CSS = """body{font-family:Segoe UI,Arial,sans-serif;background:#f7f5f2;color:#1f1f1f;margin:0;padding:28px 40px;width:1020px}
h1{font-size:20px;margin:0 0 4px}.meta{color:#666;font-size:13px;margin-bottom:18px}
.u{background:#e8e2d8;border-radius:12px;padding:12px 16px;margin:14px 0 8px;font-size:15px}
.a{background:#fff;border:1px solid #ddd;border-radius:12px;padding:12px 16px;font-size:15px;line-height:1.5}
.who{font-weight:600;font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:#a0522d;margin-bottom:4px}
.note{font-size:12px;color:#777;margin-top:18px}"""


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    d = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    e = html.escape
    modelo = d.get('etiqueta_modelo', 'Modelo')
    partes = [f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{e(d["titulo"])}</title><style>{CSS}</style></head><body>',
              f'<h1>{e(d["titulo"])}</h1><div class="meta">{e(d.get("subtitulo", ""))}</div>']
    for it in d['items']:
        partes.append(f'<div class="u"><div class="who" style="color:#555">{e(it["etiqueta"])} · pregunta</div>{e(it["pregunta"])}</div>')
        partes.append(f'<div class="a"><div class="who">{e(modelo)}</div>{e(it["respuesta"])}</div>')
    if d.get('nota'):
        partes.append(f'<div class="note">{e(d["nota"])}</div>')
    partes.append('</body></html>')
    Path(sys.argv[2]).write_text('\n'.join(partes), encoding='utf-8')
    print('HTML:', sys.argv[2])


if __name__ == '__main__':
    sys.exit(main())
