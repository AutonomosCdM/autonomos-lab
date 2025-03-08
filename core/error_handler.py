import logging
import traceback
from typing import Dict, Any, Optional, Callable
import json
from datetime import datetime
import os
import uuid
import sys

class ErrorSeverity:
    """
    Defines error severity levels with increasing criticality.
    """
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

class AgentError(Exception):
    """
    Base exception for agent-related errors with additional context.
    """
    def __init__(
        self, 
        message: str, 
        severity: int = ErrorSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an AgentError with detailed information.
        
        :param message: Error message
        :param severity: Error severity level
        :param context: Additional context about the error
        """
        super().__init__(message)
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
        self.severity = severity
        self.context = context or {}
        self.traceback = traceback.format_exc()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to a dictionary for logging or serialization.
        
        :return: Dictionary representation of the error
        """
        return {
            'id': self.id,
            'message': str(self),
            'timestamp': self.timestamp,
            'severity': self.severity,
            'context': self.context,
            'traceback': self.traceback
        }

class ErrorHandler:
    """
    Centralized error handling and logging system for the agent framework.
    """
    def __init__(
        self, 
        log_dir: str = 'logs', 
        log_level: int = logging.INFO,
        max_log_files: int = 10,
        max_log_size_mb: int = 10
    ):
        """
        Initialize the ErrorHandler with logging configuration.
        
        :param log_dir: Directory to store log files
        :param log_level: Logging level
        :param max_log_files: Maximum number of log files to keep
        :param max_log_size_mb: Maximum size of each log file in MB
        """
        self._log_dir = os.path.join(os.getcwd(), log_dir)
        self._max_log_files = max_log_files
        self._max_log_size_mb = max_log_size_mb

        # Ensure log directory exists
        os.makedirs(self._log_dir, exist_ok=True)

        # Configure structured logging
        self._logger = logging.getLogger('agent_framework')
        self._logger.setLevel(log_level)

        # JSON formatter for structured logging
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    'timestamp': datetime.now().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage(),
                    'logger': record.name,
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                # Add any extra attributes
                if hasattr(record, 'extra'):
                    log_record.update(record.extra)
                
                return json.dumps(log_record)

        # File handler with log rotation
        file_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self._log_dir, 'agent_framework.log'),
            maxBytes=self._max_log_size_mb * 1024 * 1024,
            backupCount=self._max_log_files
        )
        file_handler.setFormatter(JsonFormatter())
        self._logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self._logger.addHandler(console_handler)

    def log(
        self, 
        message: str, 
        level: int = logging.INFO, 
        extra: Optional[Dict[str, Any]] = None
    ):
        """
        Log a message with optional extra context.
        
        :param message: Log message
        :param level: Logging level
        :param extra: Additional context for the log
        """
        extra = extra or {}
        self._logger.log(level, message, extra=extra)

    def handle_error(
        self, 
        error: Union[Exception, AgentError], 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentError:
        """
        Handle and log an error, converting it to an AgentError.
        
        :param error: Exception to handle
        :param context: Additional context about the error
        :return: Processed AgentError
        """
        # If already an AgentError, just log it
        if isinstance(error, AgentError):
            agent_error = error
        else:
            # Convert to AgentError
            agent_error = AgentError(
                message=str(error),
                severity=ErrorSeverity.ERROR,
                context=context
            )

        # Log the error
        self.log(
            f"Error: {agent_error}",
            level=logging.ERROR,
            extra={
                'error_id': agent_error.id,
                'error_context': agent_error.context,
                'traceback': agent_error.traceback
            }
        )

        return agent_error

    def retry_with_backoff(
        self, 
        func: Callable, 
        max_retries: int = 3, 
        base_delay: float = 1.0, 
        backoff_factor: float = 2.0
    ) -> Callable:
        """
        Decorator to add retry mechanism with exponential backoff.
        
        :param func: Function to retry
        :param max_retries: Maximum number of retry attempts
        :param base_delay: Initial delay between retries
        :param backoff_factor: Factor to increase delay between retries
        :return: Wrapped function with retry mechanism
        """
        import time
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = base_delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    
                    # Log the retry attempt
                    self.log(
                        f"Retry attempt {retries} for {func.__name__}",
                        level=logging.WARNING,
                        extra={
                            'error': str(e),
                            'retry_count': retries
                        }
                    )
                    
                    # Stop retrying if max retries reached
                    if retries >= max_retries:
                        raise

                    # Wait with exponential backoff
                    time.sleep(delay)
                    delay *= backoff_factor

        return wrapper

    def create_error_boundary(
        self, 
        default_return: Any = None, 
        log_errors: bool = True
    ) -> Callable:
        """
        Create an error boundary decorator to handle exceptions gracefully.
        
        :param default_return: Value to return if an error occurs
        :param log_errors: Whether to log errors
        :return: Decorator function
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if log_errors:
                        self.handle_error(e)
                    return default_return
            return wrapper
        return decorator
