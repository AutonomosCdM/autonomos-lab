#!/usr/bin/env python3
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from agents.gcp_integration.src.gcp_integration.workspace_loader import WorkspaceLoader

def main():
    # Initialize WorkspaceLoader with mock readers for demonstration
    loader = WorkspaceLoader()
    
    # Mock readers are already set up in the test file
    from tests.test_google_workspace_integration import MockGoogleDocsReader, MockGoogleSheetsReader
    loader.docs_reader = MockGoogleDocsReader()
    loader.sheets_reader = MockGoogleSheetsReader()
    
    # Load documents
    print("=== Documentos Cargados ===")
    docs = loader.load_documents([
        'proyecto_investigacion', 
        'estrategia_hackathon'
    ])
    
    for doc in docs:
        print("\n--- Documento ---")
        print(f"ID: {doc['id']}")
        print(f"Título: {doc['metadata'].get('title', 'Sin título')}")
        print(f"Última Modificación: {doc['metadata'].get('last_modified', 'Desconocida')}")
        print(f"Autor: {doc['metadata'].get('author', 'Desconocido')}")
        print(f"Prioridad: {doc['priority']}")
        print("\nContenido:")
        print(doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content'])
        print(f"\nEtiquetas: {doc['metadata'].get('tags', [])}")
    
    # Load sheets
    print("\n\n=== Hojas de Cálculo Cargadas ===")
    sheets = loader.load_sheets([
        'metricas_proyecto', 
        'planificacion_hackathon'
    ])
    
    for sheet in sheets:
        print("\n--- Hoja de Cálculo ---")
        print(f"ID: {sheet['id']}")
        print(f"Nombre de Hoja: {sheet['metadata'].get('sheet_name', 'Sin nombre')}")
        print(f"Última Modificación: {sheet['metadata'].get('last_modified', 'Desconocida')}")
        print(f"Prioridad: {sheet['priority']}")
        print("\nContenido:")
        print(sheet['content'][:500] + "..." if len(sheet['content']) > 500 else sheet['content'])
        print(f"\nEtiquetas: {sheet['metadata'].get('tags', [])}")

if __name__ == "__main__":
    main()
