import logging
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime, timedelta
import uuid

class TokenTracker:
    """
    Tracks and manages token usage across different models, users, and interactions.
    Provides detailed insights into token consumption and cost management.
    """
    
    def __init__(
        self, 
        token_log_dir: str = 'data/token_logs',
        token_rates: Optional[Dict[str, float]] = None
    ):
        """
        Initialize TokenTracker.
        
        :param token_log_dir: Directory to store token usage logs
        :param token_rates: Optional dictionary of token rates per model
        """
        self.token_log_dir = token_log_dir
        self.logger = logging.getLogger(__name__)
        
        # Default token rates (input/output cost per 1000 tokens)
        self.token_rates = token_rates or {
            'gpt-3.5-turbo': {
                'input': 0.0015,   # $0.0015 per 1k input tokens
                'output': 0.002    # $0.002 per 1k output tokens
            },
            'gpt-4': {
                'input': 0.03,     # $0.03 per 1k input tokens
                'output': 0.06     # $0.06 per 1k output tokens
            },
            'claude-2': {
                'input': 0.008,    # $0.008 per 1k input tokens
                'output': 0.024    # $0.024 per 1k output tokens
            }
        }
        
        # Ensure token log directory exists
        os.makedirs(token_log_dir, exist_ok=True)
    
    def log_token_usage(
        self, 
        user_id: str, 
        interaction_id: str, 
        model: str, 
        input_tokens: int, 
        output_tokens: int,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log detailed token usage for a specific interaction.
        
        :param user_id: Unique identifier for the user
        :param interaction_id: Unique identifier for the interaction
        :param model: Name of the language model used
        :param input_tokens: Number of input tokens
        :param output_tokens: Number of output tokens
        :param additional_metadata: Optional additional context
        :return: Unique token usage log ID
        """
        try:
            # Generate unique log ID
            log_id = str(uuid.uuid4())
            
            # Calculate token costs
            model_rates = self.token_rates.get(model, {
                'input': 0.001,  # Default rate
                'output': 0.001
            })
            
            input_cost = (input_tokens / 1000) * model_rates['input']
            output_cost = (output_tokens / 1000) * model_rates['output']
            total_cost = input_cost + output_cost
            
            # Prepare token usage record
            token_record = {
                'id': log_id,
                'user_id': user_id,
                'interaction_id': interaction_id,
                'model': model,
                'timestamp': datetime.now().isoformat(),
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'input_cost': input_cost,
                'output_cost': output_cost,
                'total_cost': total_cost,
                'metadata': additional_metadata or {}
            }
            
            # Create user-specific token log file
            token_log_path = os.path.join(
                self.token_log_dir, 
                f'{user_id}_token_usage.jsonl'
            )
            
            # Append token usage record
            with open(token_log_path, 'a') as f:
                json.dump(token_record, f)
                f.write('\n')
            
            self.logger.info(
                f"Logged token usage for user {user_id}, "
                f"interaction {interaction_id}: {input_tokens} input, "
                f"{output_tokens} output tokens"
            )
            
            return log_id
        
        except Exception as e:
            self.logger.error(f"Error logging token usage: {e}")
            raise
    
    def get_user_token_summary(
        self, 
        user_id: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate a summary of token usage for a specific user.
        
        :param user_id: Unique identifier for the user
        :param start_date: Optional start date for filtering
        :param end_date: Optional end date for filtering
        :return: Dictionary with token usage summary
        """
        try:
            # Prepare token usage summary
            token_summary = {
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_cost': 0,
                'usage_by_model': {},
                'interactions_count': 0
            }
            
            # Find user's token log file
            token_log_path = os.path.join(
                self.token_log_dir, 
                f'{user_id}_token_usage.jsonl'
            )
            
            if not os.path.exists(token_log_path):
                return token_summary
            
            # Read and process token log
            with open(token_log_path, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    record_time = datetime.fromisoformat(record['timestamp'])
                    
                    # Apply date filtering
                    if (start_date and record_time < start_date) or \
                       (end_date and record_time > end_date):
                        continue
                    
                    # Update summary metrics
                    token_summary['total_input_tokens'] += record['input_tokens']
                    token_summary['total_output_tokens'] += record['output_tokens']
                    token_summary['total_cost'] += record['total_cost']
                    token_summary['interactions_count'] += 1
                    
                    # Aggregate by model
                    model = record['model']
                    if model not in token_summary['usage_by_model']:
                        token_summary['usage_by_model'][model] = {
                            'input_tokens': 0,
                            'output_tokens': 0,
                            'total_cost': 0,
                            'interactions_count': 0
                        }
                    
                    model_summary = token_summary['usage_by_model'][model]
                    model_summary['input_tokens'] += record['input_tokens']
                    model_summary['output_tokens'] += record['output_tokens']
                    model_summary['total_cost'] += record['total_cost']
                    model_summary['interactions_count'] += 1
            
            return token_summary
        
        except Exception as e:
            self.logger.error(f"Error generating user token summary: {e}")
            return {}
    
    def analyze_token_efficiency(
        self, 
        time_window: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
        Analyze token usage efficiency across all users.
        
        :param time_window: Time window for analysis
        :return: Dictionary with token efficiency insights
        """
        try:
            # Prepare token efficiency analysis
            token_efficiency = {
                'total_users': 0,
                'total_tokens': 0,
                'total_cost': 0,
                'average_tokens_per_interaction': 0,
                'model_efficiency': {},
                'cost_distribution': {
                    'low_cost_users': 0,
                    'medium_cost_users': 0,
                    'high_cost_users': 0
                }
            }
            
            # Find all user token log files
            user_costs = []
            for filename in os.listdir(self.token_log_dir):
                if filename.endswith('_token_usage.jsonl'):
                    user_id = filename.replace('_token_usage.jsonl', '')
                    user_summary = self.get_user_token_summary(
                        user_id, 
                        start_date=datetime.now() - time_window
                    )
                    
                    # Skip users with no activity
                    if user_summary['interactions_count'] == 0:
                        continue
                    
                    token_efficiency['total_users'] += 1
                    token_efficiency['total_tokens'] += (
                        user_summary['total_input_tokens'] + 
                        user_summary['total_output_tokens']
                    )
                    token_efficiency['total_cost'] += user_summary['total_cost']
                    
                    # Track user costs for distribution
                    user_costs.append(user_summary['total_cost'])
                    
                    # Model-specific efficiency
                    for model, model_data in user_summary['usage_by_model'].items():
                        if model not in token_efficiency['model_efficiency']:
                            token_efficiency['model_efficiency'][model] = {
                                'total_tokens': 0,
                                'total_cost': 0,
                                'interactions_count': 0
                            }
                        
                        model_efficiency = token_efficiency['model_efficiency'][model]
                        model_efficiency['total_tokens'] += (
                            model_data['input_tokens'] + model_data['output_tokens']
                        )
                        model_efficiency['total_cost'] += model_data['total_cost']
                        model_efficiency['interactions_count'] += model_data['interactions_count']
            
            # Calculate average tokens per interaction
            if token_efficiency['total_users'] > 0:
                token_efficiency['average_tokens_per_interaction'] = (
                    token_efficiency['total_tokens'] / 
                    (token_efficiency['total_users'] * time_window.days)
                )
            
            # Categorize users by cost
            if user_costs:
                user_costs.sort()
                low_threshold = user_costs[len(user_costs) // 3]
                high_threshold = user_costs[2 * len(user_costs) // 3]
                
                for cost in user_costs:
                    if cost < low_threshold:
                        token_efficiency['cost_distribution']['low_cost_users'] += 1
                    elif cost < high_threshold:
                        token_efficiency['cost_distribution']['medium_cost_users'] += 1
                    else:
                        token_efficiency['cost_distribution']['high_cost_users'] += 1
            
            return token_efficiency
        
        except Exception as e:
            self.logger.error(f"Error analyzing token efficiency: {e}")
            return {}
