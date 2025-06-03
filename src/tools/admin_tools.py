"""
Administrative tools for Redmine MCP Server
"""
from typing import Dict, Any


class HealthCheckTool:
    """Tool for checking Redmine server health"""
    
    def __init__(self, service):
        self.service = service
        
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute health check"""
        try:
            health = self.service.health_check()
            return {
                "status": "healthy" if health else "unhealthy",
                "healthy": health
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "healthy": False,
                "error": str(e)
            }


class GetCurrentUserTool:
    """Tool for getting current user information"""
    
    def __init__(self, service):
        self.service = service
        
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get current user"""
        return self.service.get_current_user()