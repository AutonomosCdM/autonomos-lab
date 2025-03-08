from typing import Dict, Any, Type
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    def process_message(self, message: str) -> str:
        pass

class AgentFactory:
    _agents: Dict[str, Type[BaseAgent]] = {}
    _configurations: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register_agent(cls, name: str, agent_class: Type[BaseAgent], config: Dict[str, Any] = None):
        """
        Register a new agent type with optional configuration.
        
        :param name: Unique identifier for the agent type
        :param agent_class: The agent class to register
        :param config: Optional configuration for the agent type
        """
        cls._agents[name] = agent_class
        if config:
            cls._configurations[name] = config

    @classmethod
    def create_agent(cls, name: str, **kwargs) -> BaseAgent:
        """
        Create an agent instance based on registered type.
        
        :param name: Name of the agent type to create
        :param kwargs: Additional arguments for agent initialization
        :return: An instance of the specified agent type
        """
        if name not in cls._agents:
            raise ValueError(f"No agent type registered with name: {name}")
        
        agent_class = cls._agents[name]
        config = cls._configurations.get(name, {})
        config.update(kwargs)
        
        return agent_class(**config)

    @classmethod
    def list_available_agents(cls) -> Dict[str, Dict[str, Any]]:
        """
        List all registered agent types and their configurations.
        
        :return: Dictionary of registered agent types and their configurations
        """
        return {
            name: cls._configurations.get(name, {}) 
            for name in cls._agents.keys()
        }
