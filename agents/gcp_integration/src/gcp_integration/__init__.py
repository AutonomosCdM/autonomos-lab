"""
Módulo de integración con Google Workspace.
Proporciona funcionalidades para interactuar con Gmail, Google Docs y Google Sheets.
"""

from .workspace_loader import WorkspaceLoader
from .oauth_config import GoogleOAuthConfig
from .oauth_flow import GoogleOAuthFlow

__all__ = ["WorkspaceLoader", "GoogleOAuthConfig", "GoogleOAuthFlow"]
