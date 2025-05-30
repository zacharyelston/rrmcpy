#!/usr/bin/env python3
"""
STDIO-compatible MCP Server for Redmine
Simplified implementation that works properly with MCP clients
"""
import asyncio
import json
import logging
import os
import sys

from typing import Any, Dict, List, Union


from src.redmine_client import RedmineClient


class RedmineSTDIOServer:
    """
    STDIO-compatible Redmine MCP Server
    Handles MCP protocol directly via stdin/stdout
    """
    
    def __init__(self, redmine_url: str, api_key: str):
        """Initialize the STDIO server"""
        self.redmine_url = redmine_url
        self.api_key = api_key
        self.redmine_client = RedmineClient(redmine_url, api_key)
        
        # Configure logging to stderr only
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stderr
        )
        self.logger = logging.getLogger(__name__)
        
        # Available tools
        self.tools = {
            "list_issues": self._list_issues,
            "get_issue": self._get_issue,
            "create_issue": self._create_issue,
            "update_issue": self._update_issue,
            "list_projects": self._list_projects,
            "get_project": self._get_project,
            "get_current_user": self._get_current_user,
            "list_users": self._list_users,
            "health_check": self._health_check,
        }
    
    def _list_issues(self, **kwargs) -> Dict[str, Any]:
        """List issues with optional filtering"""
        params = {}
        if kwargs.get("project_id"):
            params["project_id"] = kwargs["project_id"]
        if kwargs.get("status_id"):
            params["status_id"] = kwargs["status_id"]
        if kwargs.get("assigned_to_id"):
            params["assigned_to_id"] = kwargs["assigned_to_id"]
        if kwargs.get("limit"):
            params["limit"] = kwargs["limit"]
        
        result = self.redmine_client.get_issues(params)
        return result.get('issues', [])
    
    def _get_issue(self, issue_id: int) -> Dict[str, Any]:
        """Get a specific issue"""
        result = self.redmine_client.get_issue(issue_id)
        if result.get('error'):
            raise Exception(f"Error getting issue: {result.get('message', 'Unknown error')}")
        return result.get('issue', {})
    
    def _create_issue(self, **kwargs) -> Dict[str, Any]:
        """Create a new issue"""
        issue_data = {
            "subject": kwargs.get("subject"),
            "project_id": kwargs.get("project_id"),
            "description": kwargs.get("description", ""),
        }
        
        # Add optional fields
        if kwargs.get("tracker_id"):
            issue_data["tracker_id"] = kwargs["tracker_id"]
        if kwargs.get("status_id"):
            issue_data["status_id"] = kwargs["status_id"]
        if kwargs.get("priority_id"):
            issue_data["priority_id"] = kwargs["priority_id"]
        if kwargs.get("assigned_to_id"):
            issue_data["assigned_to_id"] = kwargs["assigned_to_id"]
        
        result = self.redmine_client.create_issue(issue_data)
        if result.get('error'):
            raise Exception(f"Error creating issue: {result.get('message', 'Unknown error')}")
        return result.get('issue', {})
    
    def _update_issue(self, issue_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing issue"""
        update_data = {}
        for field in ["subject", "description", "status_id", "priority_id", "assigned_to_id"]:
            if kwargs.get(field) is not None:
                update_data[field] = kwargs[field]
        
        result = self.redmine_client.update_issue(issue_id, update_data)
        if result.get('error'):
            raise Exception(f"Error updating issue: {result.get('message', 'Unknown error')}")
        return {"success": True, "issue_id": issue_id}
    
    def _list_projects(self, **kwargs) -> List[Dict[str, Any]]:
        """List projects"""
        result = self.redmine_client.get_projects()
        return result.get('projects', [])
    
    def _get_project(self, project_id: str) -> Dict[str, Any]:
        """Get a specific project"""
        result = self.redmine_client.get_project(project_id)
        if result.get('error'):
            raise Exception(f"Error getting project: {result.get('message', 'Unknown error')}")
        return result.get('project', {})
    
    def _get_current_user(self, **kwargs) -> Dict[str, Any]:
        """Get current user information"""
        result = self.redmine_client.get_current_user()
        if result.get('error'):
            raise Exception(f"Error getting current user: {result.get('message', 'Unknown error')}")
        return result.get('user', {})
    
    def _list_users(self, **kwargs) -> List[Dict[str, Any]]:
        """List users"""
        result = self.redmine_client.get_users()
        return result.get('users', [])
    
    def _health_check(self, **kwargs) -> Dict[str, Any]:
        """Check connection health"""
        healthy = self.redmine_client.health_check()
        return {
            "healthy": healthy,
            "redmine_url": self.redmine_url,
            "timestamp": self.redmine_client.issues._get_timestamp()
        }
    

    def _ensure_valid_id(self, request_id: Union[str, int, None]) -> Union[str, int]:
        """Ensure the request ID is valid for MCP protocol"""
        if request_id is None:
            return "0"  # Use string "0" as default for null IDs
        return request_id
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP request"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = self._ensure_valid_id(request.get("id"))
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "redmine-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "list_issues",
                                "description": "List issues with optional filtering",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "project_id": {"type": "string"},
                                        "status_id": {"type": "integer"},
                                        "assigned_to_id": {"type": "integer"},
                                        "limit": {"type": "integer"}
                                    }
                                }
                            },
                            {
                                "name": "get_issue",
                                "description": "Get a specific issue by ID",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "issue_id": {"type": "integer"}
                                    },
                                    "required": ["issue_id"]
                                }
                            },
                            {
                                "name": "create_issue",
                                "description": "Create a new issue",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "subject": {"type": "string"},
                                        "project_id": {"type": "string"},
                                        "description": {"type": "string"},
                                        "tracker_id": {"type": "integer"},
                                        "status_id": {"type": "integer"},
                                        "priority_id": {"type": "integer"},
                                        "assigned_to_id": {"type": "integer"}
                                    },
                                    "required": ["subject", "project_id"]
                                }
                            },
                            {
                                "name": "list_projects",
                                "description": "List all accessible projects",
                                "inputSchema": {"type": "object", "properties": {}}
                            },
                            {
                                "name": "get_current_user",
                                "description": "Get current user information",
                                "inputSchema": {"type": "object", "properties": {}}
                            },
                            {
                                "name": "health_check",
                                "description": "Check Redmine connection health",
                                "inputSchema": {"type": "object", "properties": {}}
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name in self.tools:
                    try:
                        result = self.tools[tool_name](**arguments)
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(result, indent=2)
                                    }
                                ]
                            }
                        }
                    except Exception as e:
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32000,
                                "message": str(e)
                            }
                        }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
        
        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",

                "id": self._ensure_valid_id(request.get("id")),

                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def run(self):
        """Run the STDIO server"""
        self.logger.info(f"Starting Redmine STDIO MCP Server for {self.redmine_url}")
        
        try:
            while True:
                # Read from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    response = await self.handle_request(request)
                    
                    # Write to stdout
                    print(json.dumps(response), flush=True)
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON received: {e}")
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing request: {e}")
                    continue
        
        except KeyboardInterrupt:
            self.logger.info("Server stopped by user")
        except Exception as e:
            self.logger.error(f"Server error: {e}")


def main():
    """Main entry point for STDIO server"""
    # Get configuration from environment
    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    redmine_api_key = os.environ.get('REDMINE_API_KEY')
    
    if not redmine_api_key:
        logging.error("REDMINE_API_KEY environment variable is required")
        sys.exit(1)
    
    # Create and run server
    server = RedmineSTDIOServer(redmine_url, redmine_api_key)
    asyncio.run(server.run())


if __name__ == '__main__':
    main()