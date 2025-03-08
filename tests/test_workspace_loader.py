import pytest
import numpy as np

from agents.gcp_integration.src.gcp_integration.workspace_loader import WorkspaceLoader, ContextCompressor

class MockGoogleDocsReader:
    def __init__(self, credentials=None):
        self.credentials = credentials

    def load_data(self, document_id):
        class MockDocument:
            def __init__(self, text, metadata):
                self.text = text
                self.metadata = metadata
        
        mock_docs = {
            'doc1': MockDocument(
                "Este es un documento urgente sobre un proyecto crítico.",
                {'title': 'Proyecto Urgente', 'last_modified': '2025-03-08'}
            ),
            'doc2': MockDocument(
                "Informe de reunión mensual con detalles de seguimiento.",
                {'title': 'Reunión Mensual', 'last_modified': '2025-03-07'}
            ),
            'doc3': MockDocument(
                "Documento informativo sin prioridad específica.",
                {'title': 'Documento Informativo', 'last_modified': '2025-03-06'}
            )
        }
        return [mock_docs[document_id]]

class MockGoogleSheetsReader:
    def __init__(self, credentials=None):
        self.credentials = credentials

    def load_data(self, spreadsheet_id):
        class MockSheet:
            def __init__(self, text, metadata):
                self.text = text
                self.metadata = metadata
        
        mock_sheets = {
            'sheet1': MockSheet(
                "Datos financieros importantes para el proyecto.",
                {'sheet_name': 'Finanzas', 'last_modified': '2025-03-08'}
            ),
            'sheet2': MockSheet(
                "Seguimiento de tareas y progreso del equipo.",
                {'sheet_name': 'Tareas', 'last_modified': '2025-03-07'}
            )
        }
        return [mock_sheets[spreadsheet_id]]

class MockOAuthFlow:
    def get_credentials(self):
        return None

@pytest.fixture
def workspace_loader():
    loader = WorkspaceLoader()
    # Replace actual readers with mock readers
    loader.docs_reader = MockGoogleDocsReader()
    loader.sheets_reader = MockGoogleSheetsReader()
    loader.oauth_flow = MockOAuthFlow()
    return loader

def test_document_loading(workspace_loader):
    """Test loading of Google Documents"""
    docs = workspace_loader.load_documents(['doc1', 'doc2', 'doc3'])
    
    assert len(docs) == 3
    assert all('id' in doc for doc in docs)
    assert all('content' in doc for doc in docs)
    assert all('metadata' in doc for doc in docs)
    assert all('priority' in doc for doc in docs)

def test_sheet_loading(workspace_loader):
    """Test loading of Google Sheets"""
    sheets = workspace_loader.load_sheets(['sheet1', 'sheet2'])
    
    assert len(sheets) == 2
    assert all('id' in sheet for sheet in sheets)
    assert all('content' in sheet for sheet in sheets)
    assert all('metadata' in sheet for sheet in sheets)
    assert all('priority' in sheet for sheet in sheets)

def test_document_priority_classification(workspace_loader):
    """Test priority classification of documents"""
    docs = workspace_loader.load_documents(['doc1', 'doc2', 'doc3'])
    
    # Check priority classification
    assert docs[0]['priority'] == 'Alta'  # Urgent document
    assert docs[1]['priority'] == 'Media'  # Meeting report
    assert docs[2]['priority'] == 'Baja'  # Informative document

def test_context_compression():
    """Test context compression mechanism"""
    documents = [
        "Este es un documento muy largo con mucha información detallada sobre un proyecto importante.",
        "Otro documento con información relevante pero menos crítica.",
        "Un documento corto con detalles complementarios."
    ]
    
    compressed_docs = ContextCompressor.compress_context(documents, max_tokens=50)
    
    assert len(compressed_docs) > 0
    assert len(compressed_docs) <= len(documents)
    
    # Verify token reduction
    def count_tokens(text):
        return len(text.split())
    
    total_original_tokens = sum(count_tokens(doc) for doc in documents)
    total_compressed_tokens = sum(count_tokens(doc) for doc in compressed_docs)
    
    assert total_compressed_tokens <= 50

def test_multilingual_priority_classification(workspace_loader):
    """Test priority classification with multilingual keywords"""
    test_docs = [
        {"metadata": {"subject": "Urgent Meeting about Critical Project"}},
        {"metadata": {"subject": "Reunión de seguimiento de proyecto"}},
        {"metadata": {"subject": "Información general"}}
    ]
    
    priorities = [
        workspace_loader._classify_document_priority(doc.get('metadata', {}).get('subject', '')) 
        for doc in test_docs
    ]
    
    assert priorities[0] == 'Alta'
    assert priorities[1] == 'Media'
    assert priorities[2] == 'Baja'
