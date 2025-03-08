import logging
import logging
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime, timedelta
import uuid

class QuotaManager:
    """
    Manages resource quotas for users, models, and system-wide usage.
    Provides flexible and granular control over resource consumption.
    """
    
    def __init__(
        self, 
        quota_config_dir: str = 'config/quotas',
        token_tracker: Optional['TokenTracker'] = None
    ):
        """
        Initialize QuotaManager.
        
        :param quota_config_dir: Directory to store quota configurations
        :param token_tracker: Optional TokenTracker instance for usage tracking
        """
        self.quota_config_dir = quota_config_dir
        self.token_tracker = token_tracker
        self.logger = logging.getLogger(__name__)
        
        # Ensure quota configuration directory exists
        os.makedirs(quota_config_dir, exist_ok=True)
        
        # Load existing quota configurations
        self.quota_configs = self._load_quota_configs()
    
    def _load_quota_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Load existing quota configurations.
        
        :return: Dictionary of quota configurations
        """
        try:
            quota_configs = {}
            for filename in os.listdir(self.quota_config_dir):
                if filename.endswith('.json'):
                    config_path = os.path.join(self.quota_config_dir, filename)
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        quota_configs[config['id']] = config
            return quota_configs
        except Exception as e:
            self.logger.error(f"Error loading quota configurations: {e}")
            return {}
    
    def create_quota_config(
        self, 
        entity_type: str, 
        entity_id: str, 
        quota_limits: Dict[str, Any]
    ) -> str:
        """
        Create a new quota configuration.
        
        :param entity_type: Type of entity (user, model, global)
        :param entity_id: Unique identifier for the entity
        :param quota_limits: Dictionary of quota limits
        :return: Unique quota configuration ID
        """
        try:
            # Generate unique configuration ID
            config_id = str(uuid.uuid4())
            
            # Prepare quota configuration
            quota_config = {
                'id': config_id,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'limits': quota_limits,
                'created_at': datetime.now().isoformat(),
                'status': 'active',
                'usage_history': []
            }
            
            # Save configuration
            config_path = os.path.join(
                self.quota_config_dir, 
                f'{config_id}.json'
            )
            
            with open(config_path, 'w') as f:
                json.dump(quota_config, f, indent=2)
            
            # Update in-memory configurations
            self.quota_configs[config_id] = quota_config
            
            self.logger.info(
                f"Created quota configuration for {entity_type} {entity_id}"
            )
            
            return config_id
        
        except Exception as e:
            self.logger.error(f"Error creating quota configuration: {e}")
            raise
    
    def check_quota_compliance(
        self, 
        config_id: str, 
        usage_amount: float, 
        usage_type: str
    ) -> bool:
        """
        Check if a specific usage amount complies with quota limits.
        
        :param config_id: Unique quota configuration ID
        :param usage_amount: Amount of resource used
        :param usage_type: Type of resource (tokens, compute, etc.)
        :return: Boolean indicating quota compliance
        """
        try:
            # Retrieve quota configuration
            config = self.quota_configs.get(config_id)
            
            if not config:
                self.logger.warning(f"Quota configuration {config_id} not found")
                return False
            
            # Check quota limits
            limits = config['limits']
            
            if usage_type not in limits:
                self.logger.warning(f"No limit defined for {usage_type}")
                return True
            
            # Retrieve current usage
            current_usage = self._get_current_usage(config_id, usage_type)
            
            # Check against limit
            limit_value = limits[usage_type]
            
            # Different limit types
            if isinstance(limit_value, (int, float)):
                # Simple numeric limit
                return current_usage + usage_amount <= limit_value
            
            elif isinstance(limit_value, dict):
                # More complex limit with time-based constraints
                period = limit_value.get('period', 'daily')
                max_amount = limit_value.get('max_amount', float('inf'))
                
                # Calculate usage within the specified period
                period_usage = self._get_period_usage(
                    config_id, 
                    usage_type, 
                    period
                )
                
                return period_usage + usage_amount <= max_amount
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error checking quota compliance: {e}")
            return False
    
    def _get_current_usage(
        self, 
        config_id: str, 
        usage_type: str
    ) -> float:
        """
        Get current usage for a specific quota configuration and usage type.
        
        :param config_id: Unique quota configuration ID
        :param usage_type: Type of resource
        :return: Current usage amount
        """
        try:
            config = self.quota_configs.get(config_id)
            
            if not config:
                return 0
            
            # If token tracker is available, use it for more accurate tracking
            if self.token_tracker and usage_type == 'tokens':
                # Assuming entity_id is a user_id
                user_summary = self.token_tracker.get_user_token_summary(
                    config['entity_id']
                )
                return user_summary['total_input_tokens'] + user_summary['total_output_tokens']
            
            # Fallback to usage history in configuration
            usage_history = config.get('usage_history', [])
            
            return sum(
                entry['amount'] 
                for entry in usage_history 
                if entry['type'] == usage_type
            )
        
        except Exception as e:
            self.logger.error(f"Error getting current usage: {e}")
            return 0
    
    def _get_period_usage(
        self, 
        config_id: str, 
        usage_type: str, 
        period: str = 'daily'
    ) -> float:
        """
        Get usage within a specific time period.
        
        :param config_id: Unique quota configuration ID
        :param usage_type: Type of resource
        :param period: Time period (daily, weekly, monthly)
        :return: Usage amount within the specified period
        """
        try:
            config = self.quota_configs.get(config_id)
            
            if not config:
                return 0
            
            # Determine time threshold based on period
            now = datetime.now()
            if period == 'daily':
                threshold = now - timedelta(days=1)
            elif period == 'weekly':
                threshold = now - timedelta(weeks=1)
            elif period == 'monthly':
                threshold = now - timedelta(days=30)
            else:
                return 0
            
            # Filter usage history
            usage_history = config.get('usage_history', [])
            period_usage = sum(
                entry['amount'] 
                for entry in usage_history 
                if (entry['type'] == usage_type and 
                    datetime.fromisoformat(entry['timestamp']) >= threshold)
            )
            
            return period_usage
        
        except Exception as e:
            self.logger.error(f"Error getting period usage: {e}")
            return 0
    
    def record_usage(
        self, 
        config_id: str, 
        usage_amount: float, 
        usage_type: str
    ) -> bool:
        """
        Record resource usage for a quota configuration.
        
        :param config_id: Unique quota configuration ID
        :param usage_amount: Amount of resource used
        :param usage_type: Type of resource
        :return: Boolean indicating successful usage recording
        """
        try:
            # Retrieve quota configuration
            config = self.quota_configs.get(config_id)
            
            if not config:
                self.logger.warning(f"Quota configuration {config_id} not found")
                return False
            
            # Prepare usage record
            usage_record = {
                'amount': usage_amount,
                'type': usage_type,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add to usage history
            if 'usage_history' not in config:
                config['usage_history'] = []
            
            config['usage_history'].append(usage_record)
            
            # Save updated configuration
            config_path = os.path.join(
                self.quota_config_dir, 
                f'{config_id}.json'
            )
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Update in-memory configuration
            self.quota_configs[config_id] = config
            
            self.logger.info(
                f"Recorded {usage_amount} {usage_type} usage for config {config_id}"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error recording usage: {e}")
            return False
