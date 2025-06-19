"""
Centralized logging configuration for Redmine MCP Server

This module provides:
- Structured logging with consistent format
- Component-based log filtering
- Context-aware logging
- Integration with error handling
"""
import sys
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from .config import LogConfig


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured logs"""
    
    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra
        
    def format(self, record: logging.LogRecord) -> str:
        # Base log structure
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add location info
        log_data["location"] = {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName
        }
        
        # Add any extra fields
        if self.include_extra:
            # Standard fields to exclude
            exclude_fields = {
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'pathname', 'process', 'processName', 'relativeCreated',
                'thread', 'threadName', 'getMessage', 'stack_info',
                'exc_info', 'exc_text'
            }
            
            extras = {k: v for k, v in record.__dict__.items() 
                     if k not in exclude_fields}
            if extras:
                log_data["context"] = extras
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Format based on log level
        if record.levelno >= logging.ERROR:
            # For errors, always use structured format
            return json.dumps(log_data, separators=(',', ':'))
        else:
            # For info/debug, use simpler format unless extra data present
            if "context" in log_data or "exception" in log_data:
                return json.dumps(log_data, separators=(',', ':'))
            else:
                return f"{log_data['timestamp']} - {record.name} - {record.levelname} - {record.getMessage()}"


class ComponentFilter(logging.Filter):
    """Filter logs by component name"""
    
    def __init__(self, components: Optional[list] = None):
        super().__init__()
        self.components = components or []
        
    def filter(self, record: logging.LogRecord) -> bool:
        if not self.components:
            return True
        
        # Check if record is from an allowed component
        for component in self.components:
            if record.name.startswith(f"redmine_mcp_server.{component}"):
                return True
        return False


def setup_logging(config: Optional[LogConfig] = None) -> logging.Logger:
    """
    Setup centralized logging configuration with structured logging
    
    Args:
        config: LogConfig instance, defaults to environment-based config
        
    Returns:
        Configured logger instance
    """
    if config is None:
        config = LogConfig.from_environment()
    
    # Remove existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create handler with structured formatter
    handler = logging.StreamHandler(sys.stderr)
    
    # Use structured formatter for production, simple for development
    if config.level.upper() in ('ERROR', 'WARNING', 'INFO'):
        formatter = StructuredFormatter(include_extra=True)
    else:
        # Development mode - use readable format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger.setLevel(config.get_level())
    root_logger.addHandler(handler)
    
    # Get logger for the application
    logger = logging.getLogger('redmine_mcp_server')
    logger.setLevel(config.get_level())
    
    # Add component filter if specified in environment
    components = config.get_filtered_components()
    if components:
        logger.addFilter(ComponentFilter(components))
    
    logger.info(f"Logging configured at {config.level} level", extra={
        "config": {
            "level": config.level,
            "format": config.format,
            "components": components
        }
    })
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with consistent configuration
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    # Ensure name is properly namespaced
    if not name.startswith('redmine_mcp_server'):
        name = f'redmine_mcp_server.{name}'
    return logging.getLogger(name)


def log_operation(logger: logging.Logger, operation: str, **context):
    """
    Log an operation with context
    
    Args:
        logger: Logger instance
        operation: Operation name
        **context: Additional context to log
    """
    logger.info(f"Operation: {operation}", extra={
        "operation": operation,
        **context
    })


def log_api_request(logger: logging.Logger, method: str, url: str, 
                   duration_ms: float, status_code: int, **extra):
    """
    Log an API request with standard fields
    
    Args:
        logger: Logger instance
        method: HTTP method
        url: Request URL
        duration_ms: Request duration in milliseconds
        status_code: Response status code
        **extra: Additional context
    """
    logger.info(f"API request: {method} {url} ({status_code}) in {duration_ms:.2f}ms", extra={
        "api_request": {
            "method": method,
            "url": url,
            "duration_ms": duration_ms,
            "status_code": status_code
        },
        **extra
    })


def log_error_with_context(logger: logging.Logger, error: Exception, 
                          operation: str, **context):
    """
    Log an error with full context
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        operation: Operation during which error occurred
        **context: Additional context
    """
    logger.error(f"Error in {operation}: {str(error)}", extra={
        "error_type": type(error).__name__,
        "error_message": str(error),
        "operation": operation,
        **context
    }, exc_info=True)
