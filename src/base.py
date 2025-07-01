"""
Base module for Redmine API functionality
Contains common code shared across feature modules
"""
import json
import logging
import requests
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from .connection_manager import ConnectionManager
from .core.errors import (
    ErrorHandler, ErrorResponse, ErrorCode,
    validation_error, http_error, connection_error, 
    timeout_error, unexpected_error
)
from .core.logging import log_api_request, log_error_with_context


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
        
        # Initialize error handler with logger
        self.error_handler = ErrorHandler(self.logger)
        
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
            return self.error_handler.handle_validation_error(
                "Request data must be a dictionary",
                context={"data_type": type(data).__name__}
            )
        
        # Check required fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return self.error_handler.handle_validation_error(
                f"Missing required fields: {', '.join(missing_fields)}",
                field_errors={field: "This field is required" for field in missing_fields},
                context={"provided_fields": list(data.keys())}
            )
        
        # Check field types if specified
        if field_types:
            field_errors = {}
            for field, expected_types in field_types.items():
                if field not in data or data[field] is None:
                    continue
                    
                # Convert single type to tuple for consistent handling
                expected_types = expected_types if isinstance(expected_types, tuple) else (expected_types,)
                
                # Check if the field value is an instance of any of the expected types
                if not any(isinstance(data[field], t) for t in expected_types if t is not type(None)):
                    # Format type names for error message
                    type_names = []
                    for t in expected_types:
                        if t is type(None):
                            type_names.append('None')
                        elif hasattr(t, '__name__'):
                            type_names.append(t.__name__)
                        else:
                            type_names.append(str(t))
                    field_errors[field] = f"Must be one of: {', '.join(type_names)}"
            
            if field_errors:
                return self.error_handler.handle_validation_error(
                    "Field type validation failed",
                    field_errors=field_errors,
                    context={"data": data}
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
            
            # Log successful request with structured logging
            log_api_request(
                self.logger,
                method,
                url,
                duration_ms,
                response.status_code,
                params=params,
                has_data=bool(data)
            )
            
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
            log_api_request(
                self.logger,
                method,
                url,
                duration_ms,
                0,  # No status code for failed requests
                error=str(e),
                error_type=type(e).__name__
            )
            return self._handle_request_error(e, method, url, data or {})
        except ValueError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_error_with_context(
                self.logger,
                e,
                f"JSON parsing for {method} {url}",
                duration_ms=duration_ms,
                url=url
            )
            return ErrorResponse.create(
                ErrorCode.INVALID_JSON,
                f"Invalid JSON response: {str(e)}",
                502,
                context={"url": url, "method": method}
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_error_with_context(
                self.logger,
                e,
                f"API request {method} {url}",
                duration_ms=duration_ms,
                url=url,
                data=data
            )
            return self.error_handler.handle_unexpected_error(
                e,
                operation=f"{method} {url}",
                context={"data": data, "params": params}
            )
    
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
        # Handle specific error types
        if isinstance(error, requests.exceptions.ConnectionError):
            return self.error_handler.handle_connection_error(
                error,
                url=url,
                context={"method": method, "data": data}
            )
            
        elif isinstance(error, requests.exceptions.Timeout):
            return self.error_handler.handle_timeout_error(
                error,
                url=url,
                timeout=getattr(self.connection_manager, 'timeout', None)
            )
            
        elif isinstance(error, requests.exceptions.HTTPError):
            if hasattr(error, 'response') and error.response is not None:
                status_code = error.response.status_code
                response_body = error.response.text
                
                # Build appropriate error message based on status code
                message_map = {
                    401: "Invalid API key or insufficient permissions",
                    403: "Access forbidden - check user permissions",
                    404: f"Resource not found",
                    422: "Invalid data provided",
                    429: "Rate limit exceeded",
                    500: "Redmine server error",
                    502: "Bad gateway",
                    503: "Service unavailable",
                    504: "Gateway timeout"
                }
                
                base_message = message_map.get(status_code, f"HTTP {status_code} error")
                
                # Try to extract more specific error from response
                try:
                    response_data = error.response.json()
                    if 'errors' in response_data:
                        if isinstance(response_data['errors'], list):
                            base_message += f": {', '.join(response_data['errors'])}"
                        else:
                            base_message += f": {response_data['errors']}"
                    elif 'error' in response_data:
                        base_message += f": {response_data['error']}"
                except:
                    pass
                
                return self.error_handler.handle_http_error(
                    status_code,
                    base_message,
                    response_body=response_body,
                    url=url,
                    method=method
                )
            else:
                # HTTP error without response
                return ErrorResponse.create(
                    ErrorCode.REQUEST_ERROR,
                    f"HTTP error: {str(error)}",
                    500,
                    context={"url": url, "method": method}
                )
                
        else:
            # Generic request error
            return ErrorResponse.create(
                ErrorCode.REQUEST_ERROR,
                f"Request failed: {str(error)}",
                500,
                details={"error_type": type(error).__name__},
                context={"url": url, "method": method, "data": data}
            )
    
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
            
        # Redmine API typically uses URL patterns like '/issues/123.json' or 'https://example.org/issues/123.json'
        try:
            # Handle both absolute and relative URLs
            # First, get just the path part if it's an absolute URL
            if location.startswith('http'):
                # For absolute URLs, extract just the path
                from urllib.parse import urlparse
                location = urlparse(location).path
            
            # Strip off any file extension (.json, .xml)
            location = location.split('.')[0] if '.' in location else location
            
            # Split by '/' and get the last part which should be the ID
            parts = [p for p in location.rstrip('/').split('/') if p]
            if not parts:
                return None
                
            # Try to convert the last part to an integer (the ID)
            id_str = parts[-1]
            if id_str.isdigit():
                return int(id_str)
            else:
                self.logger.warning(f"Last part of Location '{id_str}' is not a digit")
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
        # Use the new ErrorResponse class
        return ErrorResponse.create(
            error_code,
            error_message,
            status_code
        )
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
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
