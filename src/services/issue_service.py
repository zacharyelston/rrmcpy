"""
Issue service layer for Redmine MCP Server
Provides business logic for issue operations
"""
from typing import Dict, Any, Optional, List
import logging
from .base_service import BaseService


class IssueService(BaseService):
    """Service layer for issue operations"""
    
    def __init__(self, config: Any, issue_client: Any, logger: logging.Logger):
        super().__init__(config, issue_client, logger)
        self.issue_client = issue_client  # Keep for backward compatibility
        
    def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new issue"""
        try:
            return self.issue_client.create_issue(issue_data)
        except Exception as e:
            self.logger.error(f"Failed to create issue: {e}")
            return {"error": str(e), "success": False}
            
    def get_issue(self, issue_id: int, include: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get an issue by ID"""
        try:
            return self.issue_client.get_issue(issue_id, include)
        except Exception as e:
            self.logger.error(f"Failed to get issue {issue_id}: {e}")
            return {"error": str(e), "success": False}
            
    def get_issues(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Get list of issues with optional parameters"""
        try:
            return self.issue_client.get_issues(params)
        except Exception as e:
            self.logger.error(f"Failed to get issues: {e}")
            return {"error": str(e), "success": False}
            
    def update_issue(self, issue_id: int, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing issue"""
        try:
            return self.issue_client.update_issue(issue_id, issue_data)
        except Exception as e:
            self.logger.error(f"Failed to update issue {issue_id}: {e}")
            return {"error": str(e), "success": False}
            
    def delete_issue(self, issue_id: int) -> Dict[str, Any]:
        """Delete an issue"""
        try:
            return self.issue_client.delete_issue(issue_id)
        except Exception as e:
            self.logger.error(f"Failed to delete issue {issue_id}: {e}")
            return {"error": str(e), "success": False}
            
    def health_check(self) -> bool:
        """Check health of issue service"""
        try:
            return self.issue_client.health_check()
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
            
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user information"""
        try:
            return self.issue_client.get_current_user()
        except Exception as e:
            self.logger.error(f"Failed to get current user: {e}")
            return {"error": str(e), "success": False}
