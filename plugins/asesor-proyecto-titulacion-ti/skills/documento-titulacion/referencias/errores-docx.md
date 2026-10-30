# Errores ya vividos al generar el Word (y su corrección)

| Síntoma | Causa | Corrección (ya incluida en docx_titulacion.py) |
|---|---|---|
| La nueva referencia salió pegada al DOI de la referencia vecina | `deepcopy` del párrafo vecino copió también su hipervínculo | `insertar_referencia` borra todos los hijos del párrafo copiado salvo `w:pPr` |
| «Tabla 3» quedó al final de una página y la tabla en la siguiente | Leyendas sin `keep_with_next` | Leyenda, título e imagen con `keep_with_next`; encabezado de tabla repetido |
| El texto de instrucciones de la plantilla («Se refiere a…», «(La extensión de este apartado…)») quedó visible | El generador insertaba debajo sin borrar la guía | Borrar esos párrafos con `eliminar(buscar(doc, 'Se refiere a'))`; revisar el PDF |
| La sección 3.1 midió solo 2 páginas | Poco contenido | `verificar_coherencia.py` mide cada sección en el PDF; se amplió con la figura de la metodología, la tabla de control de calidad y la organización |
| Referencias y Anexos aparecían numerados («5. Referencias») | Numeración automática del estilo Heading 1 | `quitar_numeracion(buscar(doc, 'Referencias'))` |
| Una barra invertida en una ruta de Windows se convirtió en retorno de carro | Escribir archivos con heredoc de la shell (`\r` interpretado) | Escribir archivos con la herramienta Write o con Python usando `chr(92)`; no con heredoc |
| Cifras distintas entre Resumen y cuerpo | Texto escrito a mano en dos lugares | Las dos salen del mismo artefacto; el verificador compara ambas |
| «Tres corridas» en el texto cuando había cuatro | Un conteo escrito a mano | Contar desde los archivos (`len(corridas)`) |
| El índice mostraba números de página viejos | python-docx no actualiza campos | `docx_a_pdf.ps1` (Word COM) actualiza el índice y los campos antes de exportar |
| Cambios a mano de la usuaria perdidos al regenerar | Sobrescribir el `.docx` | El generador compara la **huella del texto** registrada (`huella_texto`); si cambió, se detiene y guarda una copia `_editado_a_mano` |
| El generador creía que el Word se había editado a mano justo después de exportar el PDF | Word vuelve a guardar el `.docx` al actualizar el índice, y el md5 cambia | Se compara la huella del texto (párrafos y tablas, sin la tabla de contenido), no el md5 del archivo |

## Revisión visual rápida del PDF
```python
import pymupdf
d = pymupdf.open('documento/Avance_2.pdf')
for i in range(40, 46):                         # páginas nuevas
    d[i].get_pixmap(dpi=70).save(f'rev_{i+1}.png')  # y mirarlas con la herramienta Read
```
