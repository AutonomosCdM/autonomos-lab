import logging
import time
import random
from typing import Callable, Any, List, Optional, Union
from functools import wraps

class FailoverStrategy:
    """
    Comprehensive failover and recovery mechanism for distributed systems
    """
    
    class CircuitBreakerState:
        """
        Represents the state of a circuit breaker
        """
        CLOSED = 'closed'   # Normal operation
        OPEN = 'open'       # Temporarily disabled
        HALF_OPEN = 'half-open'  # Testing recovery
    
    def __init__(self, 
                 max_failures: int = 3, 
                 reset_timeout: float = 60.0,
                 backoff_strategy: str = 'exponential'):
        """
        Initialize failover strategy
        
        :param max_failures: Number of consecutive failures before circuit breaks
        :param reset_timeout: Time to wait before attempting recovery
        :param backoff_strategy: Backoff method for retries
        """
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.backoff_strategy = backoff_strategy
        
        # Tracking failures and circuit state
        self.failures: Dict[str, int] = {}
        self.last_failure_time: Dict[str, float] = {}
        self.circuit_state: Dict[str, str] = {}
        
        # Fallback mechanisms
        self.fallback_handlers: Dict[str, Callable] = {}
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def _calculate_backoff(self, attempt: int) -> float:
        """
        Calculate backoff time based on strategy
        
        :param attempt: Current retry attempt
        :return: Backoff time in seconds
        """
        if self.backoff_strategy == 'exponential':
            # Exponential backoff with jitter
            base_delay = min(self.reset_timeout, 2 ** attempt)
            jitter = random.uniform(0, 0.1 * base_delay)
            return base_delay + jitter
        elif self.backoff_strategy == 'linear':
            # Linear backoff
            return min(self.reset_timeout, attempt * 5)
        else:
            # Constant backoff
            return self.reset_timeout
    
    def register_fallback(self, func_name: str, fallback_handler: Callable):
        """
        Register a fallback handler for a specific function
        
        :param func_name: Name of the function to register fallback for
        :param fallback_handler: Function to call when primary fails
        """
        self.fallback_handlers[func_name] = fallback_handler
    
    def decorator(self, func: Callable):
        """
        Decorator to apply circuit breaker and failover logic
        
        :param func: Function to be protected
        :return: Wrapped function with failover mechanism
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use function name as key
            key = func.__name__
            
            # Initialize state if not exists
            if key not in self.circuit_state:
                self.circuit_state[key] = self.CircuitBreakerState.CLOSED
                self.failures[key] = 0
            
            current_time = time.time()
            
            # Check circuit state
            if self.circuit_state[key] == self.CircuitBreakerState.OPEN:
                # Check if reset timeout has passed
                if current_time - self.last_failure_time.get(key, 0) < self.reset_timeout:
                    # Circuit still open, try fallback if available
                    if key in self.fallback_handlers:
                        self.logger.warning(f"Circuit open for {key}, using fallback")
                        return self.fallback_handlers[key](*args, **kwargs)
                    else:
                        raise RuntimeError(f"Circuit breaker open for {key}")
                
                # Move to half-open state to test recovery
                self.circuit_state[key] = self.CircuitBreakerState.HALF_OPEN
            
            try:
                # Attempt to execute the function
                result = func(*args, **kwargs)
                
                # Reset failure count on success
                if self.circuit_state[key] == self.CircuitBreakerState.HALF_OPEN:
                    self.circuit_state[key] = self.CircuitBreakerState.CLOSED
                self.failures[key] = 0
                
                return result
            
            except Exception as e:
                # Track and handle failures
                self.failures[key] += 1
                self.last_failure_time[key] = current_time
                
                # Log the failure
                self.logger.error(f"Failure in {key}: {e}")
                
                # Check if failure threshold is reached
                if self.failures[key] >= self.max_failures:
                    # Open the circuit
                    self.circuit_state[key] = self.CircuitBreakerState.OPEN
                    self.logger.warning(f"Circuit breaker opened for {key}")
                
                # Attempt fallback if available
                if key in self.fallback_handlers:
                    try:
                        return self.fallback_handlers[key](*args, **kwargs)
                    except Exception as fallback_error:
                        self.logger.error(f"Fallback failed for {key}: {fallback_error}")
                
                # If no fallback, raise the original exception
                raise
        
        return wrapper
    
    def reset_circuit(self, key: Optional[str] = None):
        """
        Reset circuit breaker state
        
        :param key: Specific function to reset. If None, reset all.
        """
        if key:
            self.circuit_state[key] = self.CircuitBreakerState.CLOSED
            self.failures[key] = 0
        else:
            # Reset all circuits
            self.circuit_state.clear()
            self.failures.clear()
            self.last_failure_time.clear()
    
    def get_circuit_status(self, key: str) -> Dict[str, Union[str, int]]:
        """
        Get current status of a circuit
        
        :param key: Function name to check
        :return: Dictionary with circuit status details
        """
        return {
            'state': self.circuit_state.get(key, self.CircuitBreakerState.CLOSED),
            'failures': self.failures.get(key, 0),
            'last_failure_time': self.last_failure_time.get(key, None)
        }
