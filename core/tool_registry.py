from typing import Dict, Any, Callable, Optional, Type
import inspect
import functools

class ToolPermissionError(Exception):
    """Exception raised when a tool is accessed without proper permissions."""
    pass

class ToolRegistry:
    """
    A centralized registry for managing and accessing tools across different agents.
    """
    _tools: Dict[str, Dict[str, Any]] = {}
    _permissions: Dict[str, list] = {}

    @classmethod
    def register_tool(
        cls, 
        name: str, 
        func: Callable, 
        description: Optional[str] = None, 
        category: Optional[str] = None,
        permissions: Optional[list] = None
    ):
        """
        Register a new tool in the registry.
        
        :param name: Unique name for the tool
        :param func: The actual function/tool to register
        :param description: Optional description of the tool's purpose
        :param category: Optional category for tool organization
        :param permissions: Optional list of required permissions to use the tool
        """
        # Extract function signature details
        signature = inspect.signature(func)
        parameters = {
            param_name: {
                'type': param.annotation.__name__ if param.annotation != inspect.Parameter.empty else 'Any',
                'default': param.default if param.default != inspect.Parameter.empty else None
            }
            for param_name, param in signature.parameters.items()
        }

        # Wrap the function to add permission checking
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            # Check permissions before executing the tool
            if name in cls._permissions:
                # Implement permission checking logic here
                # This is a placeholder and should be expanded based on your specific permission system
                pass
            return func(*args, **kwargs)

        # Store tool metadata
        cls._tools[name] = {
            'function': wrapped_func,
            'description': description or func.__doc__,
            'category': category,
            'parameters': parameters,
            'return_type': signature.return_annotation.__name__ if signature.return_annotation != inspect.Signature.empty else 'Any'
        }

        # Store permissions if provided
        if permissions:
            cls._permissions[name] = permissions

        return wrapped_func

    @classmethod
    def get_tool(cls, name: str) -> Callable:
        """
        Retrieve a registered tool by name.
        
        :param name: Name of the tool to retrieve
        :return: The registered tool function
        :raises KeyError: If the tool is not found
        """
        if name not in cls._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        return cls._tools[name]['function']

    @classmethod
    def list_tools(cls, category: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        List all registered tools, optionally filtered by category.
        
        :param category: Optional category to filter tools
        :return: Dictionary of tools matching the category
        """
        if category is None:
            return cls._tools
        
        return {
            name: tool_info 
            for name, tool_info in cls._tools.items() 
            if tool_info['category'] == category
        }

    @classmethod
    def get_tool_info(cls, name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific tool.
        
        :param name: Name of the tool
        :return: Dictionary containing tool metadata
        :raises KeyError: If the tool is not found
        """
        if name not in cls._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        return cls._tools[name]

    @classmethod
    def remove_tool(cls, name: str) -> None:
        """
        Remove a tool from the registry.
        
        :param name: Name of the tool to remove
        """
        if name in cls._tools:
            del cls._tools[name]
        
        # Also remove any associated permissions
        if name in cls._permissions:
            del cls._permissions[name]

    @classmethod
    def add_tool_permission(cls, tool_name: str, permission: str) -> None:
        """
        Add a permission requirement for a specific tool.
        
        :param tool_name: Name of the tool
        :param permission: Permission to add
        """
        if tool_name not in cls._tools:
            raise KeyError(f"Tool '{tool_name}' not found in registry")
        
        if tool_name not in cls._permissions:
            cls._permissions[tool_name] = []
        
        if permission not in cls._permissions[tool_name]:
            cls._permissions[tool_name].append(permission)

    @classmethod
    def remove_tool_permission(cls, tool_name: str, permission: str) -> None:
        """
        Remove a permission requirement for a specific tool.
        
        :param tool_name: Name of the tool
        :param permission: Permission to remove
        """
        if tool_name in cls._permissions and permission in cls._permissions[tool_name]:
            cls._permissions[tool_name].remove(permission)

# Example usage decorator for easy tool registration
def register_tool(
    name: Optional[str] = None, 
    description: Optional[str] = None, 
    category: Optional[str] = None,
    permissions: Optional[list] = None
):
    """
    Decorator to register a function as a tool in the ToolRegistry.
    
    :param name: Optional custom name for the tool (defaults to function name)
    :param description: Optional description of the tool
    :param category: Optional category for tool organization
    :param permissions: Optional list of required permissions
    """
    def decorator(func: Callable):
        tool_name = name or func.__name__
        return ToolRegistry.register_tool(
            name=tool_name, 
            func=func, 
            description=description, 
            category=category,
            permissions=permissions
        )
    return decorator
