"""
Base module for Redmine API functionality
Contains common code shared across feature modules
"""
import logging
import requests
from typing import Dict, List, Optional, Any, Union


class RedmineBaseClient:
    """
    Base client for Redmine API interactions
    Provides core functionality used by feature-specific modules
    """
    def __init__(self, base_url: str, api_key: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the Redmine API client
        
        Args:
            base_url: The base URL of the Redmine instance
            api_key: The API key for authentication
            logger: Optional logger instance for logging
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.logger = logger or logging.getLogger(__name__)
        
        # Common headers for all requests
        self.headers = {
            'X-Redmine-API-Key': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                   params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Redmine API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint to call
            data: Optional data to send in the request body
            params: Optional query parameters
            
        Returns:
            Dictionary containing the API response
        """
        url = f"{self.base_url}/{endpoint}"
        self.logger.debug(f"Making {method} request to {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, params=params)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, params=params)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making request to Redmine API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status code: {e.response.status_code}")
                self.logger.error(f"Response body: {e.response.text}")
            raise