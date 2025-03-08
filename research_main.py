#!/usr/bin/env python
"""
Main entry point for running Research agent.
"""
import os
import logging
import warnings
from pathlib import Path
from dotenv import load_dotenv
import signal
import sys
import threading

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

from agents.search_research_agent import SearchResearchAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="research_agent.log",
    filemode="a"
)
logger = logging.getLogger("research_main")

def create_research_agent() -> SearchResearchAgent:
    """
    Create the Research agent.
    
    Returns:
        SearchResearchAgent: Configured Research agent
    """
    return SearchResearchAgent(
        name="Research Agent",
        personality="metódico, detallado y orientado a la investigación",
        primary_objective="Recopilar y sintetizar información técnica relevante",
        llm_model="llama-3.3-70b-versatile",
        temperature=0.5
    )

def main():
    """
    Main entry point for the Research agent.
    """
    # Explicitly set the path to the .env file
    current_dir = os.getcwd()
    print(f"Current Working Directory: {current_dir}")

    # Construct the path to the .env file
    env_path = Path(current_dir) / '.env'
    print(f"Looking for .env at: {env_path}")

    # Load environment variables with explicit path and verbose logging
    load_dotenv(dotenv_path=env_path, verbose=True)

    # Print all environment variables for debugging
    print("Environment Variables:")
    for key, value in os.environ.items():
        if key.startswith(("RESEARCH_", "GROQ_")):
            print(f"{key}: {value}")

    # Global flag to control agent running state
    agent_running = threading.Event()

    def signal_handler(sig, frame):
        """Handle keyboard interrupt gracefully"""
        print("\nReceived interrupt signal. Shutting down Research agent...")
        agent_running.set()
        sys.exit(0)

    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Create Research agent
        agent = create_research_agent()
        logger.info(f"Created agent: {agent.name}")
        
        # Example research query
        query = "What are the latest advancements in RAG (Retrieval Augmented Generation)?"
        
        # Perform research
        print(f"\nResearching: {query}")
        results = agent.research(query)
        
        # Print results
        print("\nResearch Results:")
        print("=" * 80)
        print(results["results"])
        print("=" * 80)
        
        # Wait for interrupt
        print("\nResearch agent is ready. Press Ctrl+C to exit.")
        agent_running.wait()
        
    except Exception as e:
        logger.error(f"Error running Research agent: {e}")
        raise

if __name__ == "__main__":
    main()
