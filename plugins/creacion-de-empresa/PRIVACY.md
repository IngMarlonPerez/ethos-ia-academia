# Privacidad

El plugin **no envía datos a ningún servicio**. Todo lo que genera (documentos, TXT, logos, calendarios) queda en las carpetas que tú indicas, en tu equipo.

- `empresa.json` contiene cédulas y datos personales: se queda local. `iniciar_empresa.py` agrega al `.gitignore` del expediente `empresa.json`, la carpeta de firma electrónica, `*.p12`, `*.pfx` y `.env*`.
- Las skills **nunca** piden ni escriben contraseñas, claves del SRI o de la Superintendencia, ni tokens. Las claves y las firmas electrónicas las usa la persona titular en los portales.
- `verificar_expediente.py` lee los archivos de la carpeta que le indiques y muestra los hallazgos en pantalla; no copia ni transmite su contenido.
- Las acciones hacia afuera (presentar un trámite, firmar, pagar, publicar un sitio, subir a GitHub o a Drive, escribir a terceros) se preparan y se confirman con la persona antes de ejecutarse.
- Las búsquedas web que pueden hacer las skills (por ejemplo, para confirmar precios o contactos de contadores) no incluyen datos personales de la empresa.
