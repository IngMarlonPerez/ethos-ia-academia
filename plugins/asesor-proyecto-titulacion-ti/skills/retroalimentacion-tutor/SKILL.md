---
name: retroalimentacion-tutor
description: 'Convierte las observaciones de los tutores en un plan de cambios trazable por sección y código, lo ejecuta y deja tabla de atención y registro de cambios. Usar cuando pegue o cuente observaciones o correcciones, o diga «me devolvieron el avance».'
---

# Retroalimentación del tutor (etapa 11)

Este es el flujo que se usó para el Avance 2 de la tesis VicMar Data AI. Las tutoras pidieron, entre otras cosas:
- RF y RNF por pieza, historias de usuario, protección de datos y métricas;
- CRISP-DM documentado, diccionario de datos, UML, código con resultados reales y demo.

## 1. Entender antes de planear
- Copia la retroalimentación **textual** en `retroalimentacion/Observaciones_Avance<N>.md`, con fecha y tutor.
- Separa cada frase en **requisitos atómicos**, con un ID (OBS-01…). Por ejemplo, «RF/RNF de las cuatro piezas» se vuelve un requisito por pieza.
- Ubica cada uno:
  - **sección** de la plantilla (del perfil);
  - **skill** que lo atiende;
  - **archivos** del código o del proyecto que toca.
- Lee el avance entregado y el código relacionado. Si una observación se atiende con algo que ya existe, dilo.

## 2. Diagnóstico documento ↔ código
Tabla «# | Qué afirma el documento (sección / autor citado) | Qué hace el código hoy | Acción». Aquí aparecen las incoherencias que el tutor todavía no vio. En la tesis VicMar hubo 14. Por ejemplo:
- «predice antes de que ocurra», pero el modelo solo detectaba;
- «SMOTE aplicado», pero SMOTE no estaba en el código;
- datos personales reales en el dataset de prueba.

Atenderlas evita la siguiente ronda de observaciones.

## 3. Decisiones de la usuaria
Pregunta **solo** lo que cambia el alcance o tiene costos distintos, con opciones y una recomendación. Por ejemplo:
- ¿rediseñar el modelo o documentar la limitación?
- ¿agregar un dataset real como segunda fuente?
- ¿documento nuevo o editar el entregado?

Lo técnico se decide con valores por defecto razonables, y se informa.

## 4. Plan por fases
En modo plan cuando es grande. Cada fase tiene:
- los archivos que toca;
- la skill que la ejecuta;
- su verificación.

Orden típico:
1. entorno reproducible;
2. privacidad;
3. datos;
4. modelo o componente;
5. evaluación;
6. demo;
7. documento;
8. matrices;
9. verificación final.

Antes de cambios grandes, **propón un respaldo** en una rama local con commit; hazlo solo con autorización y sin push.

## 5. Ejecutar y registrar
- Ejecuta cada fase con su skill.
- Llena `plantillas/atencion_observaciones.md` → `retroalimentacion/Atencion_Avance<N>.md`: «OBS | Observación | Dónde se atendió (sección / archivo) | Evidencia (tabla, figura, prueba, cifra) | Estado».
- Todo cambio en texto ya entregado va a `documento/Registro_cambios_Avance<N>.md` (skill `documento-titulacion`).
- Lo que deben hacer los autores (sesiones con usuarios, firmas, videos) va en «Pendientes para los autores», no se finge hecho.

## 6. Cerrar
- Corre `verificar-coherencia`.
- Envía a la usuaria el documento, el PDF, la tabla de atención y el registro.
- Marca la etapa 11 en el tablero con la nota «N observaciones atendidas, M pendientes de los autores».

**Control:**
- cada observación tiene su cambio, su lugar y su evidencia, o una justificación escrita de por qué no se atendió;
- no hay cambios silenciosos: todo está en el registro.
