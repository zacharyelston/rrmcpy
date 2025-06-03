"""
Base service class for Redmine MCP Server
Provides common validation and error handling patterns
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging


class BaseService(ABC):
    """Abstract base class with common validation and error handling"""
    
    def __init__(self, config: Any, client: Any, logger: logging.Logger):
        self.config = config
        self.client = client
        self.logger = logger
        
    def _create_error_response(self, error_message: str, error_code: str = "OPERATION_FAILED") -> Dict[str, Any]:
        """Create a standardized error response"""
        return {
            "success": False,
            "error": error_message,
            "error_code": error_code
        }
        
    def _create_success_response(self, data: Any) -> Dict[str, Any]:
        """Create a standardized success response"""
        return {
            "success": True,
            "data": data
        }
        
    def _validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> Optional[Dict[str, Any]]:
        """Validate that required fields are present in data"""
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            return self._create_error_response(
                f"Missing required fields: {', '.join(missing_fields)}",
                "VALIDATION_ERROR"
            )
        return None
        
    def _safe_execute(self, operation_name: str, operation_func, *args, **kwargs) -> Dict[str, Any]:
        """Safely execute an operation with standardized error handling"""
        try:
            self.logger.debug(f"Executing {operation_name}")
            result = operation_func(*args, **kwargs)
            self.logger.debug(f"Successfully completed {operation_name}")
            return self._create_success_response(result)
        except Exception as e:
            self.logger.error(f"Failed to execute {operation_name}: {e}")
            return self._create_error_response(str(e))
            
    @abstractmethod
    def health_check(self) -> bool:
        """Check health of the service"""
        pass