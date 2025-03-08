import logging
from typing import List, Dict, Any, Callable
from datetime import datetime
import json
import os
import importlib
import traceback

class DataMigrationPipeline:
    """
    Automated data migration process for handling schema and data transformations.
    Supports versioned migrations with rollback capabilities.
    """
    
    def __init__(self, migration_dir: str = 'migrations'):
        """
        Initialize the DataMigrationPipeline.
        
        :param migration_dir: Directory to store migration logs and scripts
        """
        self.migration_dir = migration_dir
        self.logger = logging.getLogger(__name__)
        self.migration_log_path = os.path.join(migration_dir, 'migration_history.json')
        
        # Ensure migration directory exists
        os.makedirs(migration_dir, exist_ok=True)
        
        # Load migration history
        self.migration_history = self._load_migration_history()
    
    def _load_migration_history(self) -> List[Dict[str, Any]]:
        """
        Load migration history from JSON file.
        
        :return: List of migration records
        """
        try:
            if os.path.exists(self.migration_log_path):
                with open(self.migration_log_path, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Error loading migration history: {e}")
            return []
    
    def _save_migration_history(self):
        """
        Save migration history to JSON file.
        """
        try:
            with open(self.migration_log_path, 'w') as f:
                json.dump(self.migration_history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving migration history: {e}")
    
    def register_migration_script(
        self, 
        script_path: str, 
        source_version: str, 
        target_version: str
    ):
        """
        Register a new migration script.
        
        :param script_path: Path to the migration script
        :param source_version: Source data version
        :param target_version: Target data version
        """
        migration_record = {
            'script_path': script_path,
            'source_version': source_version,
            'target_version': target_version,
            'registered_at': datetime.now().isoformat(),
            'status': 'registered'
        }
        self.migration_history.append(migration_record)
        self._save_migration_history()
    
    def execute_migration(
        self, 
        source_version: str, 
        target_version: str
    ) -> bool:
        """
        Execute migration between specified versions.
        
        :param source_version: Source data version
        :param target_version: Target data version
        :return: Boolean indicating migration success
        """
        # Find appropriate migration script
        migration_script = self._find_migration_script(source_version, target_version)
        
        if not migration_script:
            self.logger.error(f"No migration script found for {source_version} to {target_version}")
            return False
        
        try:
            # Dynamically import and execute migration script
            module_name = migration_script.replace('/', '.').replace('.py', '')
            migration_module = importlib.import_module(module_name)
            
            # Assume the module has a migrate() function
            if hasattr(migration_module, 'migrate'):
                migration_result = migration_module.migrate()
                
                # Update migration history
                self._update_migration_status(
                    source_version, 
                    target_version, 
                    'completed' if migration_result else 'failed'
                )
                
                return migration_result
            else:
                self.logger.error(f"Migration script {migration_script} lacks migrate() function")
                return False
        
        except Exception as e:
            self.logger.error(f"Migration error: {e}")
            self.logger.error(traceback.format_exc())
            
            # Update migration history with failure
            self._update_migration_status(
                source_version, 
                target_version, 
                'failed'
            )
            
            return False
    
    def _find_migration_script(
        self, 
        source_version: str, 
        target_version: str
    ) -> Optional[str]:
        """
        Find the appropriate migration script for given versions.
        
        :param source_version: Source data version
        :param target_version: Target data version
        :return: Path to migration script or None
        """
        # Search for migration scripts in migration directory
        for filename in os.listdir(self.migration_dir):
            if filename.startswith(f'migrate_{source_version}_to_{target_version}') and filename.endswith('.py'):
                return os.path.join(self.migration_dir, filename)
        
        return None
    
    def _update_migration_status(
        self, 
        source_version: str, 
        target_version: str, 
        status: str
    ):
        """
        Update the status of a migration in the history.
        
        :param source_version: Source data version
        :param target_version: Target data version
        :param status: Migration status (registered, completed, failed)
        """
        for record in self.migration_history:
            if (record['source_version'] == source_version and 
                record['target_version'] == target_version):
                record['status'] = status
                record['completed_at'] = datetime.now().isoformat()
                break
        
        self._save_migration_history()
    
    def rollback_migration(
        self, 
        source_version: str, 
        target_version: str
    ) -> bool:
        """
        Rollback a migration to the previous version.
        
        :param source_version: Source data version
        :param target_version: Target data version
        :return: Boolean indicating successful rollback
        """
        try:
            # Find rollback script
            rollback_script = self._find_rollback_script(source_version, target_version)
            
            if not rollback_script:
                self.logger.error(f"No rollback script found for {target_version} to {source_version}")
                return False
            
            # Dynamically import and execute rollback script
            module_name = rollback_script.replace('/', '.').replace('.py', '')
            rollback_module = importlib.import_module(module_name)
            
            # Assume the module has a rollback() function
            if hasattr(rollback_module, 'rollback'):
                rollback_result = rollback_module.rollback()
                
                # Update migration history
                self._update_migration_status(
                    source_version, 
                    target_version, 
                    'rolled_back' if rollback_result else 'rollback_failed'
                )
                
                return rollback_result
            else:
                self.logger.error(f"Rollback script {rollback_script} lacks rollback() function")
                return False
        
        except Exception as e:
            self.logger.error(f"Rollback error: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def _find_rollback_script(
        self, 
        source_version: str, 
        target_version: str
    ) -> Optional[str]:
        """
        Find the appropriate rollback script for given versions.
        
        :param source_version: Source data version
        :param target_version: Target data version
        :return: Path to rollback script or None
        """
        # Search for rollback scripts in migration directory
        for filename in os.listdir(self.migration_dir):
            if filename.startswith(f'rollback_{target_version}_to_{source_version}') and filename.endswith('.py'):
                return os.path.join(self.migration_dir, filename)
        
        return None
