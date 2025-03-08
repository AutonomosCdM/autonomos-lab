from typing import Dict, Any, Optional, Union, List
import json
from datetime import datetime
from core.error_handler import AgentError, ErrorSeverity
from enum import Enum, auto
import re

class ResponseParserError(AgentError):
    """Exception raised for response parsing errors."""
    pass

class DataType(Enum):
    """
    Enumeration of common data types for normalization.
    """
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    DATETIME = auto()
    LIST = auto()
    DICT = auto()
    NULL = auto()

class ResponseParser:
    """
    Centralized parser for normalizing and validating API responses
    across different service providers.
    """
    @staticmethod
    def normalize_response(
        response: Dict[str, Any], 
        schema: Optional[Dict[str, Union[type, Dict[str, Any]]]] = None,
        strict: bool = False
    ) -> Dict[str, Any]:
        """
        Normalize and validate an API response against a given schema.
        
        :param response: Raw API response
        :param schema: Optional schema for validation and type conversion
        :param strict: If True, raises error on unexpected fields
        :return: Normalized response
        """
        # If no schema, return response as-is
        if not schema:
            return response

        normalized_response = {}

        for key, type_spec in schema.items():
            # Check if field exists in response
            if key not in response:
                if strict:
                    raise ResponseParserError(
                        f"Missing required field: {key}",
                        severity=ErrorSeverity.ERROR,
                        context={'response': response, 'schema': schema}
                    )
                continue

            value = response[key]

            # Handle complex type specifications
            if isinstance(type_spec, dict):
                # Nested schema
                if 'type' in type_spec:
                    # Type conversion
                    value = ResponseParser._convert_type(
                        value, 
                        type_spec['type'], 
                        type_spec.get('format'),
                        type_spec.get('optional', False)
                    )

                    # Additional validation
                    if 'validation' in type_spec:
                        ResponseParser._validate_value(
                            value, 
                            type_spec['validation']
                        )
            else:
                # Simple type conversion
                value = ResponseParser._convert_type(
                    value, 
                    type_spec
                )

            normalized_response[key] = value

        # Check for unexpected fields in strict mode
        if strict:
            unexpected_fields = set(response.keys()) - set(schema.keys())
            if unexpected_fields:
                raise ResponseParserError(
                    f"Unexpected fields: {unexpected_fields}",
                    severity=ErrorSeverity.WARNING,
                    context={'unexpected_fields': list(unexpected_fields)}
                )

        return normalized_response

    @staticmethod
    def _convert_type(
        value: Any, 
        target_type: Union[type, DataType], 
        format_spec: Optional[str] = None,
        optional: bool = False
    ) -> Any:
        """
        Convert value to specified type with optional formatting.
        
        :param value: Value to convert
        :param target_type: Target type for conversion
        :param format_spec: Optional format specification
        :param optional: Whether the field is optional
        :return: Converted value
        """
        # Handle None values
        if value is None:
            if optional:
                return None
            raise ResponseParserError(
                "Non-optional field cannot be None",
                severity=ErrorSeverity.ERROR
            )

        try:
            # Type conversion
            if target_type == DataType.STRING or target_type == str:
                return str(value)
            
            elif target_type == DataType.INTEGER or target_type == int:
                return int(value)
            
            elif target_type == DataType.FLOAT or target_type == float:
                return float(value)
            
            elif target_type == DataType.BOOLEAN or target_type == bool:
                if isinstance(value, str):
                    return value.lower() in ['true', '1', 'yes', 'y']
                return bool(value)
            
            elif target_type == DataType.DATETIME or target_type == datetime:
                # Handle different datetime formats
                if format_spec:
                    return datetime.strptime(str(value), format_spec)
                return datetime.fromisoformat(str(value))
            
            elif target_type == DataType.LIST or target_type == list:
                if not isinstance(value, list):
                    return [value]
                return value
            
            elif target_type == DataType.DICT or target_type == dict:
                if not isinstance(value, dict):
                    raise ValueError("Cannot convert to dictionary")
                return value
            
            else:
                return value

        except (ValueError, TypeError) as e:
            raise ResponseParserError(
                f"Type conversion error: {str(e)}",
                severity=ErrorSeverity.ERROR,
                context={
                    'value': value, 
                    'target_type': target_type,
                    'original_error': str(e)
                }
            )

    @staticmethod
    def _validate_value(
        value: Any, 
        validation_rules: Dict[str, Any]
    ):
        """
        Apply validation rules to a value.
        
        :param value: Value to validate
        :param validation_rules: Dictionary of validation rules
        """
        # Regex pattern validation
        if 'pattern' in validation_rules:
            pattern = validation_rules['pattern']
            if not re.match(pattern, str(value)):
                raise ResponseParserError(
                    f"Value does not match pattern: {pattern}",
                    severity=ErrorSeverity.ERROR,
                    context={'value': value, 'pattern': pattern}
                )

        # Minimum value validation
        if 'min' in validation_rules:
            min_val = validation_rules['min']
            if value < min_val:
                raise ResponseParserError(
                    f"Value must be greater than or equal to {min_val}",
                    severity=ErrorSeverity.ERROR,
                    context={'value': value, 'min': min_val}
                )

        # Maximum value validation
        if 'max' in validation_rules:
            max_val = validation_rules['max']
            if value > max_val:
                raise ResponseParserError(
                    f"Value must be less than or equal to {max_val}",
                    severity=ErrorSeverity.ERROR,
                    context={'value': value, 'max': max_val}
                )

        # Enum validation
        if 'enum' in validation_rules:
            allowed_values = validation_rules['enum']
            if value not in allowed_values:
                raise ResponseParserError(
                    f"Value must be one of {allowed_values}",
                    severity=ErrorSeverity.ERROR,
                    context={'value': value, 'allowed_values': allowed_values}
                )

    @staticmethod
    def extract_nested_value(
        response: Dict[str, Any], 
        path: str, 
        default: Optional[Any] = None
    ) -> Any:
        """
        Extract a nested value from a complex response dictionary.
        
        :param response: Response dictionary
        :param path: Dot-separated path to the value
        :param default: Default value if path is not found
        :return: Extracted value or default
        """
        keys = path.split('.')
        current = response

        for key in keys:
            if not isinstance(current, dict):
                return default
            
            if key not in current:
                return default
            
            current = current[key]

        return current

    @staticmethod
    def merge_responses(
        *responses: Dict[str, Any], 
        strategy: str = 'overwrite'
    ) -> Dict[str, Any]:
        """
        Merge multiple API responses using a specified strategy.
        
        :param responses: Multiple response dictionaries
        :param strategy: Merge strategy ('overwrite', 'append', 'unique')
        :return: Merged response
        """
        if not responses:
            return {}

        merged = responses[0].copy()

        for response in responses[1:]:
            for key, value in response.items():
                if key not in merged:
                    merged[key] = value
                else:
                    if strategy == 'overwrite':
                        merged[key] = value
                    elif strategy == 'append':
                        if isinstance(merged[key], list):
                            merged[key].extend(value if isinstance(value, list) else [value])
                        else:
                            merged[key] = [merged[key], value]
                    elif strategy == 'unique':
                        if isinstance(merged[key], list):
                            merged[key] = list(set(merged[key] + (value if isinstance(value, list) else [value])))
                        else:
                            merged[key] = value

        return merged
