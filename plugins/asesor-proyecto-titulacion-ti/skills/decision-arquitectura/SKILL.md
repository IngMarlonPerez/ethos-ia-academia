---
name: decision-arquitectura
description: 'Decide la arquitectura de la tesis de TI: compara 3 estilos con matriz ponderada, registra el ADR y verifica el código. Usar ante «¿microservicios o monolito?» o revisar que el código siga la arquitectura.'
---

# Decisión y verificación de la arquitectura (etapa 5)

La arquitectura se evalúa **siempre en tres lugares**:
1. **En la literatura:** qué arquitectura usaron los trabajos previos (columna «Arquitectura»).
2. **En el diseño:** al menos 3 estilos comparados.
3. **En el código:** lo implementado debe coincidir con lo declarado.

## 1. Estilos candidatos
Pertinentes al problema: el mínimo del perfil (UNEMI: 3), de `referencias/estilos-arquitectura.md`. Casi siempre entran:
- monolito en capas o modular;
- cliente-servidor desacoplado (SPA + API REST);
- microservicios.

Agrega orientada a eventos, serverless o hexagonal si el dominio lo sugiere.

## 2. Escenarios de atributos de calidad (ATAM ligero)
Con `referencias/atam-ligero.md`, convierte los RNF de la etapa 3 en 5 a 8 escenarios medibles («fuente → estímulo → respuesta → medida»), por ejemplo: «Si se agrega una segunda institución, se integra solo con un perfil de mapeo, sin cambiar el código». Incluye siempre:
- las restricciones del equipo y del plazo (p. ej. 2 personas, 6 meses);
- el costo de operar (un servidor institucional frente a un clúster).

Los escenarios pesan más que la moda: a una tesis de 2 personas los microservicios suelen costarle más de lo que le dan. **Eso se demuestra con los escenarios y la evidencia, no se da por supuesto.**

## 3. Evidencia
- Los conteos de la columna Arquitectura (`tabla_trabajos_previos.py --conteos`).
- Los artículos de la búsqueda de arquitectura de la etapa 2. Si falta evidencia, haz una búsqueda extra con `asistente-investigacion-cientifica:revision-sistematica`.
- Un agente `evaluador-tecnologia` por estilo, en paralelo, igual que en la selección tecnológica.

## 4. Matriz y ADR
Usa el mismo motor de la etapa 4, con `"tipo": "arquitectura"` en `decisiones/DT-NN_arquitectura.json`: los criterios son los escenarios y cada uno tiene su peso.

`python "${CLAUDE_PLUGIN_ROOT}/skills/seleccion-tecnologica/scripts/matriz_decision.py" decisiones/DT-NN_arquitectura.json --adr --tabla documento/tabla_arquitectura.json`

Completa el ADR con `referencias/adr-plantilla.md`: contexto, opciones, decisión, consecuencias y **reglas verificables**.

## 5. Reglas verificables
Copia `${CLAUDE_PLUGIN_ROOT}/skills/decision-arquitectura/plantillas/arquitectura_reglas.json` a `decisiones/arquitectura_reglas.json` y tradúcelo al estilo elegido:
- `estilo_esperado`;
- `desplegables` (mínimo y máximo);
- `componentes` (carpetas por capa) y `dependencias_prohibidas` (p. ej. el cliente no importa la capa de datos; el dominio no importa la API);
- `sin_bd_en_frontend`;
- `patrones_prohibidos` (SQL o contraseñas en el cliente);
- `excepciones` justificadas con el ADR.

## 6. Verificación en el código
Lanza el agente `auditor-arquitectura` con la ruta del repositorio (`titulacion.json` → `repositorio_codigo`) y las reglas. El agente ejecuta:

`python "${CLAUDE_PLUGIN_ROOT}/skills/decision-arquitectura/scripts/detectar_arquitectura.py" <repo> --md decisiones/arquitectura_detectada.md`
`python "${CLAUDE_PLUGIN_ROOT}/skills/decision-arquitectura/scripts/verificar_reglas.py" decisiones/arquitectura_reglas.json <repo>`

Después confirma leyendo los puntos de entrada y devuelve las violaciones con su archivo y línea. Por cada violación, una de dos:
- **se corrige el código** (con autorización de la usuaria);
- **se documenta como excepción** en el ADR y en `excepciones`, si es un falso positivo o una decisión consciente.

También informa las **dependencias declaradas que el código no importa**: son restos de una arquitectura anterior y conviene limpiarlas o justificarlas.

## 7. Para el documento (3.2 a)
- Estilo elegido, con la figura de arquitectura (skill `diseno-uml-datos`, `uml_arquitectura_*.mmd`).
- Descripción de cada capa o componente: responsabilidad, tecnología y rol dentro de la arquitectura.
- Tabla de comparación de estilos, escenarios de calidad, frase de sensibilidad y razón con citas.
- Mecanismos transversales: seguridad por capas, manejo de datos personales, configuración por entorno.
- Frase de verificación, por ejemplo: «La arquitectura implementada se verificó automáticamente sobre el repositorio: 2 desplegables, sin dependencias prohibidas».

**Control:**
- al menos 3 estilos comparados con escenarios y evidencia;
- el ADR tiene reglas verificables;
- `verificar_reglas.py` termina sin violaciones, o cada una está justificada como excepción en el ADR.
