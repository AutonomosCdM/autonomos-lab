import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import os

class SlackConversationTracker:
    """
    Advanced Slack conversation tracking and context management
    """
    
    def __init__(self, 
                 max_history_days: int = 7, 
                 storage_path: Optional[str] = None):
        """
        Initialize conversation tracker
        
        :param max_history_days: Maximum days to retain conversation history
        :param storage_path: Path to store conversation history
        """
        # Conversation storage
        self._conversations: Dict[str, List[Dict[str, Any]]] = {}
        
        # Thread tracking
        self._thread_contexts: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.max_history_days = max_history_days
        
        # Storage configuration
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'data', 
            'slack_conversations'
        )
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def add_message(self, 
                    channel_id: str, 
                    message: Dict[str, Any], 
                    thread_ts: Optional[str] = None):
        """
        Add a message to conversation history
        
        :param channel_id: Slack channel ID
        :param message: Message dictionary
        :param thread_ts: Thread timestamp
        """
        # Ensure channel exists in conversations
        if channel_id not in self._conversations:
            self._conversations[channel_id] = []
        
        # Add timestamp and channel to message
        message['channel_id'] = channel_id
        message['timestamp'] = datetime.now().isoformat()
        
        # Handle thread context
        if thread_ts:
            message['thread_ts'] = thread_ts
            if thread_ts not in self._thread_contexts:
                self._thread_contexts[thread_ts] = {
                    'messages': [],
                    'metadata': {}
                }
            self._thread_contexts[thread_ts]['messages'].append(message)
        
        # Add to channel conversations
        self._conversations[channel_id].append(message)
        
        # Prune old messages
        self._prune_history(channel_id)
    
    def _prune_history(self, channel_id: str):
        """
        Remove messages older than max_history_days
        
        :param channel_id: Channel to prune
        """
        cutoff_date = datetime.now() - timedelta(days=self.max_history_days)
        
        self._conversations[channel_id] = [
            msg for msg in self._conversations[channel_id]
            if datetime.fromisoformat(msg['timestamp']) > cutoff_date
        ]
    
    def get_channel_history(self, 
                             channel_id: str, 
                             limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a channel
        
        :param channel_id: Channel to retrieve history for
        :param limit: Maximum number of messages to return
        :return: List of messages
        """
        if channel_id not in self._conversations:
            return []
        
        history = sorted(
            self._conversations[channel_id], 
            key=lambda x: x['timestamp'], 
            reverse=True
        )
        
        return history[:limit] if limit else history
    
    def get_thread_context(self, thread_ts: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve full context for a specific thread
        
        :param thread_ts: Thread timestamp
        :return: Thread context or None
        """
        return self._thread_contexts.get(thread_ts)
    
    def save_conversation_snapshot(self, channel_id: str):
        """
        Save conversation history to a persistent file
        
        :param channel_id: Channel to save
        """
        try:
            filename = f"{channel_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.storage_path, filename)
            
            with open(filepath, 'w') as f:
                json.dump(
                    self._conversations.get(channel_id, []), 
                    f, 
                    indent=2
                )
            
            self.logger.info(f"Conversation snapshot saved: {filename}")
        except Exception as e:
            self.logger.error(f"Error saving conversation snapshot: {e}")
    
    def analyze_conversation_patterns(self, 
                                      channel_id: str) -> Dict[str, Any]:
        """
        Analyze conversation patterns and metadata
        
        :param channel_id: Channel to analyze
        :return: Conversation analytics
        """
        if channel_id not in self._conversations:
            return {}
        
        messages = self._conversations[channel_id]
        
        # Basic analytics
        analytics = {
            'total_messages': len(messages),
            'users': {},
            'message_types': {},
            'threads': {}
        }
        
        for msg in messages:
            # User message count
            user = msg.get('user', 'unknown')
            analytics['users'][user] = analytics['users'].get(user, 0) + 1
            
            # Message type tracking
            msg_type = msg.get('type', 'unknown')
            analytics['message_types'][msg_type] = analytics['message_types'].get(msg_type, 0) + 1
            
            # Thread tracking
            if 'thread_ts' in msg:
                thread_ts = msg['thread_ts']
                analytics['threads'][thread_ts] = analytics['threads'].get(thread_ts, 0) + 1
        
        return analytics
    
    def reset_channel_history(self, channel_id: str):
        """
        Clear conversation history for a specific channel
        
        :param channel_id: Channel to reset
        """
        if channel_id in self._conversations:
            del self._conversations[channel_id]
            self.logger.info(f"Conversation history reset for channel {channel_id}")
