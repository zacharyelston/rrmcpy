"""
Redmine MCP Server with modular architecture and tool registry
"""
import sys
import os
import logging
import json
import subprocess
from typing import Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from fastmcp import FastMCP
except ImportError:
    # Fallback if fastmcp not available
    FastMCP = None

try:
    from .core import AppConfig, ConfigurationError, setup_logging, get_logger
    from .core.errors import RedmineAPIError, ToolExecutionError
    from .users import UserClient
    from .projects import ProjectClient
    from .issues import IssueClient
    from .groups import GroupClient
    from .versions import VersionClient
    from .roadmap import RoadmapClient
    from .tools import ToolRegistry, CreateIssueTool, GetIssueTool, ListIssuesTool, UpdateIssueTool, DeleteIssueTool
    from .tools import HealthCheckTool, GetCurrentUserTool
    from .services import IssueService
except ImportError:
    from src.core import AppConfig, ConfigurationError, setup_logging, get_logger
    from src.core.errors import RedmineAPIError, ToolExecutionError
    from src.users import UserClient
    from src.projects import ProjectClient
    from src.issues import IssueClient
    from src.groups import GroupClient
    from src.versions import VersionClient
    from src.roadmap import RoadmapClient
    from src.tools import ToolRegistry, CreateIssueTool, GetIssueTool, ListIssuesTool, UpdateIssueTool, DeleteIssueTool
    from src.tools import HealthCheckTool, GetCurrentUserTool
    from src.services import IssueService


class RedmineMCPServer:
    """Main MCP Server for Redmine with modular architecture"""
    
    def __init__(self):
        self.config: Optional[AppConfig] = None
        self.logger = None
        self.tool_registry = None
        self.mcp = None
        self.services = {}
        self.clients = {}
    
    def initialize(self):
        """Initialize server configuration and components"""
        try:
            # Load configuration
            self.config = AppConfig.from_environment()
            
            # Setup logging
            self.logger = setup_logging(self.config.logging)
            
            # Get git version info for debugging
            try:
                git_sha = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], 
                                                 stderr=subprocess.DEVNULL).decode('utf-8').strip()
            except (subprocess.SubprocessError, FileNotFoundError):
                # Handle case where git is not available (e.g., in Docker)
                git_sha = os.environ.get('GIT_COMMIT', 'unknown')
                
            self.logger.info(f"Starting Redmine MCP Server (version: {git_sha})")
            self.logger.info(f"Server mode: {self.config.server.mode}")
            self.logger.info(f"Redmine URL: {self.config.redmine.url}")
            
            # Initialize FastMCP
            if FastMCP is None:
                raise ConfigurationError("FastMCP is not available - please install fastmcp package")
            self.logger.debug(f"Using transport: {self.config.server.transport}")
            
            # Run the MCP server using FastMCP's run method
            # Following our fighting complexity philosophy:
            # 1. Use simple synchronous approach as primary pattern
            # 2. Handle container environments as needed
            try:
                # Plain and simple - let FastMCP handle everything
                self.mcp = FastMCP("Redmine MCP Server")
                self.mcp.run(self.config.server.transport)
            except RuntimeError as e:
                # Specific handling for container environments with event loop conflicts
                if "already running" in str(e).lower():
                    self.logger.warning("Event loop conflict detected - running in container compatibility mode")
                    self.logger.info("Server started successfully in container mode")
                    return
                else:
                    # Re-raise unexpected runtime errors
                    raise
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to initialize server: {e}")
                else:
                    print(f"Failed to initialize server: {e}", file=sys.stderr)
                raise ConfigurationError(f"Server initialization failed: {e}")
    
    def _initialize_clients(self):
        """Initialize API clients"""
        self.logger.debug("Initializing API clients")
        
        # Initialize issue client
        self.clients['issues'] = IssueClient(
            base_url=self.config.redmine.url,
            api_key=self.config.redmine.api_key,
            logger=get_logger('issue_client')
        )
        
        # Initialize roadmap client for version management
        from .roadmap import RoadmapClient
        self.clients['roadmap'] = RoadmapClient(
            base_url=self.config.redmine.url,
            api_key=self.config.redmine.api_key,
            logger=get_logger('roadmap_client')
        )
        
        # Add convenience properties for FastMCP tools
        self.issue_client = self.clients['issues']
        self.roadmap_client = self.clients['roadmap']
        
        self.logger.debug("API clients initialized")
    
    def _initialize_services(self):
        """Initialize service layer"""
        self.logger.debug("Initializing services")
        
        # Initialize issue service
        self.services['issues'] = IssueService(
            config=self.config.redmine,
            issue_client=self.clients['issues'],
            logger=get_logger('issue_service')
        )
        
        self.logger.debug("Services initialized")
    
    def _register_tools(self):
        """Register all tools with the tool registry"""
        self.logger.debug("Registering tools")
        
        issue_service = self.services['issues']
        
        # Register issue tools
        tools_to_register = [
            (CreateIssueTool, issue_service),
            (GetIssueTool, issue_service),
            (ListIssuesTool, issue_service),
            (UpdateIssueTool, issue_service),
            (DeleteIssueTool, issue_service),
            (HealthCheckTool, issue_service),
            (GetCurrentUserTool, issue_service)
        ]
        
        for tool_class, service in tools_to_register:
            try:
                self.tool_registry.register(tool_class, service)
            except Exception as e:
                self.logger.error(f"Failed to register tool {tool_class.__name__}: {e}")
                raise
        
        self._register_mcp_tools()
        
        tool_count = len(self.tool_registry.list_tool_names())
        self.logger.info(f"Registered {tool_count} tools: {', '.join(self.tool_registry.list_tool_names())}")
    
    def _register_mcp_tools(self):
        """Register all MCP tools"""
        self._register_issue_tools()
        self._register_admin_tools()  # For health check and current user
        self._register_version_tools()  # For version/roadmap management
    
    def _register_issue_tools(self):
        """Register issue management tools with FastMCP following standard patterns"""
        
        @self.mcp.tool("redmine-create-issue")
        async def create_issue(project_id: str, subject: str, description: str = None, 
                               tracker_id: int = None, status_id: int = None, 
                               priority_id: int = None, assigned_to_id: int = None):
            """Create a new issue in Redmine"""
            try:
                # Input validation - ensure required fields are present
                if not project_id:
                    error = "project_id is required"
                    self.logger.error(f"MCP tool redmine-create-issue failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                    
                if not subject:
                    error = "subject is required"
                    self.logger.error(f"MCP tool redmine-create-issue failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                
                # Build issue data
                issue_data = {"project_id": project_id, "subject": subject}
                if description: issue_data["description"] = description
                if tracker_id: issue_data["tracker_id"] = tracker_id
                if status_id: issue_data["status_id"] = status_id
                if priority_id: issue_data["priority_id"] = priority_id
                if assigned_to_id: issue_data["assigned_to_id"] = assigned_to_id
                
                # Log the incoming request
                self.logger.info(f"MCP tool redmine-create-issue called with data: {issue_data}")
                
                # Call the client to create the issue
                result = self.issue_client.create_issue(issue_data)
                
                # Handle error responses
                if isinstance(result, dict) and "error" in result:
                    self.logger.error(f"Issue client returned error: {result['error']}")
                    return json.dumps(result, indent=2)
                
                # Handle unexpected list response (should not happen with direct HTTPS URL)
                if isinstance(result, dict) and 'issues' in result:
                    self.logger.error(f"create_issue unexpectedly returned a list of issues instead of the created issue")
                    return json.dumps({"error": "Received list of issues instead of created issue. Please check REDMINE_URL configuration."}, indent=2)
                
                # Verify we have an issue object in the response
                if isinstance(result, dict) and 'issue' in result:
                    issue_id = result['issue'].get('id')
                    self.logger.info(f"Successfully created issue #{issue_id}: {result['issue'].get('subject')}")
                    return json.dumps(result, indent=2)
                
                # If we reach here, we got an unexpected response format
                self.logger.error(f"Unexpected response format from create_issue: {result}")
                return json.dumps({"error": "Unexpected response format", "response": result}, indent=2)
            except Exception as e:
                error_msg = f"Error creating issue: {str(e)}"
                self.logger.error(error_msg)
                if hasattr(e, '__traceback__'):
                    import traceback
                    tb = ''.join(traceback.format_tb(e.__traceback__))
                    self.logger.error(f"Traceback: {tb}")
                return json.dumps({"error": error_msg}, indent=2)
        
        @self.mcp.tool("redmine-get-issue")
        async def get_issue(issue_id: int, include: list = None):
            """Get a specific issue by ID"""
            try:
                result = self.issue_client.get_issue(issue_id, include)
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error getting issue {issue_id}: {str(e)}"
        
        @self.mcp.tool("redmine-list-issues")
        async def list_issues(project_id: str = None, status_id: int = None, 
                            assigned_to_id: int = None, tracker_id: int = None,
                            limit: int = None, offset: int = None):
            """List issues with optional filtering"""
            try:
                params = {}
                if project_id: params["project_id"] = project_id
                if status_id: params["status_id"] = status_id
                if assigned_to_id: params["assigned_to_id"] = assigned_to_id
                if tracker_id: params["tracker_id"] = tracker_id
                if limit: params["limit"] = limit
                if offset: params["offset"] = offset
                
                result = self.issue_client.get_issues(params)
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error listing issues: {str(e)}"
        
        @self.mcp.tool("redmine-update-issue")
        async def update_issue(issue_id: int, subject: str = None, description: str = None,
                             status_id: int = None, priority_id: int = None, 
                             assigned_to_id: int = None, notes: str = None):
            """Update an existing issue"""
            try:
                issue_data = {}
                if subject: issue_data["subject"] = subject
                if description: issue_data["description"] = description
                if status_id: issue_data["status_id"] = status_id
                if priority_id: issue_data["priority_id"] = priority_id
                if assigned_to_id: issue_data["assigned_to_id"] = assigned_to_id
                if notes: issue_data["notes"] = notes
                
                result = self.issue_client.update_issue(issue_id, issue_data)
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error updating issue {issue_id}: {str(e)}"
        
        @self.mcp.tool("redmine-delete-issue")
        async def delete_issue(issue_id: int):
            """Delete an issue"""
            try:
                result = self.issue_client.delete_issue(issue_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error deleting issue {issue_id}: {str(e)}"
    
    def _register_version_tools(self):
        """Register version management tools with FastMCP following standard patterns"""
        
        @self.mcp.tool("redmine-list-versions")
        async def list_versions(project_id: str):
            """List versions for a project"""
            if not project_id:
                return json.dumps({"error": "project_id is required"}, indent=2)
                
            try:
                result = self.roadmap_client.get_versions(project_id)
                self.logger.info(f"Listed versions for project {project_id}")
                return json.dumps(result, indent=2)
            except Exception as e:
                error_msg = f"Error listing versions: {str(e)}"
                self.logger.error(error_msg)
                return json.dumps({"error": error_msg}, indent=2)
        
        @self.mcp.tool("redmine-get-version")
        async def get_version(version_id: int):
            """Get a specific version by ID"""
            if not version_id:
                return json.dumps({"error": "version_id is required"}, indent=2)
                
            try:
                result = self.roadmap_client.get_version(version_id)
                self.logger.info(f"Retrieved version {version_id}")
                return json.dumps(result, indent=2)
            except Exception as e:
                error_msg = f"Error retrieving version: {str(e)}"
                self.logger.error(error_msg)
                return json.dumps({"error": error_msg}, indent=2)
        
        @self.mcp.tool("redmine-create-version")
        async def create_version(project_id: str, name: str, description: str = "", due_date: str = "", status: str = "open"):
            """Create a new version"""
            if not project_id or not name:
                return json.dumps({"error": "project_id and name are required"}, indent=2)
                
            try:
                # Use the convenience method for simplifying version creation
                result = self.roadmap_client.create_roadmap_version(
                    project_id=project_id,
                    name=name,
                    description=description,
                    due_date=due_date,
                    status=status
                )
                self.logger.info(f"Created version '{name}' for project {project_id}")
                return json.dumps(result, indent=2)
            except Exception as e:
                error_msg = f"Error creating version: {str(e)}"
                self.logger.error(error_msg)
                return json.dumps({"error": error_msg}, indent=2)
                
        @self.mcp.tool("redmine-update-version")
        async def update_version(version_id: int, name: str = "", description: str = "", due_date: str = "", status: str = ""):
            """Update an existing version"""
            if not version_id:
                return json.dumps({"error": "version_id is required"}, indent=2)
                
            # Build update data (only include non-empty fields)
            version_data = {}
            if name:
                version_data["name"] = name
            if description:
                version_data["description"] = description
            if due_date:
                version_data["due_date"] = due_date
            if status:
                version_data["status"] = status
                
            if not version_data:
                return json.dumps({"error": "At least one field to update must be provided"}, indent=2)
                
            try:
                result = self.roadmap_client.update_version(version_id, version_data)
                self.logger.info(f"Updated version {version_id}")
                return json.dumps(result, indent=2)
            except Exception as e:
                error_msg = f"Error updating version: {str(e)}"
                self.logger.error(error_msg)
                return json.dumps({"error": error_msg}, indent=2)
                
        @self.mcp.tool("redmine-delete-version")
        async def delete_version(version_id: int):
            """Delete a version"""
            if not version_id:
                return json.dumps({"error": "version_id is required"}, indent=2)
                
            try:
                result = self.roadmap_client.delete_version(version_id)
                self.logger.info(f"Deleted version {version_id}")
                return json.dumps({"success": True}, indent=2)
            except Exception as e:
                error_msg = f"Error deleting version: {str(e)}"
                self.logger.error(error_msg)
                return json.dumps({"error": error_msg}, indent=2)
                
        @self.mcp.tool("redmine-get-issues-by-version")
        async def get_issues_by_version(version_id: int):
            """Get all issues for a specific version"""
            if not version_id:
                return json.dumps({"error": "version_id is required"}, indent=2)
                
            try:
                result = self.roadmap_client.get_issues_by_version(version_id)
                self.logger.info(f"Retrieved issues for version {version_id}")
                return json.dumps(result, indent=2)
            except Exception as e:
                error_msg = f"Error retrieving issues by version: {str(e)}"
                self.logger.error(error_msg)
                return json.dumps({"error": error_msg}, indent=2)

    def _register_admin_tools(self):
        """Register administrative tools with FastMCP following standard patterns"""
        import platform
        import datetime
        import os
        
        @self.mcp.tool("redmine-health-check")
        async def health_check():
            """Check Redmine server health and connectivity"""
            try:
                result = self.issue_client.health_check()
                return json.dumps({"healthy": result, "status": "Connected" if result else "Disconnected"}, indent=2)
            except Exception as e:
                return f"Health check failed: {str(e)}"
        
        @self.mcp.tool("redmine-get-current-user")
        async def get_current_user():
            """Get current authenticated user information"""
            try:
                # Use a simple API call to get user info
                result = self.issue_client.make_request("GET", "/users/current.json")
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error getting current user: {str(e)}"
        
        @self.mcp.tool("redmine-version-info")
        async def version_info():
            """Get version information about the Redmine MCP server"""
            try:
                # Get basic version info
                info = {
                    "server": {
                        "name": "Redmine MCP Server",
                        "version": "0.1.0",  # Replace with actual version when available
                        "timestamp": datetime.datetime.now().isoformat(),
                        "python_version": platform.python_version(),
                        "platform": platform.platform()
                    },
                    "redmine": {
                        "url": self.config.redmine.url,
                        # Don't include API key for security
                        "api_key_configured": bool(self.config.redmine.api_key)
                    },
                    "configuration": {
                        "server_mode": self.config.server.mode
                    }
                }
                
                # Add git commit if available
                git_commit = os.environ.get("GIT_COMMIT")
                if git_commit:
                    info["server"]["git_commit"] = git_commit
                
                # Add health information
                try:
                    redmine_healthy = self.connection_manager.health_check()
                    info["redmine"]["connection_healthy"] = redmine_healthy
                except Exception as e:
                    info["redmine"]["connection_healthy"] = False
                    info["redmine"]["connection_error"] = str(e)
                
                # Add registered tools
                info["tools"] = self.mcp.list_tools() if hasattr(self, "mcp") else []
                
                self.logger.info(f"Provided version info")
                return json.dumps(info, indent=2)
            except Exception as e:
                error_msg = f"Error getting version info: {str(e)}"
                self.logger.error(error_msg)
                return json.dumps({"error": error_msg}, indent=2)
    
    def run(self, transport: Optional[str] = None):
        """Run the server in live mode
        
        Args:
            transport: Optional transport override (stdio, http, etc)
        """
        try:
            self.logger.info(f"Starting Redmine MCP Server in live mode...")
            
            # Use configured transport or fallback to stdio
            if not transport:
                transport = "stdio"
                
            if hasattr(self.config.server, 'transport') and self.config.server.transport:
                transport = self.config.server.transport
                
            self.logger.debug(f"Using transport: {transport}")
            
            await self.mcp.run(transport)
            
        except KeyboardInterrupt:
            self.logger.info("Server stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            sys.exit(1)
    
    def _run_test_mode_sync(self):
        """Run the server in test mode with comprehensive validation - synchronous version"""
        self.logger.info("Running server in test mode - performing validation tests...")
        
        test_results = []
        
        # Test 1: Configuration validation
        try:
            self.logger.info("Test 1: Configuration validation")
            config_test = {
                "test": "configuration_validation",
                "redmine_url": self.config.redmine.url,
                "has_api_key": bool(self.config.redmine.api_key),
                "server_mode": self.config.server.mode,
                "transport": self.config.server.transport,
                "status": "PASS"
            }
            test_results.append(config_test)
            self.logger.info("✓ Configuration validation: PASS")
        except Exception as e:
            test_results.append({"test": "configuration_validation", "status": "FAIL", "error": str(e)})
            self.logger.error(f"✗ Configuration validation: FAIL - {e}")
        
        # Test 2: Tool registry validation
        try:
            self.logger.info("Test 2: Tool registry validation")
            tool_names = self.tool_registry.list_tool_names()
            registry_test = {
                "test": "tool_registry_validation",
                "registered_tools": tool_names,
                "tool_count": len(tool_names),
                "status": "PASS"
            }
            test_results.append(registry_test)
            self.logger.info(f"✓ Tool registry validation: PASS - {len(tool_names)} tools registered")
        except Exception as e:
            test_results.append({"test": "tool_registry_validation", "status": "FAIL", "error": str(e)})
            self.logger.error(f"✗ Tool registry validation: FAIL - {e}")
        
        # Test 3: Health check
        try:
            self.logger.info("Test 3: Redmine connectivity health check")
            health_tool = self.tool_registry.get_tool("HealthCheckTool")
            if health_tool:
                health_result = health_tool.execute({})
                test_results.append({
                    "test": "redmine_health_check",
                    "result": health_result,
                    "status": "PASS"
                })
                self.logger.info("✓ Redmine health check: PASS")
            else:
                raise Exception("Health check tool not available")
        except Exception as e:
            test_results.append({"test": "redmine_health_check", "status": "FAIL", "error": str(e)})
            self.logger.error(f"✗ Redmine health check: FAIL - {e}")
        
        # Test 4: User authentication
        try:
            self.logger.info("Test 4: User authentication validation")
            user_tool = self.tool_registry.get_tool("GetCurrentUserTool")
            if user_tool:
                user_result = user_tool.execute({})
                test_results.append({
                    "test": "user_authentication",
                    "result": user_result,
                    "status": "PASS"
                })
                self.logger.info("✓ User authentication: PASS")
            else:
                raise Exception("User authentication tool not available")
        except Exception as e:
            test_results.append({"test": "user_authentication", "status": "FAIL", "error": str(e)})
            self.logger.error(f"✗ User authentication: FAIL - {e}")
        
        # Test Summary
        passed_tests = len([t for t in test_results if t.get("status") == "PASS"])
        total_tests = len(test_results)
        
        self.logger.info(f"\n=== TEST MODE SUMMARY ===")
        self.logger.info(f"Tests passed: {passed_tests}/{total_tests}")
        
        for result in test_results:
            status_symbol = "✓" if result.get("status") == "PASS" else "✗"
            self.logger.info(f"{status_symbol} {result['test']}: {result['status']}")
        
        if passed_tests == total_tests:
            self.logger.info("All tests passed! Server is ready for production.")
            return True
        else:
            self.logger.error(f"{total_tests - passed_tests} test(s) failed. Please resolve issues before production use.")
            return False
    
    def _perform_startup_health_check(self):
        """Perform startup health check - synchronous version"""
        self.logger.info("Performing startup health check...")
        
        try:
            health_tool = self.tool_registry.get_tool("HealthCheckTool")
            if health_tool:
                result = health_tool.execute({})
                if result.get("healthy"):
                    self.logger.info("Health check passed - Redmine connection is healthy")
                else:
                    self.logger.warning(f"Health check warning: {result.get('error', 'Unknown error')}")
            else:
                self.logger.warning("Health check tool not found")
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            if self.config.server.mode == "live":
                raise ConfigurationError("Cannot start server - health check failed")


def run_server():
    """Simplified entry point that avoids event loop conflicts"""
    server = RedmineMCPServer()
    
    try:
        # Initialize the server
        server.initialize()
        
        # Perform health check directly
        server._perform_startup_health_check()
        
        # Let FastMCP handle its own event loop
        server.logger.info(f"Starting Redmine MCP Server in {server.config.server.mode} mode...")
        server.mcp.run()
        
    except ConfigurationError as e:
        if server and server.logger:
            server.logger.error(f"Configuration error: {e}")
        else:
            print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if server and server.logger:
            server.logger.error(f"Fatal error: {e}")
        else:
            print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_server()