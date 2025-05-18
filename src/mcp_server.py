"""
FastMCP server implementation for Redmine integration
This server exposes Redmine functionality through the MCP protocol
"""
import os
import logging
import json
import time
import sys
import threading
import socket
from typing import Dict, List, Any, Optional, Callable, Union
from redmine_api import RedmineAPI

# Minimal implementation for MCPServer - we don't use a pre-existing FastMCP package
class MCPRequest:
    def __init__(self, method: str, path: str, data: Optional[Dict] = None):
        self.method = method
        self.path = path
        self.data = data or {}

class MCPResponse:
    def __init__(self, data: Optional[Dict] = None, status: int = 200):
        self.data = data or {}
        self.status = status

class MCPServer:
    def __init__(self):
        self.routes = {}
        self.running = False
        self.logger = logging.getLogger("MCPServer")
    
    def route(self, path: str, methods: List[str]):
        def decorator(func):
            for method in methods:
                route_key = f"{method.upper()}:{path}"
                self.routes[route_key] = func
            return func
        return decorator
    
    def start(self):
        """Start the server - reads from stdin and writes to stdout"""
        self.running = True
        self.logger.info("MCPServer started using STDIO")
        
        # Process messages from stdin
        while self.running:
            try:
                # Read a line from stdin
                line = sys.stdin.readline().strip()
                if not line:
                    # Empty line, could be EOF
                    time.sleep(0.1)
                    continue
                
                try:
                    request_data = json.loads(line)
                    method = request_data.get('method', '').upper()
                    path = request_data.get('path', '')
                    payload = request_data.get('data', {})
                    
                    self.logger.debug(f"Received request: {method} {path}")
                    
                    request = MCPRequest(method, path, payload)
                    response = self._process_request(request)
                    
                    # Write response to stdout
                    response_json = json.dumps({
                        'status': response.status,
                        'data': response.data
                    })
                    print(response_json, flush=True)
                    
                except json.JSONDecodeError:
                    self.logger.error("Invalid JSON received")
                    response_json = json.dumps({
                        'status': 400,
                        'data': {'error': 'Invalid request format'}
                    })
                    print(response_json, flush=True)
                    
            except Exception as e:
                self.logger.error(f"Error processing request: {e}")
                response_json = json.dumps({
                    'status': 500,
                    'data': {'error': f'Server error: {str(e)}'}
                })
                print(response_json, flush=True)
    
    def _process_request(self, request: MCPRequest) -> MCPResponse:
        """Process an incoming MCP request"""
        route_key = f"{request.method}:{request.path}"
        
        if route_key in self.routes:
            handler = self.routes[route_key]
            try:
                return handler(request)
            except Exception as e:
                self.logger.error(f"Error in route handler {route_key}: {e}")
                return MCPResponse({"error": str(e)}, 500)
        else:
            return MCPResponse({"error": "Not Found"}, 404)
    
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
        
        # Initialize the Redmine API client
        self.redmine_api = RedmineAPI(redmine_url, api_key, self.logger)
        
        # Initialize the MCP server
        self.server = MCPServer()
        
        self.logger.info(f"Starting Redmine MCP Server using STDIO")
        self.logger.info(f"Connected to Redmine at {redmine_url}")
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register all the MCP routes"""
        # Health check
        @self.server.route("/health", methods=["GET"])
        def health_check(request: MCPRequest) -> MCPResponse:
            return MCPResponse({
                "status": "ok",
                "server_mode": self.server_mode,
                "redmine_url": self.redmine_url
            })
        
        # ===== Issues API =====
        @self.server.route("/issues", methods=["GET"])
        def get_issues(request: MCPRequest) -> MCPResponse:
            try:
                params = request.data.get('params', {})
                result = self.redmine_api.get_issues(params)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting issues: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/issues/{issue_id}", methods=["GET"])
        def get_issue(request: MCPRequest) -> MCPResponse:
            try:
                issue_id = int(request.path.split('/')[-1])
                include = request.data.get('include', [])
                result = self.redmine_api.get_issue(issue_id, include)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting issue: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/issues", methods=["POST"])
        def create_issue(request: MCPRequest) -> MCPResponse:
            try:
                issue_data = request.data.get('issue', {})
                result = self.redmine_api.create_issue(issue_data)
                return MCPResponse(result, 201)
            except Exception as e:
                self.logger.error(f"Error creating issue: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/issues/{issue_id}", methods=["PUT"])
        def update_issue(request: MCPRequest) -> MCPResponse:
            try:
                issue_id = int(request.path.split('/')[-1])
                issue_data = request.data.get('issue', {})
                result = self.redmine_api.update_issue(issue_id, issue_data)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error updating issue: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/issues/{issue_id}", methods=["DELETE"])
        def delete_issue(request: MCPRequest) -> MCPResponse:
            try:
                issue_id = int(request.path.split('/')[-1])
                self.redmine_api.delete_issue(issue_id)
                return MCPResponse({"status": "success"})
            except Exception as e:
                self.logger.error(f"Error deleting issue: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        # ===== Projects API =====
        @self.server.route("/projects", methods=["GET"])
        def get_projects(request: MCPRequest) -> MCPResponse:
            try:
                params = request.data.get('params', {})
                result = self.redmine_api.get_projects(params)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting projects: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/projects/{project_id}", methods=["GET"])
        def get_project(request: MCPRequest) -> MCPResponse:
            try:
                project_id = request.path.split('/')[-1]
                include = request.data.get('include', [])
                result = self.redmine_api.get_project(project_id, include)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting project: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/projects", methods=["POST"])
        def create_project(request: MCPRequest) -> MCPResponse:
            try:
                project_data = request.data.get('project', {})
                result = self.redmine_api.create_project(project_data)
                return MCPResponse(result, 201)
            except Exception as e:
                self.logger.error(f"Error creating project: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/projects/{project_id}", methods=["PUT"])
        def update_project(request: MCPRequest) -> MCPResponse:
            try:
                project_id = request.path.split('/')[-1]
                project_data = request.data.get('project', {})
                result = self.redmine_api.update_project(project_id, project_data)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error updating project: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/projects/{project_id}", methods=["DELETE"])
        def delete_project(request: MCPRequest) -> MCPResponse:
            try:
                project_id = request.path.split('/')[-1]
                self.redmine_api.delete_project(project_id)
                return MCPResponse({"status": "success"})
            except Exception as e:
                self.logger.error(f"Error deleting project: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        # ===== Versions API =====
        @self.server.route("/projects/{project_id}/versions", methods=["GET"])
        def get_versions(request: MCPRequest) -> MCPResponse:
            try:
                project_id = request.path.split('/')[-2]
                result = self.redmine_api.get_versions(project_id)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting versions: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/versions/{version_id}", methods=["GET"])
        def get_version(request: MCPRequest) -> MCPResponse:
            try:
                version_id = int(request.path.split('/')[-1])
                result = self.redmine_api.get_version(version_id)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting version: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/versions", methods=["POST"])
        def create_version(request: MCPRequest) -> MCPResponse:
            try:
                version_data = request.data.get('version', {})
                result = self.redmine_api.create_version(version_data)
                return MCPResponse(result, 201)
            except Exception as e:
                self.logger.error(f"Error creating version: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/versions/{version_id}", methods=["PUT"])
        def update_version(request: MCPRequest) -> MCPResponse:
            try:
                version_id = int(request.path.split('/')[-1])
                version_data = request.data.get('version', {})
                result = self.redmine_api.update_version(version_id, version_data)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error updating version: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/versions/{version_id}", methods=["DELETE"])
        def delete_version(request: MCPRequest) -> MCPResponse:
            try:
                version_id = int(request.path.split('/')[-1])
                self.redmine_api.delete_version(version_id)
                return MCPResponse({"status": "success"})
            except Exception as e:
                self.logger.error(f"Error deleting version: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        # ===== Users API =====
        @self.server.route("/users", methods=["GET"])
        def get_users(request: MCPRequest) -> MCPResponse:
            try:
                params = request.data.get('params', {})
                result = self.redmine_api.get_users(params)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting users: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/users/{user_id}", methods=["GET"])
        def get_user(request: MCPRequest) -> MCPResponse:
            try:
                user_id = int(request.path.split('/')[-1])
                include = request.data.get('include', [])
                result = self.redmine_api.get_user(user_id, include)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting user: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/users", methods=["POST"])
        def create_user(request: MCPRequest) -> MCPResponse:
            try:
                user_data = request.data.get('user', {})
                result = self.redmine_api.create_user(user_data)
                return MCPResponse(result, 201)
            except Exception as e:
                self.logger.error(f"Error creating user: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/users/{user_id}", methods=["PUT"])
        def update_user(request: MCPRequest) -> MCPResponse:
            try:
                user_id = int(request.path.split('/')[-1])
                user_data = request.data.get('user', {})
                result = self.redmine_api.update_user(user_id, user_data)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error updating user: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/users/{user_id}", methods=["DELETE"])
        def delete_user(request: MCPRequest) -> MCPResponse:
            try:
                user_id = int(request.path.split('/')[-1])
                self.redmine_api.delete_user(user_id)
                return MCPResponse({"status": "success"})
            except Exception as e:
                self.logger.error(f"Error deleting user: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/users/current", methods=["GET"])
        def current_user(request: MCPRequest) -> MCPResponse:
            try:
                result = self.redmine_api.get_current_user()
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting current user: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        # ===== Groups API =====
        @self.server.route("/groups", methods=["GET"])
        def get_groups(request: MCPRequest) -> MCPResponse:
            try:
                params = request.data.get('params', {})
                result = self.redmine_api.get_groups(params)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting groups: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/groups/{group_id}", methods=["GET"])
        def get_group(request: MCPRequest) -> MCPResponse:
            try:
                group_id = int(request.path.split('/')[-1])
                include = request.data.get('include', [])
                result = self.redmine_api.get_group(group_id, include)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error getting group: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/groups", methods=["POST"])
        def create_group(request: MCPRequest) -> MCPResponse:
            try:
                group_data = request.data.get('group', {})
                result = self.redmine_api.create_group(group_data)
                return MCPResponse(result, 201)
            except Exception as e:
                self.logger.error(f"Error creating group: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/groups/{group_id}", methods=["PUT"])
        def update_group(request: MCPRequest) -> MCPResponse:
            try:
                group_id = int(request.path.split('/')[-1])
                group_data = request.data.get('group', {})
                result = self.redmine_api.update_group(group_id, group_data)
                return MCPResponse(result)
            except Exception as e:
                self.logger.error(f"Error updating group: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/groups/{group_id}", methods=["DELETE"])
        def delete_group(request: MCPRequest) -> MCPResponse:
            try:
                group_id = int(request.path.split('/')[-1])
                self.redmine_api.delete_group(group_id)
                return MCPResponse({"status": "success"})
            except Exception as e:
                self.logger.error(f"Error deleting group: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/groups/{group_id}/users", methods=["POST"])
        def add_user_to_group(request: MCPRequest) -> MCPResponse:
            try:
                group_id = int(request.path.split('/')[-2])
                user_id = request.data.get('user_id')
                if user_id is None:
                    return MCPResponse({"error": "Missing user_id parameter"}, 400)
                user_id = int(user_id)
                result = self.redmine_api.add_user_to_group(group_id, user_id)
                return MCPResponse(result, 201)
            except Exception as e:
                self.logger.error(f"Error adding user to group: {e}")
                return MCPResponse({"error": str(e)}, 500)
        
        @self.server.route("/groups/{group_id}/users/{user_id}", methods=["DELETE"])
        def remove_user_from_group(request: MCPRequest) -> MCPResponse:
            try:
                group_id = int(request.path.split('/')[-3])
                user_id = int(request.path.split('/')[-1])
                self.redmine_api.remove_user_from_group(group_id, user_id)
                return MCPResponse({"status": "success"})
            except Exception as e:
                self.logger.error(f"Error removing user from group: {e}")
                return MCPResponse({"error": str(e)}, 500)
    
    def start(self):
        """Start the MCP server"""
        self.logger.info("Starting Redmine MCP Server using STDIO")
        
        # Start the server directly - for STDIO communication we don't need a separate thread
        self.server.start()
    
    def stop(self):
        """Stop the MCP server"""
        self.logger.info("Stopping Redmine MCP Server")
        self.server.stop()
        self.logger.info("Redmine MCP Server stopped")