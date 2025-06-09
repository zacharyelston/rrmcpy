"""
Base tool class for Redmine MCP Server
Provides standardized tool definition and execution patterns
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging


class BaseTool(ABC):
    """Abstract interface for all MCP tools"""
    
    def __init__(self, service: Any, logger: Optional[logging.Logger] = None):
        self.service = service
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def get_name(self) -> str:
        """Get the tool name (without redmine- prefix)"""
        pass
        
    @abstractmethod
    def get_description(self) -> str:
        """Get the tool description"""
        pass
        
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get the tool parameter schema"""
        pass
        
    @abstractmethod
    def _execute_operation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual tool operation"""
        pass
        
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with error handling and safety wrappers"""
        try:
            self.logger.debug(f"Executing tool {self.get_name()} with arguments: {arguments}")
            
            # Validate arguments if needed
            validation_error = self._validate_arguments(arguments)
            if validation_error:
                return validation_error
                
            # Execute the operation
            result = self._execute_operation(arguments)
            
            self.logger.debug(f"Tool {self.get_name()} completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Tool {self.get_name()} failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "TOOL_EXECUTION_ERROR"
            }
            
    def _validate_arguments(self, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate tool arguments - override in subclasses if needed"""
        return None
        
    def _create_error_response(self, error_message: str, error_code: str = "TOOL_ERROR") -> Dict[str, Any]:
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
