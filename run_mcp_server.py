#!/usr/bin/env python3
"""
Main entry point for the Redmine MCPServer
Run this script to start the MCPServer
"""
import os
import sys
import logging
import argparse

# Add the src directory to Python path to find our modules
sys.path.append('.')

from redmine_mcpserver.fixed_mcp_server import RedmineMCPServer

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the MCP server"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the Redmine MCP Server')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--project', type=str, default='p1', help='Test project identifier')
    args = parser.parse_args()
    
    # Get environment variables or use defaults
    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    redmine_api_key = os.environ.get('REDMINE_API_KEY', '')
    server_mode = 'test' if args.test else os.environ.get('SERVER_MODE', 'live')
    
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
    
    if server_mode == 'test':
        test_project = os.environ.get('TEST_PROJECT', args.project)
        logger.info(f"Test mode enabled - will run tests against project: {test_project}")
        # Import the test suite only if needed
        from tests.test_suite import RedmineTestSuite
        test_suite = RedmineTestSuite()
        test_suite.run_all_tests()
        test_suite.print_results()
        sys.exit(0)
    else:
        # Run the server in live mode
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