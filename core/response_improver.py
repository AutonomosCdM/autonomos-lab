import logging
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime, timedelta
import numpy as np

class ResponseImprover:
    """
    Improves agent responses based on historical feedback and interaction patterns.
    Provides mechanisms for learning and adapting response strategies.
    """
    
    def __init__(
        self, 
        improvement_dir: str = 'data/response_improvements',
        feedback_collector: Optional['FeedbackCollector'] = None
    ):
        """
        Initialize ResponseImprover.
        
        :param improvement_dir: Directory to store response improvement data
        :param feedback_collector: Optional FeedbackCollector instance
        """
        self.improvement_dir = improvement_dir
        self.logger = logging.getLogger(__name__)
        self.feedback_collector = feedback_collector
        
        # Ensure improvement directory exists
        os.makedirs(improvement_dir, exist_ok=True)
    
    def analyze_response_quality(
        self, 
        interaction_id: str
    ) -> Dict[str, Any]:
        """
        Analyze the quality of a specific interaction's response.
        
        :param interaction_id: Unique identifier for the interaction
        :return: Dictionary with response quality metrics
        """
        try:
            # If no feedback collector is provided, return empty analysis
            if not self.feedback_collector:
                self.logger.warning("No FeedbackCollector available for analysis")
                return {}
            
            # Find all feedback for this interaction
            interaction_feedback = []
            for filename in os.listdir(self.feedback_collector.feedback_dir):
                filepath = os.path.join(self.feedback_collector.feedback_dir, filename)
                
                with open(filepath, 'r') as f:
                    for line in f:
                        feedback = json.loads(line)
                        if feedback['interaction_id'] == interaction_id:
                            interaction_feedback.append(feedback)
            
            # Analyze feedback
            if not interaction_feedback:
                return {'status': 'no_feedback'}
            
            quality_analysis = {
                'total_feedback_count': len(interaction_feedback),
                'feedback_types': {},
                'sentiment_scores': [],
                'improvement_areas': set()
            }
            
            for feedback in interaction_feedback:
                # Aggregate feedback types
                feedback_type = feedback['type']
                if feedback_type not in quality_analysis['feedback_types']:
                    quality_analysis['feedback_types'][feedback_type] = 0
                quality_analysis['feedback_types'][feedback_type] += 1
                
                # Collect sentiment scores
                sentiment = feedback['data'].get('sentiment', 0)
                quality_analysis['sentiment_scores'].append(sentiment)
                
                # Identify improvement areas
                if 'improvement_suggestion' in feedback['data']:
                    quality_analysis['improvement_areas'].add(
                        feedback['data']['improvement_suggestion']
                    )
            
            # Calculate aggregate metrics
            quality_analysis['average_sentiment'] = (
                np.mean(quality_analysis['sentiment_scores']) 
                if quality_analysis['sentiment_scores'] 
                else 0
            )
            quality_analysis['improvement_areas'] = list(quality_analysis['improvement_areas'])
            
            return quality_analysis
        
        except Exception as e:
            self.logger.error(f"Error analyzing response quality: {e}")
            return {}
    
    def generate_response_improvement_strategy(
        self, 
        interaction_id: str, 
        time_window: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
        Generate improvement strategies based on historical feedback.
        
        :param interaction_id: Unique identifier for the interaction
        :param time_window: Time window for historical analysis
        :return: Dictionary with improvement strategies
        """
        try:
            # Analyze current interaction
            current_analysis = self.analyze_response_quality(interaction_id)
            
            # If no feedback collector, return empty strategy
            if not self.feedback_collector:
                return {}
            
            # Analyze broader trends
            feedback_trends = self.feedback_collector.analyze_feedback_trends(
                time_window=time_window
            )
            
            # Generate improvement strategy
            improvement_strategy = {
                'current_interaction': current_analysis,
                'overall_trends': feedback_trends,
                'recommended_actions': []
            }
            
            # Derive improvement recommendations
            if current_analysis.get('average_sentiment', 0) < 0.5:
                improvement_strategy['recommended_actions'].append(
                    "Enhance response depth and relevance"
                )
            
            if current_analysis.get('improvement_areas'):
                improvement_strategy['recommended_actions'].extend(
                    current_analysis['improvement_areas']
                )
            
            # Trend-based recommendations
            for feedback_type, count in feedback_trends.get('feedback_by_type', {}).items():
                if count > 10:  # Significant feedback volume
                    improvement_strategy['recommended_actions'].append(
                        f"Review and optimize {feedback_type} response strategies"
                    )
            
            return improvement_strategy
        
        except Exception as e:
            self.logger.error(f"Error generating improvement strategy: {e}")
            return {}
    
    def apply_improvement_strategy(
        self, 
        interaction_id: str, 
        improvement_strategy: Dict[str, Any]
    ) -> bool:
        """
        Apply the generated improvement strategy to future responses.
        
        :param interaction_id: Unique identifier for the interaction
        :param improvement_strategy: Improvement strategy to apply
        :return: Boolean indicating successful strategy application
        """
        try:
            # Prepare improvement record
            improvement_record = {
                'interaction_id': interaction_id,
                'strategy': improvement_strategy,
                'applied_at': datetime.now().isoformat()
            }
            
            # Save improvement record
            improvement_path = os.path.join(
                self.improvement_dir, 
                f'{interaction_id}_improvement.json'
            )
            
            with open(improvement_path, 'w') as f:
                json.dump(improvement_record, f, indent=2)
            
            self.logger.info(
                f"Applied improvement strategy for interaction {interaction_id}"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error applying improvement strategy: {e}")
            return False
    
    def get_historical_improvements(
        self, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve historical improvement records.
        
        :param start_date: Optional start date for filtering
        :param end_date: Optional end date for filtering
        :return: List of improvement records
        """
        try:
            historical_improvements = []
            
            for filename in os.listdir(self.improvement_dir):
                if filename.endswith('_improvement.json'):
                    filepath = os.path.join(self.improvement_dir, filename)
                    
                    with open(filepath, 'r') as f:
                        improvement = json.load(f)
                        applied_time = datetime.fromisoformat(improvement['applied_at'])
                        
                        # Apply date filtering
                        if (not start_date or applied_time >= start_date) and \
                           (not end_date or applied_time <= end_date):
                            historical_improvements.append(improvement)
            
            return historical_improvements
        
        except Exception as e:
            self.logger.error(f"Error retrieving historical improvements: {e}")
            return []
