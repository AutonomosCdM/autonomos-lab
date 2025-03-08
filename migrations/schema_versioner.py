from typing import Dict, Any
import json
import os

class SchemaVersioner:
    """
    Manages versioning of data structures across the system.
    Tracks schema versions and provides migration capabilities.
    """
    
    def __init__(self, version_file: str = 'schema_versions.json'):
        self.version_file = os.path.join('migrations', version_file)
        self.versions = self._load_versions()
    
    def _load_versions(self) -> Dict[str, str]:
        """Load existing schema versions from file."""
        if os.path.exists(self.version_file):
            with open(self.version_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_versions(self):
        """Save current schema versions to file."""
        with open(self.version_file, 'w') as f:
            json.dump(self.versions, f, indent=2)
    
    def register_schema(self, schema_name: str, version: str):
        """
        Register a new schema version.
        
        :param schema_name: Name of the schema
        :param version: Version identifier
        """
        self.versions[schema_name] = version
        self._save_versions()
    
    def get_schema_version(self, schema_name: str) -> str:
        """
        Retrieve the current version of a schema.
        
        :param schema_name: Name of the schema
        :return: Current version or None if not found
        """
        return self.versions.get(schema_name)
    
    def is_compatible(self, schema_name: str, target_version: str) -> bool:
        """
        Check if the current schema version is compatible with the target version.
        
        :param schema_name: Name of the schema
        :param target_version: Version to check compatibility against
        :return: Boolean indicating compatibility
        """
        current_version = self.get_schema_version(schema_name)
        if not current_version:
            return False
        
        # Simple version comparison - can be extended with semantic versioning logic
        return current_version == target_version
