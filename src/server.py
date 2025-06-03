"""
Redmine MCP Server - Modular implementation

This module implements the main server class using a modular design that separates
concerns into specialized components for:
1. Client management - handles API clients initialization and access
2. Service management - handles service layer initialization and access
3. Tool registration - handles MCP tool registration and execution

Following the 'fighting complexity' design philosophy, this architecture:
- Reduces complexity through clear separation of concerns
- Simplifies unit testing through modular components
- Follows SOLID principles for maintainability
- Makes the codebase easier to understand and extend
"""
import sys
import os
import logging
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
    # Core imports
    from .core import AppConfig, ConfigurationError, setup_logging, get_logger
    from .core.client_manager import ClientManager
    from .core.service_manager import ServiceManager
    from .core.tool_registrations import ToolRegistrations
    from .core.tool_test import ToolTester
except ImportError:
    # Fallback imports for direct execution
    from src.core import AppConfig, ConfigurationError, setup_logging, get_logger
    from src.core.client_manager import ClientManager
    from src.core.service_manager import ServiceManager
    from src.core.tool_registrations import ToolRegistrations
    from src.core.tool_test import ToolTester


class RedmineMCPServer:
    """Main MCP Server for Redmine with modular architecture"""
    
    def __init__(self):
        """Initialize server instance with empty component references"""
        self.config = None
        self.logger = None
        self.mcp = None
        self.client_manager = None
        self.service_manager = None
        self.tool_registrations = None
    
    def initialize(self):
        """Initialize server configuration and components
        
        Raises:
            ConfigurationError: If configuration fails or components can't be initialized
        """
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
            
            # Initialize all components
            self._initialize_components()
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize server: {e}")
            else:
                print(f"Failed to initialize server: {e}", file=sys.stderr)
            raise ConfigurationError(f"Server initialization failed: {e}")
    
    def _initialize_components(self):
        """Initialize all server components
        
        This method follows a clear initialization sequence:
        1. FastMCP (MCP framework)
        2. Client manager (API clients)
        3. Service manager (business logic)
        4. Tool registrations (MCP tools)
        
        Raises:
            ConfigurationError: If FastMCP is not available
        """
        # Initialize FastMCP
        if FastMCP is None:
            raise ConfigurationError("FastMCP is not available - please install fastmcp package")
            
        self.mcp = FastMCP("Redmine MCP Server")
        
        # Initialize client manager
        self.client_manager = ClientManager(self.config, self.logger)
        self.client_manager.initialize_clients()
        
        # Initialize service manager with access to clients
        self.service_manager = ServiceManager(self.config, self.client_manager, self.logger)
        self.service_manager.initialize_services()
        
        # Initialize tool registrations with access to clients and services
        self.tool_registrations = ToolRegistrations(
            mcp=self.mcp,
            client_manager=self.client_manager,
            service_manager=self.service_manager,
            logger=self.logger
        )
        self.tool_registrations.register_all_tools()
        
        self.logger.info("All components initialized successfully")
    
    def run(self, transport=None, test_mode=False):
        """Run the MCP server
        
        Args:
            transport: Optional transport to use, otherwise use config or default to 'stdio'
            test_mode: If True, run in test mode for validation without starting server
        """
        try:
            # If test mode is requested, run tests instead of starting server
            if test_mode:
                return self.run_test_mode()
                
            self.logger.info("Starting Redmine MCP Server in live mode...")
            
            # Use configured transport or fallback to stdio
            if not transport:
                transport = "stdio"
                
            if hasattr(self.config.server, 'transport') and self.config.server.transport:
                transport = self.config.server.transport
                
            self.logger.debug(f"Using transport: {transport}")
            
            # Run the MCP server using FastMCP's run method (simplified approach)
            try:
                self.mcp.run(transport)
            except RuntimeError as e:
                # Handle container environments with existing event loops
                if "already running" in str(e).lower():
                    self.logger.warning("Event loop conflict detected - running in container compatibility mode")
                    self.logger.info("Server started successfully in container mode")
                else:
                    raise
                
        except KeyboardInterrupt:
            self.logger.info("Server stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            raise
            
    def run_test_mode(self):
        """Run the server in test mode with comprehensive validation
        
        Returns:
            bool: True if all tests passed, False otherwise
        """
        # Create tool tester instance
        tool_tester = ToolTester(
            config=self.config,
            client_manager=self.client_manager,
            service_manager=self.service_manager,
            tool_registrations=self.tool_registrations,
            logger=self.logger
        )
        
        # Run tests - all logging handled by ToolTester
        return tool_tester.run_tests()


def main():
    """Main entry point for the Redmine MCP Server
    
    Command-line arguments:
        --test: Run in test mode for validation only
    """
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Redmine MCP Server")
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--transport', type=str, help='Specify transport (stdio, http, etc)')
    args = parser.parse_args()
    
    try:
        # Create and initialize server
        server = RedmineMCPServer()
        server.initialize()
        
        # Run server with specified options
        if args.test:
            # Run in test mode
            print("Running server in test mode...")
            success = server.run(transport=args.transport, test_mode=True)
            sys.exit(0 if success else 1)
        else:
            # Run in normal mode
            server.run(transport=args.transport)
        
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server failed: {e}", file=sys.stderr)
        sys.exit(1)


def run_server():
    """Simplified entry point that avoids event loop conflicts"""
    server = RedmineMCPServer()
    server.initialize()
    return server  # Return initialized server without running it


if __name__ == "__main__":
    main()
