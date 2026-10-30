# UML en Mermaid: cómo dibujar cada tipo (y errores ya vividos)

| UML | Sintaxis Mermaid | Notas |
|---|---|---|
| Secuencia | `sequenceDiagram` con `autonumber` | Participantes = archivos o servicios reales; `alt/else` para los caminos de error; `Note over` para las reglas de seguridad |
| Colaboración (comunicación) | `flowchart LR` con aristas numeradas `-- "1: mensaje" -->` | Mermaid no tiene este diagrama; la numeración muestra el orden |
| Casos de uso | `flowchart LR`: actores `A1(("Actor"))`, casos dentro de `subgraph SIS["Sistema"]` | `-. "incluye" .->` / `-. "extiende" .->` |
| Actividades con carriles | `flowchart LR` con un `subgraph` por carril y `direction TB` dentro | Enlaza los subgrafos entre sí (`C1 --> C2`) para que no queden gigantes |
| Estados | `stateDiagram-v2` con `direction LR` | Estados compuestos con `state "…" as X { … }` |
| Flujo de trabajo | `flowchart LR` con decisiones `{¿…?}` | Proceso de negocio de punta a punta |
| Entidad-relación / estrella | `erDiagram` | Cardinalidades `||--o{`; atributos con PK/FK |
| Arquitectura / despliegue | `flowchart LR` con subgrafos por capa o nodo | Protocolos en las aristas (HTTPS, SQL, MQTT) |

## Legibilidad
- A 6,2 pulgadas de ancho, un diagrama con relación ancho/alto mayor a ~3,2 queda plano e ilegible, y uno menor a ~0,35 queda como una tira vertical. El script avisa en ambos casos.
- **Clave:** Mermaid **ignora el `direction` de un subgrafo si alguno de sus nodos se enlaza con un nodo de otro subgrafo**. Para que se respete, enlaza los **subgrafos** entre sí (`CLI --> SRV`) y deja los enlaces entre nodos solo dentro de cada subgrafo. Así se obtienen bandas legibles, como en `uml_arquitectura_capas.mmd` y `metodologia_crisp_dm.mmd`.
- **Demasiado alto** (actividades con muchos pasos): `flowchart LR` afuera y subgrafos con `direction TB` adentro, uno por carril, enlazados entre subgrafos.
- **Demasiado plano** (muchos nodos en fila): `flowchart TB`, o agrupa en subgrafos.
- Texto de nodo corto; salto de línea con `<br/>`; nada de párrafos dentro de un nodo.
- De 12 a 18 nodos como máximo por diagrama. Si hay más, divídelo (p. ej. secuencia del login y secuencia de la consulta).

## Render (errores ya resueltos)
- `puppeteer.json` con la ruta de Edge o Chrome: el script lo escribe con `json.dumps`, porque escribirlo a mano rompía las barras invertidas de Windows.
- mmdc no acepta `-w` en todas las versiones: usa la escala `-s 2`.
- Sin Chromium descargado: `PUPPETEER_SKIP_DOWNLOAD=1` y el navegador del sistema.
- «Failed to launch the browser process» con Edge abierto: Edge le pasa la orden a la ventana que ya está abierta y se cierra. El script prefiere `chrome-headless-shell` de `~/.cache/puppeteer` si existe; si no, cierra Edge o pasa otro navegador con `--navegador`.
- Tildes y «ñ»: guarda el `.mmd` en UTF-8.
- Mira siempre el PNG resultante (herramienta Read) antes de insertarlo.
