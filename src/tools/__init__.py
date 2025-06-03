"""
Tool registry system for Redmine MCP Server
Decoupled tool definitions with plugin-like architecture
"""
from .registry import ToolRegistry
from .base_tool import BaseTool
from .issue_tools import CreateIssueTool, GetIssueTool, ListIssuesTool, UpdateIssueTool, DeleteIssueTool
from .admin_tools import HealthCheckTool, GetCurrentUserTool

__all__ = [
    'ToolRegistry',
    'BaseTool',
    'CreateIssueTool',
    'GetIssueTool', 
    'ListIssuesTool',
    'UpdateIssueTool',
    'DeleteIssueTool',
    'HealthCheckTool',
    'GetCurrentUserTool'
]