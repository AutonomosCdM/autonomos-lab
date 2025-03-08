import logging
from typing import Dict, Any, Optional
import json
import os
import copy
import uuid

class ConfigIsolation:
    """
    Manages configuration isolation for different tenants.
    Provides methods for creating, retrieving, and managing tenant-specific configurations.
    """
    
    def __init__(self, config_base_dir: str = 'config/tenant_configs'):
        """
        Initialize ConfigIsolation.
        
        :param config_base_dir: Base directory for storing tenant configurations
        """
        self.config_base_dir = config_base_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure base configuration directory exists
        os.makedirs(config_base_dir, exist_ok=True)
    
    def create_tenant_config(
        self, 
        tenant_id: str, 
        base_config: Optional[Dict[str, Any]] = None, 
        overrides: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a tenant-specific configuration.
        
        :param tenant_id: Unique tenant identifier
        :param base_config: Base configuration to start from
        :param overrides: Tenant-specific configuration overrides
        :return: Boolean indicating successful config creation
        """
        try:
            # Start with a deep copy of base configuration or empty dict
            tenant_config = copy.deepcopy(base_config) if base_config else {}
            
            # Apply tenant-specific overrides
            if overrides:
                self._deep_update(tenant_config, overrides)
            
            # Add tenant-specific metadata
            tenant_config['tenant_id'] = tenant_id
            tenant_config['config_id'] = str(uuid.uuid4())
            tenant_config['created_at'] = datetime.now().isoformat()
            
            # Ensure tenant config directory exists
            tenant_config_dir = os.path.join(self.config_base_dir, tenant_id)
            os.makedirs(tenant_config_dir, exist_ok=True)
            
            # Save configuration
            config_path = os.path.join(tenant_config_dir, 'config.json')
            with open(config_path, 'w') as f:
                json.dump(tenant_config, f, indent=2)
            
            self.logger.info(f"Created configuration for tenant {tenant_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error creating tenant configuration: {e}")
            return False
    
    def get_tenant_config(
        self, 
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve tenant-specific configuration.
        
        :param tenant_id: Unique tenant identifier
        :return: Tenant configuration or None
        """
        try:
            config_path = os.path.join(self.config_base_dir, tenant_id, 'config.json')
            
            if not os.path.exists(config_path):
                self.logger.warning(f"No configuration found for tenant {tenant_id}")
                return None
            
            with open(config_path, 'r') as f:
                return json.load(f)
        
        except Exception as e:
            self.logger.error(f"Error retrieving tenant configuration: {e}")
            return None
    
    def update_tenant_config(
        self, 
        tenant_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update tenant-specific configuration.
        
        :param tenant_id: Unique tenant identifier
        :param updates: Configuration updates to apply
        :return: Boolean indicating successful update
        """
        try:
            # Retrieve existing configuration
            current_config = self.get_tenant_config(tenant_id)
            
            if not current_config:
                self.logger.error(f"Cannot update config for non-existent tenant {tenant_id}")
                return False
            
            # Apply updates
            self._deep_update(current_config, updates)
            
            # Update modification timestamp
            current_config['updated_at'] = datetime.now().isoformat()
            
            # Save updated configuration
            config_path = os.path.join(self.config_base_dir, tenant_id, 'config.json')
            with open(config_path, 'w') as f:
                json.dump(current_config, f, indent=2)
            
            self.logger.info(f"Updated configuration for tenant {tenant_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error updating tenant configuration: {e}")
            return False
    
    def delete_tenant_config(
        self, 
        tenant_id: str
    ) -> bool:
        """
        Delete tenant-specific configuration.
        
        :param tenant_id: Unique tenant identifier
        :return: Boolean indicating successful deletion
        """
        try:
            tenant_config_dir = os.path.join(self.config_base_dir, tenant_id)
            
            if not os.path.exists(tenant_config_dir):
                self.logger.warning(f"No configuration found for tenant {tenant_id}")
                return False
            
            # Remove entire tenant configuration directory
            import shutil
            shutil.rmtree(tenant_config_dir)
            
            self.logger.info(f"Deleted configuration for tenant {tenant_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error deleting tenant configuration: {e}")
            return False
    
    def _deep_update(
        self, 
        original: Dict[str, Any], 
        updates: Dict[str, Any]
    ):
        """
        Recursively update a nested dictionary.
        
        :param original: Original dictionary to update
        :param updates: Dictionary with updates to apply
        """
        for key, value in updates.items():
            if isinstance(value, dict):
                # Recursively update nested dictionaries
                original[key] = self._deep_update(
                    original.get(key, {}), 
                    value
                )
            else:
                # Replace or add non-dictionary values
                original[key] = value
        
        return original
    
    def list_tenant_configs(
        self, 
        filter_criteria: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List tenant configurations with optional filtering.
        
        :param filter_criteria: Optional dictionary of filter conditions
        :return: List of tenant configurations
        """
        try:
            tenant_configs = []
            
            # Iterate through tenant config directories
            for tenant_id in os.listdir(self.config_base_dir):
                config = self.get_tenant_config(tenant_id)
                
                # Apply filtering if criteria provided
                if config and (not filter_criteria or all(
                    config.get(k) == v for k, v in filter_criteria.items()
                )):
                    tenant_configs.append(config)
            
            return tenant_configs
        
        except Exception as e:
            self.logger.error(f"Error listing tenant configurations: {e}")
            return []
