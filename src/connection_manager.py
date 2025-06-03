"""
Connection manager for robust Redmine API connectivity
Handles automatic reconnection, retry logic, and connection health monitoring
"""
import time
import random
import logging
import requests
from typing import Dict, Optional, Callable, Any
from functools import wraps


class ConnectionManager:
    """
    Manages connections to Redmine with automatic retry and health checking
    """
    
    def __init__(self, base_url: str, api_key: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the connection manager
        
        Args:
            base_url: The base URL of the Redmine instance
            api_key: The API key for authentication
            logger: Optional logger instance
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.logger = logger or logging.getLogger(__name__)
        
        # Connection settings
        self.max_retries = 3
        self.base_delay = 1.0  # Base delay in seconds
        self.max_delay = 60.0  # Maximum delay in seconds
        self.backoff_factor = 2.0  # Exponential backoff factor
        self.timeout = 30.0  # Request timeout in seconds
        
        # Connection state
        self._connection_healthy = True
        self._last_health_check = 0
        self._health_check_interval = 300  # 5 minutes
        
        # Headers for requests
        self.headers = {
            'X-Redmine-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Create a session for connection reuse and consistent headers
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Log initialization
        self.logger.debug(f"ConnectionManager initialized for {base_url}")
        self.logger.debug(f"Using API key: {'*'*(len(self.api_key)-4)}{self.api_key[-4:] if len(self.api_key) > 4 else '****'}")
    
    def configure_retry_settings(self, max_retries: int = None, base_delay: float = None,
                                max_delay: float = None, backoff_factor: float = None,
                                timeout: float = None):
        """
        Configure retry and connection settings
        
        Args:
            max_retries: Maximum number of retries for failed requests
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            backoff_factor: Factor for exponential backoff
            timeout: Request timeout in seconds
        """
        if max_retries is not None:
            self.max_retries = max_retries
        if base_delay is not None:
            self.base_delay = base_delay
        if max_delay is not None:
            self.max_delay = max_delay
        if backoff_factor is not None:
            self.backoff_factor = backoff_factor
        if timeout is not None:
            self.timeout = timeout
            
        self.logger.debug(f"Retry settings: max_retries={self.max_retries}, "
                         f"base_delay={self.base_delay}, max_delay={self.max_delay}, "
                         f"backoff_factor={self.backoff_factor}, timeout={self.timeout}")
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for exponential backoff with jitter
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        # Exponential backoff: base_delay * (backoff_factor ^ attempt)
        delay = self.base_delay * (self.backoff_factor ** attempt)
        
        # Cap at maximum delay
        delay = min(delay, self.max_delay)
        
        # Add jitter (random factor between 0.5 and 1.5)
        jitter = random.uniform(0.5, 1.5)
        delay *= jitter
        
        return delay
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error is retryable
        
        Args:
            error: The exception that occurred
            
        Returns:
            True if the error should be retried
        """
        if isinstance(error, requests.exceptions.ConnectionError):
            return True
        elif isinstance(error, requests.exceptions.Timeout):
            return True
        elif isinstance(error, requests.exceptions.HTTPError):
            if hasattr(error, 'response') and error.response is not None:
                status_code = error.response.status_code
                # Retry on server errors (5xx) and some client errors
                if status_code >= 500:
                    return True
                elif status_code in [408, 429]:  # Request timeout, too many requests
                    return True
        
        return False
    
    def health_check(self) -> bool:
        """
        Perform a health check on the Redmine connection
        
        Returns:
            True if the connection is healthy
        """
        current_time = time.time()
        
        # Use cached result if within interval
        if (current_time - self._last_health_check) < self._health_check_interval:
            return self._connection_healthy
        
        self.logger.debug("Performing Redmine connection health check")
        
        try:
            # Use a lightweight endpoint for health checking
            url = f"{self.base_url}/users/current.json"
            self.logger.debug(f"Health check URL: {url}")
            
            # Use the session for consistent headers and authentication
            response = self.session.get(url, timeout=10)
            
            # Log response details
            self.logger.debug(f"Health check status code: {response.status_code}")
            
            response.raise_for_status()
            
            # Try to get user info to verify authentication
            user_data = response.json()
            if user_data and 'user' in user_data:
                username = user_data['user'].get('login', 'unknown')
                self.logger.debug(f"Authenticated as: {username}")
            
            self._connection_healthy = True
            self._last_health_check = current_time
            self.logger.info("Health check passed - Redmine connection is healthy")
            
        except Exception as e:
            self._connection_healthy = False
            self._last_health_check = current_time
            self.logger.warning(f"Health check failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    self.logger.warning(f"Error details: {error_details}")
                except:
                    self.logger.warning(f"Error status code: {e.response.status_code}")
        
        return self._connection_healthy
    
    def execute_with_retry(self, request_func: Callable, *args, **kwargs) -> Any:
        """
        Execute a request function with automatic retry logic
        
        Args:
            request_func: Function to execute (should make the HTTP request)
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the request function
            
        Raises:
            The last exception if all retries fail
        """
        last_exception = None
        
        # Create a copy of kwargs to avoid modifying the original
        request_kwargs = kwargs.copy()
        if 'timeout' not in request_kwargs:
            request_kwargs['timeout'] = self.timeout
        
        for attempt in range(self.max_retries + 1):
            try:
                # Call request_func without any arguments since our _make_request is self-contained
                result = request_func()
                
                # If we get here, the request succeeded
                if attempt > 0:
                    self.logger.info(f"Request succeeded on attempt {attempt + 1}")
                
                # Mark connection as healthy after successful request
                self._connection_healthy = True
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Log the error
                self.logger.warning(f"Request failed on attempt {attempt + 1}: {e}")
                
                # Check if we should retry
                if attempt < self.max_retries and self._is_retryable_error(e):
                    delay = self._calculate_delay(attempt)
                    self.logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    # Mark connection as unhealthy after final failure
                    self._connection_healthy = False
                    break
        
        # All retries exhausted
        self.logger.error(f"Request failed after {self.max_retries + 1} attempts")
        raise last_exception
    
    def make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make an HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: Full URL for the request
            **kwargs: Additional arguments for requests
            
        Returns:
            requests.Response object
        """
        # Add headers if not provided
        if 'headers' not in kwargs:
            kwargs['headers'] = self.headers.copy()
        else:
            # Merge with default headers
            merged_headers = self.headers.copy()
            merged_headers.update(kwargs['headers'])
            kwargs['headers'] = merged_headers
        
        # Set up timeout for this request
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        # Define the request function that doesn't take any parameters
        def _make_request():
            self.logger.debug(f"Executing {method} request to {url} with session ID {id(self.session)}")
            
            if method.upper() == 'GET':
                return self.session.get(url, **kwargs)
            elif method.upper() == 'POST':
                self.logger.debug(f"Making POST with data: {kwargs.get('json')}")
                return self.session.post(url, **kwargs)
            elif method.upper() == 'PUT':
                return self.session.put(url, **kwargs)
            elif method.upper() == 'DELETE':
                return self.session.delete(url, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Execute with retry - no parameters needed since _make_request is self-contained
        return self.execute_with_retry(_make_request)


def with_connection_retry(connection_manager: ConnectionManager):
    """
    Decorator to add automatic retry logic to methods
    
    Args:
        connection_manager: ConnectionManager instance to use for retries
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return connection_manager.execute_with_retry(func, *args, **kwargs)
        return wrapper
    return decorator