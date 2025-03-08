from typing import Dict, Any, List
import json
import os
from datetime import datetime, timedelta
import uuid

class MemoryManager:
    def __init__(self, memory_dir: str = 'memory', max_memory_size: int = 100, retention_days: int = 30):
        """
        Initialize MemoryManager with configurable memory storage.
        
        :param memory_dir: Directory to store memory files
        :param max_memory_size: Maximum number of memory entries to keep
        :param retention_days: Number of days to retain memory entries
        """
        self.memory_dir = os.path.join(os.getcwd(), memory_dir)
        self.max_memory_size = max_memory_size
        self.retention_days = retention_days
        
        # Ensure memory directory exists
        os.makedirs(self.memory_dir, exist_ok=True)

    def _get_memory_file_path(self, context_id: str) -> str:
        """
        Generate a file path for a specific context memory.
        
        :param context_id: Unique identifier for the context
        :return: Full file path for the memory file
        """
        return os.path.join(self.memory_dir, f"{context_id}_memory.json")

    def store_memory(self, context_id: str, memory_data: Dict[str, Any]) -> None:
        """
        Store memory for a specific context.
        
        :param context_id: Unique identifier for the context
        :param memory_data: Dictionary of memory data to store
        """
        # Add timestamp to memory
        memory_data['timestamp'] = datetime.now().isoformat()
        memory_data['id'] = str(uuid.uuid4())

        # Get the file path
        file_path = self._get_memory_file_path(context_id)

        # Read existing memories
        memories = self._read_memories(context_id)

        # Add new memory
        memories.append(memory_data)

        # Prune memories if exceeding max size or retention period
        memories = self._prune_memories(memories)

        # Write updated memories
        with open(file_path, 'w') as f:
            json.dump(memories, f, indent=2)

    def _read_memories(self, context_id: str) -> List[Dict[str, Any]]:
        """
        Read existing memories for a context.
        
        :param context_id: Unique identifier for the context
        :return: List of memory entries
        """
        file_path = self._get_memory_file_path(context_id)
        
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r') as f:
            return json.load(f)

    def _prune_memories(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prune memories based on max size and retention period.
        
        :param memories: List of memory entries
        :return: Pruned list of memory entries
        """
        # Sort memories by timestamp (newest first)
        memories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        # Remove memories older than retention period
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        memories = [
            memory for memory in memories 
            if datetime.fromisoformat(memory.get('timestamp', datetime.min.isoformat())) > cutoff_date
        ]

        # Limit to max memory size
        return memories[:self.max_memory_size]

    def retrieve_memories(self, context_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve memories for a specific context.
        
        :param context_id: Unique identifier for the context
        :param limit: Optional limit on number of memories to retrieve
        :return: List of memory entries
        """
        memories = self._read_memories(context_id)
        
        # Sort memories by timestamp (newest first)
        memories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Apply optional limit
        return memories[:limit] if limit is not None else memories

    def clear_memories(self, context_id: str) -> None:
        """
        Clear all memories for a specific context.
        
        :param context_id: Unique identifier for the context
        """
        file_path = self._get_memory_file_path(context_id)
        
        if os.path.exists(file_path):
            os.remove(file_path)

    def search_memories(self, context_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Search memories for a specific context based on a query.
        
        :param context_id: Unique identifier for the context
        :param query: Search query to filter memories
        :return: List of matching memory entries
        """
        memories = self._read_memories(context_id)
        
        # Simple case-insensitive substring search across all memory fields
        return [
            memory for memory in memories
            if any(query.lower() in str(value).lower() for value in memory.values())
        ]
