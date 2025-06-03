"""
Base service class for Redmine MCP Server
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from ..core.config import RedmineConfig
from ..core.errors import ValidationError, format_error_response


class BaseService(ABC):
    """Abstract base class for all services"""
    
    def __init__(self, config: RedmineConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> None:
        """Validate that required fields are present in data"""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                field=missing_fields[0] if len(missing_fields) == 1 else None
            )
    
    def validate_field_type(self, data: Dict[str, Any], field: str, expected_type: type) -> None:
        """Validate that a field has the expected type"""
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
                raise ValidationError(
                    f"Field '{field}' must be of type {expected_type.__name__}",
                    field=field,
                    value=data[field]
                )
    
    def handle_service_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """Handle and format service errors"""
        self.logger.error(f"Error in {operation}: {error}")
        return format_error_response(error)
    
    def format_success_response(self, data: Any, message: Optional[str] = None) -> Dict[str, Any]:
        """Format successful service response"""
        response = {"success": True, "data": data}
        if message:
            response["message"] = message
        return response