---
description: 'Empieza la creación de una empresa nueva: crea el expediente, empresa.json y el tablero de etapas, y propone la siguiente etapa'
argument-hint: "<razón social tentativa> [carpeta]"
allowed-tools: Bash, Read, Write, Edit, Glob, Skill
---

Inicia el proceso de creación de empresa para **$ARGUMENTS**.

1. Invoca la skill `creacion-de-empresa:asistente-creacion-empresa` y sigue su flujo.
2. Busca primero un `empresa.json` en la carpeta indicada o en la actual. Si existe, muestra el tablero y propón la siguiente etapa abierta; **no vuelvas a pedir datos que ya están ahí**.
3. Si no existe, invoca `creacion-de-empresa:iniciar-empresa`: lee los documentos que haya en la carpeta antes de preguntar y pide solo lo que falte (razón social y alternativas, nombre comercial, ciudad, representante, socios, a qué se dedica).
4. No inventes datos: el RUC, el expediente y el número de inscripción se llenan solo cuando la Superintendencia los entrega.
5. Termina diciendo cuál es la siguiente etapa, qué skill la resuelve y qué necesitas de la usuaria para empezarla. No envíes ni firmes nada.
