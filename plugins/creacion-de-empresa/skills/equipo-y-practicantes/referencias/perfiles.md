# Perfiles de práctica

Cada perfil dice qué parte de las plataformas de la empresa alimenta el practicante, qué produce por actividad y qué verificaciones están permitidas.

| Perfil | Aporta a | Producto típico por actividad | Verificaciones permitidas |
|---|---|---|---|
| **Ciberseguridad** | Seguridad de ERP, CRM y sitio | Inventario de activos, matriz de riesgos, revisión de cabeceras y TLS, revisión de dependencias (`npm audit`), política de contraseñas, plan de respuesta a incidentes | Solo pasivas (DNS, cabeceras HTTP, certificado TLS, lectura de código, `npm audit`, pruebas) sobre activos propios |
| **Soporte y mesa de ayuda** | Operación y atención de usuarios | Catálogo de incidentes, base de conocimiento, procedimientos, modelo de mesa de ayuda con datos de prueba | Laboratorio en Docker (GLPI u otro) con datos sintéticos |
| **Redes e infraestructura** | Conectividad y servidores | Inventario de red, diseño propuesto rotulado como tal, mediciones reales, guías de cableado y respaldo | Laboratorio en Docker; el trabajo físico lo aporta el estudiante |
| **Desarrollo del ERP** | Finanzas, compras, inventario, facturación | Mapa de procesos, historias de usuario con criterios Dado/Cuando/Entonces, modelo de datos, contrato de API, un módulo pequeño de extremo a extremo | Pruebas automáticas; el código vive en el repositorio de la empresa (rama + pull request) |
| **CRM comercial** | Ventas y atención al cliente | Embudo, campos y etapas, reglas de seguimiento, integración con WhatsApp y correo | Datos de prueba; nada de clientes reales |
| **Sistema académico inteligente** | Gestión académica con IA | Modelos de datos, flujos, evaluación de resultados reales | Datos seudonimizados |

## Estructura de un perfil (para crear uno nuevo)
1. Aporte a las plataformas y pre-lectura (máximo un día).
2. Tabla: actividad del cronograma → producto reutilizable → fuentes reales y verificaciones permitidas.
3. Reglas específicas: qué **no** se puede presentar como realizado sin evidencia del estudiante; qué datos deben ser sintéticos.
4. Calidad mínima: criterios medibles (severidades, criterios de aceptación, formato de hallazgos).
5. Requisitos que aporta a las plataformas.

## Carpeta de evidencias (si la universidad la exige)
Subcarpetas: `01. Cronograma` · `02. Actividades realizadas` · `03. Productos o recursos elaborados` · `04. Evidencia fotográfica` · `05. Reuniones y comunicaciones` · `06. Informes` · `07. Certificado`, más un índice general. **Ninguna carpeta vacía**: lo que falte lleva un `LEEME.txt` que dice qué debe aportarse y quién. Nombres cortos (la ruta total no debe superar 259 caracteres). El enlace compartido se prueba en ventana de incógnito antes de pegarlo en la tarea.
