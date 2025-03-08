import logging
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime, timedelta
import numpy as np

class CostOptimizer:
    """
    Provides intelligent strategies for reducing token and computational costs.
    Analyzes usage patterns and recommends optimization techniques.
    """
    
    def __init__(
        self, 
        token_tracker: Optional['TokenTracker'] = None,
        optimization_dir: str = 'data/cost_optimizations'
    ):
        """
        Initialize CostOptimizer.
        
        :param token_tracker: Optional TokenTracker instance
        :param optimization_dir: Directory to store optimization recommendations
        """
        self.token_tracker = token_tracker
        self.optimization_dir = optimization_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure optimization directory exists
        os.makedirs(optimization_dir, exist_ok=True)
    
    def generate_optimization_recommendations(
        self, 
        time_window: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
        Generate cost optimization recommendations.
        
        :param time_window: Time window for analysis
        :return: Dictionary with optimization recommendations
        """
        try:
            # If no token tracker is provided, return empty recommendations
            if not self.token_tracker:
                self.logger.warning("No TokenTracker available for optimization")
                return {}
            
            # Analyze token efficiency
            token_efficiency = self.token_tracker.analyze_token_efficiency(time_window)
            
            # Prepare optimization recommendations
            optimization_recommendations = {
                'global_recommendations': [],
                'model_specific_recommendations': {},
                'user_cost_optimization': {
                    'high_cost_users': [],
                    'optimization_strategies': []
                }
            }
            
            # Global recommendations
            if token_efficiency['total_cost'] > 100:  # Significant total cost
                optimization_recommendations['global_recommendations'].append(
                    "Consider implementing more aggressive token reduction strategies"
                )
            
            # Model-specific recommendations
            for model, efficiency in token_efficiency.get('model_efficiency', {}).items():
                model_recommendations = []
                
                # High token usage
                if efficiency['total_tokens'] > 100000:
                    model_recommendations.append(
                        f"Explore alternative models or compression techniques for {model}"
                    )
                
                # High cost per interaction
                avg_cost_per_interaction = (
                    efficiency['total_cost'] / efficiency['interactions_count']
                    if efficiency['interactions_count'] > 0 else 0
                )
                
                if avg_cost_per_interaction > 0.1:
                    model_recommendations.append(
                        f"Optimize prompt engineering for {model} to reduce token consumption"
                    )
                
                if model_recommendations:
                    optimization_recommendations['model_specific_recommendations'][model] = model_recommendations
            
            # User cost optimization
            high_cost_users = [
                filename.replace('_token_usage.jsonl', '')
                for filename in os.listdir(self.token_tracker.token_log_dir)
                if filename.endswith('_token_usage.jsonl')
            ]
            
            for user_id in high_cost_users:
                user_summary = self.token_tracker.get_user_token_summary(
                    user_id, 
                    start_date=datetime.now() - time_window
                )
                
                # Identify high-cost users
                if user_summary['total_cost'] > 50:  # Threshold for high-cost users
                    optimization_recommendations['user_cost_optimization']['high_cost_users'].append({
                        'user_id': user_id,
                        'total_cost': user_summary['total_cost'],
                        'interactions_count': user_summary['interactions_count']
                    })
            
            # User optimization strategies
            if optimization_recommendations['user_cost_optimization']['high_cost_users']:
                optimization_recommendations['user_cost_optimization']['optimization_strategies'] = [
                    "Implement user-specific token usage limits",
                    "Provide token usage dashboards for transparency",
                    "Offer incentives for efficient token usage",
                    "Develop personalized token reduction guidance"
                ]
            
            # Save optimization recommendations
            recommendation_path = os.path.join(
                self.optimization_dir, 
                f'optimization_recommendations_{datetime.now().isoformat()}.json'
            )
            
            with open(recommendation_path, 'w') as f:
                json.dump(optimization_recommendations, f, indent=2)
            
            return optimization_recommendations
        
        except Exception as e:
            self.logger.error(f"Error generating optimization recommendations: {e}")
            return {}
    
    def apply_cost_reduction_strategy(
        self, 
        strategy: Dict[str, Any]
    ) -> bool:
        """
        Apply a specific cost reduction strategy.
        
        :param strategy: Cost reduction strategy details
        :return: Boolean indicating successful strategy application
        """
        try:
            # Validate strategy
            if not strategy or 'type' not in strategy:
                self.logger.error("Invalid cost reduction strategy")
                return False
            
            # Strategy application logic
            strategy_type = strategy['type']
            strategy_details = strategy.get('details', {})
            
            if strategy_type == 'model_switch':
                # Switch to a more cost-effective model
                return self._apply_model_switch_strategy(strategy_details)
            
            elif strategy_type == 'prompt_compression':
                # Compress prompts to reduce token usage
                return self._apply_prompt_compression_strategy(strategy_details)
            
            elif strategy_type == 'usage_limit':
                # Implement usage limits for specific users or models
                return self._apply_usage_limit_strategy(strategy_details)
            
            else:
                self.logger.warning(f"Unsupported strategy type: {strategy_type}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error applying cost reduction strategy: {e}")
            return False
    
    def _apply_model_switch_strategy(
        self, 
        strategy_details: Dict[str, Any]
    ) -> bool:
        """
        Apply model switching strategy.
        
        :param strategy_details: Details of model switch strategy
        :return: Boolean indicating successful strategy application
        """
        try:
            source_model = strategy_details.get('source_model')
            target_model = strategy_details.get('target_model')
            
            if not source_model or not target_model:
                self.logger.error("Invalid model switch strategy")
                return False
            
            # Log model switch recommendation
            recommendation_path = os.path.join(
                self.optimization_dir, 
                f'model_switch_{source_model}_to_{target_model}.json'
            )
            
            with open(recommendation_path, 'w') as f:
                json.dump({
                    'source_model': source_model,
                    'target_model': target_model,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
            
            self.logger.info(
                f"Recommended model switch from {source_model} to {target_model}"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error applying model switch strategy: {e}")
            return False
    
    def _apply_prompt_compression_strategy(
        self, 
        strategy_details: Dict[str, Any]
    ) -> bool:
        """
        Apply prompt compression strategy.
        
        :param strategy_details: Details of prompt compression strategy
        :return: Boolean indicating successful strategy application
        """
        try:
            compression_method = strategy_details.get('method', 'default')
            target_reduction_percentage = strategy_details.get('target_reduction', 0.3)
            
            # Log prompt compression recommendation
            recommendation_path = os.path.join(
                self.optimization_dir, 
                f'prompt_compression_{compression_method}.json'
            )
            
            with open(recommendation_path, 'w') as f:
                json.dump({
                    'method': compression_method,
                    'target_reduction': target_reduction_percentage,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
            
            self.logger.info(
                f"Recommended prompt compression using {compression_method} "
                f"with {target_reduction_percentage * 100}% reduction target"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error applying prompt compression strategy: {e}")
            return False
    
    def _apply_usage_limit_strategy(
        self, 
        strategy_details: Dict[str, Any]
    ) -> bool:
        """
        Apply usage limit strategy.
        
        :param strategy_details: Details of usage limit strategy
        :return: Boolean indicating successful strategy application
        """
        try:
            limit_type = strategy_details.get('type', 'global')
            limit_value = strategy_details.get('value', 0)
            
            # Log usage limit recommendation
            recommendation_path = os.path.join(
                self.optimization_dir, 
                f'usage_limit_{limit_type}.json'
            )
            
            with open(recommendation_path, 'w') as f:
                json.dump({
                    'type': limit_type,
                    'value': limit_value,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
            
            self.logger.info(
                f"Recommended {limit_type} usage limit of {limit_value}"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error applying usage limit strategy: {e}")
            return False
