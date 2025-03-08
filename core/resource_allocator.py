import logging
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime, timedelta

class ResourceAllocator:
    """
    Intelligent resource distribution and management system.
    Handles allocation, tracking, and optimization of computational resources.
    """
    
    def __init__(self, max_resources: Optional[Dict[str, int]] = None):
        """
        Initialize ResourceAllocator with logging and resource tracking.
        
        :param max_resources: Optional dictionary defining maximum resources per type
        """
        self.logger = logging.getLogger(__name__)
        self.resource_pool: Dict[str, Dict[str, Any]] = {}
        self.tenant_resource_map: Dict[str, List[str]] = {}
        
        # Default maximum resources if not specified
        self.max_resources = max_resources or {
            'compute': 100,  # CPU cores
            'memory': 1024,  # GB
            'storage': 10240,  # GB
            'network_bandwidth': 1000  # Mbps
        }
        
        # Current resource usage tracking
        self.current_resources: Dict[str, int] = {
            resource_type: 0 for resource_type in self.max_resources
        }
    
    def allocate_resource(
        self, 
        tenant_id: str, 
        resource_type: str, 
        resource_specs: Dict[str, Any]
    ) -> Optional[str]:
        """
        Allocate a resource to a specific tenant.
        
        :param tenant_id: Unique tenant identifier
        :param resource_type: Type of resource (e.g., 'compute', 'storage')
        :param resource_specs: Specifications for the resource
        :return: Unique resource identifier or None if allocation fails
        """
        try:
            # Validate resource type
            if resource_type not in self.max_resources:
                self.logger.error(f"Unsupported resource type: {resource_type}")
                return None
            
            # Check resource availability
            requested_amount = resource_specs.get('amount', 0)
            if not self._can_allocate_resource(resource_type, requested_amount):
                self.logger.warning(f"Insufficient {resource_type} resources")
                return None
            
            # Generate unique resource ID
            resource_id = str(uuid.uuid4())
            
            # Prepare resource allocation record
            resource_record = {
                'id': resource_id,
                'tenant_id': tenant_id,
                'type': resource_type,
                'specs': resource_specs,
                'allocated_at': datetime.now().isoformat(),
                'expiration': (
                    datetime.now() + timedelta(
                        hours=resource_specs.get('duration_hours', 24)
                    )
                ).isoformat()
            }
            
            # Store resource in pool
            self.resource_pool[resource_id] = resource_record
            
            # Track tenant's resources
            if tenant_id not in self.tenant_resource_map:
                self.tenant_resource_map[tenant_id] = []
            self.tenant_resource_map[tenant_id].append(resource_id)
            
            # Update current resource usage
            self.current_resources[resource_type] += requested_amount
            
            self.logger.info(
                f"Allocated {requested_amount} {resource_type} "
                f"to tenant {tenant_id} (Resource ID: {resource_id})"
            )
            
            return resource_id
        
        except Exception as e:
            self.logger.error(f"Resource allocation error: {e}")
            return None
    
    def _can_allocate_resource(
        self, 
        resource_type: str, 
        requested_amount: int
    ) -> bool:
        """
        Check if requested resource can be allocated.
        
        :param resource_type: Type of resource
        :param requested_amount: Amount of resource requested
        :return: Boolean indicating allocation possibility
        """
        current_usage = self.current_resources.get(resource_type, 0)
        max_allowed = self.max_resources.get(resource_type, 0)
        
        return current_usage + requested_amount <= max_allowed
    
    def release_resource(
        self, 
        resource_id: str
    ) -> bool:
        """
        Release a previously allocated resource.
        
        :param resource_id: Unique resource identifier
        :return: Boolean indicating successful resource release
        """
        try:
            # Retrieve resource record
            resource = self.resource_pool.get(resource_id)
            
            if not resource:
                self.logger.warning(f"Resource {resource_id} not found")
                return False
            
            # Update current resource usage
            resource_type = resource['type']
            requested_amount = resource['specs'].get('amount', 0)
            self.current_resources[resource_type] -= requested_amount
            
            # Remove from tenant's resource map
            tenant_id = resource['tenant_id']
            if tenant_id in self.tenant_resource_map:
                self.tenant_resource_map[tenant_id].remove(resource_id)
            
            # Remove from resource pool
            del self.resource_pool[resource_id]
            
            self.logger.info(
                f"Released {requested_amount} {resource_type} "
                f"for tenant {tenant_id} (Resource ID: {resource_id})"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Resource release error: {e}")
            return False
    
    def get_tenant_resources(
        self, 
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all resources allocated to a specific tenant.
        
        :param tenant_id: Unique tenant identifier
        :return: List of resource records
        """
        try:
            # Get resource IDs for the tenant
            resource_ids = self.tenant_resource_map.get(tenant_id, [])
            
            # Retrieve full resource records
            return [
                self.resource_pool[resource_id] 
                for resource_id in resource_ids 
                if resource_id in self.resource_pool
            ]
        
        except Exception as e:
            self.logger.error(f"Error retrieving tenant resources: {e}")
            return []
    
    def cleanup_expired_resources(self):
        """
        Automatically release resources that have expired.
        """
        try:
            now = datetime.now()
            expired_resources = [
                resource_id for resource_id, resource in self.resource_pool.items()
                if datetime.fromisoformat(resource['expiration']) <= now
            ]
            
            for resource_id in expired_resources:
                self.release_resource(resource_id)
            
            self.logger.info(f"Cleaned up {len(expired_resources)} expired resources")
        
        except Exception as e:
            self.logger.error(f"Resource cleanup error: {e}")
