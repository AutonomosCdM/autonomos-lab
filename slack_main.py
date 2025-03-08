#!/usr/bin/env python
"""
Main entry point for running Slack agent on Slack.
"""
import os
import logging
import warnings
from pathlib import Path
from dotenv import load_dotenv
import signal
import sys
import threading
import multiprocessing
from flask import Flask, jsonify

# Global variables for health check
slack_adapter = None
agent = None

# Create a Flask app for health checks
health_app = Flask(__name__)

@health_app.route('/health')
def health_check():
    """
    Provide a simple health check endpoint for Railway deployment
    """
    return jsonify({
        "status": "healthy",
        "agent": "HackathonAgents",
        "version": "0.1.0",
        "slack_connected": slack_adapter is not None
    }), 200

def run_health_server():
    """
    Run the health check server in a separate process
    """
    health_app.run(host='0.0.0.0', port=8000)

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

from agents.base_agent import BaseAgent
from slack.base_adapter import SlackAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="slack_bot.log",
    filemode="a"
)
logger = logging.getLogger("slack_main")

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

def main():
    """
    Main entry point for the Slack bot.
    """
    global slack_adapter, agent

    # Start health check server in a separate process
    health_server_process = multiprocessing.Process(target=run_health_server, daemon=True)
    health_server_process.start()

    # Explicitly set the path to the .env file
    current_dir = os.getcwd()
    print(f"Current Working Directory: {current_dir}")

    # Construct the path to the .env file
    env_path = Path(current_dir) / '.env'
    print(f"Looking for .env at: {env_path}")

    # Load environment variables with explicit path and verbose logging
    load_dotenv(dotenv_path=env_path, verbose=True)

    # Manually set environment variables from .env file
    with open(env_path, 'r') as f:
        content = f.read()
        # Remove the first line (comment) and any surrounding quotes
        content = content.split('\n', 1)[1].strip().strip('"')
        
        # Parse each line
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle potential parsing issues
                try:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    if key.startswith(("SLACK_", "GROQ_")):
                        os.environ[key] = value
                except ValueError:
                    logger.warning(f"Could not parse line: {line}")

    # Print all environment variables for debugging
    print("Environment Variables:")
    for key, value in os.environ.items():
        if key.startswith(("SLACK_", "GROQ_")):
            print(f"{key}: {value}")

    # Global flag to control bot running state
    bot_running = threading.Event()

    def signal_handler(sig, frame):
        """Handle keyboard interrupt gracefully"""
        print("\nReceived interrupt signal. Shutting down Slack bot...")
        bot_running.set()
        sys.exit(0)

    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Create Slack agent
        agent = create_slack_agent()
        logger.info(f"Created agent: {agent.name}")
        
        # Create Slack adapter with explicit tokens
        slack_adapter = SlackAdapter(
            agent=agent,
            mention_only=False,  # Respond to all messages, not just mentions
            bot_token=os.environ.get("SLACK_BOT_TOKEN"),
            app_token=os.environ.get("SLACK_APP_TOKEN")
        )
        
        # Log token status for debugging
        logger.info(f"Bot token present: {bool(os.environ.get('SLACK_BOT_TOKEN'))}")
        logger.info(f"App token present: {bool(os.environ.get('SLACK_APP_TOKEN'))}")
        
        logger.info("Created Slack adapter")
        
        # Start the Slack bot in a separate thread
        def start_bot():
            try:
                slack_adapter.start()
            except Exception as e:
                logger.error(f"Error in Slack bot thread: {e}")
                bot_running.set()

        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()

        logger.info("Slack bot started. Press Ctrl+C to exit.")
        
        # Wait for interrupt
        bot_running.wait()
        
    except Exception as e:
        logger.error(f"Error starting Slack bot: {e}")
        raise

if __name__ == "__main__":
    main()
