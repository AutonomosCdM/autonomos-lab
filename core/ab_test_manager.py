import logging
import logging
from typing import Dict, Any, List, Optional
import json
import os
import uuid
from datetime import datetime, timedelta
import numpy as np
import random

class ABTestManager:
    """
    Manages A/B testing for agent configurations, prompts, and model variations.
    Provides structured approach to experimental design and result tracking.
    """
    
    def __init__(
        self, 
        experiment_dir: str = 'data/ab_tests',
        token_tracker: Optional['TokenTracker'] = None
    ):
        """
        Initialize ABTestManager.
        
        :param experiment_dir: Directory to store A/B test configurations and results
        :param token_tracker: Optional TokenTracker for cost tracking
        """
        self.experiment_dir = experiment_dir
        self.token_tracker = token_tracker
        self.logger = logging.getLogger(__name__)
        
        # Ensure experiment directory exists
        os.makedirs(experiment_dir, exist_ok=True)
        os.makedirs(os.path.join(experiment_dir, 'configs'), exist_ok=True)
        os.makedirs(os.path.join(experiment_dir, 'results'), exist_ok=True)
    
    def create_experiment(
        self, 
        experiment_name: str, 
        variants: List[Dict[str, Any]],
        allocation_strategy: str = 'random',
        sample_size: Optional[int] = None
    ) -> str:
        """
        Create a new A/B testing experiment.
        
        :param experiment_name: Unique name for the experiment
        :param variants: List of variant configurations to test
        :param allocation_strategy: Method for allocating users to variants
        :param sample_size: Optional maximum number of participants
        :return: Unique experiment ID
        """
        try:
            # Generate unique experiment ID
            experiment_id = str(uuid.uuid4())
            
            # Validate variants
            if len(variants) < 2:
                raise ValueError("At least two variants are required for A/B testing")
            
            # Prepare experiment configuration
            experiment_config = {
                'id': experiment_id,
                'name': experiment_name,
                'created_at': datetime.now().isoformat(),
                'variants': variants,
                'allocation_strategy': allocation_strategy,
                'sample_size': sample_size,
                'status': 'active',
                'participants': {},
                'results': {
                    variant['id']: {
                        'total_interactions': 0,
                        'metrics': {}
                    } for variant in variants
                }
            }
            
            # Save experiment configuration
            config_path = os.path.join(
                self.experiment_dir, 
                'configs', 
                f'{experiment_id}.json'
            )
            
            with open(config_path, 'w') as f:
                json.dump(experiment_config, f, indent=2)
            
            self.logger.info(
                f"Created A/B test experiment: {experiment_name} "
                f"(ID: {experiment_id})"
            )
            
            return experiment_id
        
        except Exception as e:
            self.logger.error(f"Error creating A/B test experiment: {e}")
            raise
    
    def assign_variant(
        self, 
        experiment_id: str, 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Assign a user to an experiment variant.
        
        :param experiment_id: Unique experiment identifier
        :param user_id: Unique user identifier
        :return: Selected variant configuration
        """
        try:
            # Load experiment configuration
            config_path = os.path.join(
                self.experiment_dir, 
                'configs', 
                f'{experiment_id}.json'
            )
            
            with open(config_path, 'r') as f:
                experiment_config = json.load(f)
            
            # Check experiment status
            if experiment_config['status'] != 'active':
                self.logger.warning(f"Experiment {experiment_id} is not active")
                return None
            
            # Check sample size
            if (experiment_config['sample_size'] and 
                len(experiment_config['participants']) >= experiment_config['sample_size']):
                self.logger.warning(f"Experiment {experiment_id} has reached sample size")
                return None
            
            # Allocation strategy
            variants = experiment_config['variants']
            
            if experiment_config['allocation_strategy'] == 'random':
                # Randomly select variant
                selected_variant = random.choice(variants)
            
            elif experiment_config['allocation_strategy'] == 'balanced':
                # Select variant with fewest participants
                variant_counts = {
                    variant['id']: sum(
                        1 for p_id, p_data in experiment_config['participants'].items()
                        if p_data['variant_id'] == variant['id']
                    )
                    for variant in variants
                }
                selected_variant = min(variants, key=lambda v: variant_counts.get(v['id'], 0))
            
            else:
                # Default to random
                selected_variant = random.choice(variants)
            
            # Record participant
            experiment_config['participants'][user_id] = {
                'variant_id': selected_variant['id'],
                'assigned_at': datetime.now().isoformat()
            }
            
            # Save updated configuration
            with open(config_path, 'w') as f:
                json.dump(experiment_config, f, indent=2)
            
            return selected_variant
        
        except Exception as e:
            self.logger.error(f"Error assigning experiment variant: {e}")
            return None
    
    def record_interaction(
        self, 
        experiment_id: str, 
        user_id: str, 
        interaction_metrics: Dict[str, Any]
    ) -> bool:
        """
        Record interaction metrics for a specific experiment variant.
        
        :param experiment_id: Unique experiment identifier
        :param user_id: Unique user identifier
        :param interaction_metrics: Dictionary of interaction metrics
        :return: Boolean indicating successful recording
        """
        try:
            # Load experiment configuration
            config_path = os.path.join(
                self.experiment_dir, 
                'configs', 
                f'{experiment_id}.json'
            )
            
            with open(config_path, 'r') as f:
                experiment_config = json.load(f)
            
            # Retrieve user's variant
            if user_id not in experiment_config['participants']:
                self.logger.warning(f"User {user_id} not found in experiment {experiment_id}")
                return False
            
            variant_id = experiment_config['participants'][user_id]['variant_id']
            
            # Update variant results
            variant_results = experiment_config['results'][variant_id]
            variant_results['total_interactions'] += 1
            
            # Aggregate metrics
            for metric_name, metric_value in interaction_metrics.items():
                if metric_name not in variant_results['metrics']:
                    variant_results['metrics'][metric_name] = {
                        'total': 0,
                        'count': 0
                    }
                
                metric_data = variant_results['metrics'][metric_name]
                metric_data['total'] += metric_value
                metric_data['count'] += 1
            
            # Save updated configuration
            with open(config_path, 'w') as f:
                json.dump(experiment_config, f, indent=2)
            
            # Optional: Track token usage if token tracker is available
            if self.token_tracker:
                # Assuming interaction_metrics includes token information
                input_tokens = interaction_metrics.get('input_tokens', 0)
                output_tokens = interaction_metrics.get('output_tokens', 0)
                
                self.token_tracker.log_token_usage(
                    user_id, 
                    f"{experiment_id}_{variant_id}", 
                    interaction_metrics.get('model', 'unknown'),
                    input_tokens, 
                    output_tokens,
                    {'experiment_id': experiment_id, 'variant_id': variant_id}
                )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error recording interaction metrics: {e}")
            return False
    
    def analyze_experiment_results(
        self, 
        experiment_id: str
    ) -> Dict[str, Any]:
        """
        Analyze and compare results across experiment variants.
        
        :param experiment_id: Unique experiment identifier
        :return: Dictionary with experiment analysis
        """
        try:
            # Load experiment configuration
            config_path = os.path.join(
                self.experiment_dir, 
                'configs', 
                f'{experiment_id}.json'
            )
            
            with open(config_path, 'r') as f:
                experiment_config = json.load(f)
            
            # Prepare results analysis
            results_analysis = {
                'experiment_name': experiment_config['name'],
                'total_participants': len(experiment_config['participants']),
                'variants': {}
            }
            
            # Analyze each variant
            for variant_id, variant_results in experiment_config['results'].items():
                variant_analysis = {
                    'total_interactions': variant_results['total_interactions'],
                    'metrics': {}
                }
                
                # Calculate metrics
                for metric_name, metric_data in variant_results['metrics'].items():
                    if metric_data['count'] > 0:
                        variant_analysis['metrics'][metric_name] = {
                            'mean': metric_data['total'] / metric_data['count'],
                            'total': metric_data['total'],
                            'count': metric_data['count']
                        }
                
                results_analysis['variants'][variant_id] = variant_analysis
            
            # Perform statistical analysis
            results_analysis['statistical_significance'] = self._calculate_statistical_significance(
                experiment_config
            )
            
            # Save analysis results
            analysis_path = os.path.join(
                self.experiment_dir, 
                'results', 
                f'{experiment_id}_analysis.json'
            )
            
            with open(analysis_path, 'w') as f:
                json.dump(results_analysis, f, indent=2)
            
            return results_analysis
        
        except Exception as e:
            self.logger.error(f"Error analyzing experiment results: {e}")
            return {}
    
    def _calculate_statistical_significance(
        self, 
        experiment_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate statistical significance between variants.
        
        :param experiment_config: Experiment configuration dictionary
        :return: Dictionary with statistical significance results
        """
        try:
            # Placeholder for statistical significance calculation
            # In a real implementation, this would use more sophisticated statistical tests
            significance_results = {
                'method': 'basic_comparison',
                'metric_comparisons': {}
            }
            
            variants = list(experiment_config['results'].keys())
            base_variant = variants[0]
            
            for metric_name in experiment_config['results'][base_variant]['metrics']:
                base_metric = experiment_config['results'][base_variant]['metrics'][metric_name]
                
                comparisons = {}
                for variant in variants[1:]:
                    variant_metric = experiment_config['results'][variant]['metrics'][metric_name]
                    
                    # Basic percentage difference
                    base_mean = base_metric['total'] / base_metric['count']
                    variant_mean = variant_metric['total'] / variant_metric['count']
                    
                    percentage_difference = (
                        (variant_mean - base_mean) / base_mean * 100 
                        if base_mean != 0 else 0
                    )
                    
                    comparisons[variant] = {
                        'percentage_difference': percentage_difference,
                        'statistically_significant': abs(percentage_difference) > 10  # Placeholder threshold
                    }
                
                significance_results['metric_comparisons'][metric_name] = comparisons
            
            return significance_results
        
        except Exception as e:
            self.logger.error(f"Error calculating statistical significance: {e}")
            return {}
