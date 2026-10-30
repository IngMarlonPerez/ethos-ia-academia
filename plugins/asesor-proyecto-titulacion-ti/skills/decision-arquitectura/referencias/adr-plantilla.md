# Plantilla de ADR (Architecture Decision Record)

`matriz_decision.py --adr` genera el esqueleto en `decisiones/adr/ADR-NNN-<tema>.md`. Complétalo con estas secciones:

```markdown
# ADR-NNN: <decisión>

- Estado: Propuesta | Aceptada | Reemplazada por ADR-MMM · Fecha: AAAA-MM-DD
- Decisión: <opción elegida y versión>

## Contexto
Problema, fuerzas en juego (RNF, restricciones del equipo y del plazo, datos personales), qué pasa si no se decide.

## Criterios (origen → peso)
Escenarios o criterios, cada uno con el RNF, objetivo o restricción del que sale.

## Opciones evaluadas
Para cada una, puntaje por criterio con justificación y fuente.

## Resultado y sensibilidad
Tabla de puntajes ponderados; estable o inestable (con el desempate).

## Decisión y razón
Por qué la opción elegida responde mejor a los escenarios, con citas.

## Consecuencias
- Positivas: qué se gana.
- Negativas: qué se sacrifica y cómo se mitiga.
- Riesgos abiertos.

## Reglas verificables (solo para la arquitectura)
Lista de lo que el código debe cumplir → decisiones/arquitectura_reglas.json.
Excepciones aceptadas y su justificación.

## Verificación en el código
Resultado de verificar_reglas.py / verificar_coherencia.py con la fecha.
```

## Reglas
- Un ADR por decisión. No se borra: si cambia la decisión, se crea otro que lo reemplaza y el viejo cambia a «Reemplazada por…».
- El ADR va en el repositorio de código o en la carpeta del proyecto, y su resumen entra en las matrices (hoja «Decisiones»).
