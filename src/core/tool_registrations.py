"""
Tool registration module for FastMCP tools
"""
import json
import logging
from typing import Any, Dict, Optional

from fastmcp import FastMCP
from ..core import get_logger
from ..core.errors import RedmineAPIError

class ToolRegistrations:
    """Handles registration of FastMCP tools"""
    
    def __init__(self, mcp: FastMCP, client_manager, logger=None):
        """
        Initialize tool registrations
        
        Args:
            mcp: FastMCP instance
            client_manager: Client manager instance
            logger: Optional logger instance
        """
        self.mcp = mcp
        self.client_manager = client_manager
        self.logger = logger or logging.getLogger("redmine_mcp_server.tool_registrations")
        self._registered_tools = []
        self.logger.debug("Tool registrations initialized")
    
    def register_all_tools(self):
        """Register all tools with FastMCP"""
        self.register_issue_tools()
        self.register_admin_tools()
        self.register_version_tools()
        self.register_project_tools()
        
        self.logger.info(f"Registered {len(self._registered_tools)} tools: {', '.join(self._registered_tools)}")
        return self._registered_tools
        
    def register_issue_tools(self):
        """Register issue management tools with FastMCP"""
        issue_client = self.client_manager.get_client('issues')
        self.logger.debug("Registering issue tools")
        
        @self.mcp.tool("redmine-create-issue")
        async def create_issue(project_id: str, subject: str, description: str = None, 
                               tracker_id: int = None, status_id: int = None, 
                               priority_id: int = None, assigned_to_id: int = None):
            """Create a new issue in Redmine"""
            try:
                # Input validation
                if not project_id or not subject:
                    error = "project_id and subject are required"
                    self.logger.error(f"MCP tool redmine-create-issue failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                
                # Build issue data
                issue_data = {"project_id": project_id, "subject": subject}
                
                # Add optional fields if provided
                if description:
                    issue_data["description"] = description
                if tracker_id:
                    issue_data["tracker_id"] = tracker_id
                if status_id:
                    issue_data["status_id"] = status_id
                if priority_id:
                    issue_data["priority_id"] = priority_id
                if assigned_to_id:
                    issue_data["assigned_to_id"] = assigned_to_id
                
                result = issue_client.create_issue(issue_data)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error creating issue: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
        
        self._registered_tools.append("redmine-create-issue")
        
        @self.mcp.tool("redmine-get-issue")
        async def get_issue(issue_id: int):
            """Get issue details by ID"""
            try:
                if not issue_id:
                    error = "issue_id is required"
                    self.logger.error(f"MCP tool redmine-get-issue failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                    
                result = issue_client.get_issue(issue_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error getting issue: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
                
        self._registered_tools.append("redmine-get-issue")
        
        @self.mcp.tool("redmine-list-issues")
        async def list_issues(project_id: str = None, status_id: str = None, 
                             tracker_id: str = None, limit: int = 25):
            """List issues with optional filters"""
            try:
                filters = {}
                if project_id:
                    filters["project_id"] = project_id
                if status_id:
                    filters["status_id"] = status_id
                if tracker_id:
                    filters["tracker_id"] = tracker_id
                    
                # Use params parameter as expected by IssueClient.get_issues method
                params = filters
                if limit:
                    params['limit'] = limit
                result = issue_client.get_issues(params=params)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error listing issues: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
                
        self._registered_tools.append("redmine-list-issues")
        
        @self.mcp.tool("redmine-update-issue")
        async def update_issue(issue_id: int, subject: str = None, description: str = None, 
                              status_id: int = None, priority_id: int = None, 
                              assigned_to_id: int = None, tracker_id: int = None):
            """Update an existing issue"""
            try:
                if not issue_id:
                    error = "issue_id is required"
                    self.logger.error(f"MCP tool redmine-update-issue failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                
                # Build issue data
                issue_data = {}
                
                # Add fields if provided
                if subject:
                    issue_data["subject"] = subject
                if description:
                    issue_data["description"] = description
                if status_id:
                    issue_data["status_id"] = status_id
                if priority_id:
                    issue_data["priority_id"] = priority_id
                if assigned_to_id:
                    issue_data["assigned_to_id"] = assigned_to_id
                if tracker_id:
                    issue_data["tracker_id"] = tracker_id
        
                if not issue_data:
                    error = "No update fields provided"
                    self.logger.error(f"MCP tool redmine-update-issue failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                    
                result = issue_client.update_issue(issue_id, issue_data)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error updating issue: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
                
        self._registered_tools.append("redmine-update-issue")
        
        @self.mcp.tool("redmine-delete-issue")
        async def delete_issue(issue_id: int):
            """Delete an issue by ID"""
            try:
                if not issue_id:
                    error = "issue_id is required"
                    self.logger.error(f"MCP tool redmine-delete-issue failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                    
                result = issue_client.delete_issue(issue_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error deleting issue: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
                
        self._registered_tools.append("redmine-delete-issue")
        
    def register_admin_tools(self):
        """Register administrative tools with FastMCP"""
        issue_client = self.client_manager.get_client('issues')
        self.logger.debug("Registering admin tools")
        
        @self.mcp.tool("redmine-health-check")
        async def health_check():
            """Check Redmine API health"""
            try:
                result = issue_client.connection_manager.health_check()
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error in health check: {e}")
                return json.dumps({"error": str(e), "status": "error"}, indent=2)
                
        self._registered_tools.append("redmine-health-check")
        
        @self.mcp.tool("redmine-version-info")
        async def version_info():
            """Get version and environment information"""
            try:
                # Get git version if available
                import subprocess
                import os
                
                try:
                    git_sha = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], 
                                                     stderr=subprocess.DEVNULL).decode('utf-8').strip()
                except (subprocess.SubprocessError, FileNotFoundError):
                    git_sha = os.environ.get('GIT_COMMIT', 'unknown')
                
                info = {
                    "version": git_sha,
                    "server_mode": os.environ.get('SERVER_MODE', 'unknown'),
                    "log_level": os.environ.get('LOG_LEVEL', 'unknown'),
                    "redmine_url": os.environ.get('REDMINE_URL', 'unknown').replace('http://', 'https://'),
                    "transport": os.environ.get('MCP_TRANSPORT', 'stdio')
                }
                
                return json.dumps(info, indent=2)
            except Exception as e:
                self.logger.error(f"Error getting version info: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
                
        self._registered_tools.append("redmine-version-info")
        
        @self.mcp.tool("redmine-current-user")
        async def current_user():
            """Get current authenticated user information"""
            try:
                user_client = self.client_manager.get_client('users')
                if not user_client:
                    return json.dumps({"error": "User client not available"}, indent=2)
                    
                result = user_client.get_current_user()
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error getting current user: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
                
        self._registered_tools.append("redmine-current-user")
        
    def register_version_tools(self):
        """Register version management tools with FastMCP"""
        roadmap_client = self.client_manager.get_client('roadmap')
        self.logger.debug("Registering version tools")
        
        @self.mcp.tool("redmine-list-versions")
        async def list_versions(project_id: str):
            """List versions for a project"""
            try:
                if not project_id:
                    error = "project_id is required"
                    self.logger.error(f"MCP tool redmine-list-versions failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                    
                result = roadmap_client.get_versions(project_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error listing versions: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
                
        self._registered_tools.append("redmine-list-versions")
        
        @self.mcp.tool("redmine-get-version")
        async def get_version(version_id: int):
            """Get version details by ID"""
            try:
                if not version_id:
                    error = "version_id is required"
                    self.logger.error(f"MCP tool redmine-get-version failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                    
                result = roadmap_client.get_version(version_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error getting version: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
                
        self._registered_tools.append("redmine-get-version")
        
        @self.mcp.tool("redmine-create-version")
        async def create_version(project_id: str, name: str, description: str = None, 
                                status: str = "open", sharing: str = "none", 
                                due_date: str = None):
            """Create a new version"""
            try:
                if not project_id or not name:
                    error = "project_id and name are required"
                    self.logger.error(f"MCP tool redmine-create-version failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                
                # Build version data
                version_data = {
                    "project_id": project_id,
                    "name": name
                }
                
                # Add optional fields if provided
                if description:
                    version_data["description"] = description
                if status:
                    version_data["status"] = status
                if sharing:
                    version_data["sharing"] = sharing
                if due_date:
                    version_data["due_date"] = due_date
                    
                result = roadmap_client.create_version(version_data)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error creating version: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
                
        self._registered_tools.append("redmine-create-version")
        
        @self.mcp.tool("redmine-update-version")
        async def update_version(version_id: int, name: str = None, description: str = None, 
                                status: str = None, sharing: str = None, 
                                due_date: str = None):
            """Update an existing version"""
            try:
                if not version_id:
                    error = "version_id is required"
                    self.logger.error(f"MCP tool redmine-update-version failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                
                # Build version data
                version_data = {}
                
                # Add fields if provided
                if name:
                    version_data["name"] = name
                if description:
                    version_data["description"] = description
                if status:
                    version_data["status"] = status
                if sharing:
                    version_data["sharing"] = sharing
                if due_date:
                    version_data["due_date"] = due_date
                
                if not version_data:
                    error = "No update fields provided"
                    self.logger.error(f"MCP tool redmine-update-version failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                    
                result = roadmap_client.update_version(version_id, version_data)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error updating version: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
                
        self._registered_tools.append("redmine-update-version")
        
        @self.mcp.tool("redmine-delete-version")
        async def delete_version(version_id: int):
            """Delete a version by ID"""
            try:
                if not version_id:
                    error = "version_id is required"
                    self.logger.error(f"MCP tool redmine-delete-version failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                    
                result = roadmap_client.delete_version(version_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error deleting version: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
                
        self._registered_tools.append("redmine-delete-version")
        
        @self.mcp.tool("redmine-get-issues-by-version")
        async def get_issues_by_version(version_id: int):
            """Get all issues for a specific version"""
            try:
                if not version_id:
                    error = "version_id is required"
                    self.logger.error(f"MCP tool redmine-get-issues-by-version failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                    
                result = roadmap_client.get_issues_by_version(version_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error getting issues by version: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
                
        self._registered_tools.append("redmine-get-issues-by-version")
        
    def register_project_tools(self):
        """Register project management tools with FastMCP"""
        project_client = self.client_manager.get_client('projects')
        self.logger.debug("Registering project tools")
        
        @self.mcp.tool("redmine-list-projects")
        async def list_projects(include: list = None):
            """Lists all available projects
            
            Args:
                include: Optional list of associations to include
                         (trackers, issue_categories, enabled_modules, etc.)
            """
            try:
                params = {}
                if include:
                    if isinstance(include, list):
                        params['include'] = ','.join(include)
                    else:
                        params['include'] = include
                        
                result = project_client.get_projects(params=params)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error listing projects: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
        
        self._registered_tools.append("redmine-list-projects")
        
        @self.mcp.tool("redmine-create-project")
        async def create_project(name: str, identifier: str, description: str = None,
                                is_public: bool = True, parent_id: int = None,
                                inherit_members: bool = False):
            """Create a new project in Redmine"""
            try:
                # Input validation
                if not name or not identifier:
                    error = "name and identifier are required"
                    self.logger.error(f"MCP tool redmine-create-project failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                
                # Build project data
                project_data = {
                    "name": name,
                    "identifier": identifier,
                    "is_public": is_public
                }
                
                # Add optional fields if provided
                if description:
                    project_data["description"] = description
                if parent_id:
                    project_data["parent_id"] = parent_id
                if inherit_members:
                    project_data["inherit_members"] = inherit_members
                
                result = project_client.create_project(project_data)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error creating project: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
        
        self._registered_tools.append("redmine-create-project")
        
        @self.mcp.tool("redmine-update-project")
        async def update_project(project_id: str, name: str = None, description: str = None,
                                is_public: bool = None, parent_id: int = None):
            """Update attributes of an existing project"""
            try:
                # Input validation
                if not project_id:
                    error = "project_id is required"
                    self.logger.error(f"MCP tool redmine-update-project failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                
                # Build project data
                project_data = {}
                
                # Add fields if provided
                if name:
                    project_data["name"] = name
                if description:
                    project_data["description"] = description
                if is_public is not None:
                    project_data["is_public"] = is_public
                if parent_id:
                    project_data["parent_id"] = parent_id
                
                if not project_data:
                    error = "No update fields provided"
                    self.logger.error(f"MCP tool redmine-update-project failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                
                result = project_client.update_project(project_id, project_data)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error updating project: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
        
        self._registered_tools.append("redmine-update-project")
        
        @self.mcp.tool("redmine-delete-project")
        async def delete_project(project_id: str):
            """Delete a project by its ID or identifier"""
            try:
                # Input validation
                if not project_id:
                    error = "project_id is required"
                    self.logger.error(f"MCP tool redmine-delete-project failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                
                result = project_client.delete_project(project_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                self.logger.error(f"Error deleting project: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
        
        self._registered_tools.append("redmine-delete-project")
