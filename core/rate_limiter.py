import time
import logging
from typing import Dict, Any, Callable
from functools import wraps

class RateLimiter:
    """
    Intelligent rate limiting system with adaptive strategies
    """
    
    def __init__(self, 
                 max_calls: int = 10, 
                 period: float = 60.0, 
                 adaptive: bool = True):
        """
        Initialize rate limiter
        
        :param max_calls: Maximum number of calls allowed in the given period
        :param period: Time window in seconds
        :param adaptive: Enable adaptive rate limiting
        """
        self.max_calls = max_calls
        self.period = period
        self.adaptive = adaptive
        
        # Tracking call history
        self.calls: Dict[str, list] = {}
        
        # Adaptive parameters
        self.error_threshold = 0.1  # 10% error rate triggers adaptation
        self.call_errors: Dict[str, int] = {}
        self.current_max_calls = max_calls
    
    def _clean_call_history(self, key: str):
        """
        Remove old call timestamps outside the current period
        """
        current_time = time.time()
        self.calls[key] = [
            timestamp for timestamp in self.calls.get(key, []) 
            if current_time - timestamp <= self.period
        ]
    
    def is_allowed(self, key: str = 'default') -> bool:
        """
        Check if a call is allowed based on rate limiting rules
        
        :param key: Unique identifier for the rate-limited resource
        :return: Boolean indicating if the call is allowed
        """
        current_time = time.time()
        
        # Clean old call history
        self._clean_call_history(key)
        
        # Check current call count
        call_count = len(self.calls.get(key, []))
        
        # Adaptive rate limiting
        if self.adaptive:
            # Adjust max calls based on error rate
            error_rate = self.call_errors.get(key, 0) / max(call_count, 1)
            if error_rate > self.error_threshold:
                # Reduce max calls if error rate is high
                self.current_max_calls = max(1, self.current_max_calls // 2)
                logging.warning(f"Rate limit reduced for {key} due to high error rate")
            else:
                # Gradually increase max calls if error rate is low
                self.current_max_calls = min(self.max_calls, self.current_max_calls + 1)
        
        # Check if calls are within limit
        if call_count < self.current_max_calls:
            # Record this call
            if key not in self.calls:
                self.calls[key] = []
            self.calls[key].append(current_time)
            return True
        
        return False
    
    def decorator(self, func: Callable):
        """
        Decorator to apply rate limiting to a function
        
        :param func: Function to be rate limited
        :return: Wrapped function with rate limiting
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use function name as default key
            key = func.__name__
            
            # Check if call is allowed
            if not self.is_allowed(key):
                raise RuntimeError(f"Rate limit exceeded for {key}")
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                # Track errors for adaptive rate limiting
                self.call_errors[key] = self.call_errors.get(key, 0) + 1
                raise
        
        return wrapper
    
    def wait_for_call(self, key: str = 'default', timeout: float = None):
        """
        Wait until a call is allowed
        
        :param key: Unique identifier for the rate-limited resource
        :param timeout: Maximum time to wait (None for infinite)
        :return: True if call is allowed, False if timed out
        """
        start_time = time.time()
        
        while not self.is_allowed(key):
            # Check timeout
            if timeout is not None and time.time() - start_time > timeout:
                return False
            
            # Wait a bit before retrying
            time.sleep(0.1)
        
        return True
    
    def reset(self, key: str = 'default'):
        """
        Reset call history for a specific key
        
        :param key: Unique identifier to reset
        """
        if key in self.calls:
            del self.calls[key]
        if key in self.call_errors:
            del self.call_errors[key]
