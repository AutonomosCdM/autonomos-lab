#!/usr/bin/env python
"""
Centralized Credential Management CLI for Autonomos Lab Agents
"""
import os
import json
from pathlib import Path
from typing import Dict, Any

class CredentialManager:
    """
    Manages credentials for Autonomos Lab agents
    Provides secure storage, retrieval, and rotation of credentials
    """
    
    CREDENTIAL_FILE = Path(os.path.expanduser("~/.autonomos_credentials.json"))
    
    @classmethod
    def _ensure_credential_file(cls):
        """Ensure the credential file exists with proper permissions"""
        if not cls.CREDENTIAL_FILE.exists():
            cls.CREDENTIAL_FILE.touch(mode=0o600)  # Read/write for owner only
            cls.CREDENTIAL_FILE.write_text(json.dumps({}))
    
    @classmethod
    def set_credential(cls, service: str, key: str, value: str):
        """
        Set a credential for a specific service
        
        Args:
            service (str): Service name (e.g., 'slack', 'groq')
            key (str): Credential key (e.g., 'bot_token', 'api_key')
            value (str): Credential value
        """
        cls._ensure_credential_file()
        
        # Read existing credentials
        with open(cls.CREDENTIAL_FILE, 'r') as f:
            credentials = json.load(f)
        
        # Update credentials
        if service not in credentials:
            credentials[service] = {}
        credentials[service][key] = value
        
        # Write back to file
        with open(cls.CREDENTIAL_FILE, 'w') as f:
            json.dump(credentials, f, indent=2)
        
        print(f"Credential for {service} ({key}) set successfully.")
    
    @classmethod
    def get_credential(cls, service: str, key: str) -> str:
        """
        Retrieve a credential
        
        Args:
            service (str): Service name
            key (str): Credential key
        
        Returns:
            str: Credential value or empty string if not found
        """
        cls._ensure_credential_file()
        
        with open(cls.CREDENTIAL_FILE, 'r') as f:
            credentials = json.load(f)
        
        return credentials.get(service, {}).get(key, '')
    
    @classmethod
    def list_services(cls):
        """List all services with stored credentials"""
        cls._ensure_credential_file()
        
        with open(cls.CREDENTIAL_FILE, 'r') as f:
            credentials = json.load(f)
        
        print("Stored Services:")
        for service in credentials.keys():
            print(f"- {service}")
    
    @classmethod
    def backup_credentials(cls, backup_path: str = None):
        """
        Create a backup of credentials
        
        Args:
            backup_path (str, optional): Path to backup file
        """
        if not backup_path:
            backup_path = f"{cls.CREDENTIAL_FILE}.backup"
        
        import shutil
        shutil.copy2(cls.CREDENTIAL_FILE, backup_path)
        print(f"Credentials backed up to {backup_path}")

def main():
    """CLI interface for credential management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Autonomos Lab Credential Manager")
    parser.add_argument('action', choices=['set', 'get', 'list', 'backup'], 
                        help='Action to perform')
    parser.add_argument('--service', help='Service name')
    parser.add_argument('--key', help='Credential key')
    parser.add_argument('--value', help='Credential value')
    parser.add_argument('--backup-path', help='Path for credential backup')
    
    args = parser.parse_args()
    
    if args.action == 'set':
        if not all([args.service, args.key, args.value]):
            parser.error("set requires --service, --key, and --value")
        CredentialManager.set_credential(args.service, args.key, args.value)
    
    elif args.action == 'get':
        if not all([args.service, args.key]):
            parser.error("get requires --service and --key")
        value = CredentialManager.get_credential(args.service, args.key)
        print(f"Credential value: {value}")
    
    elif args.action == 'list':
        CredentialManager.list_services()
    
    elif args.action == 'backup':
        CredentialManager.backup_credentials(args.backup_path)

if __name__ == "__main__":
    main()
