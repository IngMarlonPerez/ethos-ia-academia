---
description: 'Muestra en qué etapa va la empresa, los plazos que corren y las inconsistencias detectadas en el expediente'
argument-hint: "[ruta de empresa.json]"
allowed-tools: Bash, Read, Glob
---

Muestra el estado de la empresa. Usa `$ARGUMENTS` como ruta de `empresa.json`; si está vacío, búscalo en la carpeta actual.

1. Tablero de etapas:
   `python "${CLAUDE_PLUGIN_ROOT}/skills/asistente-creacion-empresa/scripts/tablero.py" ver --empresa "<empresa.json>"`
2. Si `constitucion.inscripcion_fecha` está llena, el calendario de plazos con la fecha de hoy:
   `python "${CLAUDE_PLUGIN_ROOT}/skills/obligaciones-post-constitucion/scripts/calendario_plazos.py" --inscripcion <fecha> --ruc <ruc>`
3. El control de coherencia, sin modificar nada:
   `python "${CLAUDE_PLUGIN_ROOT}/skills/verificar-expediente/scripts/verificar_expediente.py" --empresa "<empresa.json>" --carpeta "<carpeta del expediente>"`
4. Resume en pocas líneas: etapa actual, **plazos vencidos o a menos de 7 días**, hallazgos de coherencia y la próxima acción con su skill. Destaca lo que solo la usuaria puede hacer (firmar, pagar, presentar en el portal).
