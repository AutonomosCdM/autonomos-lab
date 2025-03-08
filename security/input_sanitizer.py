import re
import html
from typing import Any, Dict, List, Union

class InputSanitizer:
    """
    Comprehensive input sanitization system to prevent prompt injection 
    and protect against various security vulnerabilities.
    """
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize input text by:
        1. Escaping HTML entities
        2. Removing potentially dangerous control characters
        3. Limiting input length
        4. Blocking known injection patterns
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        
        # HTML escape
        sanitized = html.escape(text)
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1F\x7F]', '', sanitized)
        
        # Limit input length
        sanitized = sanitized[:2000]
        
        # Block potential injection patterns
        injection_patterns = [
            r'(SELECT|INSERT|UPDATE|DELETE)\s+.*FROM',  # SQL Injection
            r'\$\{.*\}',  # JNDI/Log4j style injection
            r'<script>.*</script>',  # XSS
            r'eval\(.*\)',  # Code execution
            r'import\s+.*',  # Python import injection
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError("Potential security threat detected in input")
        
        return sanitized
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively sanitize dictionary inputs
        """
        sanitized_dict = {}
        for key, value in data.items():
            sanitized_key = InputSanitizer.sanitize_text(str(key))
            
            if isinstance(value, str):
                sanitized_dict[sanitized_key] = InputSanitizer.sanitize_text(value)
            elif isinstance(value, dict):
                sanitized_dict[sanitized_key] = InputSanitizer.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized_dict[sanitized_key] = InputSanitizer.sanitize_list(value)
            else:
                sanitized_dict[sanitized_key] = value
        
        return sanitized_dict
    
    @staticmethod
    def sanitize_list(data: List[Any]) -> List[Any]:
        """
        Recursively sanitize list inputs
        """
        return [
            InputSanitizer.sanitize_text(item) if isinstance(item, str) else
            InputSanitizer.sanitize_dict(item) if isinstance(item, dict) else
            InputSanitizer.sanitize_list(item) if isinstance(item, list) else
            item
            for item in data
        ]
    
    @staticmethod
    def validate_input(input_data: Union[str, Dict[str, Any], List[Any]]) -> Union[str, Dict[str, Any], List[Any]]:
        """
        Comprehensive input validation and sanitization
        """
        if isinstance(input_data, str):
            return InputSanitizer.sanitize_text(input_data)
        elif isinstance(input_data, dict):
            return InputSanitizer.sanitize_dict(input_data)
        elif isinstance(input_data, list):
            return InputSanitizer.sanitize_list(input_data)
        else:
            raise ValueError("Unsupported input type for sanitization")
