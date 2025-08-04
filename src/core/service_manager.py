"""
Service manager module for initializing and accessing service objects

This component is part of the modular architecture that separates
client management from service management, following the "Built for Clarity"
design philosophy.
"""
import logging
from typing import Dict, Any, Optional

from ..core import get_logger
from ..services.search_service import SearchService

class ServiceManager:
    """Manages the lifecycle and access to service objects
    
    The ServiceManager is responsible for:
    1. Initializing service objects with proper configuration
    2. Managing service dependencies
    3. Providing a consistent interface to access services
    
    This follows the dependency injection pattern, allowing services
    to be mocked during testing while keeping the core application
    code clean and focused.
    """
    
    def __init__(self, config, client_manager, logger=None):
        """
        Initialize the service manager
        
        Args:
            config: Application configuration object
            client_manager: Client manager instance for accessing API clients
            logger: Optional logger instance
        """
        self.config = config
        self.client_manager = client_manager
        self.logger = logger or logging.getLogger("redmine_mcp_server.service_manager")
        self.services = {}
        self.logger.debug("Service manager initialized")
    
    def initialize_services(self):
        """Initialize all services with appropriate clients"""
        self.logger.debug("Initializing services")
        
        # Initialize search service
        issue_client = self.client_manager.get_client('issues')
        if issue_client:
            self.services['search'] = SearchService(
                config=self.config,
                client=issue_client,
                logger=get_logger('search_service')
            )
            self.logger.debug("Search service initialized")
        else:
            self.logger.warning("Could not initialize search service - issue client not available")
            
        # Additional services can be added here as they are developed
        
        self.logger.info(f"Initialized {len(self.services)} services")
        return self.services
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """
        Get a service by name
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            The service instance or None if not found
        """
        service = self.services.get(service_name)
        if not service:
            self.logger.warning(f"Requested service '{service_name}' not found")
        return service
        
    def get_search_service(self) -> Optional[SearchService]:
        """
        Get the search service instance
        
        Returns:
            The search service or None if not initialized
        """
        return self.get_service('search')
