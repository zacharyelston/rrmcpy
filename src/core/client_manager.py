"""
Client manager module for initializing and accessing API clients
"""
import logging
from typing import Dict, Any, Optional

from ..core import get_logger
from ..users import UserClient
from ..projects import ProjectClient
from ..issues import IssueClient
from ..groups import GroupClient
from ..roadmap import RoadmapClient
from ..versions import VersionClient

class ClientManager:
    """Manages the lifecycle and access to API clients"""
    
    def __init__(self, config, logger=None):
        """
        Initialize the client manager
        
        Args:
            config: Application configuration object
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or logging.getLogger("redmine_mcp_server.client_manager")
        self.clients = {}
        self.logger.debug("Client manager initialized")
    
    def initialize_clients(self):
        """Initialize all API clients"""
        self.logger.debug("Initializing API clients")
        
        # Initialize issue client
        self.clients['issues'] = IssueClient(
            base_url=self.config.redmine.url,
            api_key=self.config.redmine.api_key,
            logger=get_logger('issue_client')
        )
        
        # Initialize project client
        self.clients['projects'] = ProjectClient(
            base_url=self.config.redmine.url,
            api_key=self.config.redmine.api_key,
            logger=get_logger('project_client')
        )
        
        # Initialize user client
        self.clients['users'] = UserClient(
            base_url=self.config.redmine.url,
            api_key=self.config.redmine.api_key,
            logger=get_logger('user_client')
        )
        
        # Initialize group client
        self.clients['groups'] = GroupClient(
            base_url=self.config.redmine.url,
            api_key=self.config.redmine.api_key,
            logger=get_logger('group_client')
        )
        
        # Initialize roadmap client for version management
        self.clients['roadmap'] = RoadmapClient(
            base_url=self.config.redmine.url,
            api_key=self.config.redmine.api_key,
            logger=get_logger('roadmap_client')
        )
        
        # Initialize version client
        self.clients['versions'] = VersionClient(
            base_url=self.config.redmine.url,
            api_key=self.config.redmine.api_key,
            logger=get_logger('version_client')
        )
        
        self.logger.debug("API clients initialized")
        return self.clients
        
    def get_client(self, client_name: str) -> Any:
        """Get a client by name"""
        if client_name not in self.clients:
            self.logger.error(f"Client '{client_name}' not found")
            return None
        return self.clients[client_name]
    
    def get_all_clients(self) -> Dict[str, Any]:
        """Get all clients"""
        return self.clients
