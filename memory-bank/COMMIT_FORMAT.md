## Buenas Prácticas

- Escribir commits atómicos (un cambio por commit)
- Mantener contexto técnico claro
- Evitar commits con cambios muy diversos
- Usar referencias cruzadas cuando sea posible

## Regla Crítica de Preservación Histórica

- PROHIBIDO BORRAR CONTENIDO HISTÓRICO DE DOCUMENTOS
  - Todos los documentos en memory-bank son registros de desarrollo
  - Las actualizaciones deben ser ADITIVAS, no destructivas
  - Conservar siempre el historial completo de cambios y decisiones
  - Si se requiere una corrección o actualización, añadir nuevas secciones
  - Mantener la integridad del registro de desarrollo como principio fundamental

## Timestamp de Última Actualización

**Fecha**: 3/7/2025
**Hora**: 18:26 (America/Santiago)

## Actualización: 8 de marzo de 2025

### Formato de Commits para Integración con Google Workspace

Para mantener la trazabilidad de los cambios relacionados con la integración de Google Workspace, se ha establecido el siguiente formato de commits:

```
gcp(servicio): descripción concisa del cambio

- Detalle 1
- Detalle 2
- Detalle 3

Refs: #issue-number
```

Donde:
- `gcp` es el prefijo para todos los cambios relacionados con Google Cloud Platform
- `servicio` puede ser: `gmail`, `docs`, `sheets`, `auth`, etc.
- La descripción debe ser clara y concisa
- Los detalles deben proporcionar información adicional relevante
- La referencia al issue es opcional pero recomendada

### Ejemplos:

```
gcp(gmail): implementar clasificación de prioridad de correos

- Añadir algoritmo de análisis de asunto
- Implementar sistema de puntuación
- Añadir tests unitarios

Refs: #42
```

```
gcp(auth): mejorar seguridad en rotación de tokens

- Implementar cifrado de tokens
- Añadir validación de expiración
- Crear mecanismo de renovación automática

Refs: #45
```

### Importancia de la Documentación Histórica

Se refuerza la importancia crítica de preservar el contexto histórico en todos los documentos. La integración con Google Workspace representa una expansión significativa del proyecto, y es esencial mantener un registro claro de todas las decisiones, implementaciones y evoluciones del sistema.

Cada cambio debe ser documentado de manera que:
1. Preserve el contexto histórico previo
2. Añada claramente la nueva información
3. Mantenga la trazabilidad de las decisiones
4. Facilite la comprensión de la evolución del proyecto
