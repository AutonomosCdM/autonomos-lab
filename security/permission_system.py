from typing import Dict, Any, List, Optional, Set
import uuid
from enum import Enum, auto
from core.error_handler import AgentError, ErrorSeverity
import json
import os

class PermissionLevel(Enum):
    """
    Defines granular permission levels for access control.
    """
    NONE = 0
    READ = 1
    WRITE = 2
    EXECUTE = 3
    ADMIN = 4

class PermissionError(AgentError):
    """Exception raised for permission-related errors."""
    pass

class Role:
    """
    Represents a role with a set of permissions.
    """
    def __init__(
        self, 
        name: str, 
        permissions: Optional[Dict[str, PermissionLevel]] = None
    ):
        """
        Initialize a role with specific permissions.
        
        :param name: Name of the role
        :param permissions: Dictionary of resource permissions
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self._permissions = permissions or {}

    def add_permission(
        self, 
        resource: str, 
        level: PermissionLevel
    ):
        """
        Add or update a permission for a specific resource.
        
        :param resource: Resource identifier
        :param level: Permission level
        """
        self._permissions[resource] = level

    def remove_permission(self, resource: str):
        """
        Remove a permission for a specific resource.
        
        :param resource: Resource identifier
        """
        if resource in self._permissions:
            del self._permissions[resource]

    def check_permission(
        self, 
        resource: str, 
        required_level: PermissionLevel
    ) -> bool:
        """
        Check if the role has sufficient permissions for a resource.
        
        :param resource: Resource identifier
        :param required_level: Minimum required permission level
        :return: True if permission is granted, False otherwise
        """
        current_level = self._permissions.get(resource, PermissionLevel.NONE)
        return current_level.value >= required_level.value

    def get_permissions(self) -> Dict[str, PermissionLevel]:
        """
        Get all permissions for this role.
        
        :return: Dictionary of resource permissions
        """
        return self._permissions.copy()

class User:
    """
    Represents a user with assigned roles and individual permissions.
    """
    def __init__(
        self, 
        username: str, 
        roles: Optional[List[Role]] = None
    ):
        """
        Initialize a user with roles.
        
        :param username: Unique username
        :param roles: List of roles assigned to the user
        """
        self.id = str(uuid.uuid4())
        self.username = username
        self._roles = roles or []
        self._individual_permissions: Dict[str, PermissionLevel] = {}

    def add_role(self, role: Role):
        """
        Add a role to the user.
        
        :param role: Role to add
        """
        if role not in self._roles:
            self._roles.append(role)

    def remove_role(self, role: Role):
        """
        Remove a role from the user.
        
        :param role: Role to remove
        """
        if role in self._roles:
            self._roles.remove(role)

    def add_individual_permission(
        self, 
        resource: str, 
        level: PermissionLevel
    ):
        """
        Add an individual permission that overrides role-based permissions.
        
        :param resource: Resource identifier
        :param level: Permission level
        """
        self._individual_permissions[resource] = level

    def check_permission(
        self, 
        resource: str, 
        required_level: PermissionLevel
    ) -> bool:
        """
        Check if the user has sufficient permissions for a resource.
        
        :param resource: Resource identifier
        :param required_level: Minimum required permission level
        :return: True if permission is granted, False otherwise
        """
        # Check individual permissions first (highest priority)
        if resource in self._individual_permissions:
            current_level = self._individual_permissions[resource]
            return current_level.value >= required_level.value

        # Check role-based permissions
        for role in self._roles:
            if role.check_permission(resource, required_level):
                return True

        return False

class PermissionManager:
    """
    Centralized permission management system.
    """
    def __init__(
        self, 
        config_dir: str = 'config/permissions',
        default_role: Optional[Role] = None
    ):
        """
        Initialize PermissionManager.
        
        :param config_dir: Directory to store permission configurations
        :param default_role: Optional default role for new users
        """
        self._config_dir = os.path.join(os.getcwd(), config_dir)
        os.makedirs(self._config_dir, exist_ok=True)
        
        # Roles registry
        self._roles: Dict[str, Role] = {}
        
        # Users registry
        self._users: Dict[str, User] = {}
        
        # Default role
        self._default_role = default_role

    def create_role(
        self, 
        name: str, 
        permissions: Optional[Dict[str, PermissionLevel]] = None
    ) -> Role:
        """
        Create a new role.
        
        :param name: Name of the role
        :param permissions: Initial permissions for the role
        :return: Created Role instance
        """
        if name in self._roles:
            raise PermissionError(
                f"Role '{name}' already exists",
                severity=ErrorSeverity.WARNING
            )
        
        role = Role(name, permissions)
        self._roles[name] = role
        return role

    def get_role(self, name: str) -> Role:
        """
        Retrieve a role by name.
        
        :param name: Name of the role
        :return: Role instance
        """
        if name not in self._roles:
            raise PermissionError(
                f"Role '{name}' not found",
                severity=ErrorSeverity.ERROR
            )
        return self._roles[name]

    def create_user(
        self, 
        username: str, 
        roles: Optional[List[Role]] = None
    ) -> User:
        """
        Create a new user.
        
        :param username: Unique username
        :param roles: Optional initial roles
        :return: Created User instance
        """
        if username in self._users:
            raise PermissionError(
                f"User '{username}' already exists",
                severity=ErrorSeverity.WARNING
            )
        
        # Use default role if no roles provided
        roles = roles or ([self._default_role] if self._default_role else [])
        
        user = User(username, roles)
        self._users[username] = user
        return user

    def get_user(self, username: str) -> User:
        """
        Retrieve a user by username.
        
        :param username: Username of the user
        :return: User instance
        """
        if username not in self._users:
            raise PermissionError(
                f"User '{username}' not found",
                severity=ErrorSeverity.ERROR
            )
        return self._users[username]

    def save_configuration(self, filename: str = 'permissions.json'):
        """
        Save current permission configuration to a file.
        
        :param filename: Name of the configuration file
        """
        config = {
            'roles': {
                name: {
                    'id': role.id,
                    'permissions': {
                        resource: level.name 
                        for resource, level in role.get_permissions().items()
                    }
                } 
                for name, role in self._roles.items()
            },
            'users': {
                username: {
                    'id': user.id,
                    'roles': [role.name for role in user._roles],
                    'individual_permissions': {
                        resource: level.name 
                        for resource, level in user._individual_permissions.items()
                    }
                }
                for username, user in self._users.items()
            }
        }
        
        filepath = os.path.join(self._config_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)

    def load_configuration(self, filename: str = 'permissions.json'):
        """
        Load permission configuration from a file.
        
        :param filename: Name of the configuration file
        """
        filepath = os.path.join(self._config_dir, filename)
        
        with open(filepath, 'r') as f:
            config = json.load(f)
        
        # Clear existing roles and users
        self._roles.clear()
        self._users.clear()
        
        # Recreate roles
        for name, role_data in config.get('roles', {}).items():
            role = self.create_role(
                name, 
                {
                    resource: PermissionLevel[level] 
                    for resource, level in role_data.get('permissions', {}).items()
                }
            )
        
        # Recreate users
        for username, user_data in config.get('users', {}).items():
            user = self.create_user(
                username, 
                [self.get_role(role_name) for role_name in user_data.get('roles', [])]
            )
            
            # Add individual permissions
            for resource, level in user_data.get('individual_permissions', {}).items():
                user.add_individual_permission(
                    resource, 
                    PermissionLevel[level]
                )
