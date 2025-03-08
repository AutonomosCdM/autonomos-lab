import os
import json
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
from core.error_handler import AgentError, ErrorSeverity
import hashlib
import uuid

class CredentialError(AgentError):
    """Exception raised for credential-related errors."""
    pass

class CredentialStore:
    """
    Secure management of API credentials with encryption and access control.
    """
    def __init__(
        self, 
        store_path: str = 'credentials', 
        encryption_key: Optional[str] = None
    ):
        """
        Initialize CredentialStore with optional encryption.
        
        :param store_path: Directory to store encrypted credentials
        :param encryption_key: Optional encryption key for additional security
        """
        # Ensure store directory exists
        self._store_path = os.path.join(os.getcwd(), store_path)
        os.makedirs(self._store_path, exist_ok=True)
        
        # Setup encryption
        self._encryption_key = encryption_key
        self._cipher_suite = Fernet(self._encryption_key.encode()) if self._encryption_key else None
        
        # Access control
        self._access_control: Dict[str, List[str]] = {}

    def _generate_credential_id(self, provider: str, username: str) -> str:
        """
        Generate a unique, deterministic ID for a credential.
        
        :param provider: API or service provider
        :param username: Username or identifier
        :return: Unique credential identifier
        """
        # Create a hash that's consistent but not easily reversible
        return hashlib.sha256(
            f"{provider}:{username}".encode()
        ).hexdigest()[:16]

    def store_credential(
        self, 
        provider: str, 
        username: str, 
        credential: Dict[str, Any],
        allowed_roles: Optional[List[str]] = None
    ) -> str:
        """
        Store a credential securely.
        
        :param provider: API or service provider
        :param username: Username or identifier
        :param credential: Credential details to store
        :param allowed_roles: Optional list of roles that can access this credential
        :return: Unique credential identifier
        """
        # Validate input
        if not provider or not username:
            raise CredentialError(
                "Provider and username are required",
                severity=ErrorSeverity.ERROR
            )
        
        # Generate unique ID
        credential_id = self._generate_credential_id(provider, username)
        
        # Prepare credential for storage
        credential_data = {
            'id': credential_id,
            'provider': provider,
            'username': username,
            'created_at': str(uuid.uuid4()),
            'data': credential
        }
        
        # Encrypt if encryption is enabled
        if self._cipher_suite:
            encrypted_data = self._cipher_suite.encrypt(
                json.dumps(credential_data).encode()
            ).decode()
            
            # Store encrypted
            with open(os.path.join(self._store_path, f"{credential_id}.enc"), 'w') as f:
                f.write(encrypted_data)
        else:
            # Store unencrypted (not recommended)
            with open(os.path.join(self._store_path, f"{credential_id}.json"), 'w') as f:
                json.dump(credential_data, f, indent=2)
        
        # Set access control if roles provided
        if allowed_roles:
            self._access_control[credential_id] = allowed_roles
        
        return credential_id

    def retrieve_credential(
        self, 
        credential_id: str, 
        current_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve a stored credential.
        
        :param credential_id: Unique credential identifier
        :param current_role: Role attempting to access the credential
        :return: Decrypted credential data
        """
        # Check access control
        if credential_id in self._access_control:
            if current_role and current_role not in self._access_control[credential_id]:
                raise CredentialError(
                    "Access denied: Insufficient permissions",
                    severity=ErrorSeverity.WARNING,
                    context={'required_roles': self._access_control[credential_id]}
                )
        
        # Determine file path
        encrypted_path = os.path.join(self._store_path, f"{credential_id}.enc")
        unencrypted_path = os.path.join(self._store_path, f"{credential_id}.json")
        
        # Try encrypted file first
        if os.path.exists(encrypted_path):
            if not self._cipher_suite:
                raise CredentialError(
                    "Encryption key required to access encrypted credentials",
                    severity=ErrorSeverity.ERROR
                )
            
            # Read and decrypt
            with open(encrypted_path, 'r') as f:
                encrypted_data = f.read()
                decrypted_data = self._cipher_suite.decrypt(encrypted_data.encode()).decode()
                return json.loads(decrypted_data)
        
        # Fallback to unencrypted
        elif os.path.exists(unencrypted_path):
            with open(unencrypted_path, 'r') as f:
                return json.load(f)
        
        # Credential not found
        raise CredentialError(
            f"Credential {credential_id} not found",
            severity=ErrorSeverity.ERROR
        )

    def delete_credential(
        self, 
        credential_id: str, 
        current_role: Optional[str] = None
    ):
        """
        Delete a stored credential.
        
        :param credential_id: Unique credential identifier
        :param current_role: Role attempting to delete the credential
        """
        # Check access control
        if credential_id in self._access_control:
            if current_role and current_role not in self._access_control[credential_id]:
                raise CredentialError(
                    "Access denied: Cannot delete credential",
                    severity=ErrorSeverity.WARNING,
                    context={'required_roles': self._access_control[credential_id]}
                )
        
        # Remove encrypted file
        encrypted_path = os.path.join(self._store_path, f"{credential_id}.enc")
        if os.path.exists(encrypted_path):
            os.remove(encrypted_path)
        
        # Remove unencrypted file
        unencrypted_path = os.path.join(self._store_path, f"{credential_id}.json")
        if os.path.exists(unencrypted_path):
            os.remove(unencrypted_path)
        
        # Remove from access control
        if credential_id in self._access_control:
            del self._access_control[credential_id]

    def list_credentials(
        self, 
        provider: Optional[str] = None,
        current_role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List stored credentials, optionally filtered by provider.
        
        :param provider: Optional provider to filter credentials
        :param current_role: Role attempting to list credentials
        :return: List of credential metadata
        """
        credentials = []
        
        # Scan credential files
        for filename in os.listdir(self._store_path):
            # Skip non-credential files
            if not (filename.endswith('.enc') or filename.endswith('.json')):
                continue
            
            credential_id = filename.split('.')[0]
            
            # Check access control
            if credential_id in self._access_control:
                if current_role and current_role not in self._access_control[credential_id]:
                    continue
            
            try:
                credential = self.retrieve_credential(credential_id)
                
                # Filter by provider if specified
                if provider and credential['provider'] != provider:
                    continue
                
                credentials.append(credential)
            except CredentialError:
                # Skip credentials that can't be retrieved
                continue
        
        return credentials

    def rotate_encryption_key(self, new_encryption_key: str):
        """
        Rotate the encryption key for all stored credentials.
        
        :param new_encryption_key: New encryption key
        """
        # Validate new key
        if not new_encryption_key:
            raise CredentialError(
                "New encryption key cannot be empty",
                severity=ErrorSeverity.ERROR
            )
        
        # Create new cipher suite
        new_cipher_suite = Fernet(new_encryption_key.encode())
        
        # Rotate all encrypted credentials
        for filename in os.listdir(self._store_path):
            if filename.endswith('.enc'):
                filepath = os.path.join(self._store_path, filename)
                
                # Read and decrypt with old key
                with open(filepath, 'r') as f:
                    encrypted_data = f.read()
                    decrypted_data = self._cipher_suite.decrypt(encrypted_data.encode()).decode()
                
                # Re-encrypt with new key
                new_encrypted_data = new_cipher_suite.encrypt(decrypted_data.encode()).decode()
                
                # Write back
                with open(filepath, 'w') as f:
                    f.write(new_encrypted_data)
        
        # Update encryption key and cipher suite
        self._encryption_key = new_encryption_key
        self._cipher_suite = new_cipher_suite
