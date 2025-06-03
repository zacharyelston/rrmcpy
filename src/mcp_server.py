"""
Redmine MCP Server with modular architecture and tool registry
"""
import sys
import os
import asyncio
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
        
        # Initialize the server components
        self.initialize()
    
    def initialize(self):
        """Initialize server configuration and components"""
        try:
            # Load configuration
            self.config = AppConfig.from_environment()
            
            # Setup logging
            self.logger = setup_logging(self.config.logging)
            self.logger.info("Starting Redmine MCP Server")
            self.logger.info(f"Server mode: {self.config.server.mode}")
            self.logger.info(f"Redmine URL: {self.config.redmine.url}")
            
            # Initialize FastMCP
            if FastMCP is None:
                raise ConfigurationError("FastMCP is not available - please install fastmcp package")
            self.mcp = FastMCP("Redmine MCP Server")
            
            # Initialize tool registry
            self.tool_registry = ToolRegistry(self.logger)
            
            # Initialize clients
            self._initialize_clients()
            
            # Initialize services
            self._initialize_services()
            
            # Register tools
            self._register_tools()
            
            self.logger.info("Server initialization completed successfully")
            
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
        
        # Register tools with FastMCP manually for each tool
        self._register_issue_tools()
        self._register_admin_tools()
        
        tool_count = len(self.tool_registry.list_tool_names())
        self.logger.info(f"Registered {tool_count} tools: {', '.join(self.tool_registry.list_tool_names())}")
    
    def _register_issue_tools(self):
        """Register issue management tools with FastMCP"""
        
        @self.mcp.tool("redmine-create-issue")
        async def create_issue(project_id: str, subject: str, description: str = None, 
                             tracker_id: int = None, status_id: int = None, 
                             priority_id: int = None, assigned_to_id: int = None):
            kwargs = {k: v for k, v in locals().items() if v is not None}
            tool = self.tool_registry.get_tool("CreateIssueTool")
            result = tool.safe_execute(**kwargs)
            import json
            return [{"type": "text", "text": json.dumps(result, indent=2)}]
        
        @self.mcp.tool("redmine-get-issue")
        async def get_issue(issue_id: int, include: list = None):
            kwargs = {k: v for k, v in locals().items() if v is not None}
            tool = self.tool_registry.get_tool("GetIssueTool")
            result = tool.safe_execute(**kwargs)
            import json
            return [{"type": "text", "text": json.dumps(result, indent=2)}]
        
        @self.mcp.tool("redmine-list-issues")
        async def list_issues(project_id: str = None, status_id: int = None, 
                            assigned_to_id: int = None, tracker_id: int = None,
                            limit: int = None, offset: int = None):
            kwargs = {k: v for k, v in locals().items() if v is not None}
            tool = self.tool_registry.get_tool("ListIssuesTool")
            result = tool.safe_execute(**kwargs)
            import json
            return [{"type": "text", "text": json.dumps(result, indent=2)}]
        
        @self.mcp.tool("redmine-update-issue")
        async def update_issue(issue_id: int, subject: str = None, description: str = None,
                             status_id: int = None, priority_id: int = None, 
                             assigned_to_id: int = None, notes: str = None):
            kwargs = {k: v for k, v in locals().items() if v is not None}
            tool = self.tool_registry.get_tool("UpdateIssueTool")
            result = tool.safe_execute(**kwargs)
            import json
            return [{"type": "text", "text": json.dumps(result, indent=2)}]
        
        @self.mcp.tool("redmine-delete-issue")
        async def delete_issue(issue_id: int):
            kwargs = {k: v for k, v in locals().items() if v is not None}
            tool = self.tool_registry.get_tool("DeleteIssueTool")
            result = tool.safe_execute(**kwargs)
            import json
            return [{"type": "text", "text": json.dumps(result, indent=2)}]
    
    def _register_admin_tools(self):
        """Register administrative tools with FastMCP"""
        
        @self.mcp.tool("redmine-health-check")
        async def health_check():
            tool = self.tool_registry.get_tool("HealthCheckTool")
            result = tool.safe_execute()
            import json
            return [{"type": "text", "text": json.dumps(result, indent=2)}]
        
        @self.mcp.tool("redmine-get-current-user")
        async def get_current_user():
            tool = self.tool_registry.get_tool("GetCurrentUserTool")
            result = tool.safe_execute()
            import json
            return [{"type": "text", "text": json.dumps(result, indent=2)}]
    
    async def run(self):
        """Run the MCP server"""
        try:
            self.logger.info(f"Starting Redmine MCP Server in {self.config.server.mode} mode...")
            
            # Handle different server modes
            if self.config.server.mode == "test":
                await self._run_test_mode()
                return
            
            # Perform health check for live/debug modes
            await self._perform_startup_health_check()
            
            # Run the server
            await self.mcp.run(transport=self.config.server.transport)
            
        except KeyboardInterrupt:
            self.logger.info("Server stopped by user")
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise
    
    async def _run_test_mode(self):
        """Run the server in test mode with comprehensive validation"""
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
            health_tool = self.tool_registry.get_tool("redmine-health-check")
            if health_tool:
                health_result = health_tool.safe_execute()
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
            user_tool = self.tool_registry.get_tool("redmine-get-current-user")
            if user_tool:
                user_result = user_tool.safe_execute()
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
    
    async def _perform_startup_health_check(self):
        """Perform startup health check"""
        self.logger.info("Performing startup health check...")
        
        try:
            health_tool = self.tool_registry.get_tool("redmine-health-check")
            if health_tool:
                result = health_tool.safe_execute()
                if result.get("success"):
                    self.logger.info("Health check passed - Redmine connection is healthy")
                else:
                    self.logger.warning(f"Health check warning: {result.get('error', 'Unknown error')}")
            else:
                self.logger.warning("Health check tool not found")
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            if self.config.server.mode == "live":
                raise ConfigurationError("Cannot start server - health check failed")


async def main():
    """Main entry point"""
    server = RedmineMCPServer()
    
    try:
        server.initialize()
        await server.run()
    except ConfigurationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if server.logger:
            server.logger.error(f"Fatal error: {e}")
        else:
            print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())