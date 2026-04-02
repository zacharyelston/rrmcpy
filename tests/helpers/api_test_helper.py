#!/usr/bin/env python3
"""
API Test Helper for Redmine MCP testing.

Provides utilities for testing with real Redmine API connections
or FastMCP in-memory testing patterns.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List

# Handle import paths for both local development and CI environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from src.base import RedmineBaseClient
    from src.core.client_manager import ClientManager
    from src.core.service_manager import ServiceManager
except ImportError:
    # Alternative import path for CI environment
    from rrmcpy.src.base import RedmineBaseClient
    from rrmcpy.src.core.client_manager import ClientManager
    from rrmcpy.src.core.service_manager import ServiceManager


class APITestHelper:
    """Helper for testing with real Redmine API connections"""
    
    def __init__(self, redmine_url=None, api_key=None):
        """
        Initialize the API test helper
        
        Args:
            redmine_url: URL of the Redmine server (default: from environment)
            api_key: API key for Redmine (default: from environment)
        """
        self.redmine_url = redmine_url or os.environ.get('REDMINE_URL')
        self.api_key = api_key or os.environ.get('REDMINE_API_KEY')
        
        if not self.redmine_url or not self.api_key:
            raise ValueError(
                "Redmine URL and API key must be provided either directly "
                "or through environment variables REDMINE_URL and REDMINE_API_KEY"
            )
        
        self.logger = logging.getLogger(__name__)
        self.client_manager = self._create_client_manager()
        self.service_manager = ServiceManager(self.client_manager)
        
    def _create_client_manager(self):
        """Create a client manager for testing with real API connection"""
        client_manager = ClientManager()
        
        # Create real Redmine client with API key
        redmine_client = RedmineBaseClient(
            url=self.redmine_url,
            api_key=self.api_key
        )
        
        client_manager.register_client('redmine', redmine_client)
        return client_manager
        
    def get_redmine_client(self):
        """Get the Redmine client for API calls"""
        return self.client_manager.get_client('redmine')
    
    def get_service_manager(self):
        """Get the service manager for creating services"""
        return self.service_manager


class TestEnvironment:
    """Environment configuration for tests"""
    
    @staticmethod
    def is_using_real_api():
        """Check if tests should use real API connections"""
        return os.environ.get('USE_REAL_API', 'false').lower() == 'true'
    
    @staticmethod
    def get_test_project_id():
        """Get test project ID for API tests"""
        return os.environ.get('TEST_PROJECT_ID', 'test-project')
    
    @staticmethod
    def setup_test_environment():
        """Set up environment for tests"""
        # Set SERVER_MODE=live to ensure real API calls
        os.environ['SERVER_MODE'] = 'live'
        
        # Log environment configuration
        logging.info(f"Test environment: USE_REAL_API={TestEnvironment.is_using_real_api()}")
        logging.info(f"Test environment: TEST_PROJECT_ID={TestEnvironment.get_test_project_id()}")
