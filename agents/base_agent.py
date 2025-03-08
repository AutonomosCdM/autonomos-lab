from typing import Dict, Any, Optional
from .memory_system import AutonomosMemorySystem

class BaseAgent:
    """
    Base class for AI agents in the Autonomos AI Agent System.
    Provides core functionality for agent initialization,
    communication, memory management, and task execution.
    """

    def __init__(self, 
                 name: str, 
                 description: str = "", 
                 memory_path: Optional[str] = None, 
                 temperature: float = 0.7, 
                 llm_model: Optional[str] = None, 
                 **kwargs):
        """
        Initialize the base agent with a name, description, and optional parameters.
        
        :param name: Name of the agent
        :param description: Description of the agent's role and capabilities
        :param memory_path: Optional path to load persistent memory from
        :param temperature: Temperature for language model (default 0.7)
        :param llm_model: Language model to use (optional)
        :param kwargs: Additional configuration parameters
        """
        self.name = name
        self.description = description
        
        # Add temperature and model attributes
        self.temperature = temperature
        self.model_name = llm_model
        
        # Store additional configuration parameters
        # Ensure llm_model and temperature are included in config
        self.config = kwargs.copy()
        if llm_model is not None:
            self.config['llm_model'] = llm_model
        self.config['temperature'] = temperature
        
        # Initialize hybrid memory system
        self.memory = AutonomosMemorySystem()
        
        # Load memory from persistent storage if path provided
        if memory_path:
            try:
                self.memory.load_memory(memory_path)
            except Exception as e:
                print(f"Error loading memory for {name}: {e}")

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a given task with contextual memory support.
        
        :param task: Dictionary containing task details
        :return: Dictionary with task processing results
        """
        # Add task context to memory
        task_context = f"Task: {task.get('description', 'Unnamed Task')}"
        self.memory.add_context(task_context)
        
        # Retrieve relevant context for task
        context_results = self.memory.retrieve_context(task_context)
        
        # Placeholder for task processing logic with memory-enhanced context
        return {
            "status": "processed",
            "context": context_results
        }
    
    def save_agent_memory(self, path: str):
        """
        Save agent's memory to persistent storage.
        
        :param path: Path to save memory
        """
        self.memory.save_memory(path)
    
    def interact(self, input_text: str) -> Dict[str, Any]:
        """
        Interact with the agent using a given input text.
        
        :param input_text: Input text for the agent
        :return: Dictionary containing the agent's response
        """
        # Add input context to memory
        self.memory.add_context(input_text)
        
        # Retrieve context
        context_results = self.memory.retrieve_context(input_text)
        
        # Placeholder response generation
        return {
            "agent_name": self.name,
            "response": f"Mock response to: {input_text}",
            "context": context_results
        }
