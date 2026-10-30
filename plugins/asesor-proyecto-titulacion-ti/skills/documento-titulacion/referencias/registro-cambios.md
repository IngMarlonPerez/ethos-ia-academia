# Plantilla: Registro_cambios_Avance<N>.md

```markdown
# Registro de cambios del Avance <N>

El documento `Avance_<N>.docx` se generó con `_automatizacion/build_avance<N>.py` a partir de <la plantilla oficial | el Avance <N-1> entregado>, que NO se modificó.

## Secciones nuevas
| Sección | Qué contiene | Observación del tutor que atiende |
|---|---|---|
| 2.1 Requerimientos | Alternativas, actores, 10 HU, 16 RF, 11 RNF, métricas, trazabilidad | «Derivar RF/RNF de las cuatro piezas…» |

## Cambios en secciones ya entregadas
| Dónde | Antes | Ahora | Por qué |
|---|---|---|---|
| Resumen | «…ROC-AUC de 0,9999…» | «…ROC-AUC de 0,997 en validación temporal…» | El modelo se rediseñó (panel t → t+1); la cifra se lee del artefacto |

## Verificación
- verificar_coherencia.py: sin errores (fecha).
- Páginas por sección: … (salida del verificador).

## Pendientes para los autores
- [ ] Prueba con 3–5 usuarios según el protocolo de 2.1.
- [ ] Completar la tabla de actividades del Anexo y los enlaces de los videos.
- [ ] Revisar la redacción de las secciones nuevas antes de entregar.
```

Reglas: cada cambio a un texto ya entregado aparece en la tabla. Nada cambia en silencio.
