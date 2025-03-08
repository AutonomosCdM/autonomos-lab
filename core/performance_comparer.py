import logging
from typing import Dict, Any, List, Optional
import json
import os
import uuid
from datetime import datetime, timedelta
import numpy as np
import statistics

class PerformanceComparer:
    """
    Compares performance across different models, configurations, and approaches.
    Provides comprehensive analysis of system performance metrics.
    """
    
    def __init__(
        self, 
        comparison_dir: str = 'data/performance_comparisons',
        token_tracker: Optional['TokenTracker'] = None,
        ab_test_manager: Optional['ABTestManager'] = None
    ):
        """
        Initialize PerformanceComparer.
        
        :param comparison_dir: Directory to store performance comparison results
        :param token_tracker: Optional TokenTracker for cost tracking
        :param ab_test_manager: Optional ABTestManager for experimental tracking
        """
        self.comparison_dir = comparison_dir
        self.token_tracker = token_tracker
        self.ab_test_manager = ab_test_manager
        self.logger = logging.getLogger(__name__)
        
        # Ensure comparison directory exists
        os.makedirs(comparison_dir, exist_ok=True)
        os.makedirs(os.path.join(comparison_dir, 'metrics'), exist_ok=True)
        os.makedirs(os.path.join(comparison_dir, 'reports'), exist_ok=True)
    
    def compare_models(
        self, 
        models: List[str], 
        comparison_tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare performance of multiple models across specified tasks.
        
        :param models: List of model identifiers to compare
        :param comparison_tasks: List of tasks with specific evaluation criteria
        :return: Comprehensive performance comparison results
        """
        try:
            # Generate unique comparison ID
            comparison_id = str(uuid.uuid4())
            
            # Prepare comparison results
            comparison_results = {
                'id': comparison_id,
                'timestamp': datetime.now().isoformat(),
                'models': models,
                'tasks': [],
                'overall_performance': {}
            }
            
            # Evaluate each task
            for task in comparison_tasks:
                task_results = self._evaluate_task_performance(models, task)
                comparison_results['tasks'].append(task_results)
            
            # Calculate overall performance
            comparison_results['overall_performance'] = self._calculate_overall_performance(
                comparison_results['tasks']
            )
            
            # Save comparison results
            results_path = os.path.join(
                self.comparison_dir, 
                'reports', 
                f'{comparison_id}_comparison.json'
            )
            
            with open(results_path, 'w') as f:
                json.dump(comparison_results, f, indent=2)
            
            # Optional: Log to ABTestManager
            if self.ab_test_manager:
                self.ab_test_manager.record_interaction(
                    'model_performance_comparison', 
                    'system', 
                    {
                        'overall_performance': comparison_results['overall_performance'],
                        'models': models
                    }
                )
            
            return comparison_results
        
        except Exception as e:
            self.logger.error(f"Error comparing model performance: {e}")
            return {}
    
    def _evaluate_task_performance(
        self, 
        models: List[str], 
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate performance of models for a specific task.
        
        :param models: List of model identifiers
        :param task: Task configuration with evaluation criteria
        :return: Performance results for the task
        """
        try:
            task_results = {
                'name': task.get('name', 'Unnamed Task'),
                'model_performance': {}
            }
            
            # Predefined performance metrics
            performance_metrics = {
                'accuracy': self._calculate_accuracy,
                'response_time': self._calculate_response_time,
                'token_efficiency': self._calculate_token_efficiency,
                'complexity_handling': self._calculate_complexity_handling
            }
            
            # Evaluate each model
            for model in models:
                model_metrics = {}
                
                # Run each specified performance metric
                for metric_name, metric_func in performance_metrics.items():
                    try:
                        metric_result = metric_func(model, task)
                        model_metrics[metric_name] = metric_result
                    except Exception as metric_error:
                        self.logger.warning(
                            f"Error calculating {metric_name} for {model}: {metric_error}"
                        )
                        model_metrics[metric_name] = None
                
                task_results['model_performance'][model] = model_metrics
            
            return task_results
        
        except Exception as e:
            self.logger.error(f"Error evaluating task performance: {e}")
            return {}
    
    def _calculate_accuracy(
        self, 
        model: str, 
        task: Dict[str, Any]
    ) -> float:
        """
        Calculate model accuracy for a given task.
        
        :param model: Model identifier
        :param task: Task configuration
        :return: Accuracy score
        """
        # Simulated accuracy calculation
        # In a real implementation, this would involve actual model testing
        base_accuracy = 0.7  # Default baseline
        
        # Adjust accuracy based on task complexity
        complexity_factor = task.get('complexity', 1)
        accuracy = base_accuracy / complexity_factor
        
        # Add some randomness to simulate real-world variability
        accuracy += np.random.normal(0, 0.05)
        
        return max(min(accuracy, 1), 0)
    
    def _calculate_response_time(
        self, 
        model: str, 
        task: Dict[str, Any]
    ) -> float:
        """
        Calculate model response time for a given task.
        
        :param model: Model identifier
        :param task: Task configuration
        :return: Response time in seconds
        """
        # Simulated response time calculation
        base_response_time = 2.0  # Default baseline in seconds
        
        # Adjust response time based on task complexity
        complexity_factor = task.get('complexity', 1)
        response_time = base_response_time * complexity_factor
        
        # Add some randomness to simulate real-world variability
        response_time += np.random.normal(0, 0.5)
        
        return max(response_time, 0.1)
    
    def _calculate_token_efficiency(
        self, 
        model: str, 
        task: Dict[str, Any]
    ) -> float:
        """
        Calculate token efficiency for a given task.
        
        :param model: Model identifier
        :param task: Task configuration
        :return: Token efficiency score
        """
        # If token tracker is available, use actual token usage
        if self.token_tracker:
            # Retrieve token usage for this model
            token_summary = self.token_tracker.get_user_token_summary('system')
            model_usage = token_summary['usage_by_model'].get(model, {})
            
            total_tokens = model_usage.get('input_tokens', 0) + model_usage.get('output_tokens', 0)
            interactions = model_usage.get('interactions_count', 1)
            
            # Calculate average tokens per interaction
            avg_tokens_per_interaction = total_tokens / interactions
            
            # Normalize token efficiency (lower is better)
            token_efficiency = 1 / (1 + avg_tokens_per_interaction / 1000)
            
            return token_efficiency
        
        # Fallback simulated token efficiency
        base_efficiency = 0.8
        complexity_factor = task.get('complexity', 1)
        
        return max(base_efficiency / complexity_factor, 0)
    
    def _calculate_complexity_handling(
        self, 
        model: str, 
        task: Dict[str, Any]
    ) -> float:
        """
        Calculate model's ability to handle complex tasks.
        
        :param model: Model identifier
        :param task: Task configuration
        :return: Complexity handling score
        """
        # Simulated complexity handling calculation
        base_complexity_handling = 0.75
        
        # Adjust based on task complexity
        complexity_factor = task.get('complexity', 1)
        complexity_handling = base_complexity_handling / complexity_factor
        
        # Add some randomness to simulate real-world variability
        complexity_handling += np.random.normal(0, 0.1)
        
        return max(min(complexity_handling, 1), 0)
    
    def _calculate_overall_performance(
        self, 
        task_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate overall performance across all tasks.
        
        :param task_results: List of task performance results
        :return: Overall performance summary
        """
        try:
            # Aggregate performance metrics
            overall_performance = {}
            
            # Get all models from first task
            models = list(task_results[0]['model_performance'].keys())
            metrics = list(task_results[0]['model_performance'][models[0]].keys())
            
            for model in models:
                model_scores = {}
                
                for metric in metrics:
                    # Collect metric scores across tasks
                    metric_scores = [
                        task['model_performance'][model][metric]
                        for task in task_results
                        if task['model_performance'][model][metric] is not None
                    ]
                    
                    # Calculate statistical summary
                    if metric_scores:
                        model_scores[metric] = {
                            'mean': statistics.mean(metric_scores),
                            'median': statistics.median(metric_scores),
                            'std_dev': statistics.stdev(metric_scores) if len(metric_scores) > 1 else 0
                        }
                
                overall_performance[model] = model_scores
            
            return overall_performance
        
        except Exception as e:
            self.logger.error(f"Error calculating overall performance: {e}")
            return {}
