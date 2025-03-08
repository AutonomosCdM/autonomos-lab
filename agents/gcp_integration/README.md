# Google Workspace Integration

Módulo para integración con servicios de Google Workspace, incluyendo:

- Gmail
- Google Docs
- Google Sheets

## Características

- Autenticación OAuth 2.0
- Acceso de solo lectura
- Procesamiento inteligente de datos
- Clasificación de prioridad de correos
- Extracción de texto de documentos
- Análisis de datos tabulares

## Uso

```python
from agents.gcp_integration import WorkspaceLoader

# Inicializar con credenciales
workspace = WorkspaceLoader()

# Cargar correos
emails = workspace.load_gmail_emails(query="is:important", max_results=5)

# Cargar documentos
docs = workspace.load_google_docs(document_ids=["doc_id1", "doc_id2"])

# Cargar hojas de cálculo
sheets = workspace.load_google_sheets(spreadsheet_ids=["sheet_id1"])
```

## Seguridad

Este módulo sigue el principio de mínimo privilegio, solicitando únicamente permisos de lectura para los servicios de Google Workspace.
