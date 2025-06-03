"""
Base module for Redmine API functionality
Contains common code shared across feature modules
"""
import json
import logging
import requests
import time
from typing import Dict, List, Optional, Any, Union
from .connection_manager import ConnectionManager


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
        
        # Initialize connection manager for automatic reconnection
        self.connection_manager = ConnectionManager(base_url, api_key, self.logger)
        
        # Common headers for all requests
        self.headers = {
            'X-Redmine-API-Key': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def validate_input(self, data: Dict, required_fields: List[str], 
                      field_types: Optional[Dict] = None) -> Optional[Dict]:
        """
        Validate input data for API requests
        
        Args:
            data: Data to validate
            required_fields: List of required field names
            field_types: Optional mapping of field names to expected types
            
        Returns:
            Error response dict if validation fails, None if valid
        """
        if not isinstance(data, dict):
            return self._create_error_response(
                "VALIDATION_ERROR", 
                "Request data must be a dictionary", 
                400
            )
        
        # Check required fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return self._create_error_response(
                "VALIDATION_ERROR",
                f"Missing required fields: {', '.join(missing_fields)}",
                400
            )
        
        # Check field types if specified
        if field_types:
            for field, expected_type in field_types.items():
                if field in data and not isinstance(data[field], expected_type):
                    return self._create_error_response(
                        "VALIDATION_ERROR",
                        f"Field '{field}' must be of type {expected_type.__name__}",
                        400
                    )
        
        return None
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                   params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Redmine API with enhanced logging and timing
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint to call
            data: Optional data to send in the request body
            params: Optional query parameters
            
        Returns:
            Dictionary containing the API response
        """
        url = f"{self.base_url}/{endpoint}"
        start_time = time.time()
        
        self.logger.debug(f"Making {method} request to {url}")
        if data:
            self.logger.debug(f"Request data: {data}")
        if params:
            self.logger.debug(f"Request params: {params}")
        
        try:
            # Use connection manager for automatic retry and reconnection
            kwargs = {}
            if params:
                kwargs['params'] = params
            if data:
                kwargs['json'] = data
                self.logger.debug(f"REQUEST BODY: {json.dumps(data, indent=2)}")
            
            # Enhanced debug logging for request
            self.logger.debug(f"REQUEST: {method} {url} with kwargs: {kwargs}")
            self.logger.debug(f"REQUEST HEADERS: {self.connection_manager.session.headers if hasattr(self.connection_manager, 'session') else 'No session headers'}")
            
            response = self.connection_manager.make_request(method, url, **kwargs)
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Enhanced debug logging for response
            self.logger.debug(f"RESPONSE STATUS: {response.status_code}")
            self.logger.debug(f"RESPONSE HEADERS: {dict(response.headers)}")
            if response.content:
                try:
                    content_preview = json.dumps(response.json(), indent=2)[:1000] + "..." if len(response.content) > 1000 else json.dumps(response.json(), indent=2)
                    self.logger.debug(f"RESPONSE CONTENT: {content_preview}")
                except Exception as e:
                    self.logger.debug(f"RESPONSE CONTENT (non-JSON): {response.content[:500]}...")
            
            try:
                response.raise_for_status()
            except Exception as e:
                self.logger.error(f"HTTP ERROR: {str(e)}")
                raise
            
            # Log successful request
            self.logger.debug(f"Request {method} {url} completed successfully in {duration_ms:.2f}ms (status: {response.status_code})")
            
            # Handle 201 Created status specially for resource creation
            if response.status_code == 201:  # Created
                if response.content:
                    result = response.json()
                    self.logger.debug(f"Created resource with data: {list(result.keys()) if isinstance(result, dict) else 'non-dict response'}")
                    return result
                
                # For APIs that return empty 201 responses, try to extract ID from Location header
                resource_id = self._extract_id_from_location(response)
                if resource_id:
                    self.logger.debug(f"Created resource with ID: {resource_id} (extracted from Location header)")
                    return {"id": resource_id, "success": True}
                
                # Fallback for empty responses with no Location header
                return {"success": True, "status_code": 201}
            
            # Handle normal responses with content
            if response.content:
                result = response.json()
                self.logger.debug(f"Response data keys: {list(result.keys()) if isinstance(result, dict) else 'non-dict response'}")
                return result
            
            # For empty responses that aren't 201 Created
            return {"success": True, "status_code": response.status_code}
            
        except requests.exceptions.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Request {method} {url} failed after {duration_ms:.2f}ms: {e}")
            return self._handle_request_error(e, method, url, data or {})
        except ValueError as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Invalid JSON response from {url} after {duration_ms:.2f}ms: {e}")
            return self._create_error_response("INVALID_JSON", str(e), 502)
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Unexpected error making request to {url} after {duration_ms:.2f}ms: {e}")
            return self._create_error_response("UNEXPECTED_ERROR", str(e), 500)
    
    def _handle_request_error(self, error: requests.exceptions.RequestException, 
                             method: str, url: str, data: Dict) -> Dict:
        """
        Handle HTTP request errors with detailed error reporting
        
        Args:
            error: The request exception that occurred
            method: HTTP method used
            url: URL that was requested
            data: Request data if any
            
        Returns:
            Standardized error response dictionary
        """
        error_code = "REQUEST_ERROR"
        status_code = 500
        error_message = str(error)
        
        # Handle specific error types
        if isinstance(error, requests.exceptions.ConnectionError):
            error_code = "CONNECTION_ERROR"
            error_message = f"Failed to connect to Redmine server at {url}"
            status_code = 503
            self.logger.error(f"Connection error to {url}: {error}")
            
        elif isinstance(error, requests.exceptions.Timeout):
            error_code = "TIMEOUT_ERROR"
            error_message = f"Request to {url} timed out"
            status_code = 504
            self.logger.error(f"Timeout error for {method} {url}: {error}")
            
        elif isinstance(error, requests.exceptions.HTTPError):
            if hasattr(error, 'response') and error.response is not None:
                status_code = error.response.status_code
                
                # Handle specific HTTP status codes
                if status_code == 401:
                    error_code = "AUTHENTICATION_ERROR"
                    error_message = "Invalid API key or insufficient permissions"
                elif status_code == 403:
                    error_code = "AUTHORIZATION_ERROR"
                    error_message = "Access forbidden - check user permissions"
                elif status_code == 404:
                    error_code = "NOT_FOUND"
                    error_message = f"Resource not found: {url}"
                elif status_code == 422:
                    error_code = "VALIDATION_ERROR"
                    error_message = "Invalid data provided"
                    # Try to extract validation errors from response
                    try:
                        response_data = error.response.json()
                        if 'errors' in response_data:
                            error_message = f"Validation failed: {response_data['errors']}"
                    except:
                        pass
                elif status_code >= 500:
                    error_code = "SERVER_ERROR"
                    error_message = f"Redmine server error (HTTP {status_code})"
                
                self.logger.error(f"HTTP {status_code} error for {method} {url}: {error}")
                self.logger.error(f"Response body: {error.response.text}")
            else:
                self.logger.error(f"HTTP error for {method} {url}: {error}")
                
        else:
            self.logger.error(f"Request error for {method} {url}: {error}")
        
        return self._create_error_response(error_code, error_message, status_code)
    
    def _extract_id_from_location(self, response) -> Optional[int]:
        """
        Extract resource ID from Location header for POST requests
        
        Args:
            response: The HTTP response object
            
        Returns:
            Integer ID if found in Location header, None otherwise
        """
        location = response.headers.get('Location')
        if not location:
            return None
            
        # Redmine API typically uses URL patterns like '/issues/123.json'
        try:
            # Strip off any file extension (.json, .xml)
            location = location.split('.')[0] if '.' in location else location
            
            # Split by '/' and get the last part which should be the ID
            parts = location.rstrip('/').split('/')
            if not parts:
                return None
                
            # Try to convert the last part to an integer (the ID)
            id_str = parts[-1]
            if id_str.isdigit():
                return int(id_str)
        except Exception as e:
            self.logger.warning(f"Failed to extract ID from Location header '{location}': {e}")
            
        return None
        
    def _create_error_response(self, error_code: str, error_message: str, 
                              status_code: int = 500) -> Dict:
        """
        Create a standardized error response
        
        Args:
            error_code: Standard error code
            error_message: Human-readable error message
            status_code: HTTP status code
            
        Returns:
            Standardized error response dictionary
        """
        return {
            "error": True,
            "error_code": error_code,
            "message": error_message,
            "status_code": status_code,
            "timestamp": self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def health_check(self) -> bool:
        """
        Check the health of the Redmine connection
        
        Returns:
            True if the connection is healthy
        """
        return self.connection_manager.health_check()
    
    def configure_connection_settings(self, **kwargs):
        """
        Configure connection retry and timeout settings
        
        Args:
            max_retries: Maximum number of retries for failed requests
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            backoff_factor: Factor for exponential backoff
            timeout: Request timeout in seconds
        """
        self.connection_manager.configure_retry_settings(**kwargs)