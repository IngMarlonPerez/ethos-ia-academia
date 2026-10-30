---
name: matriz-consistencia
description: 'Selecciona los artículos más pertinentes con matriz de consistencia (búsqueda, cribado con puntaje, extracción, temática) y PRISMA. Usar al pedir matriz de consistencia, cribado o seleccionar artículos.'
---

# Matriz de consistencia y selección de artículos

Archivo único de datos: `Evidencias_Drive/04_Scripts_Python/config_trabajo.py` (lo crea `iniciar-trabajo`). Plantilla comentada: `${CLAUDE_PLUGIN_ROOT}/plantillas_proyecto/config_trabajo.py`.

## Pasos
1. **Preguntas Q1…Qn** (una por punto de la consigna) y **criterios** (inclusión, exclusión, prioridad, excepciones de ventana temporal o idioma).
2. **Cribado por título** con reglas explícitas y códigos (`REGLAS`): E1 otra disciplina o aplicación contemporánea sin aporte, E2 revisión de literatura o bibliométrico, E5 caso docente, E8 tema no pertinente (por defecto). Es un cribado **asistido por reglas**: decirlo y recomendar revisar una muestra en la hoja `M2a_Cribado_titulo`.
3. **Candidatos** (`CAND`, clave = DOI en minúsculas): para cada uno, puntaje 0–2 por pregunta (0 no aporta · 1 aporte parcial · 2 aporte directo y sustentado), decisión (`I` incluido / `N` elegible no seleccionado), **nivel de lectura** (`PDF` leído · `RES` resumen · `MET` solo título y palabras clave), motivo, objetivo, hallazgo y aporte por pregunta.
4. **Selección**: el conjunto de mayor puntaje que cubra **todas** las Q con al menos un 2, sin redundancias; los de aporte parcial o redundante quedan como «Elegible – no seleccionado». Preferir inglés, acceso abierto y recientes sin descartar fundacionales.
5. **Leer antes de afirmar**: para citar una afirmación fuerte hay que haber leído el texto (delegar en el agente `lector-critico-economia`, uno por PDF, en paralelo si son 6 o más). Lo que solo se conoce por título o resumen se declara así.
6. **Generar**: `python -I "${CLAUDE_PLUGIN_ROOT}/scripts/matriz_consistencia.py" <proyecto>/Evidencias_Drive/04_Scripts_Python/config_trabajo.py` → `05_Base_datos/Matriz_consistencia.xlsx` y `prisma_conteos.json`. El script **falla** si un DOI de `CAND` no está en los CSV (typos de DOI) y calcula el flujo PRISMA a partir de los CSV completos.
7. **Controles**: cada Q con cobertura 2 en `M4b_Cruce`; cifras PRISMA coherentes (identificados − filtros − duplicados = cribados); decisiones y motivos en todas las filas.
8. Revisar con ella el Excel antes de redactar. Siguiente: `citas-apa-zotero` y `graficos-economia` (figura de flujo).
