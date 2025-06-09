"""
Tool registry for managing MCP tools
"""
from typing import Dict, Any, Type
import logging


class ToolRegistry:
    """Registry for managing MCP tools"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.tools: Dict[str, Any] = {}
        
    def register(self, tool_class: Type, service: Any) -> None:
        """Register a tool with its service"""
        tool_name = tool_class.__name__
        try:
            tool_instance = tool_class(service)
            self.tools[tool_name] = tool_instance
            self.logger.debug(f"Registered tool: {tool_name}")
        except Exception as e:
            self.logger.error(f"Failed to register tool {tool_name}: {e}")
            raise
            
    def get_tool(self, tool_name: str) -> Any:
        """Get a registered tool by name"""
        return self.tools.get(tool_name)
        
    def list_tool_names(self) -> list:
        """Get list of registered tool names"""
        return list(self.tools.keys())
