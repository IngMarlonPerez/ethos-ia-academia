# Estructura del repositorio por capas: evidencia y plantilla

## Evidencia (texto completo leído; usar en el ADR-000 del proyecto)
- **Puchala, Chhabra y Rathee (2022).** La jerarquía de directorios lleva información arquitectónica.
  - Agregarla a las dependencias estructurales mejora en promedio un 32 % la recuperación de la arquitectura (MoJoFM, p. 12).
  - La calidad de la jerarquía condiciona el resultado (pp. 13, 16).
  - Es un respaldo indirecto: no mide la comprensión humana.
  - Referencia: *International Journal of Information System Modeling and Design, 13*(1), 1–20. https://doi.org/10.4018/IJISMD.297060
- **Shakikhanli y Bilicki (2025).** En proyectos de código abierto, varios repositorios concentran más colaboración alta; en el repositorio único, la productividad depende más de la colaboración; los equipos pequeños colaboran más en ambas estructuras.
  - No hay pruebas de significancia.
  - Usarlo como **advertencia** (vigilar el reparto de contribuciones), no como aval del repositorio único.
  - Referencia: *Pollack Periodica, 20*(1), 33–38. https://doi.org/10.1556/606.2024.01123
  - El PDF «online first» pagina 1–6.
- **Hassan, Abdel-Fattah y Mohamed (2025).** Migrar a microservicios exige un esfuerzo y recursos considerables, y el éxito no está garantizado (p. 1). Lo demás (monolito modular, sistemas pequeños) lo citan de otros autores: citar la fuente primaria o «citado en».
  - Referencia: *Big Data and Cognitive Computing, 9*(10), 253. https://doi.org/10.3390/bdcc9100253

## Repositorios de referencia (software; verificar estrellas y licencia con `gh api repos/<dueño>/<repo>`)
| Repositorio | Qué aporta |
|---|---|
| fastapi/full-stack-fastapi-template | `backend/` y `frontend/` (React + Vite) como hermanos |
| drivendataorg/cookiecutter-data-science | Datos crudos no versionados, modelos, documentación y código separados |
| alan2207/bulletproof-react | Frontend por páginas, componentes, hooks, servicios y utilidades |

## Plantilla de estructura (proyecto con backend, frontend, base de datos y documento)
```
codigo_fuente/      frontend/ · backend/ (api → dominio → datos) · base_de_datos/ · scripts/
documentacion/      avances/ · generador_documentos/ (con lib/ copiada) · diagramas/ · figuras/ · matrices/
                    literatura/ (pdfs/ no se versiona) · decisiones/ (DT-*.json, adr/) · tecnica/ · auditoria/
datos/              README con cómo obtener los datasets externos (externos/ no se versiona)
(solo local)        _POR_REVISAR_ELIMINAR/ · ANEXO_USO_ETICO_IA/ · _MATERIAL_EXTERNO_NO_SUBIR/
```
Los nombres internos de los paquetes no se renombran si eso rompe imports. La correspondencia carpeta → capa se escribe en `codigo_fuente/README.md`.

## Matriz del ADR-000 (ejemplo de la tesis VicMar, puntajes de 1 a 5)
| Criterio (peso) | Repositorio único por capas | Varios repositorios | Estructura plana por avance |
|---|---|---|---|
| La arquitectura se reconoce en las carpetas (30 %) | 5 | 4 | 1 |
| Reproducibilidad código ↔ documento (25 %) | 5 | 2 | 3 |
| Costo de coordinación para 2 personas (20 %) | 5 | 2 | 4 |
| Separación publicable / privado (15 %) | 4 | 4 | 1 |
| Colaboración equitativa (10 %) | 3 | 4 | 3 |
| **Ponderado** | **4,65** | **3,10** | **2,30** |
