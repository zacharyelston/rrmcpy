"""
Administrative tools for Redmine MCP Server
"""
from typing import Dict, Any
from .base_tool import BaseTool


class HealthCheckTool(BaseTool):
    """Tool for checking Redmine connection health"""
    
    def name(self) -> str:
        return "redmine-health-check"
    
    def description(self) -> str:
        return "Check the health and connectivity of the Redmine instance"
    
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            # Use the service's base client for health check
            if hasattr(self.service, 'config') and hasattr(self.service, 'issue_client'):
                health = self.service.issue_client.health_check()
                return {
                    "success": True,
                    "data": {
                        "status": "healthy" if health else "unhealthy",
                        "redmine_url": self.service.config.url,
                        "connection": "ok" if health else "failed"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Service not properly configured"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class GetCurrentUserTool(BaseTool):
    """Tool for getting current user information"""
    
    def name(self) -> str:
        return "redmine-get-current-user"
    
    def description(self) -> str:
        return "Get information about the current authenticated user"
    
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            # Make a request to get current user
            if hasattr(self.service, 'issue_client'):
                result = self.service.issue_client.make_request("GET", "/users/current.json")
                if result.get('error'):
                    return result
                return {
                    "success": True,
                    "data": result.get('user', {})
                }
            else:
                return {
                    "success": False,
                    "error": "Service not properly configured"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }