"""
Fixed version of the MCP server that properly handles responses
Based on understanding of FastMCP's _convert_to_content behavior
"""
import asyncio
import logging
import sys
import json
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


class RedmineFixedMCPServer:
    """
    Fixed FastMCP server implementation for Redmine
    This version ensures responses are properly formatted
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
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stderr
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redmine client
        self.redmine_client = RedmineClient(redmine_url, api_key, self.logger)
        
        # Initialize FastMCP
        self.app = FastMCP("Redmine Fixed MCP Server")
        
        # Register tools after MCP initialization
        self._register_tools()
    
    def _register_tools(self):
        """Register all MCP tools with proper response handling"""
        
        # Issue management tools
        @self.app.tool()
        def redmine_list_issues(
            project_id: Optional[str] = None,
            status_id: Optional[int] = None,
            assigned_to_id: Optional[int] = None,
            limit: Optional[int] = 25
        ) -> str:
            """
            List issues with optional filtering
            
            Args:
                project_id: Filter by project identifier
                status_id: Filter by status ID
                assigned_to_id: Filter by assigned user ID
                limit: Maximum number of issues to return
                
            Returns:
                JSON string of issues array
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
                
                issues = result.get('issues', [])
                
                # Return as JSON string to avoid FastMCP's conversion issues
                return json.dumps(issues, indent=2)
                
            except Exception as e:
                self.logger.error(f"Error listing issues: {e}")
                raise
        
        @self.app.tool()
        def redmine_get_issue(issue_id: int) -> str:
            """
            Get detailed information about a specific issue
            
            Args:
                issue_id: ID of the issue to retrieve
                
            Returns:
                JSON string of issue details
            """
            try:
                result = self.redmine_client.get_issue(issue_id, include=['journals', 'attachments'])
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                
                issue = result.get('issue', {})
                
                # Return as JSON string
                return json.dumps(issue, indent=2)
                
            except Exception as e:
                self.logger.error(f"Error getting issue {issue_id}: {e}")
                raise
        
        @self.app.tool()
        def redmine_create_issue(request: IssueCreateRequest) -> str:
            """
            Create a new issue
            
            Args:
                request: Issue creation parameters
                
            Returns:
                JSON string of created issue details
            """
            self.logger.debug(f"=== CREATE ISSUE START ===")
            self.logger.debug(f"Request: {request}")
            
            try:
                issue_data = request.model_dump(exclude_none=True)
                self.logger.debug(f"Issue data: {issue_data}")
                
                result = self.redmine_client.create_issue(issue_data)
                self.logger.debug(f"API result: {result}")
                
                if result.get('error'):
                    error_msg = f"Error: {result.get('message', 'Unknown error')}"
                    self.logger.error(error_msg)
                    raise Exception(error_msg)
                
                issue = result.get('issue', {})
                self.logger.debug(f"Extracted issue: {issue}")
                
                # Return as JSON string
                response = json.dumps(issue, indent=2)
                self.logger.debug(f"JSON response: {response}")
                
                return response
                
            except Exception as e:
                self.logger.error(f"Error creating issue: {e}", exc_info=True)
                raise
            finally:
                self.logger.debug(f"=== CREATE ISSUE END ===")
        
        @self.app.tool()
        def redmine_update_issue(request: IssueUpdateRequest) -> str:
            """
            Update an existing issue
            
            Args:
                request: Issue update parameters
                
            Returns:
                JSON string with success status
            """
            try:
                issue_id = request.issue_id
                update_data = request.model_dump(exclude={'issue_id'}, exclude_none=True)
                result = self.redmine_client.update_issue(issue_id, update_data)
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                
                # Return success as JSON
                return json.dumps({"success": True, "issue_id": issue_id})
                
            except Exception as e:
                self.logger.error(f"Error updating issue: {e}")
                raise
        
        # Project management tools
        @self.app.tool()
        def redmine_list_projects() -> str:
            """
            List all accessible projects
            
            Returns:
                JSON string of projects array
            """
            try:
                result = self.redmine_client.get_projects()
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                
                projects = result.get('projects', [])
                return json.dumps(projects, indent=2)
                
            except Exception as e:
                self.logger.error(f"Error listing projects: {e}")
                raise
        
        @self.app.tool()
        def redmine_get_project(project_id: str) -> str:
            """
            Get detailed information about a specific project
            
            Args:
                project_id: ID or identifier of the project
                
            Returns:
                JSON string of project details
            """
            try:
                result = self.redmine_client.get_project(project_id, include=['trackers', 'issue_categories'])
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                
                project = result.get('project', {})
                return json.dumps(project, indent=2)
                
            except Exception as e:
                self.logger.error(f"Error getting project {project_id}: {e}")
                raise
        
        @self.app.tool()
        def redmine_create_project(request: ProjectCreateRequest) -> str:
            """
            Create a new project
            
            Args:
                request: Project creation parameters
                
            Returns:
                JSON string of created project details
            """
            try:
                project_data = request.model_dump(exclude_none=True)
                result = self.redmine_client.create_project(project_data)
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                
                project = result.get('project', {})
                return json.dumps(project, indent=2)
                
            except Exception as e:
                self.logger.error(f"Error creating project: {e}")
                raise
        
        # User management tools
        @self.app.tool()
        def redmine_get_current_user() -> str:
            """
            Get information about the current authenticated user
            
            Returns:
                JSON string of current user details
            """
            try:
                result = self.redmine_client.get_current_user()
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                
                user = result.get('user', {})
                return json.dumps(user, indent=2)
                
            except Exception as e:
                self.logger.error(f"Error getting current user: {e}")
                raise
        
        @self.app.tool()
        def redmine_list_users() -> str:
            """
            List all users (requires admin privileges)
            
            Returns:
                JSON string of users array
            """
            try:
                result = self.redmine_client.get_users()
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                
                users = result.get('users', [])
                return json.dumps(users, indent=2)
                
            except Exception as e:
                self.logger.error(f"Error listing users: {e}")
                raise
        
        # Version management tools
        @self.app.tool()
        def redmine_list_versions(project_id: str) -> str:
            """
            List versions for a project
            
            Args:
                project_id: ID or identifier of the project
                
            Returns:
                JSON string of versions array
            """
            try:
                result = self.redmine_client.get_versions(project_id)
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                
                versions = result.get('versions', [])
                return json.dumps(versions, indent=2)
                
            except Exception as e:
                self.logger.error(f"Error listing versions for project {project_id}: {e}")
                raise
        
        # Health check tool
        @self.app.tool()
        def redmine_health_check() -> str:
            """
            Check the health of the Redmine connection
            
            Returns:
                JSON string of health status
            """
            try:
                healthy = self.redmine_client.health_check()
                result = {
                    "healthy": healthy,
                    "redmine_url": self.redmine_url,
                    "timestamp": self.redmine_client.issues._get_timestamp()
                }
                return json.dumps(result, indent=2)
                
            except Exception as e:
                self.logger.error(f"Error in health check: {e}")
                result = {
                    "healthy": False,
                    "error": str(e),
                    "redmine_url": self.redmine_url
                }
                return json.dumps(result, indent=2)
    
    def run_stdio(self):
        """Run the MCP server with STDIO transport for MCP clients"""
        self.logger.info(f"Starting Redmine Fixed MCP Server for {self.redmine_url}")
        # Use FastMCP's built-in run method - it handles STDIO by default
        self.app.run(transport="stdio")


def main():
    """Main entry point"""
    import os
    
    # Get configuration from environment
    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    redmine_api_key = os.environ.get('REDMINE_API_KEY')
    
    if not redmine_api_key:
        logging.error("REDMINE_API_KEY environment variable is required")
        sys.exit(1)
    
    # Create and run server
    server = RedmineFixedMCPServer(redmine_url, redmine_api_key)
    server.run_stdio()


if __name__ == '__main__':
    main()
