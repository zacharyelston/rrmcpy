#!/usr/bin/env python3
"""
FastMCP server implementation for Redmine integration using modular client
This server exposes Redmine functionality through the MCP protocol
"""
import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from modules.redmine_client import RedmineClient

# Types
class MCPRequest:
    def __init__(self, method: str, path: str, data: Optional[Dict] = None):
        self.method = method
        self.path = path
        self.data = data or {}
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MCPRequest':
        """Create an MCPRequest from a JSON string"""
        try:
            data = json.loads(json_str)
            return cls(
                method=data.get('method', 'GET'),
                path=data.get('path', '/'),
                data=data.get('data')
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in MCP request: {e}")
    
    def __str__(self) -> str:
        return f"{self.method} {self.path}"


class MCPResponse:
    def __init__(self, data: Optional[Dict] = None, status: int = 200):
        self.data = data or {}
        self.status = status
    
    def to_json(self) -> str:
        """Convert the response to a JSON string"""
        return json.dumps({
            'status': self.status,
            'data': self.data
        })
    
    def __str__(self) -> str:
        return f"Response [{self.status}]"


class MCPServer:
    def __init__(self):
        """Initialize the MCP server"""
        self.routes = {}
        self.running = False
        self.logger = logging.getLogger("MCPServer")
    
    def route(self, path: str, methods: List[str]):
        """
        Decorator to register a route handler
        
        Args:
            path: URL path to match
            methods: List of HTTP methods to match (GET, POST, PUT, DELETE)
        """
        def decorator(func: Callable):
            # Register the route for each method
            for method in methods:
                key = (method.upper(), path)
                self.routes[key] = func
            return func
        return decorator
    
    def start(self):
        """Start the server - reads from stdin and writes to stdout"""
        self.running = True
        self.logger.info("MCPServer started using STDIO")
        
        try:
            while self.running:
                line = sys.stdin.readline().strip()
                if not line:
                    self.logger.debug("Empty line received, continuing")
                    continue
                
                try:
                    request = MCPRequest.from_json(line)
                    self.logger.debug(f"Received MCP request: {request}")
                    
                    response = self._process_request(request)
                    self.logger.debug(f"Sending MCP response: {response}")
                    
                    # Write response to stdout
                    print(response.to_json())
                    sys.stdout.flush()
                except Exception as e:
                    self.logger.error(f"Error processing request: {e}")
                    error_response = MCPResponse(
                        data={"error": str(e)},
                        status=400
                    )
                    print(error_response.to_json())
                    sys.stdout.flush()
        except KeyboardInterrupt:
            self.logger.info("Server shutdown requested")
            self.running = False
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            self.running = False
    
    def _process_request(self, request: MCPRequest) -> MCPResponse:
        """Process an incoming MCP request"""
        key = (request.method, request.path)
        
        # Check if we have an exact path match
        if key in self.routes:
            handler = self.routes[key]
            return handler(request)
        
        # Try to find a route with a parameter
        for (method, path), handler in self.routes.items():
            if method != request.method:
                continue
            
            # Check if this is a parameterized route (e.g. /issues/:id)
            if ':' in path:
                parts = path.split('/')
                request_parts = request.path.split('/')
                
                if len(parts) != len(request_parts):
                    continue
                
                match = True
                for i, part in enumerate(parts):
                    if part.startswith(':'):
                        # This is a parameter, no need to match exactly
                        continue
                    elif part != request_parts[i]:
                        match = False
                        break
                
                if match:
                    return handler(request)
        
        # No route found
        return MCPResponse(
            data={"error": f"No route found for {request.method} {request.path}"},
            status=404
        )
    
    def stop(self):
        """Stop the server"""
        self.running = False
        self.logger.info("MCPServer stopped")


class RedmineMCPServer:
    """
    MCP Server implementation for Redmine using STDIO
    """
    def __init__(self, redmine_url: str, api_key: str, server_mode: str = 'live', 
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the Redmine MCP Server
        
        Args:
            redmine_url: URL of the Redmine instance
            api_key: API key for Redmine authentication
            server_mode: Server mode ('live' or 'test')
            logger: Optional logger instance
        """
        self.redmine_url = redmine_url
        self.api_key = api_key
        self.server_mode = server_mode
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize the MCP server
        self.server = MCPServer()
        
        # Initialize the Redmine client
        self.redmine = RedmineClient(redmine_url, api_key, logger)
        
        self.logger.info(f"Connected to Redmine at {redmine_url}")
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register all the MCP routes"""
        server = self.server
        
        #
        # Health Check
        #
        @server.route("/health", ["GET"])
        def health_check(request: MCPRequest) -> MCPResponse:
            """Health check endpoint"""
            return MCPResponse({
                "status": "ok",
                "mode": self.server_mode,
                "redmine_url": self.redmine_url
            })
        
        #
        # Issues
        #
        @server.route("/issues", ["GET"])
        def get_issues(request: MCPRequest) -> MCPResponse:
            """Get all issues, optionally filtered"""
            try:
                result = self.redmine.get_issues(request.data)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting issues: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/issues/:id", ["GET"])
        def get_issue(request: MCPRequest) -> MCPResponse:
            """Get a specific issue by ID"""
            try:
                issue_id = int(request.path.split('/')[-1])
                include = request.data.get('include', []) if request.data else None
                result = self.redmine.get_issue(issue_id, include)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting issue: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/issues", ["POST"])
        def create_issue(request: MCPRequest) -> MCPResponse:
            """Create a new issue"""
            try:
                if not request.data:
                    return MCPResponse({"error": "No issue data provided"}, 400)
                
                result = self.redmine.create_issue(request.data)
                return MCPResponse(result, 201)
            except Exception as e:
                self.logger.error(f"Error creating issue: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/issues/:id", ["PUT"])
        def update_issue(request: MCPRequest) -> MCPResponse:
            """Update an existing issue"""
            try:
                issue_id = int(request.path.split('/')[-1])
                if not request.data:
                    return MCPResponse({"error": "No update data provided"}, 400)
                
                result = self.redmine.update_issue(issue_id, request.data)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error updating issue: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/issues/:id", ["DELETE"])
        def delete_issue(request: MCPRequest) -> MCPResponse:
            """Delete an issue"""
            try:
                issue_id = int(request.path.split('/')[-1])
                result = self.redmine.delete_issue(issue_id)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error deleting issue: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        #
        # Projects
        #
        @server.route("/projects", ["GET"])
        def get_projects(request: MCPRequest) -> MCPResponse:
            """Get all projects"""
            try:
                result = self.redmine.get_projects(request.data)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting projects: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/projects/:id", ["GET"])
        def get_project(request: MCPRequest) -> MCPResponse:
            """Get a specific project by ID or identifier"""
            try:
                project_id = request.path.split('/')[-1]
                include = request.data.get('include', []) if request.data else None
                result = self.redmine.get_project(project_id, include)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting project: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/projects", ["POST"])
        def create_project(request: MCPRequest) -> MCPResponse:
            """Create a new project"""
            try:
                if not request.data:
                    return MCPResponse({"error": "No project data provided"}, 400)
                
                result = self.redmine.create_project(request.data)
                return MCPResponse(result, 201)
            except Exception as e:
                self.logger.error(f"Error creating project: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/projects/:id", ["PUT"])
        def update_project(request: MCPRequest) -> MCPResponse:
            """Update an existing project"""
            try:
                project_id = request.path.split('/')[-1]
                if not request.data:
                    return MCPResponse({"error": "No update data provided"}, 400)
                
                result = self.redmine.update_project(project_id, request.data)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error updating project: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/projects/:id", ["DELETE"])
        def delete_project(request: MCPRequest) -> MCPResponse:
            """Delete a project"""
            try:
                project_id = request.path.split('/')[-1]
                result = self.redmine.delete_project(project_id)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error deleting project: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        #
        # Versions
        #
        @server.route("/projects/:id/versions", ["GET"])
        def get_versions(request: MCPRequest) -> MCPResponse:
            """Get versions for a project"""
            try:
                project_id = request.path.split('/')[-2]
                result = self.redmine.get_versions(project_id)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting versions: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/versions/:id", ["GET"])
        def get_version(request: MCPRequest) -> MCPResponse:
            """Get a specific version by ID"""
            try:
                version_id = int(request.path.split('/')[-1])
                result = self.redmine.get_version(version_id)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting version: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/projects/:id/versions", ["POST"])
        def create_version(request: MCPRequest) -> MCPResponse:
            """Create a new version for a project"""
            try:
                project_id = request.path.split('/')[-2]
                if not request.data:
                    return MCPResponse({"error": "No version data provided"}, 400)
                
                # Make sure project_id is set correctly
                version_data = request.data.copy()
                version_data['project_id'] = project_id
                
                result = self.redmine.create_version(version_data)
                return MCPResponse(result, 201)
            except Exception as e:
                self.logger.error(f"Error creating version: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/versions/:id", ["PUT"])
        def update_version(request: MCPRequest) -> MCPResponse:
            """Update an existing version"""
            try:
                version_id = int(request.path.split('/')[-1])
                if not request.data:
                    return MCPResponse({"error": "No update data provided"}, 400)
                
                result = self.redmine.update_version(version_id, request.data)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error updating version: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/versions/:id", ["DELETE"])
        def delete_version(request: MCPRequest) -> MCPResponse:
            """Delete a version"""
            try:
                version_id = int(request.path.split('/')[-1])
                result = self.redmine.delete_version(version_id)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error deleting version: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        #
        # Users
        #
        @server.route("/users", ["GET"])
        def get_users(request: MCPRequest) -> MCPResponse:
            """Get all users"""
            try:
                result = self.redmine.get_users(request.data)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting users: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/users/:id", ["GET"])
        def get_user(request: MCPRequest) -> MCPResponse:
            """Get a specific user by ID"""
            try:
                user_id = int(request.path.split('/')[-1])
                include = request.data.get('include', []) if request.data else None
                result = self.redmine.get_user(user_id, include)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting user: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/users", ["POST"])
        def create_user(request: MCPRequest) -> MCPResponse:
            """Create a new user"""
            try:
                if not request.data:
                    return MCPResponse({"error": "No user data provided"}, 400)
                
                result = self.redmine.create_user(request.data)
                return MCPResponse(result, 201)
            except Exception as e:
                self.logger.error(f"Error creating user: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/users/:id", ["PUT"])
        def update_user(request: MCPRequest) -> MCPResponse:
            """Update an existing user"""
            try:
                user_id = int(request.path.split('/')[-1])
                if not request.data:
                    return MCPResponse({"error": "No update data provided"}, 400)
                
                result = self.redmine.update_user(user_id, request.data)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error updating user: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/users/:id", ["DELETE"])
        def delete_user(request: MCPRequest) -> MCPResponse:
            """Delete a user"""
            try:
                user_id = int(request.path.split('/')[-1])
                result = self.redmine.delete_user(user_id)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error deleting user: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/users/current", ["GET"])
        def current_user(request: MCPRequest) -> MCPResponse:
            """Get the current user (based on API key)"""
            try:
                result = self.redmine.get_current_user()
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting current user: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        #
        # Groups
        #
        @server.route("/groups", ["GET"])
        def get_groups(request: MCPRequest) -> MCPResponse:
            """Get all groups"""
            try:
                result = self.redmine.get_groups(request.data)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting groups: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/groups/:id", ["GET"])
        def get_group(request: MCPRequest) -> MCPResponse:
            """Get a specific group by ID"""
            try:
                group_id = int(request.path.split('/')[-1])
                include = request.data.get('include', []) if request.data else None
                result = self.redmine.get_group(group_id, include)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting group: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/groups", ["POST"])
        def create_group(request: MCPRequest) -> MCPResponse:
            """Create a new group"""
            try:
                if not request.data:
                    return MCPResponse({"error": "No group data provided"}, 400)
                
                result = self.redmine.create_group(request.data)
                return MCPResponse(result, 201)
            except Exception as e:
                self.logger.error(f"Error creating group: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/groups/:id", ["PUT"])
        def update_group(request: MCPRequest) -> MCPResponse:
            """Update an existing group"""
            try:
                group_id = int(request.path.split('/')[-1])
                if not request.data:
                    return MCPResponse({"error": "No update data provided"}, 400)
                
                result = self.redmine.update_group(group_id, request.data)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error updating group: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/groups/:id", ["DELETE"])
        def delete_group(request: MCPRequest) -> MCPResponse:
            """Delete a group"""
            try:
                group_id = int(request.path.split('/')[-1])
                result = self.redmine.delete_group(group_id)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error deleting group: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/groups/:id/users", ["POST"])
        def add_user_to_group(request: MCPRequest) -> MCPResponse:
            """Add a user to a group"""
            try:
                group_id = int(request.path.split('/')[-2])
                if not request.data or 'user_id' not in request.data:
                    return MCPResponse({"error": "No user_id provided"}, 400)
                
                user_id = request.data['user_id']
                result = self.redmine.add_user_to_group(group_id, user_id)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error adding user to group: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @server.route("/groups/:id/users/:user_id", ["DELETE"])
        def remove_user_from_group(request: MCPRequest) -> MCPResponse:
            """Remove a user from a group"""
            try:
                path_parts = request.path.split('/')
                group_id = int(path_parts[-3])
                user_id = int(path_parts[-1])
                
                result = self.redmine.remove_user_from_group(group_id, user_id)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error removing user from group: {e}")
                return MCPResponse({"error": str(e)}, 500)
    
    def start(self):
        """Start the MCP server"""
        self.logger.info("Starting Redmine MCP Server using STDIO")
        self.server.start()
    
    def stop(self):
        """Stop the MCP server"""
        self.server.stop()