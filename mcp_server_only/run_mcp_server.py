#!/usr/bin/env python3
"""
Main entry point for the Redmine MCPServer
Run this script to start the MCPServer
"""
import os
import sys
import logging
from src.fixed_mcp_server import RedmineMCPServer

def main():
    """Main entry point for the MCP server"""
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Get environment variables or use defaults
    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    redmine_api_key = os.environ.get('REDMINE_API_KEY', '')
    server_mode = os.environ.get('SERVER_MODE', 'live')
    
    # Configure logging level
    log_level = os.environ.get('LOG_LEVEL', 'debug').upper()
    numeric_level = getattr(logging, log_level, logging.DEBUG)
    logger.setLevel(numeric_level)
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is required")
        sys.exit(1)
    
    # Initialize and start the server
    logger.info(f"Starting Redmine MCP Server in {server_mode} mode")
    logger.info(f"Connecting to Redmine at {redmine_url}")
    
    # Run the server in live mode
    logger.info("Starting Redmine MCP Server using STDIO")
    server = RedmineMCPServer(redmine_url, redmine_api_key, server_mode, logger)
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        server.stop()
    except Exception as e:
        logger.error(f"Server error: {e}")
        server.stop()
        sys.exit(1)

if __name__ == '__main__':
    main()