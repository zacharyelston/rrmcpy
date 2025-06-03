"""
Base tool interface for Redmine MCP Server
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from src.core.errors import ToolExecutionError, format_error_response


class BaseTool(ABC):
    """Abstract base class for all MCP tools"""
    
    def __init__(self, service, logger: Optional[logging.Logger] = None):
        self.service = service
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def name(self) -> str:
        """Return the tool name for MCP registration"""
        pass
    
    @abstractmethod
    def description(self) -> str:
        """Return the tool description for MCP"""
        pass
    
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """Return the input schema for MCP tool registration"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get complete tool definition for MCP registration"""
        return {
            "name": self.name(),
            "description": self.description(),
            "inputSchema": self.input_schema()
        }
    
    def safe_execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool with error handling"""
        try:
            self.logger.debug(f"Executing tool {self.name()} with params: {kwargs}")
            result = self.execute(**kwargs)
            self.logger.debug(f"Tool {self.name()} completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Tool {self.name()} execution failed: {e}")
            error = ToolExecutionError(self.name(), str(e), e)
            return format_error_response(error)