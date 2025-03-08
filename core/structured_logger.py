import logging
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

class StructuredLogger:
    """
    Advanced structured logging system with JSON formatting, 
    session tracking, and configurable output.
    """
    def __init__(
        self, 
        log_dir: str = 'logs', 
        log_level: int = logging.INFO,
        max_log_files: int = 10,
        max_log_size_mb: int = 10
    ):
        """
        Initialize the structured logger.
        
        :param log_dir: Directory to store log files
        :param log_level: Logging level
        :param max_log_files: Maximum number of log files to keep
        :param max_log_size_mb: Maximum size of each log file in MB
        """
        # Ensure log directory exists
        self._log_dir = os.path.join(os.getcwd(), log_dir)
        os.makedirs(self._log_dir, exist_ok=True)
        
        # Create a unique session ID
        self._session_id = str(uuid.uuid4())
        
        # Configure root logger
        logging.basicConfig(level=log_level)
        
        # Create JSON file handler
        self._file_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self._log_dir, f'session_{self._session_id}.log'),
            maxBytes=max_log_size_mb * 1024 * 1024,
            backupCount=max_log_files
        )
        
        # Custom JSON formatter
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    'timestamp': datetime.now().isoformat(),
                    'session_id': self._session_id,
                    'level': record.levelname,
                    'logger': record.name,
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno,
                    'message': record.getMessage()
                }
                
                # Add any extra attributes
                if hasattr(record, 'extra'):
                    log_record['extra'] = record.extra
                
                return json.dumps(log_record)
        
        # Configure file handler
        formatter = JsonFormatter()
        self._file_handler.setFormatter(formatter)
        
        # Add handler to root logger
        logging.getLogger().addHandler(self._file_handler)

    def log(
        self, 
        message: str, 
        level: int = logging.INFO, 
        extra: Optional[Dict[str, Any]] = None,
        logger_name: Optional[str] = None
    ):
        """
        Log a structured message.
        
        :param message: Log message
        :param level: Logging level
        :param extra: Additional context for the log
        :param logger_name: Optional logger name
        """
        # Use specified logger or root logger
        logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()
        
        # Prepare extra information
        extra = extra or {}
        
        # Log the message
        logger.log(level, message, extra={'extra': extra})

    def track_event(
        self, 
        event_name: str, 
        event_data: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None
    ):
        """
        Track a specific event with structured data.
        
        :param event_name: Name of the event
        :param event_data: Additional event details
        :param category: Event category
        """
        event_log = {
            'event_name': event_name,
            'category': category,
            'data': event_data or {}
        }
        
        self.log(
            f"Event: {event_name}", 
            level=logging.INFO, 
            extra=event_log
        )

    def track_metric(
        self, 
        metric_name: str, 
        value: float,
        unit: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Track a numeric metric.
        
        :param metric_name: Name of the metric
        :param value: Numeric value of the metric
        :param unit: Optional unit of measurement
        :param tags: Optional tags for categorization
        """
        metric_log = {
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'tags': tags or {}
        }
        
        self.log(
            f"Metric: {metric_name} = {value}", 
            level=logging.INFO, 
            extra=metric_log
        )

    def get_session_id(self) -> str:
        """
        Get the current logging session ID.
        
        :return: Unique session identifier
        """
        return self._session_id
