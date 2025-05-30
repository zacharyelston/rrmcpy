"""
Proper FastMCP server implementation for Redmine integration
Follows FastMCP best practices and MCP protocol specification
"""
import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp.server import FastMCP
from mcp.server.models import InitializationOptions
from mcp import Tool
from pydantic import BaseModel, Field

from src.redmine_client import RedmineClient


# Pydantic models for proper type handling
class IssueCreateRequest(BaseModel):
    project_id: str = Field(description="Project identifier")
    subject: str = Field(description="Issue subject")
    description: Optional[str] = Field(default=None, description="Issue description")
    tracker_id: Optional[int] = Field(default=None, description="Tracker ID")
    status_id: Optional[int] = Field(default=None, description="Status ID")
    priority_id: Optional[int] = Field(default=None, description="Priority ID")
    assigned_to_id: Optional[int] = Field(default=None, description="Assigned user ID")


class IssueUpdateRequest(BaseModel):
    issue_id: int = Field(description="Issue ID to update")
    subject: Optional[str] = Field(default=None, description="Issue subject")
    description: Optional[str] = Field(default=None, description="Issue description")
    status_id: Optional[int] = Field(default=None, description="Status ID")
    notes: Optional[str] = Field(default=None, description="Update notes/comments")


class ProjectCreateRequest(BaseModel):
    name: str = Field(description="Project name")
    identifier: str = Field(description="Project identifier")
    description: Optional[str] = Field(default=None, description="Project description")
    homepage: Optional[str] = Field(default=None, description="Project homepage")
    is_public: Optional[bool] = Field(default=False, description="Is project public")


class RedmineMCPServer:
    """
    Proper FastMCP server implementation for Redmine
    """
    
    def __init__(self, redmine_url: str, api_key: str):
        """
        Initialize the Redmine MCP Server
        
        Args:
            redmine_url: URL of the Redmine instance
            api_key: API key for Redmine authentication
        """
        self.redmine_url = redmine_url
        self.api_key = api_key
        
        # Configure logging to stderr only (not stdout to avoid MCP interference)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stderr
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redmine client
        self.redmine_client = RedmineClient(redmine_url, api_key, self.logger)
        
        # Initialize FastMCP
        self.app = FastMCP("Redmine MCP Server")
        
        # Register tools after MCP initialization
        self._register_tools()
    
    def _register_tools(self):
        """Register all MCP tools following proper FastMCP pattern"""
        
        # Issue management tools
        @self.app.tool(name="redmine-list-issues")
        def list_issues(
            project_id: Optional[str] = None,
            status_id: Optional[int] = None,
            assigned_to_id: Optional[int] = None,
            limit: Optional[int] = 25
        ) -> List[Dict[str, Any]]:
            """
            List issues with optional filtering
            
            Args:
                project_id: Filter by project identifier
                status_id: Filter by status ID
                assigned_to_id: Filter by assigned user ID
                limit: Maximum number of issues to return
                
            Returns:
                List of issues
            """
            params = {"limit": limit}
            if project_id:
                params["project_id"] = project_id
            if status_id:
                params["status_id"] = status_id
            if assigned_to_id:
                params["assigned_to_id"] = assigned_to_id
            
            try:
                result = self.redmine_client.get_issues(params)
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                return result.get('issues', [])
            except Exception as e:
                self.logger.error(f"Error listing issues: {e}")
                raise
        
        @self.app.tool(name="redmine-get-issue")
        def get_issue(issue_id: int) -> Dict[str, Any]:
            """
            Get detailed information about a specific issue
            
            Args:
                issue_id: ID of the issue to retrieve
                
            Returns:
                Issue details
            """
            try:
                result = self.redmine_client.get_issue(issue_id, include=['journals', 'attachments'])
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                return result.get('issue', {})
            except Exception as e:
                self.logger.error(f"Error getting issue {issue_id}: {e}")
                raise
        
        @self.app.tool(name="redmine-create-issue")
        def create_issue(request: IssueCreateRequest) -> Dict[str, Any]:
            """
            Create a new issue
            
            Args:
                request: Issue creation parameters
                
            Returns:
                Created issue details
            """
            try:
                issue_data = request.model_dump(exclude_none=True)
                result = self.redmine_client.create_issue(issue_data)
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                return result.get('issue', {})
            except Exception as e:
                self.logger.error(f"Error creating issue: {e}")
                raise
        
        @self.app.tool(name="redmine-update-issue")
        def update_issue(request: IssueUpdateRequest) -> bool:
            """
            Update an existing issue
            
            Args:
                request: Issue update parameters
                
            Returns:
                True if successful
            """
            try:
                issue_id = request.issue_id
                update_data = request.model_dump(exclude={'issue_id'}, exclude_none=True)
                result = self.redmine_client.update_issue(issue_id, update_data)
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                return True
            except Exception as e:
                self.logger.error(f"Error updating issue: {e}")
                raise
        
        # Project management tools
        @self.app.tool(name="redmine-list-projects")
        def list_projects() -> List[Dict[str, Any]]:
            """
            List all accessible projects
            
            Returns:
                List of projects
            """
            try:
                result = self.redmine_client.get_projects()
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                return result.get('projects', [])
            except Exception as e:
                self.logger.error(f"Error listing projects: {e}")
                raise
        
        @self.app.tool(name="redmine-get-project")
        def get_project(project_id: str) -> Dict[str, Any]:
            """
            Get detailed information about a specific project
            
            Args:
                project_id: ID or identifier of the project
                
            Returns:
                Project details
            """
            try:
                result = self.redmine_client.get_project(project_id, include=['trackers', 'issue_categories'])
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                return result.get('project', {})
            except Exception as e:
                self.logger.error(f"Error getting project {project_id}: {e}")
                raise
        
        @self.app.tool(name="redmine-create-project")
        def create_project(request: ProjectCreateRequest) -> Dict[str, Any]:
            """
            Create a new project
            
            Args:
                request: Project creation parameters
                
            Returns:
                Created project details
            """
            try:
                project_data = request.model_dump(exclude_none=True)
                result = self.redmine_client.create_project(project_data)
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                return result.get('project', {})
            except Exception as e:
                self.logger.error(f"Error creating project: {e}")
                raise
        
        # User management tools
        @self.app.tool(name="redmine-get-current-user")
        def get_current_user() -> Dict[str, Any]:
            """
            Get information about the current authenticated user
            
            Returns:
                Current user details
            """
            try:
                result = self.redmine_client.get_current_user()
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                return result.get('user', {})
            except Exception as e:
                self.logger.error(f"Error getting current user: {e}")
                raise
        
        @self.app.tool(name="redmine-list-users")
        def list_users() -> List[Dict[str, Any]]:
            """
            List all users (requires admin privileges)
            
            Returns:
                List of users
            """
            try:
                result = self.redmine_client.get_users()
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                return result.get('users', [])
            except Exception as e:
                self.logger.error(f"Error listing users: {e}")
                raise
        
        # Version management tools
        @self.app.tool(name="redmine-list-versions")
        def list_versions(project_id: str) -> List[Dict[str, Any]]:
            """
            List versions for a project
            
            Args:
                project_id: ID or identifier of the project
                
            Returns:
                List of versions
            """
            try:
                result = self.redmine_client.get_versions(project_id)
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                return result.get('versions', [])
            except Exception as e:
                self.logger.error(f"Error listing versions for project {project_id}: {e}")
                raise
        
        # Health check tool
        @self.app.tool(name="redmine-health-check")
        def health_check() -> Dict[str, Any]:
            """
            Check the health of the Redmine connection
            
            Returns:
                Health status information
            """
            try:
                healthy = self.redmine_client.health_check()
                return {
                    "healthy": healthy,
                    "redmine_url": self.redmine_url,
                    "timestamp": self.redmine_client.issues._get_timestamp()
                }
            except Exception as e:
                self.logger.error(f"Error in health check: {e}")
                return {
                    "healthy": False,
                    "error": str(e),
                    "redmine_url": self.redmine_url
                }
    
    async def run(self):
        """Run the MCP server"""
        self.logger.info(f"Starting Redmine MCP Server for {self.redmine_url}")
        await self.app.run()


async def main():
    """Main entry point"""
    import os
    
    # Get configuration from environment
    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    redmine_api_key = os.environ.get('REDMINE_API_KEY')
    
    if not redmine_api_key:
        logging.error("REDMINE_API_KEY environment variable is required")
        sys.exit(1)
    
    # Create and run server
    server = RedmineMCPServer(redmine_url, redmine_api_key)
    await server.run()


if __name__ == '__main__':
    asyncio.run(main())