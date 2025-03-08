from typing import Dict, List, Any
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .base_agent import BaseAgent

class HackathonStrategist(BaseAgent):
    """
    Specialized agent for hackathon strategy and project planning.
    Focuses on identifying opportunities, brainstorming ideas, 
    and creating structured project roadmaps.
    """
    
    def __init__(
        self, 
        name: str = "Strategist", 
        personality: str = "analytical, creative, and methodical",
        primary_objective: str = "Develop innovative and feasible hackathon project strategies"
    ):
        super().__init__(
            name=name, 
            personality=personality, 
            primary_objective=primary_objective
        )
        
        # Extend the base prompt template with strategy-specific instructions
        self.strategy_prompt_template = PromptTemplate(
            input_variables=[
                "agent_name", 
                "personality_traits", 
                "primary_objective", 
                "conversation_history",
                "hackathon_context"
            ],
            template="""
            You are {agent_name}, an AI agent specialized in hackathon strategy.
            
            Personality Traits: {personality_traits}
            Primary Objective: {primary_objective}
            
            Hackathon Context:
            {hackathon_context}
            
            Conversation History:
            {conversation_history}
            
            Strategy Generation Guidelines:
            1. Analyze the hackathon theme, constraints, and potential impact
            2. Identify innovative technological solutions
            3. Create a structured project roadmap
            4. Assess technical feasibility and potential challenges
            5. Propose unique value proposition
            
            Respond with a comprehensive and strategic approach, 
            maintaining a creative and analytical perspective.
            """
        )
        
        # Update conversation chain with strategy-specific prompt
        self.strategy_chain = LLMChain(
            llm=self.llm, 
            prompt=self.strategy_prompt_template
        )
    
    def generate_project_strategy(
        self, 
        hackathon_context: Dict[str, Any], 
        conversation_history: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive hackathon project strategy.
        
        Args:
            hackathon_context (Dict[str, Any]): Details about the hackathon
            conversation_history (str, optional): Previous conversation context
        
        Returns:
            Dict[str, Any]: Detailed project strategy
        """
        strategy_response = self.strategy_chain.run(
            agent_name=self.name,
            personality_traits=self.personality,
            primary_objective=self.primary_objective,
            hackathon_context=str(hackathon_context),
            conversation_history=conversation_history
        )
        
        return {
            "strategy": strategy_response,
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "hackathon_context": hackathon_context
        }
