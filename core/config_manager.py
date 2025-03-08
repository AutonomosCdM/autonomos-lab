import os
import json
from typing import Dict, Any, Optional, Union
import yaml
import dotenv
from cryptography.fernet import Fernet

class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass

class ConfigManager:
    """
    Centralized configuration management with support for multiple 
    configuration sources and secure secret handling.
    """
    def __init__(
        self, 
        config_dir: str = 'config', 
        env_file: Optional[str] = '.env',
        secrets_file: Optional[str] = 'secrets.yaml',
        encryption_key: Optional[str] = None
    ):
        """
        Initialize ConfigManager with configuration sources.
        
        :param config_dir: Directory containing configuration files
        :param env_file: Path to .env file for environment variables
        :param secrets_file: Path to secrets configuration file
        :param encryption_key: Optional encryption key for sensitive data
        """
        self._config_dir = os.path.join(os.getcwd(), config_dir)
        self._env_file = os.path.join(os.getcwd(), env_file) if env_file else None
        self._secrets_file = os.path.join(self._config_dir, secrets_file) if secrets_file else None
        
        # Ensure config directory exists
        os.makedirs(self._config_dir, exist_ok=True)
        
        # Load environment variables
        if self._env_file and os.path.exists(self._env_file):
            dotenv.load_dotenv(self._env_file)
        
        # Setup encryption if key provided
        self._encryption_key = encryption_key
        self._cipher_suite = Fernet(self._encryption_key.encode()) if self._encryption_key else None

    def load_config(self, config_name: str, config_type: str = 'yaml') -> Dict[str, Any]:
        """
        Load a configuration file from the config directory.
        
        :param config_name: Name of the configuration file (without extension)
        :param config_type: Type of configuration file (yaml or json)
        :return: Parsed configuration dictionary
        """
        # Construct full file path
        file_path = os.path.join(self._config_dir, f"{config_name}.{config_type}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise ConfigurationError(f"Configuration file not found: {file_path}")
        
        # Read and parse configuration
        try:
            with open(file_path, 'r') as f:
                if config_type == 'yaml':
                    return yaml.safe_load(f)
                elif config_type == 'json':
                    return json.load(f)
                else:
                    raise ConfigurationError(f"Unsupported configuration type: {config_type}")
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ConfigurationError(f"Error parsing configuration file: {e}")

    def get_secret(self, secret_name: str) -> Optional[str]:
        """
        Retrieve a secret from the secrets configuration.
        
        :param secret_name: Name of the secret to retrieve
        :return: Decrypted secret value
        """
        # Check if secrets file exists
        if not self._secrets_file or not os.path.exists(self._secrets_file):
            return None
        
        # Load secrets
        try:
            with open(self._secrets_file, 'r') as f:
                secrets = yaml.safe_load(f) or {}
        except yaml.YAMLError:
            raise ConfigurationError("Error parsing secrets file")
        
        # Retrieve secret
        secret = secrets.get(secret_name)
        
        # Decrypt if encryption is enabled
        if secret and self._cipher_suite:
            try:
                return self._cipher_suite.decrypt(secret.encode()).decode()
            except Exception:
                raise ConfigurationError(f"Failed to decrypt secret: {secret_name}")
        
        return secret

    def set_secret(self, secret_name: str, secret_value: str) -> None:
        """
        Store a secret in the secrets configuration.
        
        :param secret_name: Name of the secret to store
        :param secret_value: Value of the secret
        """
        # Ensure secrets file exists
        if not self._secrets_file:
            raise ConfigurationError("No secrets file configured")
        
        # Load existing secrets
        try:
            with open(self._secrets_file, 'r') as f:
                secrets = yaml.safe_load(f) or {}
        except yaml.YAMLError:
            secrets = {}
        
        # Encrypt secret if encryption is enabled
        if self._cipher_suite:
            secret_value = self._cipher_suite.encrypt(secret_value.encode()).decode()
        
        # Update secrets
        secrets[secret_name] = secret_value
        
        # Write back to file
        with open(self._secrets_file, 'w') as f:
            yaml.dump(secrets, f)

    def get_env(self, env_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve an environment variable.
        
        :param env_name: Name of the environment variable
        :param default: Default value if environment variable is not set
        :return: Value of the environment variable
        """
        return os.environ.get(env_name, default)

    def generate_encryption_key(self) -> str:
        """
        Generate a new encryption key for secret management.
        
        :return: Base64 encoded encryption key
        """
        return Fernet.generate_key().decode()

    def validate_config(self, config: Dict[str, Any], schema: Dict[str, type]) -> bool:
        """
        Validate a configuration dictionary against a schema.
        
        :param config: Configuration dictionary to validate
        :param schema: Dictionary of expected key types
        :return: True if configuration is valid, False otherwise
        """
        try:
            for key, expected_type in schema.items():
                if key not in config:
                    raise ConfigurationError(f"Missing required configuration key: {key}")
                
                if not isinstance(config[key], expected_type):
                    raise ConfigurationError(
                        f"Invalid type for {key}. "
                        f"Expected {expected_type.__name__}, "
                        f"got {type(config[key]).__name__}"
                    )
            return True
        except ConfigurationError as e:
            print(f"Configuration Validation Error: {e}")
            return False
