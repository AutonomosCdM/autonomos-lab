from typing import Dict, Any, Optional, List, Callable, Union
import json
import uuid
from core.prompt_template import PromptTemplate, PromptType
from core.prompt_composer import PromptComposer
from core.tool_registry import ToolRegistry
from core.error_handler import AgentError, ErrorSeverity
from enum import Enum, auto

class PersonalityComponentError(AgentError):
    """Exception raised for personality component-related errors."""
    pass

class PersonalityDimension(Enum):
    """
    Enumeration of personality dimensions for agent characterization.
    """
    CREATIVITY = auto()
    ANALYTICAL = auto()
    EMPATHY = auto()
    ASSERTIVENESS = auto()
    CURIOSITY = auto()
    ADAPTABILITY = auto()
    RISK_TOLERANCE = auto()
    COLLABORATION = auto()

class PersonalityTrait:
    """
    Represents a specific trait or behavior component of an agent's personality.
    """
    def __init__(
        self, 
        name: str, 
        description: str,
        dimension: PersonalityDimension,
        prompt_template: Optional[PromptTemplate] = None,
        behavior_func: Optional[Callable] = None,
        intensity: float = 0.5
    ):
        """
        Initialize a personality trait.
        
        :param name: Name of the trait
        :param description: Detailed description of the trait
        :param dimension: Personality dimension this trait belongs to
        :param prompt_template: Optional prompt template for trait expression
        :param behavior_func: Optional function to modify agent behavior
        :param intensity: Trait intensity (0.0 to 1.0)
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.dimension = dimension
        self.prompt_template = prompt_template
        self.behavior_func = behavior_func
        
        # Validate intensity
        if not 0 <= intensity <= 1:
            raise PersonalityComponentError(
                f"Trait intensity must be between 0 and 1, got {intensity}",
                severity=ErrorSeverity.ERROR
            )
        self.intensity = intensity

    def apply_trait(
        self, 
        context: Dict[str, Any], 
        tools: Optional[ToolRegistry] = None
    ) -> Dict[str, Any]:
        """
        Apply the trait's influence to a given context.
        
        :param context: Current agent context
        :param tools: Optional tool registry for trait-specific actions
        :return: Modified context
        """
        # Apply prompt template if exists
        if self.prompt_template:
            context['trait_prompt'] = self.prompt_template.render(
                variables={'intensity': self.intensity},
                context=context
            )
        
        # Apply behavior function if exists
        if self.behavior_func:
            try:
                context = self.behavior_func(context, self.intensity, tools)
            except Exception as e:
                raise PersonalityComponentError(
                    f"Error applying trait behavior: {str(e)}",
                    severity=ErrorSeverity.WARNING,
                    context={'trait': self.name, 'error': str(e)}
                )
        
        return context

class PersonalityProfile:
    """
    Comprehensive personality profile for an agent.
    """
    def __init__(
        self, 
        name: str,
        traits: Optional[List[PersonalityTrait]] = None,
        description: Optional[str] = None
    ):
        """
        Initialize a personality profile.
        
        :param name: Name of the personality profile
        :param traits: List of personality traits
        :param description: Optional description of the profile
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description or ""
        self._traits: Dict[str, PersonalityTrait] = {}
        
        # Add initial traits
        if traits:
            for trait in traits:
                self.add_trait(trait)

    def add_trait(
        self, 
        trait: Union[PersonalityTrait, Dict[str, Any]]
    ):
        """
        Add a trait to the personality profile.
        
        :param trait: Trait to add (PersonalityTrait or trait configuration)
        """
        # Convert dict to PersonalityTrait if needed
        if isinstance(trait, dict):
            trait = PersonalityTrait(
                name=trait.get('name', 'Unnamed Trait'),
                description=trait.get('description', ''),
                dimension=trait.get('dimension', PersonalityDimension.ADAPTABILITY),
                intensity=trait.get('intensity', 0.5)
            )
        
        # Check for duplicate traits
        if trait.name in self._traits:
            raise PersonalityComponentError(
                f"Trait '{trait.name}' already exists in profile",
                severity=ErrorSeverity.WARNING
            )
        
        self._traits[trait.name] = trait

    def remove_trait(self, trait_name: str):
        """
        Remove a trait from the personality profile.
        
        :param trait_name: Name of the trait to remove
        """
        if trait_name in self._traits:
            del self._traits[trait_name]

    def get_trait(self, trait_name: str) -> PersonalityTrait:
        """
        Retrieve a specific trait.
        
        :param trait_name: Name of the trait
        :return: PersonalityTrait instance
        """
        if trait_name not in self._traits:
            raise PersonalityComponentError(
                f"Trait '{trait_name}' not found in profile",
                severity=ErrorSeverity.ERROR
            )
        return self._traits[trait_name]

    def apply_profile(
        self, 
        context: Dict[str, Any], 
        tools: Optional[ToolRegistry] = None
    ) -> Dict[str, Any]:
        """
        Apply the entire personality profile to a context.
        
        :param context: Current agent context
        :param tools: Optional tool registry for trait-specific actions
        :return: Modified context with personality traits applied
        """
        # Create a copy of the context to avoid direct modification
        modified_context = context.copy()
        
        # Apply each trait in order
        for trait in sorted(
            self._traits.values(), 
            key=lambda t: t.intensity, 
            reverse=True
        ):
            modified_context = trait.apply_trait(modified_context, tools)
        
        return modified_context

    def to_json(self) -> str:
        """
        Serialize the personality profile to JSON.
        
        :return: JSON string representation
        """
        return json.dumps({
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'traits': [
                {
                    'name': trait.name,
                    'description': trait.description,
                    'dimension': trait.dimension.name,
                    'intensity': trait.intensity
                }
                for trait in self._traits.values()
            ]
        }, indent=2)

    @classmethod
    def from_json(cls, json_config: Union[str, Dict[str, Any]]) -> 'PersonalityProfile':
        """
        Create a PersonalityProfile from a JSON configuration.
        
        :param json_config: JSON string or dictionary with profile configuration
        :return: Configured PersonalityProfile instance
        """
        # Parse JSON if needed
        if isinstance(json_config, str):
            try:
                config = json.loads(json_config)
            except json.JSONDecodeError as e:
                raise PersonalityComponentError(
                    f"Invalid JSON configuration: {str(e)}",
                    severity=ErrorSeverity.ERROR
                )
        else:
            config = json_config

        # Create profile
        profile = cls(
            name=config.get('name', 'Unnamed Profile'),
            description=config.get('description', '')
        )

        # Add traits
        for trait_config in config.get('traits', []):
            profile.add_trait({
                'name': trait_config.get('name'),
                'description': trait_config.get('description', ''),
                'dimension': PersonalityDimension[trait_config.get('dimension', 'ADAPTABILITY')],
                'intensity': trait_config.get('intensity', 0.5)
            })

        return profile
