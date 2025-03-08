from typing import Dict, Any, Optional
import json
import os
import logging
from datetime import datetime

class ModelVersionManager:
    """
    Manages compatibility and versioning for Language Models (LLMs).
    Tracks model versions, capabilities, and compatibility.
    """
    
    def __init__(self, config_path: str = 'model_versions.json'):
        """
        Initialize ModelVersionManager.
        
        :param config_path: Path to store model version configurations
        """
        self.config_path = os.path.join('config', config_path)
        self.logger = logging.getLogger(__name__)
        self.model_versions: Dict[str, Dict[str, Any]] = self._load_versions()
    
    def _load_versions(self) -> Dict[str, Dict[str, Any]]:
        """
        Load existing model versions from configuration file.
        
        :return: Dictionary of model versions
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Error loading model versions: {e}")
            return {}
    
    def _save_versions(self):
        """
        Save current model versions to configuration file.
        """
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.model_versions, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving model versions: {e}")
    
    def register_model(
        self, 
        model_name: str, 
        version: str, 
        capabilities: Dict[str, Any] = None
    ):
        """
        Register a new model version with its capabilities.
        
        :param model_name: Name of the language model
        :param version: Version identifier
        :param capabilities: Dictionary of model capabilities
        """
        if capabilities is None:
            capabilities = {}
        
        self.model_versions[model_name] = {
            'version': version,
            'capabilities': capabilities,
            'registered_at': datetime.now().isoformat()
        }
        self._save_versions()
        self.logger.info(f"Registered model {model_name} version {version}")
    
    def get_model_version(self, model_name: str) -> Optional[str]:
        """
        Retrieve the current version of a model.
        
        :param model_name: Name of the language model
        :return: Model version or None if not found
        """
        model_info = self.model_versions.get(model_name)
        return model_info['version'] if model_info else None
    
    def check_compatibility(
        self, 
        model_name: str, 
        required_capabilities: Dict[str, Any]
    ) -> bool:
        """
        Check if a model meets the required capabilities.
        
        :param model_name: Name of the language model
        :param required_capabilities: Dictionary of required capabilities
        :return: Boolean indicating compatibility
        """
        model_info = self.model_versions.get(model_name)
        if not model_info:
            self.logger.warning(f"Model {model_name} not registered")
            return False
        
        model_capabilities = model_info.get('capabilities', {})
        
        for cap, req_value in required_capabilities.items():
            if cap not in model_capabilities or model_capabilities[cap] < req_value:
                self.logger.warning(
                    f"Incompatible capability for {model_name}: {cap}"
                )
                return False
        
        return True
    
    def list_compatible_models(
        self, 
        required_capabilities: Dict[str, Any]
    ) -> List[str]:
        """
        Find all models compatible with given capabilities.
        
        :param required_capabilities: Dictionary of required capabilities
        :return: List of compatible model names
        """
        compatible_models = []
        for model_name in self.model_versions:
            if self.check_compatibility(model_name, required_capabilities):
                compatible_models.append(model_name)
        
        return compatible_models
    
    def update_model_capabilities(
        self, 
        model_name: str, 
        new_capabilities: Dict[str, Any]
    ):
        """
        Update capabilities for an existing model.
        
        :param model_name: Name of the language model
        :param new_capabilities: Dictionary of new capabilities
        """
        if model_name not in self.model_versions:
            self.logger.error(f"Model {model_name} not registered")
            return
        
        self.model_versions[model_name]['capabilities'].update(new_capabilities)
        self._save_versions()
        self.logger.info(f"Updated capabilities for {model_name}")
