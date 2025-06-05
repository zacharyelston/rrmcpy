"""
Standardized error handling for Redmine MCP Server

This module provides:
- Consistent error response format
- Error code definitions and mapping
- Error context enrichment
- Integration with logging system
"""
from typing import Dict, Optional, Any, Union
from datetime import datetime, timezone
from enum import Enum
import logging
import traceback
import json


class ErrorCode(Enum):
    """Standard error codes for the system"""
    # Client errors (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMIT = "RATE_LIMIT"
    
    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    SERVER_ERROR = "SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # Request errors
    INVALID_JSON = "INVALID_JSON"
    REQUEST_ERROR = "REQUEST_ERROR"
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"
    
    # Configuration errors
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    MISSING_DEPENDENCY = "MISSING_DEPENDENCY"


class ErrorResponse:
    """Standardized error response builder"""
    
    @staticmethod
    def create(
        error_code: Union[ErrorCode, str],
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        include_trace: bool = False
    ) -> Dict[str, Any]:
        """
        Create a standardized error response
        
        Args:
            error_code: ErrorCode enum or string
            message: Human-readable error message
            status_code: HTTP status code
            details: Additional error details
            context: Context information (request data, etc.)
            include_trace: Whether to include stack trace (only in debug mode)
            
        Returns:
            Standardized error response dictionary
        """
        if isinstance(error_code, ErrorCode):
            error_code = error_code.value
            
        response = {
            "error": True,
            "error_code": error_code,
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        if details:
            response["details"] = details
            
        if context:
            response["context"] = context
            
        if include_trace:
            response["trace"] = traceback.format_exc()
            
        return response


class ErrorHandler:
    """Centralized error handling with logging integration"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        
    def handle_validation_error(
        self,
        message: str,
        field_errors: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle validation errors"""
        details = {"field_errors": field_errors} if field_errors else None
        
        self.logger.error(f"Validation error: {message}", extra={
            "error_code": ErrorCode.VALIDATION_ERROR.value,
            "field_errors": field_errors,
            "context": context
        })
        
        return ErrorResponse.create(
            ErrorCode.VALIDATION_ERROR,
            message,
            400,
            details=details,
            context=context
        )
    
    def handle_http_error(
        self,
        status_code: int,
        message: str,
        response_body: Optional[str] = None,
        url: Optional[str] = None,
        method: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle HTTP errors from external APIs"""
        # Map HTTP status to error code
        error_code_map = {
            401: ErrorCode.AUTHENTICATION_ERROR,
            403: ErrorCode.AUTHORIZATION_ERROR,
            404: ErrorCode.NOT_FOUND,
            409: ErrorCode.CONFLICT,
            429: ErrorCode.RATE_LIMIT,
            500: ErrorCode.SERVER_ERROR,
            502: ErrorCode.SERVER_ERROR,
            503: ErrorCode.SERVICE_UNAVAILABLE,
            504: ErrorCode.TIMEOUT_ERROR
        }
        
        error_code = error_code_map.get(status_code, ErrorCode.SERVER_ERROR)
        
        # Try to extract error details from response
        details = {}
        if response_body:
            try:
                response_data = json.loads(response_body)
                if 'errors' in response_data:
                    details['api_errors'] = response_data['errors']
                elif 'error' in response_data:
                    details['api_error'] = response_data['error']
            except json.JSONDecodeError:
                details['raw_response'] = response_body[:500]  # First 500 chars
        
        context = {}
        if url:
            context['url'] = url
        if method:
            context['method'] = method
            
        self.logger.error(
            f"HTTP {status_code} error: {message}",
            extra={
                "error_code": error_code.value,
                "status_code": status_code,
                "url": url,
                "method": method,
                "response_body": response_body
            }
        )
        
        return ErrorResponse.create(
            error_code,
            message,
            status_code,
            details=details,
            context=context
        )
    
    def handle_connection_error(
        self,
        error: Exception,
        url: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle connection errors"""
        message = f"Failed to connect to server"
        if url:
            message += f" at {url}"
            
        self.logger.error(
            f"Connection error: {str(error)}",
            extra={
                "error_code": ErrorCode.CONNECTION_ERROR.value,
                "url": url,
                "context": context
            },
            exc_info=True
        )
        
        return ErrorResponse.create(
            ErrorCode.CONNECTION_ERROR,
            message,
            503,
            details={"original_error": str(error)},
            context=context
        )
    
    def handle_timeout_error(
        self,
        error: Exception,
        url: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Handle timeout errors"""
        message = "Request timed out"
        if url:
            message += f" for {url}"
            
        details = {"original_error": str(error)}
        if timeout:
            details["timeout_seconds"] = timeout
            
        self.logger.error(
            f"Timeout error: {str(error)}",
            extra={
                "error_code": ErrorCode.TIMEOUT_ERROR.value,
                "url": url,
                "timeout": timeout
            }
        )
        
        return ErrorResponse.create(
            ErrorCode.TIMEOUT_ERROR,
            message,
            504,
            details=details
        )
    
    def handle_unexpected_error(
        self,
        error: Exception,
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        include_trace: bool = None
    ) -> Dict[str, Any]:
        """Handle unexpected errors"""
        message = f"An unexpected error occurred"
        if operation:
            message += f" during {operation}"
            
        # Include trace in debug mode unless explicitly disabled
        if include_trace is None:
            include_trace = self.logger.isEnabledFor(logging.DEBUG)
            
        self.logger.error(
            f"Unexpected error: {str(error)}",
            extra={
                "error_code": ErrorCode.UNEXPECTED_ERROR.value,
                "operation": operation,
                "context": context
            },
            exc_info=True
        )
        
        return ErrorResponse.create(
            ErrorCode.UNEXPECTED_ERROR,
            message,
            500,
            details={"error_type": type(error).__name__, "error_message": str(error)},
            context=context,
            include_trace=include_trace
        )


# Global error handler instance
_error_handler = None


def get_error_handler(logger: Optional[logging.Logger] = None) -> ErrorHandler:
    """Get or create global error handler instance"""
    global _error_handler
    if _error_handler is None or logger is not None:
        _error_handler = ErrorHandler(logger)
    return _error_handler


# Convenience functions
def validation_error(message: str, **kwargs) -> Dict[str, Any]:
    """Create a validation error response"""
    return get_error_handler().handle_validation_error(message, **kwargs)


def http_error(status_code: int, message: str, **kwargs) -> Dict[str, Any]:
    """Create an HTTP error response"""
    return get_error_handler().handle_http_error(status_code, message, **kwargs)


def connection_error(error: Exception, **kwargs) -> Dict[str, Any]:
    """Create a connection error response"""
    return get_error_handler().handle_connection_error(error, **kwargs)


def timeout_error(error: Exception, **kwargs) -> Dict[str, Any]:
    """Create a timeout error response"""
    return get_error_handler().handle_timeout_error(error, **kwargs)


def unexpected_error(error: Exception, **kwargs) -> Dict[str, Any]:
    """Create an unexpected error response"""
    return get_error_handler().handle_unexpected_error(error, **kwargs)
