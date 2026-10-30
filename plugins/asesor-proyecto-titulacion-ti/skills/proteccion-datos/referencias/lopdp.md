# Protección de datos personales: principios que se traducen en RNF

Resumen de trabajo; en el documento se cita la ley (perfil → `ley_datos_personales`) y no este archivo. Verifica el artículo exacto en el texto oficial antes de citar un número de artículo.

| Principio (LOPDP del Ecuador y equivalentes: RGPD, leyes latinoamericanas) | RNF verificable en el prototipo |
|---|---|
| Finalidad | Los datos se usan solo para la predicción o el análisis declarados; no hay exportación masiva de identificadores |
| Minimización | Las consultas y los envíos a terceros llevan solo las columnas necesarias; enmascarar_filas antes de un proveedor externo |
| Seudonimización / anonimización | Datos de prueba seudonimizados (anonimizar.py), sin tabla de correspondencia |
| Confidencialidad y control de acceso | Acceso por rol; aislamiento entre instituciones en el motor de base de datos; cédula enmascarada en pantalla |
| Seguridad del tratamiento | Sin secretos en el repositorio (buscar_secretos.py); usuario de solo lectura para consultas; fallar cerrado |
| Transferencia a terceros | Ningún dato personal a servicios de IA externos; si es inevitable, consentimiento y contrato |
| Responsabilidad proactiva | Pruebas automáticas de privacidad en la batería de pruebas; registro de cambios |

## Tesis con datos reales de una institución
- Pide autorización formal de la institución y, si aplica, del comité de ética.
- Trabaja con datos seudonimizados desde el origen: la institución entrega los datos ya sin identificadores.
- Declara en las limitaciones qué datos son reales, sintéticos o seudonimizados.
