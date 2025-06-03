"""
Tool registry for managing MCP tools
"""
from typing import Dict, List, Type, Any, Optional
import logging
from .base_tool import BaseTool


class ToolRegistry:
    """Registry for managing and organizing MCP tools"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._tools: Dict[str, BaseTool] = {}
        self._tool_classes: Dict[str, Type[BaseTool]] = {}
    
    def register(self, tool_class: Type[BaseTool], service, **kwargs) -> None:
        """
        Register a tool class with its service dependency
        
        Args:
            tool_class: The tool class to register
            service: Service instance required by the tool
            **kwargs: Additional initialization parameters
        """
        try:
            # Instantiate the tool
            tool_instance = tool_class(service, self.logger, **kwargs)
            tool_name = tool_instance.name()
            
            # Store both class and instance
            self._tool_classes[tool_name] = tool_class
            self._tools[tool_name] = tool_instance
            
            self.logger.debug(f"Registered tool: {tool_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to register tool {tool_class.__name__}: {e}")
            raise
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool instance by name"""
        return self._tools.get(name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tools"""
        return self._tools.copy()
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for MCP registration"""
        return [tool.get_tool_definition() for tool in self._tools.values()]
    
    def list_tool_names(self) -> List[str]:
        """Get list of all registered tool names"""
        return list(self._tools.keys())
    
    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name with parameters
        
        Args:
            name: Tool name
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        tool = self.get_tool(name)
        if not tool:
            return {
                "error": "ToolNotFound",
                "message": f"Tool '{name}' is not registered"
            }
        
        return tool.safe_execute(**kwargs)
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all registered tools"""
        results = {}
        for name, tool in self._tools.items():
            try:
                # Simple health check - just verify tool can be accessed
                tool.name()
                results[name] = {"status": "healthy"}
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
        
        return {
            "total_tools": len(self._tools),
            "healthy_tools": len([r for r in results.values() if r["status"] == "healthy"]),
            "tools": results
        }