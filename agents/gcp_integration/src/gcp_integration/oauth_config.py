import os
import json
from pathlib import Path

class GoogleOAuthConfig:
    """
    Gestión segura de credenciales OAuth para Google Workspace
    """
    def __init__(self, credentials_path=None):
        """
        Inicializar configuración de OAuth
        
        Args:
            credentials_path (str, optional): Ruta al archivo de credenciales
        """
        if not credentials_path:
            credentials_path = Path(__file__).parent / 'credentials.json'
        
        self.credentials_path = Path(credentials_path)
        self._validate_credentials()
    
    def _validate_credentials(self):
        """
        Validar la existencia y formato de las credenciales
        """
        if not self.credentials_path.exists():
            raise FileNotFoundError(f"Archivo de credenciales no encontrado: {self.credentials_path}")
        
        try:
            with open(self.credentials_path, 'r') as f:
                credentials = json.load(f)
            
            # Validaciones básicas
            required_keys = ['installed', 'client_id', 'client_secret']
            for key in required_keys:
                if key not in credentials.get('installed', {}) and key != 'installed':
                    raise ValueError(f"Credencial faltante: {key}")
                elif key == 'installed' and key not in credentials:
                    raise ValueError(f"Credencial faltante: {key}")
        
        except json.JSONDecodeError:
            raise ValueError("Formato de credenciales inválido")
    
    def get_credentials(self):
        """
        Obtener credenciales OAuth
        
        Returns:
            dict: Credenciales OAuth
        """
        with open(self.credentials_path, 'r') as f:
            return json.load(f)
    
    def get_client_id(self):
        """
        Obtener el Client ID
        
        Returns:
            str: Client ID de Google
        """
        return self.get_credentials()['installed']['client_id']
    
    def get_client_secret(self):
        """
        Obtener el Client Secret
        
        Returns:
            str: Client Secret de Google
        """
        return self.get_credentials()['installed']['client_secret']
