#!/usr/bin/env python
"""
Test script for Slack Bolt connection.
"""
import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_slack_bolt")

def main():
    """
    Test Slack Bolt connection.
    """
    # Get tokens from environment variables
    bot_token = os.environ.get("SLACK_BOT_TOKEN")
    app_token = os.environ.get("SLACK_APP_TOKEN")
    
    logger.info(f"Bot Token: {bot_token[:10]}... (truncated)")
    logger.info(f"App Token: {app_token[:10]}... (truncated)")
    
    try:
        # Initialize Slack app
        logger.info("Initializing Slack app...")
        app = App(token=bot_token)
        
        # Test auth
        logger.info("Testing auth...")
        auth_test = app.client.auth_test()
        logger.info(f"Auth test result: {auth_test}")
        
        # Initialize Socket Mode handler
        logger.info("Initializing Socket Mode handler...")
        handler = SocketModeHandler(app, app_token)
        
        # Define a simple event handler
        @app.event("message")
        def handle_message(event, say):
            logger.info(f"Received message event: {event}")
            say("Hello from test bot!")
        
        # Start the app
        logger.info("Starting Socket Mode handler...")
        handler.start()
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
