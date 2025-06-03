"""
Configuration settings for Redmine MCP Server
"""
import os
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


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
        
        # Validate timeout and retries
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("Max retries must be non-negative")


@dataclass 
class LogConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    stream: str = "stderr"  # stderr to avoid MCP protocol interference
    
    def __post_init__(self):
        """Validate logging configuration"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {self.level}. Must be one of {valid_levels}")
        
        self.level = self.level.upper()
    
    def get_level(self) -> int:
        """Get logging level as integer"""
        return getattr(logging, self.level)


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


@dataclass
class AppConfig:
    """Complete application configuration"""
    redmine: RedmineConfig
    logging: LogConfig = field(default_factory=LogConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    
    @classmethod
    def from_environment(cls) -> 'AppConfig':
        """Create configuration from environment variables"""
        # Required Redmine config
        redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        redmine_api_key = os.environ.get('REDMINE_API_KEY')
        
        if not redmine_api_key:
            raise ValueError("REDMINE_API_KEY environment variable is required")
        
        # Optional Redmine config
        redmine_timeout = int(os.environ.get('REDMINE_TIMEOUT', '30'))
        redmine_max_retries = int(os.environ.get('REDMINE_MAX_RETRIES', '3'))
        redmine_retry_delay = float(os.environ.get('REDMINE_RETRY_DELAY', '1.0'))
        
        redmine_config = RedmineConfig(
            url=redmine_url,
            api_key=redmine_api_key,
            timeout=redmine_timeout,
            max_retries=redmine_max_retries,
            retry_delay=redmine_retry_delay
        )
        
        # Logging config
        log_config = LogConfig(
            level=os.environ.get('LOG_LEVEL', 'INFO'),
            format=os.environ.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            stream=os.environ.get('LOG_STREAM', 'stderr')
        )
        
        # Server config
        server_config = ServerConfig(
            mode=os.environ.get('SERVER_MODE', 'live'),
            transport=os.environ.get('MCP_TRANSPORT', 'stdio'),
            test_project=os.environ.get('TEST_PROJECT', 'p1')
        )
        
        return cls(
            redmine=redmine_config,
            logging=log_config,
            server=server_config
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'redmine': {
                'url': self.redmine.url,
                'timeout': self.redmine.timeout,
                'max_retries': self.redmine.max_retries,
                'retry_delay': self.redmine.retry_delay
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'stream': self.logging.stream
            },
            'server': {
                'mode': self.server.mode,
                'transport': self.server.transport,
                'test_project': self.server.test_project
            }
        }