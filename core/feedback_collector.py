import logging
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
import json
import os

class FeedbackCollector:
    """
    Structured system for capturing, storing, and analyzing user feedback.
    Provides mechanisms for collecting, categorizing, and processing feedback.
    """
    
    def __init__(self, feedback_dir: str = 'data/feedback'):
        """
        Initialize FeedbackCollector.
        
        :param feedback_dir: Directory to store feedback records
        """
        self.feedback_dir = feedback_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure feedback directory exists
        os.makedirs(feedback_dir, exist_ok=True)
    
    def collect_feedback(
        self, 
        user_id: str, 
        interaction_id: str, 
        feedback_type: str, 
        feedback_data: Dict[str, Any]
    ) -> str:
        """
        Collect and store user feedback.
        
        :param user_id: Unique identifier for the user
        :param interaction_id: Identifier for the specific interaction
        :param feedback_type: Type of feedback (e.g., 'quality', 'relevance')
        :param feedback_data: Detailed feedback information
        :return: Unique feedback record ID
        """
        try:
            # Generate unique feedback ID
            feedback_id = str(uuid.uuid4())
            
            # Prepare feedback record
            feedback_record = {
                'id': feedback_id,
                'user_id': user_id,
                'interaction_id': interaction_id,
                'type': feedback_type,
                'data': feedback_data,
                'timestamp': datetime.now().isoformat(),
                'processed': False
            }
            
            # Determine feedback file path
            feedback_path = os.path.join(
                self.feedback_dir, 
                f'{user_id}_{interaction_id}_feedback.jsonl'
            )
            
            # Append feedback record
            with open(feedback_path, 'a') as f:
                json.dump(feedback_record, f)
                f.write('\n')
            
            self.logger.info(
                f"Collected {feedback_type} feedback from user {user_id} "
                f"for interaction {interaction_id}"
            )
            
            return feedback_id
        
        except Exception as e:
            self.logger.error(f"Error collecting feedback: {e}")
            raise
    
    def get_user_feedback(
        self, 
        user_id: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve feedback for a specific user.
        
        :param user_id: Unique identifier for the user
        :param start_date: Optional start date for filtering
        :param end_date: Optional end date for filtering
        :return: List of feedback records
        """
        try:
            user_feedback = []
            
            # Find all feedback files for the user
            for filename in os.listdir(self.feedback_dir):
                if filename.startswith(f'{user_id}_'):
                    filepath = os.path.join(self.feedback_dir, filename)
                    
                    with open(filepath, 'r') as f:
                        for line in f:
                            feedback = json.loads(line)
                            feedback_time = datetime.fromisoformat(feedback['timestamp'])
                            
                            # Apply date filtering if specified
                            if (not start_date or feedback_time >= start_date) and \
                               (not end_date or feedback_time <= end_date):
                                user_feedback.append(feedback)
            
            return user_feedback
        
        except Exception as e:
            self.logger.error(f"Error retrieving user feedback: {e}")
            return []
    
    def analyze_feedback_trends(
        self, 
        feedback_type: Optional[str] = None, 
        time_window: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """
        Analyze trends in feedback across all users.
        
        :param feedback_type: Optional specific feedback type to analyze
        :param time_window: Optional time window for analysis
        :return: Dictionary with feedback trend analysis
        """
        try:
            feedback_trends = {
                'total_feedback_count': 0,
                'feedback_by_type': {},
                'average_sentiment': {}
            }
            
            # Iterate through all feedback files
            for filename in os.listdir(self.feedback_dir):
                filepath = os.path.join(self.feedback_dir, filename)
                
                with open(filepath, 'r') as f:
                    for line in f:
                        feedback = json.loads(line)
                        feedback_time = datetime.fromisoformat(feedback['timestamp'])
                        
                        # Apply time window filtering if specified
                        if time_window and (datetime.now() - feedback_time > time_window):
                            continue
                        
                        # Filter by feedback type if specified
                        if feedback_type and feedback['type'] != feedback_type:
                            continue
                        
                        # Update trend analysis
                        feedback_trends['total_feedback_count'] += 1
                        
                        # Aggregate by feedback type
                        if feedback['type'] not in feedback_trends['feedback_by_type']:
                            feedback_trends['feedback_by_type'][feedback['type']] = 0
                        feedback_trends['feedback_by_type'][feedback['type']] += 1
                        
                        # Analyze sentiment (assuming sentiment is in feedback data)
                        sentiment = feedback['data'].get('sentiment', 0)
                        if feedback['type'] not in feedback_trends['average_sentiment']:
                            feedback_trends['average_sentiment'][feedback['type']] = {
                                'total': 0,
                                'count': 0
                            }
                        
                        feedback_trends['average_sentiment'][feedback['type']]['total'] += sentiment
                        feedback_trends['average_sentiment'][feedback['type']]['count'] += 1
            
            # Calculate average sentiments
            for feedback_type, sentiment_data in feedback_trends['average_sentiment'].items():
                sentiment_data['average'] = (
                    sentiment_data['total'] / sentiment_data['count'] 
                    if sentiment_data['count'] > 0 else 0
                )
                del sentiment_data['total']
                del sentiment_data['count']
            
            return feedback_trends
        
        except Exception as e:
            self.logger.error(f"Error analyzing feedback trends: {e}")
            return {}
    
    def mark_feedback_processed(self, feedback_id: str) -> bool:
        """
        Mark a specific feedback record as processed.
        
        :param feedback_id: Unique feedback identifier
        :return: Boolean indicating successful processing mark
        """
        try:
            # Find and update the feedback record
            for filename in os.listdir(self.feedback_dir):
                filepath = os.path.join(self.feedback_dir, filename)
                
                # Temporary file for writing updated records
                temp_filepath = filepath + '.tmp'
                
                with open(filepath, 'r') as input_file, \
                     open(temp_filepath, 'w') as output_file:
                    processed = False
                    for line in input_file:
                        feedback = json.loads(line)
                        if feedback['id'] == feedback_id:
                            feedback['processed'] = True
                            processed = True
                        
                        json.dump(feedback, output_file)
                        output_file.write('\n')
                
                # Replace original file with updated file
                if processed:
                    os.replace(temp_filepath, filepath)
                    self.logger.info(f"Marked feedback {feedback_id} as processed")
                    return True
                else:
                    os.remove(temp_filepath)
            
            self.logger.warning(f"Feedback {feedback_id} not found")
            return False
        
        except Exception as e:
            self.logger.error(f"Error marking feedback as processed: {e}")
            return False
