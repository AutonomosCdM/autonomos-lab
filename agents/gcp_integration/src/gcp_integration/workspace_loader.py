from typing import List, Dict, Any, Optional
from pathlib import Path
import os
import json
import base64
from googleapiclient.discovery import build
from llama_index.readers.google import GoogleDocsReader, GoogleSheetsReader
from .oauth_config import GoogleOAuthConfig
from .oauth_flow import GoogleOAuthFlow

class GMailLoader:
    """
    Loader for Gmail emails with intelligent filtering and priority classification.
    """
    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialize the Gmail loader with OAuth 2.0 credentials.
        
        Args:
            credentials_path (str, optional): Path to OAuth credentials file
            token_path (str, optional): Path to OAuth token file
        """
        # Use OAuth configuration for handling credentials
        self.oauth_config = GoogleOAuthConfig(credentials_path)
        self.credentials_path = self.oauth_config.credentials_path
        
        # Initialize OAuth authorization flow
        self.oauth_flow = GoogleOAuthFlow(
            credentials_path=str(self.credentials_path),
            token_path=token_path
        )
    
    def load_emails(self, query: str = "in:inbox", max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Load emails with smart filtering.
        
        Args:
            query (str): Gmail search query
            max_results (int): Maximum number of emails to retrieve
        
        Returns:
            List[Dict[str, Any]]: List of processed emails
        """
        try:
            # Get valid OAuth credentials
            creds = self.oauth_flow.get_credentials()
            
            # Create Gmail service
            service = build('gmail', 'v1', credentials=creds)
            
            # Get list of messages
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print("No messages found.")
                return []
            
            # Process and prioritize emails
            processed_emails = []
            for message in messages:
                # Get message details
                msg = service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                # Extract headers
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown sender')
                
                # Extract content
                content = ""
                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            if 'data' in part['body']:
                                content = base64.urlsafe_b64decode(
                                    part['body']['data']).decode('utf-8')
                                break
                elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                    content = base64.urlsafe_b64decode(
                        msg['payload']['body']['data']).decode('utf-8')
                
                # Create email object
                email = {
                    "id": message['id'],
                    "subject": subject,
                    "sender": sender,
                    "content": content[:500],  # Limited excerpt
                    "metadata": {
                        "subject": subject,
                        "from": sender
                    },
                    "page_content": content
                }
                
                # Classify priority
                email["priority"] = self._classify_email_priority(email)
                
                processed_emails.append(email)
            
            return processed_emails
        except Exception as e:
            print(f"Error loading emails: {e}")
            return []
    
    def _classify_email_priority(self, email) -> str:
        """
        Classify email priority.
        
        Args:
            email: Email to classify
        
        Returns:
            str: Priority level
        """
        # Simple priority classification
        keywords_high = ["urgente", "importante", "inmediato", "critical", "urgent"]
        keywords_medium = ["reunión", "proyecto", "informe", "meeting", "report"]
        
        subject = email.get("metadata", {}).get("subject", "").lower()
        
        if any(keyword in subject for keyword in keywords_high):
            return "Alta"
        elif any(keyword in subject for keyword in keywords_medium):
            return "Media"
        else:
            return "Baja"

class WorkspaceLoader:
    """
    Integración de servicios de Google Workspace con capacidades de lectura limitada.
    Sigue los principios de mínimo privilegio y solo lectura.
    """
    
    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Inicializar el loader con credenciales OAuth 2.0.
        
        Args:
            credentials_path (str, optional): Ruta al archivo de credenciales OAuth
            token_path (str, optional): Ruta al archivo de token OAuth
        """
        # Usar configuración de OAuth para manejar credenciales
        self.oauth_config = GoogleOAuthConfig(credentials_path)
        self.credentials_path = self.oauth_config.credentials_path
        
        # Inicializar flujo de autorización OAuth
        self.oauth_flow = GoogleOAuthFlow(
            credentials_path=str(self.credentials_path),
            token_path=token_path
        )
    
    def load_gmail_emails(self, query: str = "in:inbox", max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Cargar correos electrónicos con filtrado inteligente.
        
        Args:
            query (str): Filtro de búsqueda de Gmail
            max_results (int): Número máximo de correos a recuperar
        
        Returns:
            List[Dict[str, Any]]: Lista de correos electrónicos procesados
        """
        try:
            # Obtener credenciales OAuth válidas
            creds = self.oauth_flow.get_credentials()
            
            # Crear servicio de Gmail
            service = build('gmail', 'v1', credentials=creds)
            
            # Obtener lista de mensajes
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print("No se encontraron mensajes.")
                return []
            
            # Procesar y priorizar correos
            processed_emails = []
            for message in messages:
                # Obtener detalles del mensaje
                msg = service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                # Extraer headers
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sin asunto')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Remitente desconocido')
                
                # Extraer contenido
                content = ""
                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            if 'data' in part['body']:
                                content = base64.urlsafe_b64decode(
                                    part['body']['data']).decode('utf-8')
                                break
                elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                    content = base64.urlsafe_b64decode(
                        msg['payload']['body']['data']).decode('utf-8')
                
                # Crear objeto de correo
                email = {
                    "id": message['id'],
                    "subject": subject,
                    "sender": sender,
                    "content": content[:500],  # Extracto limitado
                    "metadata": {
                        "subject": subject,
                        "from": sender
                    },
                    "page_content": content
                }
                
                # Clasificar prioridad
                email["priority"] = self._classify_email_priority(email)
                
                processed_emails.append(email)
            
            return processed_emails
        except Exception as e:
            print(f"Error al cargar correos: {e}")
            return []
    
    def _classify_email_priority(self, email) -> str:
        """
        Clasificar prioridad de correo electrónico.
        
        Args:
            email: Correo electrónico a clasificar
        
        Returns:
            str: Nivel de prioridad
        """
        # Implementación simple de clasificación de prioridad
        keywords_high = ["urgente", "importante", "inmediato", "critical", "urgent"]
        keywords_medium = ["reunión", "proyecto", "informe", "meeting", "report"]
        
        # Handle both dictionary and object-like inputs
        if hasattr(email, 'metadata'):
            subject = email.metadata.get('subject', '').lower()
        elif isinstance(email, dict):
            subject = email.get("metadata", {}).get("subject", "").lower()
        else:
            subject = ""
        
        if any(keyword in subject for keyword in keywords_high):
            return "Alta"
        elif any(keyword in subject for keyword in keywords_medium):
            return "Media"
        else:
            return "Baja"
