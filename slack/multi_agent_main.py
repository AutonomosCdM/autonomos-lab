#!/usr/bin/env python
"""
Main entry point for running multiple agents on Slack.
This script demonstrates how to register and run multiple agents
with the AgentRegistry.
"""
import os
import logging
import warnings
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

from agents.base_agent import BaseAgent
from slack.agent_registry import AgentRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="slack_multi_agent.log",
    filemode="a"
)
logger = logging.getLogger("slack_multi_agent")

def create_slack_agent() -> BaseAgent:
    """
    Create the Slack agent.
    
    Returns:
        BaseAgent: Configured Slack agent
    """
    return BaseAgent(
        name="Slack Agent",
        personality="innovador, analítico y orientado a soluciones",
        primary_objective="Asistir al equipo de Autonomos Lab en el desarrollo de productos y servicios innovadores",
        llm_model="llama-3.3-70b-versatile",
        temperature=0.7
    )

def create_research_agent() -> BaseAgent:
    """
    Create the Research agent.
    
    Returns:
        BaseAgent: Configured Research agent
    """
    return BaseAgent(
        name="Research Agent",
        personality="meticuloso, analítico y orientado a la investigación",
        primary_objective="Recopilar y sintetizar información técnica relevante",
        llm_model="llama-3.3-70b-versatile",
        temperature=0.6
    )

def main():
    """
    Main entry point for the multi-agent Slack bot.
    """
    # Load environment variables
    load_dotenv()
    
    try:
        # Create agent registry
        registry = AgentRegistry()
        logger.info("Created agent registry")
        
        # Create and register Slack agent
        slack_agent = create_slack_agent()
        registry.register_agent(slack_agent, mention_only=False)
        logger.info(f"Registered agent: {slack_agent.name}")
        
        # Create and register Research agent
        research_agent = create_research_agent()
        registry.register_agent(research_agent, mention_only=True)
        logger.info(f"Registered agent: {research_agent.name}")
        
        # List registered agents
        agents = registry.list_agents()
        logger.info(f"Registered agents: {agents}")
        
        # Start all agents
        logger.info("Starting all Slack adapters...")
        registry.start_all()
        
    except Exception as e:
        logger.error(f"Error starting multi-agent Slack bot: {e}")
        raise

if __name__ == "__main__":
    main()
