from typing import Dict, Any, Optional, List
import json
import os
from core.error_handler import AgentError, ErrorSeverity
from core.config_manager import ConfigManager
import uuid
from dataclasses import dataclass, asdict, field
from enum import Enum, auto

class EndpointType(Enum):
    """
    Enumeration of different endpoint types.
    """
    REST = auto()
    GRAPHQL = auto()
    WEBSOCKET = auto()
    RPC = auto()
    GRPC = auto()

class EndpointRegistryError(AgentError):
    """Exception raised for endpoint registry-related errors."""
    pass

@dataclass
class Endpoint:
    """
    Represents a detailed configuration for an API endpoint.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ''
    provider: str = ''
    base_url: str = ''
    endpoint_type: EndpointType = EndpointType.REST
    authentication_type: str = 'none'
    rate_limit: Dict[str, int] = field(default_factory=dict)
    description: str = ''
    version: str = '1.0'
    tags: List[str] = field(default_factory=list)
    required_scopes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class EndpointRegistry:
    """
    Centralized registry for managing and cataloging API endpoints 
    across different service providers.
    """
    def __init__(
        self, 
        config_manager: ConfigManager,
        registry_file: str = 'endpoints.json',
        registry_dir: str = 'config'
    ):
        """
        Initialize EndpointRegistry with configuration management.
        
        :param config_manager: Configuration management system
        :param registry_file: File to store endpoint configurations
        :param registry_dir: Directory to store endpoint registry
        """
        self._config_manager = config_manager
        self._registry_dir = os.path.join(os.getcwd(), registry_dir)
        self._registry_path = os.path.join(self._registry_dir, registry_file)
        
        # Ensure registry directory exists
        os.makedirs(self._registry_dir, exist_ok=True)
        
        # Initialize registry if not exists
        if not os.path.exists(self._registry_path):
            with open(self._registry_path, 'w') as f:
                json.dump({}, f)
        
        # Load existing registry
        self._endpoints: Dict[str, Endpoint] = self._load_registry()

    def _load_registry(self) -> Dict[str, Endpoint]:
        """
        Load existing endpoint registry from file.
        
        :return: Dictionary of endpoints
        """
        try:
            with open(self._registry_path, 'r') as f:
                raw_endpoints = json.load(f)
                return {
                    endpoint_id: Endpoint(**endpoint_data) 
                    for endpoint_id, endpoint_data in raw_endpoints.items()
                }
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_registry(self):
        """
        Save current endpoint registry to file.
        """
        try:
            with open(self._registry_path, 'w') as f:
                json.dump(
                    {
                        endpoint.id: asdict(endpoint) 
                        for endpoint in self._endpoints.values()
                    }, 
                    f, 
                    indent=2
                )
        except IOError as e:
            raise EndpointRegistryError(
                f"Failed to save endpoint registry: {str(e)}",
                severity=ErrorSeverity.CRITICAL
            )

    def register_endpoint(
        self, 
        name: str, 
        base_url: str, 
        provider: str,
        endpoint_type: EndpointType = EndpointType.REST,
        **kwargs
    ) -> str:
        """
        Register a new API endpoint.
        
        :param name: Endpoint name
        :param base_url: Base URL for the endpoint
        :param provider: Service provider
        :param endpoint_type: Type of endpoint
        :param kwargs: Additional endpoint configuration
        :return: Unique endpoint ID
        """
        # Validate required parameters
        if not name or not base_url or not provider:
            raise EndpointRegistryError(
                "Name, base_url, and provider are required",
                severity=ErrorSeverity.ERROR
            )
        
        # Create endpoint
        endpoint = Endpoint(
            name=name,
            base_url=base_url,
            provider=provider,
            endpoint_type=endpoint_type,
            **kwargs
        )
        
        # Store endpoint
        self._endpoints[endpoint.id] = endpoint
        
        # Save registry
        self._save_registry()
        
        return endpoint.id

    def get_endpoint(self, endpoint_id: str) -> Endpoint:
        """
        Retrieve an endpoint by its ID.
        
        :param endpoint_id: Unique endpoint identifier
        :return: Endpoint configuration
        """
        if endpoint_id not in self._endpoints:
            raise EndpointRegistryError(
                f"Endpoint {endpoint_id} not found",
                severity=ErrorSeverity.ERROR
            )
        
        return self._endpoints[endpoint_id]

    def list_endpoints(
        self, 
        provider: Optional[str] = None,
        endpoint_type: Optional[EndpointType] = None
    ) -> List[Endpoint]:
        """
        List endpoints, optionally filtered by provider or type.
        
        :param provider: Optional provider to filter endpoints
        :param endpoint_type: Optional endpoint type to filter
        :return: List of matching endpoints
        """
        return [
            endpoint for endpoint in self._endpoints.values()
            if (provider is None or endpoint.provider == provider) and
               (endpoint_type is None or endpoint.endpoint_type == endpoint_type)
        ]

    def update_endpoint(
        self, 
        endpoint_id: str, 
        **updates
    ):
        """
        Update an existing endpoint's configuration.
        
        :param endpoint_id: Unique endpoint identifier
        :param updates: Configuration updates to apply
        """
        if endpoint_id not in self._endpoints:
            raise EndpointRegistryError(
                f"Endpoint {endpoint_id} not found",
                severity=ErrorSeverity.ERROR
            )
        
        # Update endpoint
        current_endpoint = self._endpoints[endpoint_id]
        for key, value in updates.items():
            if hasattr(current_endpoint, key):
                setattr(current_endpoint, key, value)
        
        # Save registry
        self._save_registry()

    def delete_endpoint(self, endpoint_id: str):
        """
        Delete an endpoint from the registry.
        
        :param endpoint_id: Unique endpoint identifier
        """
        if endpoint_id not in self._endpoints:
            raise EndpointRegistryError(
                f"Endpoint {endpoint_id} not found",
                severity=ErrorSeverity.ERROR
            )
        
        # Remove endpoint
        del self._endpoints[endpoint_id]
        
        # Save registry
        self._save_registry()

    def find_endpoints_by_tag(self, tag: str) -> List[Endpoint]:
        """
        Find endpoints by a specific tag.
        
        :param tag: Tag to search for
        :return: List of endpoints with the given tag
        """
        return [
            endpoint for endpoint in self._endpoints.values()
            if tag in endpoint.tags
        ]
