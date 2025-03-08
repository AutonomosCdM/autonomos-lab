#!/usr/bin/env python
"""
Search Research Agent for Autonomos Lab.
Specialized in information gathering and synthesis.
"""
import os
import logging
import json
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from duckduckgo_search import DDGS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="research_agent.log",
    filemode="a"
)
logger = logging.getLogger("research_agent")

class SearchResearchAgent(BaseAgent):
    """
    Search Research Agent specialized in information gathering and synthesis.
    Extends the BaseAgent with research-specific capabilities.
    """
    
    def __init__(
        self,
        name: str = "Research Agent",
        personality: str = "metódico, detallado y orientado a la investigación",
        primary_objective: str = "Recopilar y sintetizar información técnica relevante",
        llm_model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.5
    ):
        """
        Initialize the Research Agent.
        
        Args:
            name (str, optional): Agent name. Defaults to "Research Agent".
            personality (str, optional): Agent personality. Defaults to "metódico, detallado...".
            primary_objective (str, optional): Agent objective. Defaults to "Recopilar y sintetizar...".
            llm_model (str, optional): LLM model to use. Defaults to "llama-3.3-70b-versatile".
            temperature (float, optional): Creativity level. Defaults to 0.5.
        """
        # Initialize base agent
        super().__init__(
            name=name,
            personality=personality,
            primary_objective=primary_objective,
            llm_model=llm_model,
            temperature=temperature
        )
        
        # Research-specific attributes
        self.research_history: List[Dict[str, Any]] = []
        self.sources: List[Dict[str, str]] = []
        
        # Initialize DuckDuckGo search
        self.ddgs = DDGS()
    
    def web_search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Perform a web search using DuckDuckGo.
        
        Args:
            query (str): Search query
            max_results (int, optional): Maximum number of results. Defaults to 5.
        
        Returns:
            List[Dict[str, str]]: Search results
        """
        logger.info(f"Performing web search for: {query}")
        
        try:
            # Perform the search
            results = list(self.ddgs.text(query, max_results=max_results))
            
            # Process and store sources
            for result in results:
                self.add_source(
                    title=result.get('title', 'Unknown Title'),
                    url=result.get('href', ''),
                    relevance=1.0
                )
            
            logger.info(f"Found {len(results)} web search results")
            return results
        except Exception as e:
            logger.error(f"Error during web search: {e}")
            return []
    
    def research(self, query: str, max_sources: int = 5) -> Dict[str, Any]:
        """
        Perform research on a given query.
        
        Args:
            query (str): Research query
            max_sources (int, optional): Maximum number of sources to use. Defaults to 5.
        
        Returns:
            Dict[str, Any]: Research results
        """
        logger.info(f"Performing research on: {query}")
        
        # Perform web search
        search_results = self.web_search(query, max_results=max_sources)
        
        # Format search results for the LLM
        formatted_results = ""
        if search_results:
            formatted_results = "Web Search Results:\n\n"
            for i, result in enumerate(search_results, 1):
                formatted_results += f"{i}. Title: {result.get('title', 'Unknown')}\n"
                formatted_results += f"   URL: {result.get('href', '')}\n"
                formatted_results += f"   Snippet: {result.get('body', '')}\n\n"
        else:
            formatted_results = "No web search results found."
        
        # Interact with LLM to get research plan
        research_plan = self.interact(
            f"You are a research planning assistant. Create a step-by-step plan to research the following query: {query}\n\nConsider these web search results:\n\n{formatted_results}"
        )
        
        # Execute research plan with web search results
        research_results = self.interact(
            f"You are a research agent. Execute the following research plan and provide detailed, well-structured results with citations. Use the web search results as your primary sources.\n\nPlan: {research_plan['response']}\n\nWeb Search Results:\n{formatted_results}\n\nQuery: {query}"
        )
        
        # Store research in history
        self.research_history.append({
            "query": query,
            "plan": research_plan["response"],
            "results": research_results["response"],
            "web_results": search_results
        })
        
        return {
            "query": query,
            "results": research_results["response"],
            "sources": self.sources[-max_sources:] if self.sources else []
        }
    
    def synthesize(self, research_results: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Synthesize multiple research results into a cohesive summary.
        
        Args:
            research_results (List[Dict[str, Any]]): List of research results
        
        Returns:
            Dict[str, str]: Synthesis results
        """
        logger.info(f"Synthesizing {len(research_results)} research results")
        
        # Combine research results
        combined_results = "\n\n".join([
            f"Research on '{result['query']}':\n{result['results']}"
            for result in research_results
        ])
        
        # Interact with LLM to synthesize results
        synthesis = self.interact(
            f"You are a research synthesis expert. Create a comprehensive, well-structured synthesis of the following research results:\n\n{combined_results}"
        )
        
        return {
            "synthesis": synthesis["response"],
            "source_count": len(research_results)
        }
    
    def add_source(self, title: str, url: str, relevance: float = 1.0) -> None:
        """
        Add a source to the agent's source list.
        
        Args:
            title (str): Source title
            url (str): Source URL
            relevance (float, optional): Relevance score (0-1). Defaults to 1.0.
        """
        self.sources.append({
            "title": title,
            "url": url,
            "relevance": relevance
        })
        logger.info(f"Added source: {title}")
