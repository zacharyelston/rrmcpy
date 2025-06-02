"""
Proper FastMCP server implementation for Redmine integration
Using the instance method approach (define methods first, then register them)
"""
import datetime
import json
import logging
import sys
from typing import Dict, List, Optional

from mcp.server import FastMCP
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
    Proper FastMCP server implementation for Redmine using instance methods
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
    
    def redmine_list_issues(self,
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
            self.logger.debug(f"List issues params: {params}")
            result = self.redmine_client.get_issues(params)
            self.logger.debug(f"API result: {result}")
            
            if result.get("error"):
                raise Exception(f"Error: {result.get('message', 'Unknown error')}")
            
            issues = result.get("issues", [])
            self.logger.debug(f"Extracted issues: {len(issues)} found")
            
            # Return as JSON string
            return json.dumps(issues, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to list issues: {e}")
            return json.dumps({"error": str(e)}, indent=2)
    
    def redmine_get_issue(self, issue_id: int) -> str:
        """
        Get detailed information about a specific issue
        
        Args:
            issue_id: ID of the issue to retrieve
            
        Returns:
            JSON string of issue details
        """
        try:
            self.logger.debug(f"Getting issue ID: {issue_id}")
            result = self.redmine_client.get_issue(issue_id)
            self.logger.debug(f"API result: {result}")
            
            if result.get("error"):
                raise Exception(f"Error: {result.get('message', 'Unknown error')}")
            
            issue = result.get("issue", {})
            
            # Return as JSON string
            return json.dumps(issue, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to get issue: {e}")
            return json.dumps({"error": str(e)}, indent=2)
    
    def redmine_create_issue(self, issue_data: IssueCreateRequest) -> str:
        """
        Create a new issue
        
        Args:
            issue_data: Issue creation parameters
            
        Returns:
            JSON string of created issue details
        """
        try:
            self.logger.debug(f"Creating issue with params: {issue_data}")
            
            # Convert Pydantic model to dict
            params = issue_data.model_dump(exclude_none=True)
            
            result = self.redmine_client.create_issue(params)
            self.logger.debug(f"API result: {result}")
            
            if result.get("error"):
                raise Exception(f"Error: {result.get('message', 'Unknown error')}")
            
            created_issue = result.get("issue", {})
            
            # Return as JSON string
            return json.dumps(created_issue, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to create issue: {e}")
            return json.dumps({"error": str(e)}, indent=2)
    
    def redmine_update_issue(self, request: IssueUpdateRequest) -> str:
        """
        Update an existing issue
        
        Args:
            request: Issue update parameters
            
        Returns:
            JSON string with success status
        """
        try:
            issue_id = request.issue_id
            self.logger.debug(f"Updating issue ID: {issue_id}")
            
            # Convert Pydantic model to dict and remove issue_id
            params = request.dict(exclude_none=True)
            params.pop("issue_id", None)
            
            result = self.redmine_client.update_issue(issue_id, params)
            self.logger.debug(f"API result: {result}")
            
            if result.get("error"):
                raise Exception(f"Error: {result.get('message', 'Unknown error')}")
            
            return json.dumps({"success": True}, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to update issue: {e}")
            return json.dumps({"error": str(e)}, indent=2)
    
    def redmine_list_projects(self) -> str:
        """
        List all accessible projects
        
        Returns:
            JSON string of projects array
        """
        try:
            self.logger.debug("Listing projects")
            result = self.redmine_client.get_projects()
            self.logger.debug(f"API result: {result}")
            
            if result.get("error"):
                raise Exception(f"Error: {result.get('message', 'Unknown error')}")
            
            projects = result.get("projects", [])
            
            # Return as JSON string
            return json.dumps(projects, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to list projects: {e}")
            return json.dumps({"error": str(e)}, indent=2)
    
    def redmine_get_project(self, project_id: str) -> str:
        """
        Get detailed information about a specific project
        
        Args:
            project_id: ID or identifier of the project
            
        Returns:
            JSON string of project details
        """
        try:
            self.logger.debug(f"Getting project: {project_id}")
            result = self.redmine_client.get_project(project_id)
            self.logger.debug(f"API result: {result}")
            
            if result.get("error"):
                raise Exception(f"Error: {result.get('message', 'Unknown error')}")
            
            project = result.get("project", {})
            
            # Return as JSON string
            return json.dumps(project, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to get project: {e}")
            return json.dumps({"error": str(e)}, indent=2)
    
    def redmine_create_project(self, request: ProjectCreateRequest) -> str:
        """
        Create a new project
        
        Args:
            request: Project creation parameters
            
        Returns:
            JSON string of created project details
        """
        try:
            self.logger.debug(f"Creating project with params: {request}")
            
            # Convert Pydantic model to dict
            params = request.dict(exclude_none=True)
            
            result = self.redmine_client.create_project(params)
            self.logger.debug(f"API result: {result}")
            
            if result.get("error"):
                raise Exception(f"Error: {result.get('message', 'Unknown error')}")
            
            created_project = result.get("project", {})
            
            # Return as JSON string
            return json.dumps(created_project, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to create project: {e}")
            return json.dumps({"error": str(e)}, indent=2)
    
    def redmine_get_current_user(self) -> str:
        """
        Get information about the current authenticated user
        
        Returns:
            JSON string of current user details
        """
        try:
            self.logger.debug("Getting current user")
            result = self.redmine_client.get_current_user()
            self.logger.debug(f"API result: {result}")
            
            if result.get("error"):
                raise Exception(f"Error: {result.get('message', 'Unknown error')}")
            
            user = result.get("user", {})
            
            # Return as JSON string
            return json.dumps(user, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to get current user: {e}")
            return json.dumps({"error": str(e)}, indent=2)
    
    def redmine_list_users(self) -> str:
        """
        List all users (requires admin privileges)
        
        Returns:
            JSON string of users array
        """
        try:
            self.logger.debug("Listing users")
            result = self.redmine_client.get_users()
            self.logger.debug(f"API result: {result}")
            
            if result.get("error"):
                raise Exception(f"Error: {result.get('message', 'Unknown error')}")
            
            users = result.get("users", [])
            
            # Return as JSON string
            return json.dumps(users, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to list users: {e}")
            return json.dumps({"error": str(e)}, indent=2)
    
    def redmine_list_versions(self, project_id: str) -> str:
        """
        List versions for a project
        
        Args:
            project_id: ID or identifier of the project
            
        Returns:
            JSON string of versions array
        """
        try:
            self.logger.debug(f"Listing versions for project: {project_id}")
            result = self.redmine_client.get_versions(project_id)
            self.logger.debug(f"API result: {result}")
            
            if result.get("error"):
                raise Exception(f"Error: {result.get('message', 'Unknown error')}")
            
            versions = result.get("versions", [])
            
            # Return as JSON string
            return json.dumps(versions, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to list versions: {e}")
            return json.dumps({"error": str(e)}, indent=2)
    
    def redmine_health_check(self) -> str:
        """
        Check the health of the Redmine connection
        
        Returns:
            JSON string of health status information
        """
        try:
            self.logger.debug("Performing health check")
            import time
            
            start_time = time.time()
            current_user = self.redmine_client.get_current_user()
            response_time = time.time() - start_time
            
            status = "healthy" if not current_user.get("error") else "unhealthy"
            
            health_data = {
                "status": status,
                "response_time_ms": round(response_time * 1000, 2),
                "timestamp": datetime.datetime.now().isoformat(),
                "server": self.redmine_url,
                "version": current_user.get("version", "unknown")
            }
            
            self.logger.debug(f"Health status: {status}")
            
            # Return as JSON string
            return json.dumps(health_data, indent=2)
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            error_data = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat(),
                "server": self.redmine_url
            }
            return json.dumps(error_data, indent=2)
    
    def _register_tools(self):
        """Register all MCP tools following proper FastMCP pattern"""
        # Register all instance methods as tools after they've been defined
        self.app.tool()(self.redmine_list_issues)
        self.app.tool()(self.redmine_get_issue)
        self.app.tool()(self.redmine_create_issue)
        self.app.tool()(self.redmine_update_issue)
        self.app.tool()(self.redmine_list_projects)
        self.app.tool()(self.redmine_get_project)
        self.app.tool()(self.redmine_create_project)
        self.app.tool()(self.redmine_get_current_user)
        self.app.tool()(self.redmine_list_users)
        self.app.tool()(self.redmine_list_versions)
        self.app.tool()(self.redmine_health_check)
        
        self.logger.info("Registered all Redmine MCP tools successfully")
    
    def run_stdio(self):
        """Run the MCP server with STDIO transport for MCP clients"""
        self.logger.info(f"Starting Redmine MCP Server for {self.redmine_url}")
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
    server = RedmineMCPServer(redmine_url, redmine_api_key)
    server.run_stdio()


if __name__ == '__main__':
    main()
