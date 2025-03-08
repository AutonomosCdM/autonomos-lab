from typing import Dict, Any, Optional, List, Union
import uuid
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse

from core.error_handler import AgentError, ErrorSeverity
from core.structured_logger import StructuredLogger
from security.credential_store import CredentialStore
from core.config_manager import ConfigManager

class SlackIntegrationError(AgentError):
    """Exception raised for Slack integration-related errors."""
    pass

class MessageFormatter:
    """
    Handles formatting of messages for optimal Slack interface presentation.
    """
    @staticmethod
    def format_message(
        text: str, 
        blocks: Optional[List[Dict[str, Any]]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Format a message for Slack with optional rich formatting.
        
        :param text: Basic text message
        :param blocks: Optional Slack Block Kit blocks
        :param attachments: Optional message attachments
        :return: Formatted message dictionary
        """
        message = {"text": text}
        
        if blocks:
            message["blocks"] = blocks
        
        if attachments:
            message["attachments"] = attachments
        
        return message

class ConversationTracker:
    """
    Tracks Slack conversation threads and provides context management.
    """
    def __init__(self, logger: Optional[StructuredLogger] = None):
        """
        Initialize conversation tracker.
        
        :param logger: Optional structured logger
        """
        self._conversations: Dict[str, Dict[str, Any]] = {}
        self._logger = logger or StructuredLogger()

    def track_conversation(
        self, 
        channel_id: str, 
        thread_ts: Optional[str] = None,
        message_data: Optional[Dict[str, Any]] = None
    ):
        """
        Track a conversation thread.
        
        :param channel_id: Slack channel ID
        :param thread_ts: Thread timestamp
        :param message_data: Optional message metadata
        """
        conversation_key = f"{channel_id}:{thread_ts or 'root'}"
        
        if conversation_key not in self._conversations:
            self._conversations[conversation_key] = {
                "channel_id": channel_id,
                "thread_ts": thread_ts,
                "messages": [],
                "metadata": {}
            }
        
        if message_data:
            self._conversations[conversation_key]["messages"].append(message_data)
            
            self._logger.track_event(
                "slack_conversation_tracked",
                {
                    "channel_id": channel_id,
                    "thread_ts": thread_ts,
                    "message_count": len(self._conversations[conversation_key]["messages"])
                }
            )

    def get_conversation_context(
        self, 
        channel_id: str, 
        thread_ts: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve conversation context.
        
        :param channel_id: Slack channel ID
        :param thread_ts: Thread timestamp
        :param limit: Maximum number of messages to return
        :return: List of recent messages
        """
        conversation_key = f"{channel_id}:{thread_ts or 'root'}"
        
        if conversation_key not in self._conversations:
            return []
        
        return self._conversations[conversation_key]["messages"][-limit:]

class EventHandler:
    """
    Manages Slack events like mentions, messages, and interactions.
    """
    def __init__(
        self, 
        slack_client: 'SlackClient',
        conversation_tracker: Optional[ConversationTracker] = None,
        logger: Optional[StructuredLogger] = None
    ):
        """
        Initialize event handler.
        
        :param slack_client: Slack client instance
        :param conversation_tracker: Optional conversation tracker
        :param logger: Optional structured logger
        """
        self._slack_client = slack_client
        self._conversation_tracker = conversation_tracker or ConversationTracker()
        self._logger = logger or StructuredLogger()
        
        # Event type to handler mapping
        self._event_handlers = {
            "message": self._handle_message,
            "app_mention": self._handle_mention
        }

    def handle_event(self, event: Dict[str, Any]):
        """
        Route events to appropriate handlers.
        
        :param event: Slack event payload
        """
        event_type = event.get("type")
        
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type](event)
            except Exception as e:
                self._logger.log(
                    f"Error handling {event_type} event",
                    level=ErrorSeverity.WARNING.value,
                    extra={
                        "event_type": event_type,
                        "error": str(e)
                    }
                )
        else:
            self._logger.log(
                f"Unhandled event type: {event_type}",
                level=ErrorSeverity.INFO.value,
                extra={"event_type": event_type}
            )

    def _handle_message(self, event: Dict[str, Any]):
        """
        Handle standard message events.
        
        :param event: Message event payload
        """
        channel_id = event.get("channel")
        thread_ts = event.get("thread_ts")
        
        self._conversation_tracker.track_conversation(
            channel_id, 
            thread_ts, 
            event
        )

    def _handle_mention(self, event: Dict[str, Any]):
        """
        Handle app mention events.
        
        :param event: App mention event payload
        """
        channel_id = event.get("channel")
        thread_ts = event.get("thread_ts")
        
        # Additional processing for mentions
        self._conversation_tracker.track_conversation(
            channel_id, 
            thread_ts, 
            event
        )

class SlackClient:
    """
    Unified Slack API client with comprehensive integration capabilities.
    """
    def __init__(
        self, 
        bot_token: str,
        app_token: Optional[str] = None,
        config_manager: Optional[ConfigManager] = None,
        credential_store: Optional[CredentialStore] = None,
        logger: Optional[StructuredLogger] = None
    ):
        """
        Initialize Slack client with comprehensive configuration.
        
        :param bot_token: Slack Bot User OAuth Token
        :param app_token: Slack App-Level Token (for Socket Mode)
        :param config_manager: Optional configuration manager
        :param credential_store: Optional credential store
        :param logger: Optional structured logger
        """
        self._bot_token = bot_token
        self._app_token = app_token
        
        # Initialize Slack WebClient
        self._web_client = WebClient(token=bot_token)
        
        # Optional components
        self._config_manager = config_manager or ConfigManager()
        self._credential_store = credential_store or CredentialStore()
        self._logger = logger or StructuredLogger()
        
        # Initialize sub-components
        self._conversation_tracker = ConversationTracker(self._logger)
        self._message_formatter = MessageFormatter()
        self._event_handler = EventHandler(
            self, 
            self._conversation_tracker, 
            self._logger
        )
        
        # Socket Mode client for real-time events (optional)
        self._socket_mode_client = None
        if app_token:
            self._socket_mode_client = SocketModeClient(
                app_token=app_token,
                web_client=self._web_client
            )

    def send_message(
        self, 
        channel: str, 
        text: str, 
        thread_ts: Optional[str] = None,
        blocks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a Slack channel.
        
        :param channel: Channel or user ID
        :param text: Message text
        :param thread_ts: Optional thread timestamp for threaded messages
        :param blocks: Optional Slack Block Kit blocks
        :return: API response
        """
        try:
            formatted_message = self._message_formatter.format_message(
                text, blocks=blocks
            )
            
            response = self._web_client.chat_postMessage(
                channel=channel,
                **formatted_message,
                thread_ts=thread_ts
            )
            
            self._logger.track_event(
                "slack_message_sent", 
                {
                    "channel": channel,
                    "thread_ts": thread_ts,
                    "message_ts": response.get("ts")
                }
            )
            
            return response
        except SlackApiError as e:
            raise SlackIntegrationError(
                f"Failed to send Slack message: {e.response['error']}",
                severity=ErrorSeverity.ERROR
            )

    def start_socket_mode(self):
        """
        Start Socket Mode for real-time event listening.
        """
        if not self._socket_mode_client:
            raise SlackIntegrationError(
                "Socket Mode not configured. Provide an app token during initialization.",
                severity=ErrorSeverity.ERROR
            )
        
        def process_event(client: SocketModeClient, req: SocketModeRequest):
            """
            Process incoming Socket Mode events.
            
            :param client: Socket Mode client
            :param req: Socket Mode request
            """
            if req.type == "events_api":
                event = req.payload.get("event", {})
                self._event_handler.handle_event(event)
            
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)
        
        self._socket_mode_client.socket_mode_request_listeners.append(process_event)
        self._socket_mode_client.connect()
        
        self._logger.track_event(
            "slack_socket_mode_started",
            {"app_token": bool(self._app_token)}
        )

class AppManifestGenerator:
    """
    Generates dynamic Slack app manifests for configuration and deployment.
    """
    @staticmethod
    def generate_manifest(
        app_name: str,
        bot_scopes: List[str],
        event_subscriptions: Optional[List[str]] = None,
        socket_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a Slack app manifest.
        
        :param app_name: Name of the Slack app
        :param bot_scopes: List of bot token scopes
        :param event_subscriptions: Optional list of subscribed event types
        :param socket_mode: Enable Socket Mode
        :return: Slack app manifest dictionary
        """
        manifest = {
            "display_information": {
                "name": app_name
            },
            "features": {
                "bot_user": {
                    "display_name": app_name
                }
            },
            "oauth_config": {
                "scopes": {
                    "bot": bot_scopes
                }
            }
        }
        
        if event_subscriptions:
            manifest["features"]["event_subscriptions"] = {
                "request_url": "",  # Replace with your event endpoint
                "bot_events": event_subscriptions
            }
        
        if socket_mode:
            manifest["features"]["socket_mode_enabled"] = True
        
        return manifest
