---
name: arranque-un-comando
description: 'Deja la tesis de TI lista con npm run dev (Docker, datos de prueba, navegador), npm test, VS Code ordenado, commit de la autora y zip limpio para Drive. Usar ante «que arranque con un solo comando» o «el zip del código».'
---

# Arranque con un solo comando y entrega del código

El tribunal, la tutora o cualquier persona deben poder **descomprimir el código, ejecutar `npm run dev` y ver el sistema funcionando**, sin instalar Python, librerías ni bases de datos. El modelo es un proyecto de predicción (`C:\\TESIS_PREDICCION\\CODIGO_FUENTE`) y su versión aplicada en FlotaControl.

El agente `preparador-entrega-codigo` ejecuta esta skill de punta a punta.

## Por qué funciona (explicárselo así a la usuaria)
- `package.json` en la raíz **sin dependencias**: `"dev": "node scripts/dev.mjs"`.
- `scripts/dev.mjs` usa **solo módulos nativos de Node**, por eso no necesita `npm install`.
- Las dependencias se instalan **dentro de las imágenes** de Docker (cada Dockerfile), no en el equipo.
- `code <proyecto>.code-workspace` abre la carpeta ya ordenada; no hay magia en VS Code.

## 1. Leer antes de tocar (solo lectura)
- `docker-compose.yml`:
  - nombre de cada servicio y qué servicios tienen `HEALTHCHECK` (en el compose o en el Dockerfile);
  - puertos publicados;
  - servicio, usuario y nombre de la base.
- **Usuario de demostración:** cómo se crea (seed al arrancar) y en qué `.env.example` está.
- **Datos de prueba:** si existe un SQL ficticio con manifiesto de conteos, y qué tabla sirve de testigo de «base vacía».
- **Pruebas:** cómo las corre la integración continua (`.github/workflows/*.yml`), para repetir el mismo comando.
- `git status`, la rama, el autor configurado (`git config user.name/email`) y las etiquetas (`git describe --tags`).

Si el proyecto no usa Docker Compose, se avisa y no se aplica la plantilla tal cual.

## 2. Aplicar las plantillas (`plantillas/`)
1. **`package.json`** en la raíz, con nombre, descripción, autora y espacio de trabajo reales. Scripts: `dev`, `dev:logs`, `estado`, `logs`, `stop`, `test` y `codigo`.
   - **Nunca un script con `docker compose down -v`**, porque borra la base.
2. **`scripts/dev.mjs`**: solo se cambia el bloque «ADAPTAR AL PROYECTO» (servicios con salud, base, puertos, gateway, datos de prueba, `.env` del usuario y comando de pruebas). Si no hay gateway o datos de prueba, esas constantes van en `null`. El script ya resuelve:
   - abre Docker Desktop en Windows y espera hasta unos 3 minutos;
   - avisa de puertos ocupados por otro programa;
   - `up --build -d` y espera a que todo esté «healthy», con un límite de 5 minutos;
   - reinicia el gateway si arrancó antes que los servicios;
   - carga los datos de prueba **solo si la tabla testigo está vacía** y verifica los conteos;
   - muestra la URL y el usuario, y abre el navegador (`--sin-navegador` lo evita);
   - `--tests`: pruebas unitarias en contenedores desechables.
3. **`.vscode/tasks.json`** (Ctrl + Shift + B levanta el sistema). Si `.gitignore` excluye `.vscode/*`, se añade `!.vscode/tasks.json`.
4. En el `.code-workspace`, añadir `**/node_modules` a `files.exclude` y `search.exclude`.

**Lecciones ya resueltas en la plantilla (no reintroducirlas):**
- En Windows, `docker` pasa por `cmd`, y `cmd` toma el `|` como tubería. Por eso el formato de `docker compose ps` usa `;` y va entre comillas.
- Node 24 avisa (DEP0190) si con `shell: true` se pasan argumentos por separado. Por eso se pasa una sola cadena (`lineaDocker`).
- La base se consulta con `docker compose exec -T` y no se publica ningún puerto de la base de datos.

## 3. Verificar de verdad (sin tocar los datos de la autora)
1. `node --check scripts/dev.mjs`.
2. `node scripts/dev.mjs --sin-navegador` sobre la pila actual: debe decir que la base ya tiene datos y no tocarla, y la app y el gateway deben responder 200.
3. **Equipo nuevo simulado:**
   - `docker compose stop`, que conserva los datos;
   - `COMPOSE_PROJECT_NAME=<proyecto>_prueba node scripts/dev.mjs --sin-navegador`: debe cargar y verificar los datos de prueba, y el inicio de sesión debe responder 200;
   - después, `docker compose -p <proyecto>_prueba down -v` **solo sobre ese proyecto de prueba**. Antes se confirma que el volumen que se borra es el de prueba;
   - volver a levantar la pila de la autora y comprobar que sus datos siguen ahí.
4. `npm test` debe pasar. Se informa cuántas pruebas son unitarias y cuántas de integración quedan fuera, y por qué.

## 4. Documentación
- **README:** sección «Arranque con un solo comando» con los requisitos (Docker Desktop y Node 18+), la tabla de atajos y la advertencia sobre `down -v`. Se conserva el arranque manual con `docker compose`.
- **Manual técnico:** requisitos, instalación con `npm run dev` paso a paso y `npm test`.
- **Manual de usuario:** una línea sobre cómo encender el sistema. Se aprovecha para comprobar que los nombres de los botones coincidan con el código.
- Regenerar Word y PDF (Word por COM) y copiar los PDF a `docs/manuales/` del repositorio.
- **Guía del video:** el paso «antes de grabar» pasa a `npm run dev` y `npm run codigo`. Si la guía exige una etiqueta exacta en `git describe`, se ajusta a la nueva salida.

## 5. Limpieza, commit y entrega (solo con autorización explícita)
1. `uso-etico-ia/scripts/rastros_ia.py` sobre el repositorio y los manuales: el resultado debe ser cero. Metadatos de Office con la autora.
2. **Commit** con la autoría de la autora y **sin `Co-Authored-By`**. Mensaje en español, describiendo el cambio.
3. **Push:** si la cuenta activa de gh no es la de la autora (error 403), usar la sesión ya guardada de la autora solo para ese push:
   `GH_TOKEN=$(gh auth token -u <cuenta>) git push origin main`.
   No se cambia la cuenta activa ni se piden contraseñas.
4. **Zip limpio para Drive:**
   `git archive --format=zip --prefix=<repo>/ --add-file=<guía del video>.pdf -o <Drive>/04_Trabajo_practico/<repo>.zip HEAD`.
   - solo entra lo versionado: nada de `node_modules`, `.env`, cachés ni temporales;
   - se descomprime en el directorio temporal, se pasa `rastros_ia.py`, se comprueba que estén los `.env.example` y se ejecuta `node --check`;
   - se actualiza el `LEEME.txt` de la carpeta con cómo ejecutarlo.
5. **No se sube nada a Drive:** lo hace la usuaria.

## Ejemplo real
FlotaControl (una autora, octubre de 2026), commit `2b149df`.
- Seis contenedores.
- En la pila real conservó 12 vehículos.
- En la base vacía cargó 12 / 13 / 640 / 1330 / 96 filas, verificadas.
- `npm test`: 837 pruebas unitarias aprobadas.
- Zip de 369 archivos con la guía v3.
