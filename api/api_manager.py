import asyncio
from typing import Dict, Any, Optional, List, Callable
import aiohttp
import logging
from core.error_handler import ErrorHandler, AgentError, ErrorSeverity
from core.config_manager import ConfigManager

class APIConnectionError(AgentError):
    """Exception raised for API connection and communication errors."""
    pass

class RateLimitError(AgentError):
    """Exception raised when API rate limits are exceeded."""
    pass

class APIManager:
    """
    Centralized manager for handling API connections, rate limiting, 
    and response parsing across different service providers.
    """
    def __init__(
        self, 
        config_manager: ConfigManager,
        error_handler: ErrorHandler,
        default_timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize APIManager with configuration and error handling.
        
        :param config_manager: Configuration management system
        :param error_handler: Error handling system
        :param default_timeout: Default timeout for API requests in seconds
        :param max_retries: Maximum number of retry attempts for failed requests
        """
        self._config_manager = config_manager
        self._error_handler = error_handler
        self._default_timeout = default_timeout
        self._max_retries = max_retries
        
        # Rate limit tracking per endpoint
        self._rate_limits: Dict[str, Dict[str, Any]] = {}

    async def make_request(
        self, 
        url: str, 
        method: str = 'GET', 
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make an asynchronous API request with rate limiting and error handling.
        
        :param url: API endpoint URL
        :param method: HTTP method (GET, POST, etc.)
        :param headers: Optional request headers
        :param params: Optional query parameters
        :param data: Optional request body
        :param provider: Optional provider name for specific rate limit tracking
        :return: Parsed JSON response
        """
        # Check rate limits
        self._check_rate_limit(url, provider)
        
        # Prepare request parameters
        headers = headers or {}
        params = params or {}
        data = data or {}
        
        # Add default timeout
        timeout = aiohttp.ClientTimeout(total=self._default_timeout)
        
        # Retry mechanism
        for attempt in range(self._max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method, 
                        url, 
                        headers=headers, 
                        params=params, 
                        json=data, 
                        timeout=timeout
                    ) as response:
                        # Handle HTTP errors
                        if response.status >= 400:
                            raise APIConnectionError(
                                f"HTTP Error {response.status}: {response.reason}",
                                severity=ErrorSeverity.ERROR,
                                context={
                                    'url': url,
                                    'method': method,
                                    'status_code': response.status
                                }
                            )
                        
                        # Parse and return response
                        return await response.json()
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                # Log and potentially retry
                self._error_handler.log(
                    f"API Request Error (Attempt {attempt + 1}): {str(e)}",
                    level=logging.WARNING
                )
                
                # Last attempt
                if attempt == self._max_retries - 1:
                    raise APIConnectionError(
                        f"Failed to connect to {url} after {self._max_retries} attempts",
                        severity=ErrorSeverity.CRITICAL,
                        context={'url': url, 'error': str(e)}
                    )
                
                # Wait before retry with exponential backoff
                await asyncio.sleep(2 ** attempt)

    def register_rate_limit(
        self, 
        endpoint: str, 
        limit: int, 
        period: int,
        provider: Optional[str] = None
    ):
        """
        Register rate limit for a specific endpoint.
        
        :param endpoint: API endpoint or provider
        :param limit: Maximum number of requests
        :param period: Time period in seconds
        :param provider: Optional provider name
        """
        key = provider or endpoint
        self._rate_limits[key] = {
            'limit': limit,
            'period': period,
            'requests': [],
            'last_reset': None
        }

    def _check_rate_limit(self, url: str, provider: Optional[str] = None):
        """
        Check and enforce rate limits before making a request.
        
        :param url: Request URL
        :param provider: Optional provider name
        """
        key = provider or url
        
        # No rate limit configured
        if key not in self._rate_limits:
            return
        
        rate_limit = self._rate_limits[key]
        current_time = asyncio.get_event_loop().time()
        
        # Remove old requests outside the rate limit period
        rate_limit['requests'] = [
            req for req in rate_limit['requests'] 
            if current_time - req < rate_limit['period']
        ]
        
        # Check if limit is exceeded
        if len(rate_limit['requests']) >= rate_limit['limit']:
            raise RateLimitError(
                f"Rate limit exceeded for {key}",
                severity=ErrorSeverity.WARNING,
                context={
                    'limit': rate_limit['limit'],
                    'period': rate_limit['period']
                }
            )
        
        # Record this request
        rate_limit['requests'].append(current_time)

    def parse_response(
        self, 
        response: Dict[str, Any], 
        schema: Optional[Dict[str, type]] = None
    ) -> Dict[str, Any]:
        """
        Normalize and validate API responses.
        
        :param response: Raw API response
        :param schema: Optional schema for validation
        :return: Parsed and validated response
        """
        # Basic validation if schema provided
        if schema:
            try:
                for key, expected_type in schema.items():
                    if key not in response:
                        raise ValueError(f"Missing required field: {key}")
                    
                    if not isinstance(response[key], expected_type):
                        raise TypeError(
                            f"Invalid type for {key}. "
                            f"Expected {expected_type}, "
                            f"got {type(response[key])}"
                        )
            except (ValueError, TypeError) as e:
                raise APIConnectionError(
                    f"Response validation error: {str(e)}",
                    severity=ErrorSeverity.ERROR,
                    context={'response': response}
                )
        
        return response
