from typing import Dict, Any, List, Optional, Union
import os
import json

class AutonomosMemorySystem:
    def __init__(self, llm=None):
        """
        Initialize the simplified memory system for Autonomos AI Agents
        
        :param llm: Language model for memory processing (not used in simplified version)
        """
        # Simple conversation history
        self.conversation_history = []
        self.context_metadata = {}
    
    def add_context(self, context: str, metadata: Dict[str, Any] = None):
        """
        Add context to the memory system
        
        :param context: Text context to be stored
        :param metadata: Optional metadata for context
        """
        # Extract text if context is an object with a text attribute
        if hasattr(context, 'text'):
            text_content = context.text
        else:
            text_content = str(context)
            
        # Add to simple conversation history
        self.conversation_history.append(text_content)
        
        # Store metadata if provided
        if metadata:
            self.context_metadata[text_content] = metadata
    
    def retrieve_context(self, query: str, top_k: int = 5) -> List[str]:
        """
        Retrieve contextually relevant information
        
        :param query: Query to retrieve context for
        :param top_k: Number of top results to return
        :return: List of contextually relevant text snippets
        """
        # For testing purposes, just return the most recent conversation history
        if self.conversation_history:
            return self.conversation_history[-min(top_k, len(self.conversation_history)):]
        return []
    
    def clear_memory(self):
        """
        Clear all memory components
        """
        self.conversation_history = []
        self.context_metadata = {}
    
    def save_memory(self, path: str):
        """
        Save memory state to persistent storage
        
        :param path: Path to save memory state
        """
        # Create directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        
        # Save conversation history and metadata
        with open(os.path.join(path, "conversation_history.json"), "w") as f:
            json.dump(self.conversation_history, f)
        
        with open(os.path.join(path, "context_metadata.json"), "w") as f:
            # Convert dict keys to strings for JSON serialization
            serializable_metadata = {str(k): v for k, v in self.context_metadata.items()}
            json.dump(serializable_metadata, f)
    
    def load_memory(self, path: str):
        """
        Load memory state from persistent storage
        
        :param path: Path to load memory state from
        """
        # Load conversation history and metadata if they exist
        conversation_history_path = os.path.join(path, "conversation_history.json")
        if os.path.exists(conversation_history_path):
            with open(conversation_history_path, "r") as f:
                self.conversation_history = json.load(f)
        
        context_metadata_path = os.path.join(path, "context_metadata.json")
        if os.path.exists(context_metadata_path):
            with open(context_metadata_path, "r") as f:
                self.context_metadata = json.load(f)

# Example usage and testing
def test_memory_system():
    memory = AutonomosMemorySystem()
    
    # Add some context
    memory.add_context("Autonomos AiLab is developing an advanced AI agent system")
    memory.add_context("The memory system uses LlamaIndex and LangChain for hybrid memory management")
    
    # Retrieve context
    results = memory.retrieve_context("Tell me about Autonomos AiLab")
    print("Retrieved Context:", results)

if __name__ == "__main__":
    test_memory_system()
