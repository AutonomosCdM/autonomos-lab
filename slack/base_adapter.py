"""
Base adapter for Slack integration with Autonomos Lab agents.
"""
import os
import logging
import threading
from typing import Dict, Any, List, Optional, Callable
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from agents.base_agent import BaseAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="slack_bot.log",
    filemode="a"
)
logger = logging.getLogger("slack_adapter")

class SlackAdapter:
    """
    Base adapter for connecting agents to Slack.
    This class handles the connection to Slack API and event processing.
    """
    
    def __init__(
        self,
        agent: BaseAgent,
        bot_token: Optional[str] = None,
        app_token: Optional[str] = None,
        mention_only: bool = False
    ):
        """
        Initialize the Slack adapter.
        
        Args:
            agent (BaseAgent): The agent to connect to Slack
            bot_token (str, optional): Slack bot token. Defaults to env var SLACK_BOT_TOKEN.
            app_token (str, optional): Slack app token. Defaults to env var SLACK_APP_TOKEN.
            mention_only (bool, optional): Only respond to mentions. Defaults to False.
        """
        self.agent = agent
        self.mention_only = mention_only
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        
        # Get tokens from parameters or environment variables
        self.bot_token = bot_token or os.environ.get("SLACK_BOT_TOKEN")
        self.app_token = app_token or os.environ.get("SLACK_APP_TOKEN")
        
        if not self.bot_token or not self.app_token:
            raise ValueError("Slack tokens not provided. Set SLACK_BOT_TOKEN and SLACK_APP_TOKEN environment variables.")
        
        # Initialize Slack app
        self.app = App(token=self.bot_token)
        
        # Register event handlers
        self._register_event_handlers()
    
    def _register_event_handlers(self):
        """Register event handlers for Slack events."""
        
        # Handle direct messages
        @self.app.event("message")
        def handle_message(event, say):
            # Skip messages from bots
            if event.get("bot_id"):
                return
            
            # Get channel type
            channel_type = event.get("channel_type", "")
            
            # Handle direct messages
            if channel_type == "im":
                self._process_message(event, say)
            
            # Handle channel messages with mention
            elif not self.mention_only or f"<@{self.app.client.auth_test()['user_id']}>" in event.get("text", ""):
                self._process_message(event, say)
    
    def _process_message(self, event, say):
        """Process a message and generate a response."""
        try:
            user_id = event.get("user")
            channel_id = event.get("channel")
            text = event.get("text", "").strip()
            thread_ts = event.get("thread_ts", event.get("ts"))
            
            # Get conversation history for this channel/thread
            history_key = f"{channel_id}:{thread_ts}"
            if history_key not in self.conversation_history:
                self.conversation_history[history_key] = []
            
            # Add user message to history
            self.conversation_history[history_key].append({
                "role": "user",
                "content": text
            })
            
            # Convert history to string format expected by the agent
            history_str = self._format_history_for_agent(self.conversation_history[history_key])
            
            # Get response from agent
            response = self.agent.interact(text, conversation_history=history_str)
            
            # Add agent response to history
            self.conversation_history[history_key].append({
                "role": "assistant",
                "content": response["response"]
            })
            
            # Send response
            say(text=response["response"], thread_ts=thread_ts)
            
            # Log interaction
            logger.info(f"User: {user_id}, Message: {text}, Response: {response['response']}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            say(text=f"Lo siento, ocurrió un error al procesar tu mensaje: {str(e)}", thread_ts=thread_ts)
    
    def _format_history_for_agent(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history for the agent."""
        formatted_history = ""
        
        for message in history:
            role = "User" if message["role"] == "user" else self.agent.name
            formatted_history += f"{role}: {message['content']}\n"
        
        return formatted_history
    
    def start(self):
        """Start the Slack bot."""
        try:
            logger.info(f"Starting Slack bot for agent: {self.agent.name}")
            logger.info(f"Bot Token: {self.bot_token[:10]}... (truncated)")
            logger.info(f"App Token: {self.app_token[:10]}... (truncated)")
            
            # Validate tokens
            if not self.bot_token or not self.app_token:
                raise ValueError("Bot or App token is missing")
            
            # Create SocketModeHandler
            handler = SocketModeHandler(self.app, self.app_token)
            
            # Log additional connection details
            logger.info("Initializing Socket Mode connection...")
            
            # Start the handler in a separate thread
            def start_handler():
                try:
                    handler.start()
                except Exception as e:
                    logger.error(f"Error in Slack bot thread: {e}")
            
            bot_thread = threading.Thread(target=start_handler, daemon=True)
            bot_thread.start()
            
            logger.info("Slack bot started successfully in background thread")
            
            # Optional: Keep the main thread alive if needed
            # bot_thread.join()
        except Exception as e:
            logger.error(f"Detailed error starting Slack bot: {e}")
            logger.exception("Full error traceback:")
            raise
