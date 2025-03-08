from typing import Dict, Any, List, Optional, Union
from core.prompt_template import PromptTemplate, PromptType, PromptTemplateError
from core.error_handler import AgentError, ErrorSeverity
import json
import uuid

class PromptComposerError(AgentError):
    """Exception raised for prompt composition-related errors."""
    pass

class PromptCompositionStrategy:
    """
    Defines different strategies for composing prompts.
    """
    SEQUENTIAL = 'sequential'
    HIERARCHICAL = 'hierarchical'
    PARALLEL = 'parallel'
    CONDITIONAL = 'conditional'

class PromptComposer:
    """
    Advanced prompt composition system for creating complex, 
    multi-component prompts with dynamic assembly and validation.
    """
    def __init__(
        self, 
        templates: Optional[List[PromptTemplate]] = None,
        default_composition_strategy: str = PromptCompositionStrategy.SEQUENTIAL
    ):
        """
        Initialize PromptComposer with a set of templates and composition strategy.
        
        :param templates: Initial list of prompt templates
        :param default_composition_strategy: Default strategy for combining templates
        """
        self.id = str(uuid.uuid4())
        self._templates: Dict[str, PromptTemplate] = {}
        self._composition_strategy = default_composition_strategy
        
        # Add initial templates
        if templates:
            for template in templates:
                self.add_template(template)

    def add_template(
        self, 
        template: Union[PromptTemplate, Dict[str, Any], str],
        template_id: Optional[str] = None
    ) -> str:
        """
        Add a template to the composer.
        
        :param template: Template to add (PromptTemplate, dict, or JSON string)
        :param template_id: Optional custom ID for the template
        :return: Template ID
        """
        # Convert input to PromptTemplate if needed
        if isinstance(template, dict):
            template = PromptTemplate.from_json(template)
        elif isinstance(template, str):
            template = PromptTemplate.from_json(template)
        
        # Use provided ID or generate a new one
        template_id = template_id or template.id
        
        # Check for duplicate IDs
        if template_id in self._templates:
            raise PromptComposerError(
                f"Template with ID {template_id} already exists",
                severity=ErrorSeverity.WARNING
            )
        
        self._templates[template_id] = template
        return template_id

    def compose(
        self, 
        template_ids: Optional[List[str]] = None,
        variables: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        strategy: Optional[str] = None
    ) -> str:
        """
        Compose a prompt using specified templates and strategy.
        
        :param template_ids: List of template IDs to use (all templates if None)
        :param variables: Global variables for template rendering
        :param context: Global context for template rendering
        :param strategy: Composition strategy to use
        :return: Composed prompt
        """
        # Use default strategy if not provided
        strategy = strategy or self._composition_strategy
        
        # Select templates to use
        if template_ids is None:
            template_ids = list(self._templates.keys())
        
        # Validate template IDs
        selected_templates = [
            self._templates[tid] for tid in template_ids 
            if tid in self._templates
        ]
        
        if not selected_templates:
            raise PromptComposerError(
                "No valid templates selected for composition",
                severity=ErrorSeverity.ERROR
            )
        
        # Compose based on strategy
        if strategy == PromptCompositionStrategy.SEQUENTIAL:
            return self._compose_sequential(
                selected_templates, 
                variables or {}, 
                context or {}
            )
        
        elif strategy == PromptCompositionStrategy.HIERARCHICAL:
            return self._compose_hierarchical(
                selected_templates, 
                variables or {}, 
                context or {}
            )
        
        elif strategy == PromptCompositionStrategy.PARALLEL:
            return self._compose_parallel(
                selected_templates, 
                variables or {}, 
                context or {}
            )
        
        elif strategy == PromptCompositionStrategy.CONDITIONAL:
            return self._compose_conditional(
                selected_templates, 
                variables or {}, 
                context or {}
            )
        
        else:
            raise PromptComposerError(
                f"Unknown composition strategy: {strategy}",
                severity=ErrorSeverity.ERROR
            )

    def _compose_sequential(
        self, 
        templates: List[PromptTemplate], 
        variables: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Compose prompts sequentially, with each template building on the previous.
        
        :param templates: Templates to compose
        :param variables: Global variables
        :param context: Global context
        :return: Composed prompt
        """
        composed_prompt = []
        current_context = context.copy()
        
        for template in templates:
            # Render template with current context and variables
            rendered = template.render(
                variables=variables, 
                context=current_context
            )
            
            composed_prompt.append(rendered)
            
            # Update context with rendered template
            current_context['previous_prompt'] = rendered
        
        return "\n\n".join(composed_prompt)

    def _compose_hierarchical(
        self, 
        templates: List[PromptTemplate], 
        variables: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Compose prompts in a hierarchical manner, with parent-child relationships.
        
        :param templates: Templates to compose
        :param variables: Global variables
        :param context: Global context
        :return: Composed prompt
        """
        # Sort templates by type, with more general types first
        sorted_templates = sorted(
            templates, 
            key=lambda t: (
                t.prompt_type == PromptType.INSTRUCTION, 
                t.prompt_type == PromptType.ROLE_PLAY
            ), 
            reverse=True
        )
        
        composed_prompt = []
        current_context = context.copy()
        
        for template in sorted_templates:
            rendered = template.render(
                variables=variables, 
                context=current_context
            )
            composed_prompt.append(rendered)
            
            # Update context with rendered template
            current_context[f'{template.prompt_type.name.lower()}_prompt'] = rendered
        
        return "\n\n".join(composed_prompt)

    def _compose_parallel(
        self, 
        templates: List[PromptTemplate], 
        variables: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Compose prompts in parallel, generating independent prompts.
        
        :param templates: Templates to compose
        :param variables: Global variables
        :param context: Global context
        :return: Composed prompt
        """
        parallel_prompts = []
        
        for template in templates:
            rendered = template.render(
                variables=variables, 
                context=context
            )
            parallel_prompts.append(rendered)
        
        return "\n\n".join(parallel_prompts)

    def _compose_conditional(
        self, 
        templates: List[PromptTemplate], 
        variables: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Compose prompts conditionally based on context and variables.
        
        :param templates: Templates to compose
        :param variables: Global variables
        :param context: Global context
        :return: Composed prompt
        """
        conditional_prompts = []
        
        for template in templates:
            # Check if template should be included based on context
            include_template = True
            
            # Optional condition checking
            if 'condition' in variables:
                try:
                    include_template = variables['condition'](template, context)
                except Exception as e:
                    raise PromptComposerError(
                        f"Condition evaluation error: {str(e)}",
                        severity=ErrorSeverity.WARNING
                    )
            
            if include_template:
                rendered = template.render(
                    variables=variables, 
                    context=context
                )
                conditional_prompts.append(rendered)
        
        return "\n\n".join(conditional_prompts)

    def to_json(self) -> str:
        """
        Serialize the PromptComposer to a JSON configuration.
        
        :return: JSON string representation
        """
        return json.dumps({
            'id': self.id,
            'composition_strategy': self._composition_strategy,
            'templates': {
                tid: json.loads(template.to_json()) 
                for tid, template in self._templates.items()
            }
        }, indent=2)

    @classmethod
    def from_json(cls, json_config: Union[str, Dict[str, Any]]) -> 'PromptComposer':
        """
        Create a PromptComposer from a JSON configuration.
        
        :param json_config: JSON string or dictionary with composer configuration
        :return: Configured PromptComposer instance
        """
        if isinstance(json_config, str):
            try:
                config = json.loads(json_config)
            except json.JSONDecodeError as e:
                raise PromptComposerError(
                    f"Invalid JSON configuration: {str(e)}",
                    severity=ErrorSeverity.ERROR
                )
        else:
            config = json_config

        # Create composer with strategy
        composer = cls(
            default_composition_strategy=config.get(
                'composition_strategy', 
                PromptCompositionStrategy.SEQUENTIAL
            )
        )

        # Add templates
        for template_id, template_config in config.get('templates', {}).items():
            composer.add_template(template_config, template_id)

        return composer
