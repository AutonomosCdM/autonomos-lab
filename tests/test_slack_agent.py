import pytest
from agents.base_agent import BaseAgent
from slack.base_adapter import SlackAdapter
import os
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv()

class TestSlackAgent:
    @pytest.fixture
    def slack_agent(self):
        """Create a Slack agent for testing"""
        return BaseAgent(
            name="Slack Agent",
            personality="innovador, analítico y orientado a soluciones",
            primary_objective="Asistir al equipo de Autonomos Lab en el desarrollo de productos y servicios innovadores",
            llm_model="llama-3.3-70b-versatile",
            temperature=0.7
        )

    def test_agent_initialization(self, slack_agent):
        """Test basic agent initialization"""
        assert slack_agent.name == "Slack Agent"
        assert slack_agent.temperature == 0.7
        assert slack_agent.model_name == "llama-3.3-70b-versatile"

    def test_agent_interaction(self, slack_agent):
        """Test agent interaction with real LLM"""
        test_input = "Describe the main goals of Autonomos Lab"
        response = slack_agent.interact(test_input)
        
        assert "response" in response
        assert len(response["response"]) > 0
        assert response["agent_name"] == "Slack Agent"

    def test_slack_adapter_configuration(self, slack_agent):
        """Test Slack adapter configuration with real tokens"""
        # Verify required environment variables are set
        assert os.environ.get("SLACK_BOT_TOKEN"), "Slack Bot Token is not set"
        assert os.environ.get("SLACK_APP_TOKEN"), "Slack App Token is not set"

        # Create Slack adapter
        slack_adapter = SlackAdapter(
            agent=slack_agent,
            mention_only=False,
            bot_token=os.environ.get("SLACK_BOT_TOKEN"),
            app_token=os.environ.get("SLACK_APP_TOKEN")
        )

        assert slack_adapter is not None
        assert slack_adapter.agent == slack_agent
        assert slack_adapter.mention_only == False

    def test_groq_api_connection(self, slack_agent):
        """Test connection to Groq API"""
        assert os.environ.get("SLACK_AGENT_GROQ_API_KEY"), "Groq API Key is not set"
        
        # Attempt to interact with the agent to test API connection
        test_input = "Verify Groq API connection"
        response = slack_agent.interact(test_input)
        
        assert "response" in response
        assert len(response["response"]) > 0
