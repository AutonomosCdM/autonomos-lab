#!/usr/bin/env python
"""
Main entry point for running multiple agents on Slack.
This script demonstrates how to register and run multiple agents
with the AgentRegistry.
"""
import os
import logging
import warnings
import threading
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

from agents.base_agent import BaseAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("slack_multi_agent")

def create_slack_agent() -> BaseAgent:
    """
    Create the Slack agent.
    
    Returns:
        BaseAgent: Configured Slack agent
    """
    return BaseAgent(
        name="Lucius Fox",
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
        name="Alfred Pennyworth",
        personality="meticuloso, analítico y orientado a la investigación",
        primary_objective="Recopilar y sintetizar información técnica relevante",
        llm_model="llama-3.3-70b-versatile",
        temperature=0.6
    )

def start_agent_bot(agent, bot_token, app_token, mention_only=False):
    """
    Start a Slack bot for an agent.
    
    Args:
        agent (BaseAgent): The agent to connect
        bot_token (str): Slack bot token
        app_token (str): Slack app token
        mention_only (bool): Only respond to mentions
    """
    try:
        logger.info(f"Starting bot for agent: {agent.name}")
        logger.info(f"Bot Token: {bot_token[:10]}... (truncated)")
        logger.info(f"App Token: {app_token[:10]}... (truncated)")
        
        # Initialize Slack app
        app = App(token=bot_token)
        
        # Define message handler
        @app.event("message")
        def handle_message(event, say):
            # Skip messages from bots
            if event.get("bot_id"):
                return
            
            # Get channel type
            channel_type = event.get("channel_type", "")
            
            # Handle direct messages
            if channel_type == "im":
                process_message(agent, event, say)
            
            # Handle channel messages with mention
            elif not mention_only or f"<@{app.client.auth_test()['user_id']}>" in event.get("text", ""):
                process_message(agent, event, say)
        
        # Define app_mention handler
        @app.event("app_mention")
        def handle_app_mention(event, say):
            logger.info(f"Received app_mention event for {agent.name}: {event}")
            # Process the mention as a message
            process_message(agent, event, say)
        
        # Initialize Socket Mode handler
        handler = SocketModeHandler(app, app_token)
        
        # Start the handler
        logger.info(f"Starting Socket Mode handler for {agent.name}...")
        handler.start()
        
    except Exception as e:
        logger.error(f"Error starting bot for agent {agent.name}: {e}", exc_info=True)

def process_message(agent, event, say):
    """Process a message and generate a response."""
    try:
        user_id = event.get("user")
        text = event.get("text", "").strip()
        thread_ts = event.get("thread_ts", event.get("ts"))
        
        # Get response from agent
        response = agent.interact(text)
        
        # Send response
        say(text=response["response"], thread_ts=thread_ts)
        
        # Log interaction
        logger.info(f"User: {user_id}, Message: {text}, Response: {response['response']}")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        say(text=f"Lo siento, ocurrió un error al procesar tu mensaje: {str(e)}", thread_ts=thread_ts)

def main():
    """
    Main entry point for the multi-agent Slack bot.
    """
    # Load environment variables with verbose logging
    env_path = Path(os.getcwd()) / '.env'
    logger.info(f"Loading environment variables from: {env_path}")
    
    # Explicitly load environment variables
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    os.environ[key] = value
                    if key.startswith(("SLACK_", "RESEARCH_")):
                        logger.info(f"Loaded env var: {key} (first 10 chars): {value[:10]}")
                except ValueError:
                    logger.warning(f"Could not parse line: {line}")
    
    try:
        # Create agents
        slack_agent = create_slack_agent()
        research_agent = create_research_agent()
        
        # Get tokens
        slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
        slack_app_token = os.environ.get("SLACK_APP_TOKEN")
        research_bot_token = os.environ.get("RESEARCH_BOT_TOKEN")
        research_app_token = os.environ.get("RESEARCH_APP_TOKEN")
        
        # Start Slack agent bot
        slack_thread = threading.Thread(
            target=start_agent_bot,
            args=(slack_agent, slack_bot_token, slack_app_token, False),
            daemon=True
        )
        slack_thread.start()
        
        # Start Research agent bot
        research_thread = threading.Thread(
            target=start_agent_bot,
            args=(research_agent, research_bot_token, research_app_token, True),
            daemon=True
        )
        research_thread.start()
        
        # Keep the main thread alive
        logger.info("Both agents started. Press Enter to exit...")
        input()
        
    except Exception as e:
        logger.error(f"Error starting multi-agent Slack bot: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
