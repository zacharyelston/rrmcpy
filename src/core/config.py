"""
Centralized configuration management for Redmine MCP Server
"""
import os
import logging
from dataclasses import dataclass
from typing import Optional


@dataclass
class RedmineConfig:
    """Redmine API configuration"""
    url: str
    api_key: str
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.url:
            raise ValueError("Redmine URL is required")
        if not self.api_key:
            raise ValueError("Redmine API key is required")
        
        # Clean URL
        self.url = self.url.rstrip('/')
        
        # Validate values
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("Max retries must be non-negative")
        if self.retry_delay < 0:
            raise ValueError("Retry delay must be non-negative")
    
    @classmethod
    def from_environment(cls) -> 'RedmineConfig':
        """Create configuration from environment variables"""
        redmine_url = os.environ.get('REDMINE_URL', 'https://demo.redmine.org')
        redmine_api_key = os.environ.get('REDMINE_API_KEY')
        
        if not redmine_api_key:
            raise ValueError("REDMINE_API_KEY environment variable is required")
        
        return cls(
            url=redmine_url,
            api_key=redmine_api_key,
            timeout=int(os.environ.get('REDMINE_TIMEOUT', '30')),
            max_retries=int(os.environ.get('REDMINE_MAX_RETRIES', '3')),
            retry_delay=float(os.environ.get('REDMINE_RETRY_DELAY', '1.0'))
        )


@dataclass
class LogConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    components: Optional[str] = None  # Comma-separated list of components to log
    structured: bool = True  # Use structured logging format
    include_context: bool = True  # Include extra context in logs
    
    def __post_init__(self):
        """Validate logging configuration"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {self.level}. Must be one of {valid_levels}")
        self.level = self.level.upper()
    
    def get_level(self) -> int:
        """Get logging level as integer"""
        return getattr(logging, self.level)
    
    def get_filtered_components(self) -> Optional[list]:
        """Get list of components to filter logs for"""
        if not self.components:
            return None
        return [c.strip() for c in self.components.split(',') if c.strip()]
    
    @classmethod
    def from_environment(cls) -> 'LogConfig':
        """Create logging configuration from environment variables"""
        return cls(
            level=os.environ.get('LOG_LEVEL', 'INFO'),
            format=os.environ.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            components=os.environ.get('LOG_COMPONENTS'),  # e.g., "issues,projects"
            structured=os.environ.get('LOG_STRUCTURED', 'true').lower() in ('true', '1', 'yes'),
            include_context=os.environ.get('LOG_CONTEXT', 'true').lower() in ('true', '1', 'yes')
        )


@dataclass
class ServerConfig:
    """MCP Server configuration"""
    mode: str = "live"  # live, test, debug
    transport: str = "stdio"
    test_project: str = "p1"
    
    def __post_init__(self):
        """Validate server configuration"""
        valid_modes = ["live", "test", "debug"]
        if self.mode.lower() not in valid_modes:
            raise ValueError(f"Invalid server mode: {self.mode}. Must be one of {valid_modes}")
        
        valid_transports = ["stdio", "sse", "streamable-http"]
        if self.transport.lower() not in valid_transports:
            raise ValueError(f"Invalid transport: {self.transport}. Must be one of {valid_transports}")
        
        self.mode = self.mode.lower()
        self.transport = self.transport.lower()
    
    @classmethod
    def from_environment(cls) -> 'ServerConfig':
        """Create server configuration from environment variables"""
        return cls(
            mode=os.environ.get('SERVER_MODE', 'live'),
            transport=os.environ.get('MCP_TRANSPORT', 'stdio'),
            test_project=os.environ.get('TEST_PROJECT', 'p1')
        )


@dataclass
class AppConfig:
    """Complete application configuration"""
    redmine: RedmineConfig
    logging: LogConfig
    server: ServerConfig
    
    @classmethod
    def from_environment(cls) -> 'AppConfig':
        """Create complete configuration from environment variables"""
        return cls(
            redmine=RedmineConfig.from_environment(),
            logging=LogConfig.from_environment(),
            server=ServerConfig.from_environment()
        )