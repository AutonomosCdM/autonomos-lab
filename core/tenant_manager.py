import logging
from typing import Dict, Any, Optional, List
import uuid
import json
import os
from datetime import datetime

class TenantManager:
    """
    Manages tenant spaces, configurations, and isolation.
    Provides methods for creating, managing, and tracking tenants.
    """
    
    def __init__(self, tenant_config_dir: str = 'config/tenants'):
        """
        Initialize TenantManager.
        
        :param tenant_config_dir: Directory to store tenant configurations
        """
        self.tenant_config_dir = tenant_config_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure tenant config directory exists
        os.makedirs(tenant_config_dir, exist_ok=True)
        
        # Load existing tenants
        self.tenants: Dict[str, Dict[str, Any]] = self._load_tenants()
    
    def _load_tenants(self) -> Dict[str, Dict[str, Any]]:
        """
        Load existing tenant configurations.
        
        :return: Dictionary of tenant configurations
        """
        try:
            tenants = {}
            for filename in os.listdir(self.tenant_config_dir):
                if filename.endswith('.json'):
                    tenant_id = filename.replace('.json', '')
                    with open(os.path.join(self.tenant_config_dir, filename), 'r') as f:
                        tenants[tenant_id] = json.load(f)
            return tenants
        except Exception as e:
            self.logger.error(f"Error loading tenant configurations: {e}")
            return {}
    
    def create_tenant(
        self, 
        name: str, 
        description: Optional[str] = None, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new tenant with unique identifier.
        
        :param name: Tenant name
        :param description: Optional tenant description
        :param metadata: Optional additional tenant metadata
        :return: Unique tenant ID
        """
        # Generate unique tenant ID
        tenant_id = str(uuid.uuid4())
        
        # Prepare tenant configuration
        tenant_config = {
            'id': tenant_id,
            'name': name,
            'description': description or '',
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'resources': {}
        }
        
        # Save tenant configuration
        try:
            config_path = os.path.join(self.tenant_config_dir, f'{tenant_id}.json')
            with open(config_path, 'w') as f:
                json.dump(tenant_config, f, indent=2)
            
            # Update in-memory tenants
            self.tenants[tenant_id] = tenant_config
            
            self.logger.info(f"Created tenant: {name} (ID: {tenant_id})")
            return tenant_id
        
        except Exception as e:
            self.logger.error(f"Error creating tenant {name}: {e}")
            raise
    
    def get_tenant(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve tenant configuration.
        
        :param tenant_id: Unique tenant identifier
        :return: Tenant configuration or None
        """
        return self.tenants.get(tenant_id)
    
    def update_tenant(
        self, 
        tenant_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update tenant configuration.
        
        :param tenant_id: Unique tenant identifier
        :param updates: Dictionary of updates to apply
        :return: Boolean indicating successful update
        """
        if tenant_id not in self.tenants:
            self.logger.error(f"Tenant {tenant_id} not found")
            return False
        
        try:
            # Update tenant configuration
            tenant_config = self.tenants[tenant_id]
            tenant_config.update(updates)
            tenant_config['updated_at'] = datetime.now().isoformat()
            
            # Save updated configuration
            config_path = os.path.join(self.tenant_config_dir, f'{tenant_id}.json')
            with open(config_path, 'w') as f:
                json.dump(tenant_config, f, indent=2)
            
            self.logger.info(f"Updated tenant: {tenant_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error updating tenant {tenant_id}: {e}")
            return False
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """
        Delete a tenant and its configuration.
        
        :param tenant_id: Unique tenant identifier
        :return: Boolean indicating successful deletion
        """
        if tenant_id not in self.tenants:
            self.logger.error(f"Tenant {tenant_id} not found")
            return False
        
        try:
            # Remove configuration file
            config_path = os.path.join(self.tenant_config_dir, f'{tenant_id}.json')
            os.remove(config_path)
            
            # Remove from in-memory tenants
            del self.tenants[tenant_id]
            
            self.logger.info(f"Deleted tenant: {tenant_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error deleting tenant {tenant_id}: {e}")
            return False
    
    def list_tenants(
        self, 
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List tenants, optionally filtered by status.
        
        :param status: Optional status filter (e.g., 'active', 'suspended')
        :return: List of tenant configurations
        """
        if status:
            return [
                tenant for tenant in self.tenants.values() 
                if tenant.get('status') == status
            ]
        return list(self.tenants.values())
    
    def allocate_resource(
        self, 
        tenant_id: str, 
        resource_type: str, 
        resource_details: Dict[str, Any]
    ) -> bool:
        """
        Allocate a resource to a specific tenant.
        
        :param tenant_id: Unique tenant identifier
        :param resource_type: Type of resource (e.g., 'storage', 'compute')
        :param resource_details: Details of the resource allocation
        :return: Boolean indicating successful resource allocation
        """
        if tenant_id not in self.tenants:
            self.logger.error(f"Tenant {tenant_id} not found")
            return False
        
        try:
            # Generate unique resource ID
            resource_id = str(uuid.uuid4())
            
            # Add resource to tenant configuration
            tenant_config = self.tenants[tenant_id]
            if 'resources' not in tenant_config:
                tenant_config['resources'] = {}
            
            tenant_config['resources'][resource_id] = {
                'type': resource_type,
                'details': resource_details,
                'allocated_at': datetime.now().isoformat()
            }
            
            # Save updated configuration
            config_path = os.path.join(self.tenant_config_dir, f'{tenant_id}.json')
            with open(config_path, 'w') as f:
                json.dump(tenant_config, f, indent=2)
            
            self.logger.info(f"Allocated {resource_type} resource to tenant {tenant_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error allocating resource to tenant {tenant_id}: {e}")
            return False
