---
name: proteccion-datos
description: 'Protección de datos personales en la tesis de TI (LOPDP): inventario, RNF de privacidad, seudonimización y búsqueda de cédulas o claves en el repositorio. Usar con datos personales, LOPDP o anonimizar.'
---

# Protección de datos personales (etapas 3 y 8)

Surgió de un problema real de la tesis VicMar Data AI: el dataset de prueba tenía **cédulas y nombres reales** de un padrón público, con estados de «abandono» y «mora» inventados. Además, el sistema enviaba filas a proveedores externos de IA. Las tutoras pidieron «requisitos de protección de datos estudiantiles».

## 1. Inventario (etapa 3)
Lista qué datos personales toca el sistema, en qué tabla o archivo, con qué finalidad y quién los ve:
- identificadores: cédula, pasaporte, correo, teléfono;
- nombres;
- datos sensibles: salud, situación económica, rendimiento.

¿Salen del sistema? Hacia proveedores de IA, reportes o registros.

## 2. RNF de privacidad
Agrégalos a `requerimientos.json` → `rnf`, cada uno con su prueba:
- **minimización:** solo los datos necesarios para cada finalidad;
- **seudonimización** de los datos de prueba y de lo que se envía a terceros;
- **finalidad:** los datos se usan solo para el fin declarado;
- **ningún dato personal hacia servicios externos de IA** (se enmascara antes de enviar);
- **acceso por rol** (la pantalla muestra la cédula enmascarada, por ejemplo `******1234`);
- **sin secretos en el repositorio.**

Base legal: la del perfil (`ley_datos_personales`). En Ecuador es la LOPDP (Asamblea Nacional del Ecuador, 2021). Cítala en APA desde el perfil.

## 3. Datos de prueba seudonimizados
`python "${CLAUDE_PLUGIN_ROOT}/skills/proteccion-datos/scripts/anonimizar.py" --archivos alumnos.csv historial.csv --salida datos_anon/ --columna cedula=cedula_ec --columna apellidos=apellidos --columna nombres=nombres --genero genero`

Qué hace:
- usa semilla fija;
- el mismo original recibe el mismo seudónimo en todos los archivos, así que las tablas siguen unidas;
- la cédula ficticia tiene provincia «00», que nunca es real;
- **no guarda la tabla de correspondencia**;
- las demás columnas quedan idénticas, así que ninguna métrica cambia.

**Datos crudos:** se **mueven** fuera del repositorio, a una carpeta tipo `Documentos\<proyecto>_datos_personales_NO_COMPARTIR`, **con confirmación de la usuaria**. Nunca se borran. Si hay una tabla de staging con los crudos en la base de datos, también se elimina con confirmación.

## 4. Enmascarar antes de la IA externa
- Copia `${CLAUDE_PLUGIN_ROOT}/skills/proteccion-datos/plantillas/privacidad.py` al backend.
- Ajusta `_COLUMNAS_EXACTAS` a tu esquema.
- Llama a `enmascarar_filas(columns, rows)` **justo antes** de cada función que manda filas a un proveedor (la que arma el prompt para redactar resultados).
- El SQL o el esquema sin filas no llevan datos personales.
- Copia también `plantillas/test_privacidad.py`: su última prueba intercepta `requests.post` y comprueba que el cuerpo enviado no contiene ninguna cédula.
- En la narración generada por IA, verifica además que no aparezcan cifras que no están en los datos.

## 5. Secretos y datos en el repositorio
`python "${CLAUDE_PLUGIN_ROOT}/skills/proteccion-datos/scripts/buscar_secretos.py" <repo>`

Busca contraseñas, claves de API, tokens, claves privadas y cadenas de conexión con contraseña. También busca archivos con varias cédulas ecuatorianas válidas. Distingue lo que está en pruebas (valores que deben ser ficticios) y lo ignorado por git.

Cómo se corrige:
- las credenciales pasan a variables de entorno o a `.env`, que debe estar en `.gitignore`;
- los scripts leen la contraseña de la configuración y **fallan con un mensaje claro** si falta, nunca con un valor por defecto escrito en el código;
- la documentación del repositorio remite a `.env` en vez de mostrar la contraseña.

Si una contraseña real ya estuvo en un commit, dile a la usuaria que **la cambie**: borrarla del archivo no la borra del historial de git.

## 6. En el documento
- **RNF de privacidad** en 2.1.
- En 3.3: el código de `enmascarar_filas` explicado «a manera de manual» y el resultado de sus pruebas.
- En las limitaciones: qué datos son sintéticos o seudonimizados y por qué.

**Control:**
- `buscar_secretos.py` termina en 0 (sin secretos ni cédulas reales fuera de lo ignorado por git);
- las pruebas de enmascarado pasan;
- los datos crudos están fuera del repositorio;
- hay un RNF de privacidad con su prueba.
