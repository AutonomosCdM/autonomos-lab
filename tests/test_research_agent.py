import pytest
from agents.base_agent import BaseAgent
import os
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv()

class TestResearchAgent:
    @pytest.fixture
    def research_agent(self):
        """Create a Research agent for testing"""
        return BaseAgent(
            name="Research Agent",
            personality="meticuloso, analítico y orientado a la investigación",
            primary_objective="Recopilar y sintetizar información técnica relevante",
            llm_model="llama-3.3-70b-versatile",
            temperature=0.6
        )

    def test_agent_initialization(self, research_agent):
        """Test basic agent initialization"""
        assert research_agent.name == "Research Agent"
        assert research_agent.temperature == 0.6
        assert research_agent.model_name == "llama-3.3-70b-versatile"

    def test_agent_research_interaction(self, research_agent):
        """Test agent's research-oriented interaction"""
        test_input = "Describe recent trends in AI and machine learning"
        response = research_agent.interact(test_input)
        
        assert "response" in response
        assert len(response["response"]) > 0
        assert response["agent_name"] == "Research Agent"

    def test_groq_api_connection(self, research_agent):
        """Test connection to Groq API for Research Agent"""
        assert os.environ.get("RESEARCH_AGENT_GROQ_API_KEY"), "Research Agent Groq API Key is not set"
        
        # Attempt to interact with the agent to test API connection
        test_input = "Verify Groq API connection for Research Agent"
        response = research_agent.interact(test_input)
        
        assert "response" in response
        assert len(response["response"]) > 0

    def test_research_context_handling(self, research_agent):
        """Test agent's ability to maintain context in research-oriented conversations"""
        # First interaction
        initial_query = "What are the latest advancements in machine learning?"
        initial_response = research_agent.interact(initial_query)
        
        # Follow-up interaction to test context preservation
        follow_up_query = "Can you elaborate on the points you mentioned earlier?"
        follow_up_response = research_agent.interact(follow_up_query)
        
        assert "response" in follow_up_response
        assert len(follow_up_response["response"]) > 0
        assert follow_up_response["agent_name"] == "Research Agent"
