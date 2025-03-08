from typing import Dict, Any, Optional, List, Union
import json
import re
from enum import Enum, auto
from core.error_handler import AgentError, ErrorSeverity
import uuid

class PromptTemplateError(AgentError):
    """Exception raised for prompt template-related errors."""
    pass

class PromptType(Enum):
    """
    Enumeration of different prompt types.
    """
    INSTRUCTION = auto()
    CONVERSATION = auto()
    ROLE_PLAY = auto()
    TASK = auto()
    CREATIVE = auto()

class PromptTemplate:
    """
    Flexible and modular prompt template system for generating 
    context-aware and dynamically composable prompts.
    """
    def __init__(
        self, 
        template: str,
        prompt_type: PromptType = PromptType.INSTRUCTION,
        variables: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None,
        context_requirements: Optional[List[str]] = None
    ):
        """
        Initialize a prompt template with flexible configuration.
        
        :param template: Base template string with placeholders
        :param prompt_type: Type of prompt for specialized processing
        :param variables: Default variables for template rendering
        :param constraints: Validation constraints for variables
        :param context_requirements: Required context elements
        """
        self.id = str(uuid.uuid4())
        self.template = template
        self.prompt_type = prompt_type
        self._variables = variables or {}
        self._constraints = constraints or {}
        self._context_requirements = context_requirements or []

    def render(
        self, 
        variables: Optional[Dict[str, Any]] = None, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Render the prompt template with provided variables and context.
        
        :param variables: Dynamic variables to replace in template
        :param context: Additional context for advanced rendering
        :return: Fully rendered prompt
        """
        # Merge default and provided variables
        merged_variables = self._variables.copy()
        if variables:
            merged_variables.update(variables)

        # Validate variables against constraints
        self._validate_variables(merged_variables)

        # Check context requirements
        if self._context_requirements:
            self._validate_context(context or {})

        # Render template with variables
        try:
            rendered_template = self.template.format(**merged_variables)
        except KeyError as e:
            raise PromptTemplateError(
                f"Missing required variable: {e}",
                severity=ErrorSeverity.ERROR,
                context={'template': self.template, 'variables': merged_variables}
            )

        # Apply type-specific processing
        return self._process_by_type(rendered_template, context)

    def _validate_variables(self, variables: Dict[str, Any]):
        """
        Validate variables against defined constraints.
        
        :param variables: Variables to validate
        """
        for var_name, constraints in self._constraints.items():
            if var_name not in variables:
                if constraints.get('required', False):
                    raise PromptTemplateError(
                        f"Required variable '{var_name}' is missing",
                        severity=ErrorSeverity.ERROR
                    )
                continue

            value = variables[var_name]

            # Type validation
            if 'type' in constraints:
                if not isinstance(value, constraints['type']):
                    raise PromptTemplateError(
                        f"Invalid type for '{var_name}'. "
                        f"Expected {constraints['type']}, got {type(value)}",
                        severity=ErrorSeverity.ERROR
                    )

            # Pattern validation
            if 'pattern' in constraints:
                if not re.match(constraints['pattern'], str(value)):
                    raise PromptTemplateError(
                        f"Value for '{var_name}' does not match pattern: {constraints['pattern']}",
                        severity=ErrorSeverity.ERROR
                    )

            # Range validation for numeric types
            if 'min' in constraints and value < constraints['min']:
                raise PromptTemplateError(
                    f"Value for '{var_name}' must be >= {constraints['min']}",
                    severity=ErrorSeverity.ERROR
                )

            if 'max' in constraints and value > constraints['max']:
                raise PromptTemplateError(
                    f"Value for '{var_name}' must be <= {constraints['max']}",
                    severity=ErrorSeverity.ERROR
                )

            # Enum validation
            if 'enum' in constraints and value not in constraints['enum']:
                raise PromptTemplateError(
                    f"Value for '{var_name}' must be one of {constraints['enum']}",
                    severity=ErrorSeverity.ERROR
                )

    def _validate_context(self, context: Dict[str, Any]):
        """
        Validate that required context elements are present.
        
        :param context: Context dictionary to validate
        """
        for req_context in self._context_requirements:
            if req_context not in context:
                raise PromptTemplateError(
                    f"Missing required context element: {req_context}",
                    severity=ErrorSeverity.WARNING,
                    context={'required_context': self._context_requirements}
                )

    def _process_by_type(
        self, 
        rendered_template: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Apply type-specific processing to the rendered template.
        
        :param rendered_template: Template after variable substitution
        :param context: Optional context for advanced processing
        :return: Processed prompt
        """
        context = context or {}

        if self.prompt_type == PromptType.ROLE_PLAY:
            # Add role-play specific formatting
            role = context.get('role', 'Assistant')
            return f"You are a {role}. {rendered_template}"

        elif self.prompt_type == PromptType.CONVERSATION:
            # Add conversation context if available
            history = context.get('conversation_history', [])
            if history:
                conversation_context = "\n".join(
                    f"{msg['role']}: {msg['content']}" for msg in history
                )
                return f"{conversation_context}\n\n{rendered_template}"

        elif self.prompt_type == PromptType.TASK:
            # Add task-specific instructions
            task_context = context.get('task_context', '')
            return f"Task Context: {task_context}\n\n{rendered_template}"

        return rendered_template

    @classmethod
    def from_json(cls, json_config: Union[str, Dict[str, Any]]) -> 'PromptTemplate':
        """
        Create a PromptTemplate from a JSON configuration.
        
        :param json_config: JSON string or dictionary with template configuration
        :return: Configured PromptTemplate instance
        """
        if isinstance(json_config, str):
            try:
                config = json.loads(json_config)
            except json.JSONDecodeError as e:
                raise PromptTemplateError(
                    f"Invalid JSON configuration: {str(e)}",
                    severity=ErrorSeverity.ERROR
                )
        else:
            config = json_config

        return cls(
            template=config.get('template', ''),
            prompt_type=PromptType[config.get('prompt_type', 'INSTRUCTION')],
            variables=config.get('variables', {}),
            constraints=config.get('constraints', {}),
            context_requirements=config.get('context_requirements', [])
        )

    def to_json(self) -> str:
        """
        Convert the PromptTemplate to a JSON configuration.
        
        :return: JSON string representation of the template
        """
        return json.dumps({
            'id': self.id,
            'template': self.template,
            'prompt_type': self.prompt_type.name,
            'variables': self._variables,
            'constraints': self._constraints,
            'context_requirements': self._context_requirements
        }, indent=2)
