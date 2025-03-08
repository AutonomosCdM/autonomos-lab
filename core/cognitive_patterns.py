from typing import Dict, Any, Callable, Optional, List
import inspect
from core.prompt_template import PromptTemplate
from core.tool_registry import ToolRegistry
from core.error_handler import AgentError, ErrorSeverity

class CognitivePatternError(AgentError):
    """Exception raised for cognitive pattern-related errors."""
    pass

class CognitivePattern:
    """
    Represents a reusable cognitive processing pattern for agents.
    """
    def __init__(
        self, 
        name: str,
        description: str,
        processing_func: Callable,
        input_schema: Optional[Dict[str, type]] = None,
        output_schema: Optional[Dict[str, type]] = None
    ):
        """
        Initialize a cognitive pattern.
        
        :param name: Name of the cognitive pattern
        :param description: Detailed description of the pattern's purpose
        :param processing_func: Function implementing the cognitive processing
        :param input_schema: Optional schema for input validation
        :param output_schema: Optional schema for output validation
        """
        self.name = name
        self.description = description
        self._processing_func = processing_func
        self._input_schema = input_schema or {}
        self._output_schema = output_schema or {}

    def validate_input(self, input_data: Dict[str, Any]):
        """
        Validate input against the defined input schema.
        
        :param input_data: Input data to validate
        """
        for key, expected_type in self._input_schema.items():
            if key not in input_data:
                raise CognitivePatternError(
                    f"Missing required input: {key}",
                    severity=ErrorSeverity.ERROR
                )
            
            if not isinstance(input_data[key], expected_type):
                raise CognitivePatternError(
                    f"Invalid type for {key}. "
                    f"Expected {expected_type.__name__}, "
                    f"got {type(input_data[key]).__name__}",
                    severity=ErrorSeverity.ERROR
                )

    def validate_output(self, output_data: Dict[str, Any]):
        """
        Validate output against the defined output schema.
        
        :param output_data: Output data to validate
        """
        for key, expected_type in self._output_schema.items():
            if key not in output_data:
                raise CognitivePatternError(
                    f"Missing required output: {key}",
                    severity=ErrorSeverity.ERROR
                )
            
            if not isinstance(output_data[key], expected_type):
                raise CognitivePatternError(
                    f"Invalid type for {key}. "
                    f"Expected {expected_type.__name__}, "
                    f"got {type(output_data[key]).__name__}",
                    severity=ErrorSeverity.ERROR
                )

    def process(
        self, 
        input_data: Dict[str, Any], 
        tools: Optional[ToolRegistry] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the cognitive processing pattern.
        
        :param input_data: Input data for processing
        :param tools: Optional tool registry for additional processing
        :param context: Optional context for processing
        :return: Processed output
        """
        # Validate input
        self.validate_input(input_data)
        
        # Prepare context
        context = context or {}
        
        try:
            # Determine function signature
            sig = inspect.signature(self._processing_func)
            
            # Prepare arguments
            call_args = {'input_data': input_data}
            if 'tools' in sig.parameters:
                call_args['tools'] = tools
            if 'context' in sig.parameters:
                call_args['context'] = context
            
            # Execute processing function
            output = self._processing_func(**call_args)
            
            # Validate output
            if self._output_schema:
                self.validate_output(output)
            
            return output
        
        except Exception as e:
            raise CognitivePatternError(
                f"Error in cognitive pattern processing: {str(e)}",
                severity=ErrorSeverity.ERROR,
                context={'input': input_data, 'error': str(e)}
            )

class CognitivePatternRegistry:
    """
    Registry for managing and accessing cognitive processing patterns.
    """
    _patterns: Dict[str, CognitivePattern] = {}

    @classmethod
    def register_pattern(
        cls, 
        name: str, 
        description: str,
        processing_func: Callable,
        input_schema: Optional[Dict[str, type]] = None,
        output_schema: Optional[Dict[str, type]] = None
    ) -> CognitivePattern:
        """
        Register a new cognitive pattern.
        
        :param name: Name of the pattern
        :param description: Description of the pattern
        :param processing_func: Function implementing the pattern
        :param input_schema: Optional input validation schema
        :param output_schema: Optional output validation schema
        :return: Registered CognitivePattern instance
        """
        if name in cls._patterns:
            raise CognitivePatternError(
                f"Cognitive pattern '{name}' already exists",
                severity=ErrorSeverity.WARNING
            )
        
        pattern = CognitivePattern(
            name, 
            description, 
            processing_func, 
            input_schema, 
            output_schema
        )
        
        cls._patterns[name] = pattern
        return pattern

    @classmethod
    def get_pattern(cls, name: str) -> CognitivePattern:
        """
        Retrieve a registered cognitive pattern.
        
        :param name: Name of the pattern
        :return: CognitivePattern instance
        """
        if name not in cls._patterns:
            raise CognitivePatternError(
                f"Cognitive pattern '{name}' not found",
                severity=ErrorSeverity.ERROR
            )
        
        return cls._patterns[name]

    @classmethod
    def list_patterns(cls) -> List[str]:
        """
        List all registered cognitive pattern names.
        
        :return: List of pattern names
        """
        return list(cls._patterns.keys())

# Decorator for easy pattern registration
def cognitive_pattern(
    name: Optional[str] = None,
    description: Optional[str] = None,
    input_schema: Optional[Dict[str, type]] = None,
    output_schema: Optional[Dict[str, type]] = None
):
    """
    Decorator to register a function as a cognitive pattern.
    
    :param name: Optional custom name for the pattern
    :param description: Optional description of the pattern
    :param input_schema: Optional input validation schema
    :param output_schema: Optional output validation schema
    """
    def decorator(func):
        nonlocal name
        name = name or func.__name__
        
        # Use default description if not provided
        nonlocal description
        description = description or func.__doc__ or "No description provided"
        
        CognitivePatternRegistry.register_pattern(
            name, 
            description, 
            func, 
            input_schema, 
            output_schema
        )
        return func
    return decorator
