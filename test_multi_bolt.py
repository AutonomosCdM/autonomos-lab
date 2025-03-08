#!/usr/bin/env python
"""
Test script for multiple Slack Bolt connections.
"""
import os
import logging
import threading
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_multi_bolt")

def start_bot(name, bot_token, app_token):
    """
    Start a Slack bot with the given tokens.
    
    Args:
        name (str): Name of the bot
        bot_token (str): Slack bot token
        app_token (str): Slack app token
    """
    logger.info(f"Starting {name} bot...")
    logger.info(f"{name} Bot Token: {bot_token[:10]}... (truncated)")
    logger.info(f"{name} App Token: {app_token[:10]}... (truncated)")
    
    try:
        # Initialize Slack app
        logger.info(f"Initializing {name} Slack app...")
        app = App(token=bot_token)
        
        # Test auth
        logger.info(f"Testing {name} auth...")
        auth_test = app.client.auth_test()
        logger.info(f"{name} Auth test result: {auth_test}")
        
        # Initialize Socket Mode handler
        logger.info(f"Initializing {name} Socket Mode handler...")
        handler = SocketModeHandler(app, app_token)
        
        # Define a simple event handler
        @app.event("message")
        def handle_message(event, say):
            logger.info(f"{name} received message event: {event}")
            say(f"Hello from {name}!")
        
        # Start the app
        logger.info(f"Starting {name} Socket Mode handler...")
        handler.start()
        
    except Exception as e:
        logger.error(f"Error starting {name} bot: {e}", exc_info=True)

def main():
    """
    Test multiple Slack Bolt connections.
    """
    # Get tokens from environment variables
    lucius_bot_token = os.environ.get("SLACK_BOT_TOKEN")
    lucius_app_token = os.environ.get("SLACK_APP_TOKEN")
    alfred_bot_token = os.environ.get("RESEARCH_BOT_TOKEN")
    alfred_app_token = os.environ.get("RESEARCH_APP_TOKEN")
    
    # Start Lucius Fox bot
    lucius_thread = threading.Thread(
        target=start_bot,
        args=("Lucius Fox", lucius_bot_token, lucius_app_token),
        daemon=True
    )
    lucius_thread.start()
    
    # Start Alfred Pennyworth bot
    alfred_thread = threading.Thread(
        target=start_bot,
        args=("Alfred Pennyworth", alfred_bot_token, alfred_app_token),
        daemon=True
    )
    alfred_thread.start()
    
    # Keep the main thread alive
    try:
        logger.info("Both bots started. Press Ctrl+C to exit.")
        lucius_thread.join()
        alfred_thread.join()
    except KeyboardInterrupt:
        logger.info("Exiting...")

if __name__ == "__main__":
    main()
