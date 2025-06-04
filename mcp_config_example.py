#!/usr/bin/env python3
"""
Example configuration for running Redmine MCP Server directly with Python
Demonstrates environment setup, client configuration, and server startup
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the current directory to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """Configure environment variables for Redmine MCP Server"""
    
    # Required Redmine configuration
    os.environ['REDMINE_URL'] = 'https://your-redmine-instance.com'
    os.environ['REDMINE_API_KEY'] = 'your-api-key-here'
    
    # Optional server configuration
    os.environ['MCP_SERVER_MODE'] = 'live'  # Options: live, debug, test
    os.environ['MCP_LOG_LEVEL'] = 'INFO'    # Options: DEBUG, INFO, WARNING, ERROR
    
    # Optional Redmine connection settings
    os.environ['REDMINE_TIMEOUT'] = '30'
    os.environ['REDMINE_MAX_RETRIES'] = '3'
    
    print("Environment configured for Redmine MCP Server")

def validate_configuration():
    """Validate that required configuration is present"""
    required_vars = ['REDMINE_URL', 'REDMINE_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set the following:")
        for var in missing_vars:
            if var == 'REDMINE_URL':
                print(f"  {var}=https://your-redmine-instance.com")
            elif var == 'REDMINE_API_KEY':
                print(f"  {var}=your-api-key-here")
        return False
    
    print("Configuration validation passed")
    return True

async def run_fastmcp_server():
    """Run the FastMCP server (recommended approach)"""
    try:
        from fastmcp_server import main
        print("Starting FastMCP server...")
        await main()
    except ImportError:
        print("Error: fastmcp_server.py not found")
        print("Using fallback to complex server...")
        await run_complex_server()

async def run_complex_server():
    """Run the complex server implementation"""
    try:
        from src.mcp_server import RedmineMCPServer
        
        server = RedmineMCPServer()
        server.initialize()
        
        print("Starting Redmine MCP Server...")
        await server.run()
        
    except Exception as e:
        print(f"Server startup failed: {e}")
        raise

def setup_logging():
    """Configure logging for the MCP server"""
    log_level = os.getenv('MCP_LOG_LEVEL', 'INFO').upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('mcp_server.log')
        ]
    )
    
    print(f"Logging configured at {log_level} level")

async def main():
    """Main entry point for Python MCP server"""
    print("=== Redmine MCP Server Configuration ===")
    
    # Step 1: Setup environment
    setup_environment()
    
    # Step 2: Setup logging
    setup_logging()
    
    # Step 3: Validate configuration
    if not validate_configuration():
        sys.exit(1)
    
    # Step 4: Choose server implementation
    server_choice = os.getenv('MCP_SERVER_TYPE', 'fastmcp').lower()
    
    if server_choice == 'fastmcp':
        print("Using FastMCP implementation (recommended)")
        await run_fastmcp_server()
    else:
        print("Using complex server implementation")
        await run_complex_server()

def run_with_container_compatibility():
    """Run server with container environment compatibility"""
    try:
        # Check if there's already a running event loop
        loop = asyncio.get_running_loop()
        print("Detected existing event loop - using container compatibility mode")
        
        # Import nest_asyncio for nested loop support
        try:
            import nest_asyncio
            nest_asyncio.apply()
            task = loop.create_task(main())
            return task
        except ImportError:
            print("Installing nest_asyncio for container compatibility...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "nest_asyncio"])
            import nest_asyncio
            nest_asyncio.apply()
            task = loop.create_task(main())
            return task
            
    except RuntimeError:
        # No event loop running, we can start our own
        print("Starting new event loop for MCP server")
        return asyncio.run(main())

if __name__ == "__main__":
    print("""
=== Redmine MCP Server Python Configuration ===

Before running, please set your environment variables:

export REDMINE_URL="https://your-redmine-instance.com"
export REDMINE_API_KEY="your-api-key-here"

Optional settings:
export MCP_SERVER_MODE="live"          # live, debug, test
export MCP_LOG_LEVEL="INFO"            # DEBUG, INFO, WARNING, ERROR
export MCP_SERVER_TYPE="fastmcp"       # fastmcp, complex

Then run:
python mcp_config_example.py

Or use the configuration programmatically in your own script.
    """)
    
    # Check if environment is configured
    if not os.getenv('REDMINE_URL') or not os.getenv('REDMINE_API_KEY'):
        print("Please configure environment variables before running.")
        sys.exit(1)
    
    try:
        run_with_container_compatibility()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)