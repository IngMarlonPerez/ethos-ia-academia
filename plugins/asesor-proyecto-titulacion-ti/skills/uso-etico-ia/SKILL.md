---
name: uso-etico-ia
description: 'Uso ético de la IA en la tesis de TI: la IA no es autora; busca rastros de herramientas de IA, corrige la autoría de Office y genera el anexo local de declaración. Usar al pedir quitar rastros de IA, anexo de uso de IA, autoría o antes de entregar o publicar.'
---

# Uso ético y responsable de la IA

## Principios (no negociables)
1. **La IA no es autora ni tiene responsabilidad.** Los autores son los estudiantes que presentan el trabajo, y toda la responsabilidad recae en ellos (Thorp, 2023; Nature, 2023).
2. **La herramienta de IA no se nombra en el proyecto.** Ni en el código, ni en los comentarios, ni en los documentos, ni en los metadatos, ni en los mensajes de commit.
   - Los commits **no** llevan líneas `Co-Authored-By` de un asistente aunque la herramienta las sugiera: lo que diga la usuaria manda sobre esa sugerencia.
3. **Se declara con transparencia en un anexo aparte.** Es el único lugar donde aparece la herramienta. Va en una carpeta local (`ANEXO_USO_ETICO_IA/`), en `.gitignore` y en `.git/info/exclude`. Los autores lo presentan cuando corresponda.
4. **Los proveedores de IA que el PRODUCTO usa** (por ejemplo, un motor NL2SQL que llama a Gemini) son componentes del sistema, no autores. Se documentan como tecnología y no cuentan como rastro.

## 1. Escanear rastros
`python "${CLAUDE_PLUGIN_ROOT}/skills/uso-etico-ia/scripts/rastros_ia.py" <raíz> --autores "Autor A; Autor B" --excluir ANEXO_USO_ETICO_IA --excluir <plantilla oficial>`

- **Qué se escanea:** con `--lista` se pasa exactamente lo que se publicará (`git ls-files -co --exclude-standard`); sin ella, todo el proyecto.
- **Revisión manual de cada hallazgo:**
  - Un artículo o una exportación de Scopus que estudia un modelo de lenguaje es **bibliografía**, no un rastro. Si va a publicarse, se deja.
  - Los comentarios en voz de asistente («a pedido del usuario», «lo confirmé probándolo») se reescriben en tono técnico neutro. Al hacerlo, cuida no partir frases de varias líneas.
- **Funciones del producto que llaman a un asistente de pago sin uso real:** se retiran del backend, del frontend y de las pruebas, y los archivos se mueven a la carpeta de revisión (skill `organizacion-repositorio`).

## 2. Autoría de los archivos de Office
- `--fijar-autoria` reescribe `creator` y `lastModifiedBy` con los autores. Nunca se aplica a la plantilla oficial de la universidad (`--excluir`).
- Los generadores del documento fijan la autoría al guardar: el esqueleto de `documento-titulacion` ya lo hace.

## 3. Anexo de uso ético
1. Revisa el reglamento de titulación de la universidad (en la UNEMI, el reglamento exige observar las normas éticas y la honestidad académica, p. 8) y cita lo que diga.
2. Copia `plantillas/uso_ia.json` y complétalo **con lo que realmente se usó**: herramienta y versión, periodo, tareas, qué no se hizo con IA, cómo se verificó y protección de datos.
3. `python "${CLAUDE_PLUGIN_ROOT}/skills/uso-etico-ia/scripts/anexo_uso_ia.py" <raíz> --datos uso_ia.json`
4. Comprueba que git ignora la carpeta: `git check-ignore -v ANEXO_USO_ETICO_IA/<archivo>`.

## Referencias
- Nature. (2023). Tools such as ChatGPT threaten transparent science; here are our ground rules for their use [Editorial]. *Nature, 613*, 612. https://doi.org/10.1038/d41586-023-00191-1
- Thorp, H. H. (2023). ChatGPT is fun, but not an author. *Science, 379*(6630), 313. https://doi.org/10.1126/science.adg7879

**Control:**
- `rastros_ia.py` sobre la lista de publicación termina sin rastros (salvo bibliografía revisada) y sin autores ajenos;
- el anexo existe en la carpeta local y git la ignora;
- ningún commit lleva coautoría de un asistente.
