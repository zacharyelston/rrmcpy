"""
Centralized logging configuration for Redmine MCP Server
"""
import sys
import logging
from typing import Optional
from .config import LogConfig


def setup_logging(config: Optional[LogConfig] = None) -> logging.Logger:
    """
    Setup centralized logging configuration
    
    Args:
        config: LogConfig instance, defaults to environment-based config
        
    Returns:
        Configured logger instance
    """
    if config is None:
        config = LogConfig.from_environment()
    
    # Configure root logger
    logging.basicConfig(
        level=config.get_level(),
        format=config.format,
        stream=sys.stderr,  # Use stderr to avoid MCP protocol interference
        force=True  # Override any existing configuration
    )
    
    # Get logger for the application
    logger = logging.getLogger('redmine_mcp_server')
    logger.setLevel(config.get_level())
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with consistent configuration
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f'redmine_mcp_server.{name}')