import pytest
from agents.base_agent import BaseAgent
import os
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv()

class TestBaseAgent:
    @pytest.fixture
    def base_agent(self):
        """Create a base agent for testing"""
        return BaseAgent(
            name="Test Agent",
            personality="testing personality",
            primary_objective="Test the base agent functionality",
            llm_model="llama-3.3-70b-versatile",
            temperature=0.7
        )

    def test_base_agent_initialization(self, base_agent):
        """Test basic agent initialization"""
        assert base_agent.name == "Test Agent"
        assert base_agent.temperature == 0.7
        assert base_agent.model_name == "llama-3.3-70b-versatile"

    def test_base_agent_interaction(self, base_agent):
        """Test agent interaction with real LLM"""
        # Skip test if no API key is available
        groq_key = os.environ.get("SLACK_AGENT_GROQ_API_KEY") or os.environ.get("RESEARCH_AGENT_GROQ_API_KEY")
        if not groq_key:
            pytest.skip("No Groq API key available for testing")

        test_input = "Describe the purpose of an AI agent in a startup"
        response = base_agent.interact(test_input)
        
        assert "response" in response
        assert len(response["response"]) > 0
        assert response["agent_name"] == "Test Agent"

    def test_base_agent_conversation_history(self, base_agent):
        """Test agent's ability to maintain conversation context"""
        # Skip test if no API key is available
        groq_key = os.environ.get("SLACK_AGENT_GROQ_API_KEY") or os.environ.get("RESEARCH_AGENT_GROQ_API_KEY")
        if not groq_key:
            pytest.skip("No Groq API key available for testing")

        # First interaction
        initial_query = "What are the key challenges in AI development?"
        initial_response = base_agent.interact(initial_query)
        
        # Follow-up interaction to test context preservation
        follow_up_query = "Can you elaborate on the points you mentioned earlier?"
        follow_up_response = base_agent.interact(follow_up_query)
        
        assert "response" in follow_up_response
        assert len(follow_up_response["response"]) > 0
        assert follow_up_response["agent_name"] == "Test Agent"

    def test_base_agent_error_handling(self, base_agent):
        """Test agent's error handling capabilities"""
        # Attempt to interact with an extremely long input to test error handling
        long_input = "x" * 10000  # Extremely long input to potentially trigger error handling
        
        try:
            response = base_agent.interact(long_input)
            
            # Basic assertions
            assert "response" in response
            assert len(response["response"]) > 0
            assert response["agent_name"] == "Test Agent"
        except Exception as e:
            # If an exception occurs, ensure it's handled gracefully
            pytest.fail(f"Unexpected error during interaction: {str(e)}")

    def test_base_agent_temperature_variation(self):
        """Test agent's response variation with different temperature settings"""
        # Skip test if no API key is available
        groq_key = os.environ.get("SLACK_AGENT_GROQ_API_KEY") or os.environ.get("RESEARCH_AGENT_GROQ_API_KEY")
        if not groq_key:
            pytest.skip("No Groq API key available for testing")

        # Create agents with different temperature settings
        low_temp_agent = BaseAgent(
            name="Low Temp Agent",
            personality="testing personality",
            primary_objective="Test temperature variation",
            llm_model="llama-3.3-70b-versatile",
            temperature=0.1
        )

        high_temp_agent = BaseAgent(
            name="High Temp Agent",
            personality="testing personality",
            primary_objective="Test temperature variation",
            llm_model="llama-3.3-70b-versatile",
            temperature=0.9
        )

        # Test input
        test_input = "Describe innovation in AI technology"

        # Get responses
        low_temp_response = low_temp_agent.interact(test_input)
        high_temp_response = high_temp_agent.interact(test_input)

        # Assertions
        assert "response" in low_temp_response
        assert "response" in high_temp_response
        assert len(low_temp_response["response"]) > 0
        assert len(high_temp_response["response"]) > 0

        # Optional: Check for meaningful variation (this might need adjustment)
        # The key is that responses are not identical
        assert low_temp_response["response"] != high_temp_response["response"]
