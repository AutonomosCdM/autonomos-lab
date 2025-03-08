import sys
import logging
import warnings
import os
from typing import Dict, Any
from rich.console import Console
from rich.logging import RichHandler
from dotenv import load_dotenv

from agents import BaseAgent

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

# Configure logging - file only, no console output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="[%X]",
    filename="agent_interactions.log",
    filemode="a"
)
logger = logging.getLogger("autonomos_assistant_cli")

class HackathonAgentCLI:
    """
    CLI Interface for the Hackathon Agent
    Provides interactive command-line interaction with the agent
    """
    
    def __init__(
        self, 
        agent: BaseAgent, 
        log_file: str = 'agent_interactions.log'
    ):
        """
        Initialize CLI with a specific agent and logging configuration
        
        Args:
            agent (BaseAgent): The agent to interact with
            log_file (str, optional): Path for logging interactions
        """
        self.agent = agent
        self.console = Console()
        self.conversation_history = []
        
        # Configure file logging
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
    
    def start_interaction(self):
        """
        Start an interactive CLI session with the agent
        """
        self.console.print(f"[bold green]Iniciando interacción con {self.agent.name}[/bold green]")
        self.console.print("[yellow]Escribe 'salir' para terminar la conversación[/yellow]\n")
        
        while True:
            try:
                user_input = self.console.input("[bold blue]Tú: [/bold blue]")
                
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    self.console.print("[bold red]Terminando conversación...[/bold red]")
                    break
                
                # Interact with the agent
                response = self.agent.interact(
                    user_input, 
                    conversation_history="\n".join(self.conversation_history)
                )
                
                # Log response to file only
                logger.info(f"User Input: {user_input}")
                logger.info(f"Agent Response: {response['response']}")
                
                # Display response without any logging info
                self.console.print(f"[bold green]{self.agent.name}: [/bold green]{response['response']}")
                
                # Update conversation history
                self.conversation_history.append(f"User: {user_input}")
                self.conversation_history.append(f"{self.agent.name}: {response['response']}")
            
            except Exception as e:
                logger.error(f"Error during interaction: {e}")
                self.console.print(f"[bold red]Error: {e}[/bold red]")
    
    def run(self):
        """
        Run the CLI application
        """
        try:
            load_dotenv()  # Load environment variables
            self.start_interaction()
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Interacción interrumpida.[/bold red]")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        finally:
            sys.exit(0)
