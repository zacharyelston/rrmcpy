"""
Standardized error handling for Redmine MCP Server
"""
from typing import Optional, Dict, Any


class RedmineAPIError(Exception):
    """Base exception for Redmine API related errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details
        }


class ToolExecutionError(Exception):
    """Exception for tool execution failures"""
    
    def __init__(self, tool_name: str, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.tool_name = tool_name
        self.message = message
        self.cause = cause
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization"""
        return {
            "error": self.__class__.__name__,
            "tool_name": self.tool_name,
            "message": self.message,
            "cause": str(self.cause) if self.cause else None
        }


class ConfigurationError(Exception):
    """Exception for configuration related errors"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.field = field
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "field": self.field
        }


class ValidationError(Exception):
    """Exception for data validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.field = field
        self.value = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "field": self.field,
            "value": str(self.value) if self.value is not None else None
        }


class ConnectionError(RedmineAPIError):
    """Exception for connection related errors"""
    pass


class AuthenticationError(RedmineAPIError):
    """Exception for authentication related errors"""
    pass


class NotFoundError(RedmineAPIError):
    """Exception for resource not found errors"""
    pass


class RateLimitError(RedmineAPIError):
    """Exception for rate limit exceeded errors"""
    pass


def format_error_response(error: Exception) -> Dict[str, Any]:
    """Format any exception as a standardized error response"""
    if hasattr(error, 'to_dict'):
        return error.to_dict()
    
    return {
        "error": error.__class__.__name__,
        "message": str(error)
    }