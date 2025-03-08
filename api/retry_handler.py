import asyncio
import random
from typing import Callable, Any, Optional, Dict, Union, List
import logging
from core.error_handler import AgentError, ErrorSeverity
import time
import inspect
from enum import Enum, auto

class RetryStrategy(Enum):
    """
    Enumeration of retry strategies.
    """
    CONSTANT = auto()
    LINEAR = auto()
    EXPONENTIAL = auto()
    FIBONACCI = auto()

class CircuitState(Enum):
    """
    Enumeration of circuit breaker states.
    """
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()

class RetryHandlerError(AgentError):
    """Exception raised for retry-related errors."""
    pass

class RetryHandler:
    """
    Advanced retry mechanism with configurable backoff strategies
    and circuit breaker functionality.
    """
    def __init__(
        self, 
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        jitter: float = 0.1,
        circuit_failure_threshold: int = 5,
        circuit_reset_timeout: float = 30.0,
        retry_on: Optional[Union[Type[Exception], Tuple[Type[Exception], ...]]] = None
    ):
        """
        Initialize RetryHandler with advanced retry and circuit breaker configuration.
        
        :param max_retries: Maximum number of retry attempts
        :param base_delay: Initial delay between retries
        :param max_delay: Maximum delay between retries
        :param backoff_strategy: Strategy for increasing delay between retries
        :param jitter: Random variation in delay to prevent synchronized retries
        :param circuit_failure_threshold: Number of failures before opening the circuit
        :param circuit_reset_timeout: Time to wait before attempting to close the circuit
        :param retry_on: Exception types to retry on
        """
        self._max_retries = max_retries
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._backoff_strategy = backoff_strategy
        self._jitter = jitter
        
        # Circuit breaker configuration
        self._circuit_failure_threshold = circuit_failure_threshold
        self._circuit_reset_timeout = circuit_reset_timeout
        self._retry_on = retry_on or Exception
        
        # Circuit state tracking
        self._failure_count = 0
        self._circuit_state = CircuitState.CLOSED
        self._last_failure_time = None

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay between retry attempts based on strategy.
        
        :param attempt: Current retry attempt number
        :return: Delay in seconds
        """
        base_delay = self._base_delay

        # Calculate delay based on strategy
        if self._backoff_strategy == RetryStrategy.CONSTANT:
            delay = base_delay
        elif self._backoff_strategy == RetryStrategy.LINEAR:
            delay = base_delay * attempt
        elif self._backoff_strategy == RetryStrategy.EXPONENTIAL:
            delay = base_delay * (2 ** (attempt - 1))
        elif self._backoff_strategy == RetryStrategy.FIBONACCI:
            # Fibonacci-like sequence for delays
            delay = base_delay * (1.618 ** attempt)
        else:
            delay = base_delay

        # Apply maximum delay limit
        delay = min(delay, self._max_delay)

        # Add jitter to prevent synchronized retries
        jitter_amount = delay * self._jitter
        delay += random.uniform(-jitter_amount, jitter_amount)

        return max(0, delay)

    async def retry(
        self, 
        func: Callable[..., Any], 
        *args, 
        **kwargs
    ) -> Any:
        """
        Execute a function with retry and circuit breaker mechanism.
        
        :param func: Function to execute
        :param args: Positional arguments for the function
        :param kwargs: Keyword arguments for the function
        :return: Result of the function
        """
        # Check if function is async
        is_async = inspect.iscoroutinefunction(func)

        # Circuit breaker check
        if self._circuit_state == CircuitState.OPEN:
            # Check if circuit can be reset
            if time.time() - self._last_failure_time >= self._circuit_reset_timeout:
                self._circuit_state = CircuitState.HALF_OPEN
            else:
                raise RetryHandlerError(
                    "Circuit is open. Requests are currently blocked.",
                    severity=ErrorSeverity.WARNING
                )

        for attempt in range(1, self._max_retries + 1):
            try:
                # Execute function (async or sync)
                if is_async:
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Success: reset circuit
                if self._circuit_state == CircuitState.HALF_OPEN:
                    self._circuit_state = CircuitState.CLOSED
                self._failure_count = 0
                
                return result

            except self._retry_on as e:
                # Increment failure count
                self._failure_count += 1
                
                # Check circuit breaker threshold
                if self._failure_count >= self._circuit_failure_threshold:
                    self._circuit_state = CircuitState.OPEN
                    self._last_failure_time = time.time()
                    
                    raise RetryHandlerError(
                        f"Circuit breaker opened after {self._failure_count} consecutive failures",
                        severity=ErrorSeverity.CRITICAL,
                        context={'last_error': str(e)}
                    )
                
                # Last attempt
                if attempt == self._max_retries:
                    raise RetryHandlerError(
                        f"Failed after {self._max_retries} attempts",
                        severity=ErrorSeverity.ERROR,
                        context={'last_error': str(e)}
                    )
                
                # Calculate and apply delay
                delay = self._calculate_delay(attempt)
                
                # Log retry attempt
                logging.warning(
                    f"Retry attempt {attempt}: {str(e)}. "
                    f"Waiting {delay:.2f} seconds."
                )
                
                # Wait before retry
                await asyncio.sleep(delay)

    def decorator(
        self, 
        func: Optional[Callable] = None, 
        *,
        max_retries: Optional[int] = None,
        backoff_strategy: Optional[RetryStrategy] = None
    ):
        """
        Decorator for adding retry mechanism to functions.
        
        :param func: Function to decorate
        :param max_retries: Override default max retries
        :param backoff_strategy: Override default backoff strategy
        :return: Decorated function
        """
        def decorator_wrapper(f):
            # Create a wrapper that uses the retry method
            async def wrapper(*args, **kwargs):
                # Create a temporary RetryHandler with potential overrides
                temp_handler = RetryHandler(
                    max_retries=max_retries or self._max_retries,
                    backoff_strategy=backoff_strategy or self._backoff_strategy
                )
                return await temp_handler.retry(f, *args, **kwargs)
            
            return wrapper
        
        # Allow decorator to be used with or without parentheses
        if func:
            return decorator_wrapper(func)
        return decorator_wrapper
