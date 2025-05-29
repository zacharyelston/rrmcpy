"""
Comprehensive logging configuration for the Redmine MCP Server
Provides structured logging with configurable levels and formats
"""
import os
import sys
import logging
import logging.handlers
from datetime import datetime
from typing import Optional, Dict, Any
import json


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that creates structured log entries with context
    """
    def __init__(self, include_context: bool = True):
        super().__init__()
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON or plain text"""
        # Create base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add context information if available
        if self.include_context:
            if hasattr(record, 'request_id'):
                log_entry["request_id"] = record.request_id
            if hasattr(record, 'component'):
                log_entry["component"] = record.component
            if hasattr(record, 'operation'):
                log_entry["operation"] = record.operation
            if hasattr(record, 'duration_ms'):
                log_entry["duration_ms"] = record.duration_ms
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields that were passed to the logging call
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'exc_info', 'exc_text',
                          'stack_info', 'getMessage']:
                if not key.startswith('_'):
                    log_entry["extra"] = log_entry.get("extra", {})
                    log_entry["extra"][key] = value
        
        return json.dumps(log_entry, default=str)


class PlainTextFormatter(logging.Formatter):
    """
    Plain text formatter for human-readable console output
    """
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


class RedmineLogger:
    """
    Enhanced logger for the Redmine MCP Server with context management
    """
    def __init__(self, name: str, level: str = "INFO", structured: bool = False):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self.structured = structured
        self._request_context = {}
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        if structured:
            console_handler.setFormatter(StructuredFormatter())
        else:
            console_handler.setFormatter(PlainTextFormatter())
        
        self.logger.addHandler(console_handler)
        
        # Add file handler if specified in environment
        log_file = os.environ.get('LOG_FILE')
        if log_file:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(file_handler)
    
    def set_request_context(self, request_id: str, component: str = None, 
                           operation: str = None):
        """Set context for the current request"""
        self._request_context = {
            'request_id': request_id,
            'component': component,
            'operation': operation
        }
    
    def clear_context(self):
        """Clear the current request context"""
        self._request_context = {}
    
    def _add_context(self, extra: Dict[str, Any]) -> Dict[str, Any]:
        """Add request context to log extra data"""
        if extra is None:
            extra = {}
        extra.update(self._request_context)
        return extra
    
    def debug(self, message: str, extra: Dict[str, Any] = None):
        """Log debug message with context"""
        self.logger.debug(message, extra=self._add_context(extra))
    
    def info(self, message: str, extra: Dict[str, Any] = None):
        """Log info message with context"""
        self.logger.info(message, extra=self._add_context(extra))
    
    def warning(self, message: str, extra: Dict[str, Any] = None):
        """Log warning message with context"""
        self.logger.warning(message, extra=self._add_context(extra))
    
    def error(self, message: str, extra: Dict[str, Any] = None, exc_info: bool = False):
        """Log error message with context"""
        self.logger.error(message, extra=self._add_context(extra), exc_info=exc_info)
    
    def critical(self, message: str, extra: Dict[str, Any] = None, exc_info: bool = False):
        """Log critical message with context"""
        self.logger.critical(message, extra=self._add_context(extra), exc_info=exc_info)
    
    def log_api_request(self, method: str, url: str, status_code: int, 
                       duration_ms: float, extra: Dict[str, Any] = None):
        """Log API request with timing information"""
        message = f"API {method} {url} -> {status_code} ({duration_ms:.2f}ms)"
        log_extra = self._add_context(extra or {})
        log_extra.update({
            'api_method': method,
            'api_url': url,
            'status_code': status_code,
            'duration_ms': duration_ms
        })
        self.logger.info(message, extra=log_extra)
    
    def log_operation(self, operation: str, success: bool, duration_ms: float = None,
                     details: str = None, extra: Dict[str, Any] = None):
        """Log operation completion with success status"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Operation {operation} {status}"
        if duration_ms:
            message += f" ({duration_ms:.2f}ms)"
        if details:
            message += f" - {details}"
        
        log_extra = self._add_context(extra or {})
        log_extra.update({
            'operation': operation,
            'success': success
        })
        if duration_ms:
            log_extra['duration_ms'] = duration_ms
        
        level = self.info if success else self.error
        level(message, extra=log_extra)


def configure_logging(level: str = None, structured: bool = None) -> RedmineLogger:
    """
    Configure logging for the Redmine MCP Server
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        structured: Whether to use structured JSON logging
        
    Returns:
        Configured RedmineLogger instance
    """
    # Get configuration from environment if not provided
    if level is None:
        level = os.environ.get('LOG_LEVEL', 'INFO')
    
    if structured is None:
        structured = os.environ.get('LOG_FORMAT', '').lower() == 'json'
    
    # Configure the main logger
    logger = RedmineLogger('redmine_mcp', level, structured)
    
    # Log startup information
    logger.info("Logging configured", extra={
        'log_level': level,
        'structured': structured,
        'log_file': os.environ.get('LOG_FILE', 'console only')
    })
    
    return logger


# Context manager for operation logging
class LoggedOperation:
    """Context manager for logging operations with timing"""
    
    def __init__(self, logger: RedmineLogger, operation: str, component: str = None):
        self.logger = logger
        self.operation = operation
        self.component = component
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.logger.set_request_context(
            request_id=f"{self.operation}_{int(self.start_time.timestamp() * 1000)}",
            component=self.component,
            operation=self.operation
        )
        self.logger.info(f"Starting operation: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (datetime.utcnow() - self.start_time).total_seconds() * 1000
        success = exc_type is None
        
        if exc_type:
            self.logger.error(f"Operation failed: {self.operation}", 
                            extra={'error_type': exc_type.__name__, 'error_message': str(exc_val)},
                            exc_info=True)
        
        self.logger.log_operation(self.operation, success, duration_ms)
        self.logger.clear_context()