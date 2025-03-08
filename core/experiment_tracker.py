import logging
from typing import Dict, Any, List, Optional
import json
import os
import uuid
from datetime import datetime, timedelta

class ExperimentTracker:
    """
    Comprehensive tracking and management of scientific and AI experiments.
    Provides detailed logging, versioning, and reproducibility support.
    """
    
    def __init__(
        self, 
        experiment_log_dir: str = 'data/experiment_logs',
        ab_test_manager: Optional['ABTestManager'] = None,
        performance_comparer: Optional['PerformanceComparer'] = None
    ):
        """
        Initialize ExperimentTracker.
        
        :param experiment_log_dir: Directory to store experiment logs
        :param ab_test_manager: Optional ABTestManager for experiment integration
        :param performance_comparer: Optional PerformanceComparer for performance tracking
        """
        self.experiment_log_dir = experiment_log_dir
        self.ab_test_manager = ab_test_manager
        self.performance_comparer = performance_comparer
        self.logger = logging.getLogger(__name__)
        
        # Ensure experiment log directories exist
        os.makedirs(experiment_log_dir, exist_ok=True)
        os.makedirs(os.path.join(experiment_log_dir, 'metadata'), exist_ok=True)
        os.makedirs(os.path.join(experiment_log_dir, 'results'), exist_ok=True)
        os.makedirs(os.path.join(experiment_log_dir, 'versions'), exist_ok=True)
    
    def start_experiment(
        self, 
        experiment_name: str, 
        experiment_config: Dict[str, Any]
    ) -> str:
        """
        Initialize a new experiment with comprehensive tracking.
        
        :param experiment_name: Unique name for the experiment
        :param experiment_config: Detailed configuration for the experiment
        :return: Unique experiment identifier
        """
        try:
            # Generate unique experiment ID
            experiment_id = str(uuid.uuid4())
            
            # Prepare experiment metadata
            experiment_metadata = {
                'id': experiment_id,
                'name': experiment_name,
                'created_at': datetime.now().isoformat(),
                'config': experiment_config,
                'status': 'active',
                'versions': [],
                'results': []
            }
            
            # Save experiment metadata
            metadata_path = os.path.join(
                self.experiment_log_dir, 
                'metadata', 
                f'{experiment_id}_metadata.json'
            )
            
            with open(metadata_path, 'w') as f:
                json.dump(experiment_metadata, f, indent=2)
            
            # Optional: Log to ABTestManager
            if self.ab_test_manager:
                self.ab_test_manager.create_experiment(
                    experiment_name, 
                    [{'id': 'default', 'config': experiment_config}]
                )
            
            self.logger.info(
                f"Started experiment: {experiment_name} "
                f"(ID: {experiment_id})"
            )
            
            return experiment_id
        
        except Exception as e:
            self.logger.error(f"Error starting experiment: {e}")
            raise
    
    def log_experiment_version(
        self, 
        experiment_id: str, 
        version_details: Dict[str, Any]
    ) -> str:
        """
        Log a new version of the experiment.
        
        :param experiment_id: Unique experiment identifier
        :param version_details: Details of the experiment version
        :return: Unique version identifier
        """
        try:
            # Generate unique version ID
            version_id = str(uuid.uuid4())
            
            # Load experiment metadata
            metadata_path = os.path.join(
                self.experiment_log_dir, 
                'metadata', 
                f'{experiment_id}_metadata.json'
            )
            
            with open(metadata_path, 'r') as f:
                experiment_metadata = json.load(f)
            
            # Prepare version record
            version_record = {
                'id': version_id,
                'timestamp': datetime.now().isoformat(),
                'details': version_details
            }
            
            # Add version to experiment metadata
            experiment_metadata['versions'].append(version_record)
            
            # Save updated metadata
            with open(metadata_path, 'w') as f:
                json.dump(experiment_metadata, f, indent=2)
            
            # Save version-specific details
            version_path = os.path.join(
                self.experiment_log_dir, 
                'versions', 
                f'{experiment_id}_{version_id}_version.json'
            )
            
            with open(version_path, 'w') as f:
                json.dump(version_record, f, indent=2)
            
            self.logger.info(
                f"Logged version {version_id} for experiment {experiment_id}"
            )
            
            return version_id
        
        except Exception as e:
            self.logger.error(f"Error logging experiment version: {e}")
            raise
    
    def record_experiment_results(
        self, 
        experiment_id: str, 
        results: Dict[str, Any]
    ) -> bool:
        """
        Record results for a specific experiment.
        
        :param experiment_id: Unique experiment identifier
        :param results: Experiment results data
        :return: Boolean indicating successful result recording
        """
        try:
            # Load experiment metadata
            metadata_path = os.path.join(
                self.experiment_log_dir, 
                'metadata', 
                f'{experiment_id}_metadata.json'
            )
            
            with open(metadata_path, 'r') as f:
                experiment_metadata = json.load(f)
            
            # Prepare result record
            result_record = {
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'data': results
            }
            
            # Add result to experiment metadata
            experiment_metadata['results'].append(result_record)
            
            # Save updated metadata
            with open(metadata_path, 'w') as f:
                json.dump(experiment_metadata, f, indent=2)
            
            # Save detailed results
            results_path = os.path.join(
                self.experiment_log_dir, 
                'results', 
                f'{experiment_id}_{result_record["id"]}_results.json'
            )
            
            with open(results_path, 'w') as f:
                json.dump(result_record, f, indent=2)
            
            # Optional: Log to PerformanceComparer
            if self.performance_comparer and 'models' in results:
                self.performance_comparer.compare_models(
                    results['models'], 
                    [{'name': experiment_metadata['name'], 'complexity': 1}]
                )
            
            # Optional: Log to ABTestManager
            if self.ab_test_manager:
                self.ab_test_manager.record_interaction(
                    experiment_id, 
                    'system', 
                    results
                )
            
            self.logger.info(
                f"Recorded results for experiment {experiment_id}"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error recording experiment results: {e}")
            return False
    
    def get_experiment_history(
        self, 
        experiment_id: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Retrieve comprehensive experiment history.
        
        :param experiment_id: Unique experiment identifier
        :param start_date: Optional start date for filtering
        :param end_date: Optional end date for filtering
        :return: Experiment history details
        """
        try:
            # Load experiment metadata
            metadata_path = os.path.join(
                self.experiment_log_dir, 
                'metadata', 
                f'{experiment_id}_metadata.json'
            )
            
            with open(metadata_path, 'r') as f:
                experiment_metadata = json.load(f)
            
            # Filter versions and results by date
            filtered_versions = [
                version for version in experiment_metadata['versions']
                if (not start_date or datetime.fromisoformat(version['timestamp']) >= start_date) and
                   (not end_date or datetime.fromisoformat(version['timestamp']) <= end_date)
            ]
            
            filtered_results = [
                result for result in experiment_metadata['results']
                if (not start_date or datetime.fromisoformat(result['timestamp']) >= start_date) and
                   (not end_date or datetime.fromisoformat(result['timestamp']) <= end_date)
            ]
            
            # Prepare comprehensive history
            experiment_history = {
                'metadata': experiment_metadata,
                'versions': filtered_versions,
                'results': filtered_results
            }
            
            return experiment_history
        
        except Exception as e:
            self.logger.error(f"Error retrieving experiment history: {e}")
            return {}
    
    def finalize_experiment(
        self, 
        experiment_id: str, 
        final_status: str = 'completed'
    ) -> bool:
        """
        Finalize an experiment and update its status.
        
        :param experiment_id: Unique experiment identifier
        :param final_status: Final status of the experiment
        :return: Boolean indicating successful finalization
        """
        try:
            # Load experiment metadata
            metadata_path = os.path.join(
                self.experiment_log_dir, 
                'metadata', 
                f'{experiment_id}_metadata.json'
            )
            
            with open(metadata_path, 'r') as f:
                experiment_metadata = json.load(f)
            
            # Update experiment status
            experiment_metadata['status'] = final_status
            experiment_metadata['finalized_at'] = datetime.now().isoformat()
            
            # Save updated metadata
            with open(metadata_path, 'w') as f:
                json.dump(experiment_metadata, f, indent=2)
            
            self.logger.info(
                f"Finalized experiment {experiment_id} with status: {final_status}"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error finalizing experiment: {e}")
            return False
