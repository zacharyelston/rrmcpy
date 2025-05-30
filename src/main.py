#!/usr/bin/env python3
"""
Main entry point for Redmine MCP Server
This file can be run as a module (python -m src.main)
"""
import asyncio
import os
import sys
import logging

from src.stdio_server import RedmineSTDIOServer


def main():
    """Main entry point following proper FastMCP patterns"""
    # Configure logging to stderr only (critical fix)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr  # Fixed: was sys.stdout which interferes with MCP protocol
    )
    
    logger = logging.getLogger(__name__)
    
    # Get configuration from environment
    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    redmine_api_key = os.environ.get('REDMINE_API_KEY')
    server_mode = os.environ.get('SERVER_MODE', 'live')
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is required")
        sys.exit(1)
    
    # Handle test mode
    if server_mode.lower() == 'test':
        logger.info("Running in test mode")
        from tests.test_redstone import TestRedstoneConnection
        import unittest
        
        # Run basic connectivity test
        suite = unittest.TestLoader().loadTestsFromTestCase(TestRedstoneConnection)
        runner = unittest.TextTestRunner(stream=sys.stderr, verbosity=2)
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            logger.error("Tests failed, not starting server")
            sys.exit(1)
        
        logger.info("Tests passed, starting server")
    
    # Create and run the STDIO server
    server = RedmineSTDIOServer(redmine_url, redmine_api_key)
    
    try:
        # Run the STDIO server
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()