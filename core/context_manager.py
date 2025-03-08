from typing import Dict, Any, Optional
import uuid
from datetime import datetime, timedelta
import json
import os

class ContextManager:
    """
    Manages context for agents, providing a flexible way to track 
    and transfer contextual information between different agents or interactions.
    """
    def __init__(
        self, 
        context_dir: str = 'contexts', 
        max_context_age: int = 30, 
        max_contexts: int = 100
    ):
        """
        Initialize the ContextManager.
        
        :param context_dir: Directory to store context files
        :param max_context_age: Maximum age of context in minutes before expiration
        :param max_contexts: Maximum number of contexts to maintain
        """
        self._context_dir = os.path.join(os.getcwd(), context_dir)
        self._max_context_age = max_context_age
        self._max_contexts = max_contexts
        
        # Ensure context directory exists
        os.makedirs(self._context_dir, exist_ok=True)

    def create_context(self, initial_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new context with optional initial data.
        
        :param initial_data: Optional dictionary of initial context data
        :return: Unique context ID
        """
        context_id = str(uuid.uuid4())
        
        # Prepare context data
        context_data = {
            'id': context_id,
            'created_at': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat(),
            'data': initial_data or {}
        }

        # Save context to file
        context_file_path = self._get_context_file_path(context_id)
        with open(context_file_path, 'w') as f:
            json.dump(context_data, f, indent=2)

        # Manage context count and age
        self._manage_contexts()

        return context_id

    def _get_context_file_path(self, context_id: str) -> str:
        """
        Generate the file path for a specific context.
        
        :param context_id: Unique context identifier
        :return: Full file path for the context
        """
        return os.path.join(self._context_dir, f"{context_id}_context.json")

    def update_context(self, context_id: str, updates: Dict[str, Any]) -> None:
        """
        Update an existing context with new data.
        
        :param context_id: Unique context identifier
        :param updates: Dictionary of updates to apply
        """
        context_file_path = self._get_context_file_path(context_id)
        
        if not os.path.exists(context_file_path):
            raise ValueError(f"Context {context_id} does not exist")

        # Read existing context
        with open(context_file_path, 'r') as f:
            context_data = json.load(f)

        # Update context data
        context_data['data'].update(updates)
        context_data['last_accessed'] = datetime.now().isoformat()

        # Write updated context
        with open(context_file_path, 'w') as f:
            json.dump(context_data, f, indent=2)

    def get_context(self, context_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific context by its ID.
        
        :param context_id: Unique context identifier
        :return: Context data
        """
        context_file_path = self._get_context_file_path(context_id)
        
        if not os.path.exists(context_file_path):
            raise ValueError(f"Context {context_id} does not exist")

        # Read context
        with open(context_file_path, 'r') as f:
            context_data = json.load(f)

        # Update last accessed time
        context_data['last_accessed'] = datetime.now().isoformat()
        
        # Write back the updated last accessed time
        with open(context_file_path, 'w') as f:
            json.dump(context_data, f, indent=2)

        return context_data

    def delete_context(self, context_id: str) -> None:
        """
        Delete a specific context.
        
        :param context_id: Unique context identifier
        """
        context_file_path = self._get_context_file_path(context_id)
        
        if os.path.exists(context_file_path):
            os.remove(context_file_path)

    def _manage_contexts(self) -> None:
        """
        Manage context files, removing old or excess contexts.
        """
        # Get all context files
        context_files = [
            f for f in os.listdir(self._context_dir) 
            if f.endswith('_context.json')
        ]

        # Sort contexts by last accessed time
        context_details = []
        for filename in context_files:
            filepath = os.path.join(self._context_dir, filename)
            with open(filepath, 'r') as f:
                context_data = json.load(f)
                context_details.append({
                    'filename': filename,
                    'last_accessed': datetime.fromisoformat(context_data['last_accessed']),
                    'filepath': filepath
                })

        # Sort by last accessed (oldest first)
        context_details.sort(key=lambda x: x['last_accessed'])

        # Remove contexts older than max_context_age
        cutoff_time = datetime.now() - timedelta(minutes=self._max_context_age)
        old_contexts = [
            context for context in context_details 
            if context['last_accessed'] < cutoff_time
        ]

        # Remove old contexts
        for context in old_contexts:
            os.remove(context['filepath'])

        # If still too many contexts, remove oldest
        remaining_contexts = [
            f for f in os.listdir(self._context_dir) 
            if f.endswith('_context.json')
        ]
        if len(remaining_contexts) > self._max_contexts:
            # Remove oldest contexts first
            for filename in remaining_contexts[:len(remaining_contexts) - self._max_contexts]:
                os.remove(os.path.join(self._context_dir, filename))

    def search_contexts(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search through contexts based on query parameters.
        
        :param query: Dictionary of search criteria
        :return: List of matching context data
        """
        matching_contexts = []
        
        # Iterate through all context files
        for filename in os.listdir(self._context_dir):
            if filename.endswith('_context.json'):
                filepath = os.path.join(self._context_dir, filename)
                
                with open(filepath, 'r') as f:
                    context_data = json.load(f)
                
                # If no query, return all contexts
                if query is None:
                    matching_contexts.append(context_data)
                    continue
                
                # Check if context matches all query criteria
                match = all(
                    context_data['data'].get(key) == value 
                    for key, value in query.items()
                )
                
                if match:
                    matching_contexts.append(context_data)
        
        return matching_contexts
