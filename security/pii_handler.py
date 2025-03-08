import re
import hashlib
import logging
from typing import Dict, Any, Optional, Union

class PIIHandler:
    """
    Secure handling of Personally Identifiable Information (PII)
    with advanced anonymization and protection strategies
    """
    
    @staticmethod
    def hash_pii(value: str, salt: Optional[str] = None) -> str:
        """
        Cryptographically hash PII with optional salt
        """
        if not value:
            return ""
        
        # Use SHA-256 for consistent hashing
        if salt:
            value = f"{value}{salt}"
        
        return hashlib.sha256(value.encode('utf-8')).hexdigest()
    
    @staticmethod
    def mask_pii(value: str, mask_char: str = '*') -> str:
        """
        Partially mask PII while preserving some context
        """
        if not value:
            return ""
        
        # Email masking
        email_pattern = r'^(.)(.*)(@.*)$'
        email_match = re.match(email_pattern, value)
        if email_match:
            return f"{email_match.group(1)}{mask_char * (len(email_match.group(2)))}{email_match.group(3)}"
        
        # Phone number masking
        phone_pattern = r'^(\+?\d{1,3}[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?(\d{4})$'
        phone_match = re.match(phone_pattern, value)
        if phone_match:
            return re.sub(r'\d', mask_char, value[:-4]) + value[-4:]
        
        # Generic masking for other PII
        if len(value) <= 4:
            return mask_char * len(value)
        return f"{value[:2]}{mask_char * (len(value) - 4)}{value[-2:]}"
    
    @staticmethod
    def anonymize_dict(data: Dict[str, Any], 
                       pii_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Anonymize dictionary containing PII
        
        :param data: Dictionary to anonymize
        :param pii_fields: Optional mapping of field names to anonymization method
                           Methods: 'hash', 'mask', or a custom function
        """
        if pii_fields is None:
            pii_fields = {
                'email': 'mask',
                'phone': 'mask',
                'ssn': 'hash',
                'credit_card': 'hash'
            }
        
        anonymized = {}
        for key, value in data.items():
            # Check if the key matches any PII field
            anonymization_method = next((method for field, method in pii_fields.items() 
                                         if field.lower() in key.lower()), None)
            
            if anonymization_method:
                try:
                    if anonymization_method == 'hash':
                        anonymized[key] = PIIHandler.hash_pii(str(value))
                    elif anonymization_method == 'mask':
                        anonymized[key] = PIIHandler.mask_pii(str(value))
                    elif callable(anonymization_method):
                        anonymized[key] = anonymization_method(value)
                    else:
                        anonymized[key] = value
                except Exception as e:
                    logging.error(f"Error anonymizing {key}: {e}")
                    anonymized[key] = value
            else:
                anonymized[key] = value
        
        return anonymized
    
    @staticmethod
    def detect_pii(text: str) -> Dict[str, list]:
        """
        Detect potential PII in text
        
        :return: Dictionary of detected PII types and their matches
        """
        pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(\+\d{1,2}\s?)?(\d{3}[-.]?)?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }
        
        detected_pii = {}
        for pii_type, pattern in pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                detected_pii[pii_type] = list(matches)
        
        return detected_pii
    
    @staticmethod
    def redact_pii(text: str, redaction_char: str = '[REDACTED]') -> str:
        """
        Completely redact all detected PII in text
        
        :param text: Input text
        :param redaction_char: String to replace PII with
        :return: Text with PII redacted
        """
        pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(\+\d{1,2}\s?)?(\d{3}[-.]?)?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }
        
        redacted_text = text
        for pattern in pii_patterns.values():
            redacted_text = re.sub(pattern, redaction_char, redacted_text)
        
        return redacted_text
