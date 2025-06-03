"""
Tool registry module for managing MCP tools registration
"""
import logging
from typing import Dict, List, Any, Callable, Type

from ..core.errors import ToolExecutionError
from ..tools import BaseTool

class ToolRegistry:
    """Registry for MCP tools with service dependencies"""
    
    def __init__(self, logger=None):
        self.tools = {}
        self.logger = logger or logging.getLogger("redmine_mcp_server.tool_registry")
        self.logger.debug("Tool registry initialized")
    
    def register(self, tool_class: Type[BaseTool], service=None):
        """Register a tool with the registry"""
        try:
            tool_instance = tool_class(service)
            tool_name = tool_instance.get_name()
            self.tools[tool_name] = tool_instance
            self.logger.debug(f"Registered tool: {tool_name}")
            return tool_name
        except Exception as e:
            self.logger.error(f"Failed to register tool {tool_class.__name__}: {e}")
            raise ToolExecutionError(f"Tool registration failed for {tool_class.__name__}: {e}")
    
    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with arguments"""
        if tool_name not in self.tools:
            error = f"Tool '{tool_name}' not found"
            self.logger.error(error)
            raise ToolExecutionError(error)
            
        try:
            self.logger.debug(f"Executing tool: {tool_name} with arguments: {arguments}")
            result = self.tools[tool_name].execute(arguments)
            return result
        except Exception as e:
            self.logger.error(f"Tool execution failed for {tool_name}: {e}")
            raise ToolExecutionError(f"Tool execution failed for {tool_name}: {e}")
    
    def list_tool_names(self) -> List[str]:
        """Get a list of all registered tool names"""
        return list(self.tools.keys())
