import logging
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

class InteractionAnalyzer:
    """
    Analyzes interaction patterns, user engagement, and communication dynamics.
    Provides insights into agent-user interactions and communication effectiveness.
    """
    
    def __init__(
        self, 
        interaction_dir: str = 'data/interaction_logs',
        feedback_collector: Optional['FeedbackCollector'] = None
    ):
        """
        Initialize InteractionAnalyzer.
        
        :param interaction_dir: Directory to store interaction logs
        :param feedback_collector: Optional FeedbackCollector instance
        """
        self.interaction_dir = interaction_dir
        self.logger = logging.getLogger(__name__)
        self.feedback_collector = feedback_collector
        
        # Ensure interaction directory exists
        os.makedirs(interaction_dir, exist_ok=True)
    
    def log_interaction(
        self, 
        user_id: str, 
        interaction_id: str, 
        interaction_data: Dict[str, Any]
    ) -> bool:
        """
        Log detailed interaction information.
        
        :param user_id: Unique identifier for the user
        :param interaction_id: Unique identifier for the interaction
        :param interaction_data: Detailed interaction metadata
        :return: Boolean indicating successful logging
        """
        try:
            # Prepare interaction record
            interaction_record = {
                'id': interaction_id,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'metadata': interaction_data
            }
            
            # Create interaction log file
            interaction_path = os.path.join(
                self.interaction_dir, 
                f'{user_id}_{interaction_id}_interaction.jsonl'
            )
            
            # Append interaction record
            with open(interaction_path, 'a') as f:
                json.dump(interaction_record, f)
                f.write('\n')
            
            self.logger.info(
                f"Logged interaction {interaction_id} for user {user_id}"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error logging interaction: {e}")
            return False
    
    def analyze_user_engagement(
        self, 
        user_id: str, 
        time_window: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
        Analyze user engagement patterns and interaction characteristics.
        
        :param user_id: Unique identifier for the user
        :param time_window: Time window for analysis
        :return: Dictionary with user engagement metrics
        """
        try:
            # Prepare engagement analysis
            engagement_analysis = {
                'total_interactions': 0,
                'interaction_frequency': defaultdict(int),
                'interaction_types': defaultdict(int),
                'average_interaction_duration': 0,
                'engagement_trend': []
            }
            
            # Find interaction logs for the user
            interaction_logs = []
            for filename in os.listdir(self.interaction_dir):
                if filename.startswith(f'{user_id}_'):
                    filepath = os.path.join(self.interaction_dir, filename)
                    
                    with open(filepath, 'r') as f:
                        for line in f:
                            interaction = json.loads(line)
                            interaction_time = datetime.fromisoformat(interaction['timestamp'])
                            
                            # Apply time window filtering
                            if datetime.now() - interaction_time <= time_window:
                                interaction_logs.append(interaction)
            
            # Analyze interactions
            if interaction_logs:
                engagement_analysis['total_interactions'] = len(interaction_logs)
                
                # Analyze interaction frequencies and types
                for interaction in interaction_logs:
                    # Interaction frequency by day
                    interaction_date = datetime.fromisoformat(
                        interaction['timestamp']
                    ).date()
                    engagement_analysis['interaction_frequency'][str(interaction_date)] += 1
                    
                    # Interaction types
                    interaction_type = interaction['metadata'].get('type', 'unknown')
                    engagement_analysis['interaction_types'][interaction_type] += 1
                    
                    # Interaction duration
                    duration = interaction['metadata'].get('duration', 0)
                    engagement_analysis['engagement_trend'].append({
                        'timestamp': interaction['timestamp'],
                        'duration': duration
                    })
                
                # Calculate average interaction duration
                durations = [
                    item['duration'] for item in engagement_analysis['engagement_trend']
                ]
                engagement_analysis['average_interaction_duration'] = (
                    np.mean(durations) if durations else 0
                )
            
            return engagement_analysis
        
        except Exception as e:
            self.logger.error(f"Error analyzing user engagement: {e}")
            return {}
    
    def identify_communication_patterns(
        self, 
        time_window: timedelta = timedelta(days=90)
    ) -> Dict[str, Any]:
        """
        Identify broader communication patterns across all users.
        
        :param time_window: Time window for analysis
        :return: Dictionary with communication pattern insights
        """
        try:
            # Prepare communication pattern analysis
            communication_patterns = {
                'total_users': set(),
                'interaction_types_distribution': defaultdict(int),
                'peak_interaction_times': defaultdict(int),
                'user_engagement_levels': {
                    'low': 0,
                    'medium': 0,
                    'high': 0
                }
            }
            
            # Analyze all interaction logs
            for filename in os.listdir(self.interaction_dir):
                filepath = os.path.join(self.interaction_dir, filename)
                
                with open(filepath, 'r') as f:
                    for line in f:
                        interaction = json.loads(line)
                        interaction_time = datetime.fromisoformat(interaction['timestamp'])
                        
                        # Apply time window filtering
                        if datetime.now() - interaction_time <= time_window:
                            # Track unique users
                            communication_patterns['total_users'].add(interaction['user_id'])
                            
                            # Interaction type distribution
                            interaction_type = interaction['metadata'].get('type', 'unknown')
                            communication_patterns['interaction_types_distribution'][interaction_type] += 1
                            
                            # Peak interaction times
                            hour_of_day = interaction_time.hour
                            communication_patterns['peak_interaction_times'][hour_of_day] += 1
            
            # Categorize user engagement levels
            for user_id in communication_patterns['total_users']:
                user_engagement = self.analyze_user_engagement(user_id, time_window)
                total_interactions = user_engagement.get('total_interactions', 0)
                
                if total_interactions < 5:
                    communication_patterns['user_engagement_levels']['low'] += 1
                elif total_interactions < 20:
                    communication_patterns['user_engagement_levels']['medium'] += 1
                else:
                    communication_patterns['user_engagement_levels']['high'] += 1
            
            return communication_patterns
        
        except Exception as e:
            self.logger.error(f"Error identifying communication patterns: {e}")
            return {}
    
    def generate_interaction_insights(
        self, 
        user_id: Optional[str] = None, 
        time_window: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
        Generate comprehensive interaction insights.
        
        :param user_id: Optional specific user to analyze
        :param time_window: Time window for analysis
        :return: Dictionary with interaction insights
        """
        try:
            insights = {
                'user_specific': {},
                'global_patterns': {}
            }
            
            # User-specific insights
            if user_id:
                insights['user_specific'] = self.analyze_user_engagement(
                    user_id, 
                    time_window
                )
            
            # Global communication patterns
            insights['global_patterns'] = self.identify_communication_patterns(
                time_window
            )
            
            return insights
        
        except Exception as e:
            self.logger.error(f"Error generating interaction insights: {e}")
            return {}
