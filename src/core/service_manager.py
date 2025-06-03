"""
Service manager module for initializing and accessing service layer
"""
import logging
from typing import Dict, Any

from ..core import get_logger
from ..services import IssueService

class ServiceManager:
    """Manages the lifecycle and access to service layer"""
    
    def __init__(self, config, client_manager, logger=None):
        """
        Initialize the service manager
        
        Args:
            config: Application configuration
            client_manager: Client manager instance
            logger: Optional logger instance
        """
        self.config = config
        self.client_manager = client_manager
        self.logger = logger or logging.getLogger("redmine_mcp_server.service_manager")
        self.services = {}
        self.logger.debug("Service manager initialized")
    
    def initialize_services(self):
        """Initialize all services"""
        self.logger.debug("Initializing services")
        
        # Initialize issue service
        self.services['issues'] = IssueService(
            config=self.config.redmine,
            issue_client=self.client_manager.get_client('issues'),
            logger=get_logger('issue_service')
        )
        
        self.logger.debug("Services initialized")
        return self.services
        
    def get_service(self, service_name: str) -> Any:
        """Get a service by name"""
        if service_name not in self.services:
            self.logger.error(f"Service '{service_name}' not found")
            return None
        return self.services[service_name]
    
    def get_all_services(self) -> Dict[str, Any]:
        """Get all services"""
        return self.services
