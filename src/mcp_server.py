"""
Redmine MCP Server with modular architecture and tool registry
"""
import sys
import os
import asyncio
from typing import Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from fastmcp import FastMCP
from core.config import AppConfig
from core.logging import setup_logging, get_logger
from core.errors import ConfigurationError
from services.issue_service import IssueService
from issues import IssueClient
from tools.registry import ToolRegistry
from tools.issue_tools import CreateIssueTool, GetIssueTool, ListIssuesTool, UpdateIssueTool, DeleteIssueTool
from tools.admin_tools import HealthCheckTool, GetCurrentUserTool


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
            self.logger.info("Starting Redmine MCP Server")
            self.logger.info(f"Server mode: {self.config.server.mode}")
            self.logger.info(f"Redmine URL: {self.config.redmine.url}")
            
            # Initialize FastMCP
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
        
        # Register tools with FastMCP
        for tool_name, tool_instance in self.tool_registry.get_all_tools().items():
            # Create tool handler with proper closure
            def make_tool_handler(tool_inst):
                @self.mcp.tool(tool_inst.name())
                async def tool_handler(**kwargs):
                    self.logger.debug(f"Executing tool: {tool_inst.name()}")
                    result = tool_inst.safe_execute(**kwargs)
                    return [{"type": "text", "text": str(result)}]
                return tool_handler
            
            make_tool_handler(tool_instance)
        
        tool_count = len(self.tool_registry.list_tool_names())
        self.logger.info(f"Registered {tool_count} tools: {', '.join(self.tool_registry.list_tool_names())}")
    
    async def run(self):
        """Run the MCP server"""
        try:
            self.logger.info("Starting Redmine MCP Server...")
            
            # Perform health check
            if self.config.server.mode != "test":
                await self._perform_startup_health_check()
            
            # Run the server
            await self.mcp.run(transport=self.config.server.transport)
            
        except KeyboardInterrupt:
            self.logger.info("Server stopped by user")
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise
    
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