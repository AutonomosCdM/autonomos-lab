from typing import Dict, List, Any
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .base_agent import BaseAgent

class ProjectStrategist(BaseAgent):
    """
    Specialized agent for project strategy and planning.
    Focuses on identifying opportunities, brainstorming ideas, 
    and creating structured project roadmaps.
    """
    
    def __init__(
        self, 
        name: str = "Strategist", 
        personality: str = "analytical, creative, and methodical",
        primary_objective: str = "Develop innovative and feasible project strategies"
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
                "project_context"
            ],
            template="""
            You are {agent_name}, an AI agent specialized in project strategy.
            
            Personality Traits: {personality_traits}
            Primary Objective: {primary_objective}
            
            Project Context:
            {project_context}
            
            Conversation History:
            {conversation_history}
            
            Strategy Generation Guidelines:
            1. Analyze the project theme, constraints, and potential impact
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
        project_context: Dict[str, Any], 
        conversation_history: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive project strategy.
        
        Args:
            project_context (Dict[str, Any]): Details about the project
            conversation_history (str, optional): Previous conversation context
        
        Returns:
            Dict[str, Any]: Detailed project strategy
        """
        strategy_response = self.strategy_chain.run(
            agent_name=self.name,
            personality_traits=self.personality,
            primary_objective=self.primary_objective,
            project_context=str(project_context),
            conversation_history=conversation_history
        )
        
        return {
            "strategy": strategy_response,
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "project_context": project_context
        }
