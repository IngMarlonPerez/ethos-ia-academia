# Política de privacidad – Asesor de Proyecto de Titulación de TI

Última actualización: 29 de septiembre de 2026.

## Qué datos maneja
- **Archivos de tu proyecto:** documentos, JSON de requerimientos y decisiones, diagramas, matrices y tu repositorio de código. Todo se lee y se escribe en tu computadora.
- **Credenciales de bases de datos:** `diccionario_datos.py` lee la cadena de conexión de una variable de entorno que defines tú. El plugin no la guarda ni la escribe en ningún archivo.
- **Datos personales de tus datasets:** `anonimizar.py` los seudonimiza localmente y no guarda la tabla de correspondencia. `buscar_secretos.py` muestra los hallazgos enmascarados.

## Servicios externos
El Asesor no tiene servidor propio ni consulta servicios externos por sí mismo.
- La búsqueda de literatura (Scopus, OpenAlex, Unpaywall) la hace el Asistente de Investigación Científica, con su propia política de privacidad.
- `evaluador-tecnologia` puede consultar la documentación oficial pública de una tecnología (solo lectura de páginas web).
- `renderizar_diagramas.py` usa mermaid-cli y el navegador instalado **localmente**.

## Qué NO hace
- No envía datos a la autora del plugin ni a terceros.
- No recopila estadísticas de uso.
- No escribe contraseñas en formularios ni inicia sesión por ti.
- No hace commits, push, publicaciones ni envíos sin tu autorización explícita.

## Contacto
Ethos IA (ETHOSLAB S.A.S.).
