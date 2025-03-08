"""
Flujo de autorización OAuth para Google Workspace.
"""
import os
import json
import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

class GoogleOAuthFlow:
    """
    Implementación del flujo de autorización OAuth para Google Workspace.
    """
    
    def __init__(self, credentials_path=None, token_path=None, scopes=None):
        """
        Inicializar el flujo de autorización OAuth.
        
        Args:
            credentials_path (str, optional): Ruta al archivo de credenciales
            token_path (str, optional): Ruta al archivo de token
            scopes (list, optional): Lista de permisos requeridos
        """
        if not credentials_path:
            credentials_path = Path(__file__).parent / 'credentials.json'
        
        if not token_path:
            token_path = Path(__file__).parent / 'token.pickle'
        
        if not scopes:
            scopes = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/drive.readonly',
                'https://www.googleapis.com/auth/spreadsheets.readonly'
            ]
        
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.scopes = scopes
        self.creds = None
    
    def get_credentials(self):
        """
        Obtener credenciales OAuth válidas.
        Si no existen o están expiradas, inicia el flujo de autorización.
        
        Returns:
            google.oauth2.credentials.Credentials: Credenciales OAuth
        """
        # Verificar si ya tenemos un token guardado
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        # Si no hay credenciales válidas, obtenerlas
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Iniciar flujo de autorización
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), self.scopes)
                self.creds = flow.run_local_server(port=0)
            
            # Guardar las credenciales para la próxima vez
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)
        
        return self.creds
