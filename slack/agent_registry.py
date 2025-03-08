"""
Registry for managing multiple agents connected to Slack.
"""
import logging
from typing import Dict, List, Optional, Type
from agents.base_agent import BaseAgent
from slack.base_adapter import SlackAdapter

# Configure logging
logger = logging.getLogger("agent_registry")

class AgentRegistry:
    """
    Registry for managing multiple agents connected to Slack.
    This class allows registering and managing multiple agents
    that can be connected to Slack.
    """
    
    def __init__(self):
        """Initialize the agent registry."""
        self.agents: Dict[str, BaseAgent] = {}
        self.adapters: Dict[str, SlackAdapter] = {}
    
    def register_agent(
        self, 
        agent: BaseAgent,
        mention_only: bool = False,
        bot_token: Optional[str] = None,
        app_token: Optional[str] = None
    ) -> SlackAdapter:
        """
        Register an agent with the registry and create a Slack adapter for it.
        
        Args:
            agent (BaseAgent): The agent to register
            mention_only (bool, optional): Only respond to mentions. Defaults to False.
            bot_token (str, optional): Slack bot token. Defaults to env var.
            app_token (str, optional): Slack app token. Defaults to env var.
            
        Returns:
            SlackAdapter: The created Slack adapter
        """
        agent_id = agent.name
        
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} already registered. Replacing.")
        
        self.agents[agent_id] = agent
        
        # Create Slack adapter for this agent
        adapter = SlackAdapter(
            agent=agent,
            mention_only=mention_only,
            bot_token=bot_token,
            app_token=app_token
        )
        
        self.adapters[agent_id] = adapter
        logger.info(f"Registered agent {agent_id} with Slack adapter")
        
        return adapter
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id (str): The agent ID
            
        Returns:
            Optional[BaseAgent]: The agent, or None if not found
        """
        return self.agents.get(agent_id)
    
    def get_adapter(self, agent_id: str) -> Optional[SlackAdapter]:
        """
        Get a Slack adapter by agent ID.
        
        Args:
            agent_id (str): The agent ID
            
        Returns:
            Optional[SlackAdapter]: The adapter, or None if not found
        """
        return self.adapters.get(agent_id)
    
    def start_all(self):
        """Start all registered Slack adapters."""
        for agent_id, adapter in self.adapters.items():
            try:
                logger.info(f"Starting Slack adapter for agent {agent_id}")
                adapter.start()
            except Exception as e:
                logger.error(f"Error starting adapter for agent {agent_id}: {e}")
    
    def list_agents(self) -> List[str]:
        """
        List all registered agent IDs.
        
        Returns:
            List[str]: List of agent IDs
        """
        return list(self.agents.keys())
