import logging
import warnings
import os
from dotenv import load_dotenv

# Suppress all warnings before any imports
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

# Filter out specific LangChain deprecation warnings
import importlib
original_import = importlib.__import__

def custom_import(name, *args, **kwargs):
    # Suppress specific warning during import
    if 'langchain' in name or 'pydantic' in name:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            return original_import(name, *args, **kwargs)
    return original_import(name, *args, **kwargs)

importlib.__import__ = custom_import

from agents import BaseAgent
from cli import HackathonAgentCLI

def create_autonomos_agent() -> BaseAgent:
    """
    Create a base agent for Autonomos Lab assistant.
    
    Returns:
        BaseAgent: Configured agent for CLI interaction
    """
    return BaseAgent(
        name="AutonomousAssistant",
        personality="innovador, analítico y orientado a soluciones",
        primary_objective="Asistir al equipo de Autonomos Lab en el desarrollo de productos y servicios innovadores",
        llm_model="llama-3.3-70b-versatile",  # Updated to the correct Groq model name
        temperature=0.7
    )

def main():
    """
    Main entry point for the Autonomos Lab Assistant CLI application
    """
    # Configure logging to file only
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename="app.log",
        filemode="a"
    )
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Create agent
        agent = create_autonomos_agent()
        
        # Initialize and run CLI
        cli = HackathonAgentCLI(agent)
        cli.run()
    
    except Exception as e:
        logging.error(f"Error initializing Autonomos Assistant: {e}")
        raise

if __name__ == "__main__":
    main()
