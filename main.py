#!/usr/bin/env python3
"""
Main entry point for the Redmine MCPServer
"""
import os
import logging
import sys
import time
from mcp_server import RedmineMCPServer

def run_server():
    """Run the MCP server in regular mode"""
    # Get configuration from environment variables
    redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
    redmine_api_key = os.environ.get("REDMINE_API_KEY", "")
    server_mode = os.environ.get("SERVER_MODE", "live")
    log_level_str = os.environ.get("LOG_LEVEL", "debug").upper()
    
    # Set up logging
    log_level = getattr(logging, log_level_str, logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    
    logger = logging.getLogger("RedmineMCPServer")
    logger.info(f"Starting Redmine MCPServer with URL: {redmine_url}")
    logger.info(f"Server mode: {server_mode}")
    logger.info(f"Log level: {log_level_str}")
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable must be set")
        sys.exit(1)
    
    # Create and start the server
    server = RedmineMCPServer(
        redmine_url=redmine_url,
        api_key=redmine_api_key,
        server_mode=server_mode,
        logger=logger
    )
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested, stopping...")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)
    finally:
        server.stop()

def run_test_suite():
    """Run the automated test suite"""
    from test_suite import RedmineTestSuite
    
    # Get configuration
    test_project = os.environ.get("TEST_PROJECT", "p1")
    logger = logging.getLogger("TestRunner")
    logger.info(f"Running test suite against project {test_project}")
    
    # Run tests and print results
    start_time = time.time()
    test_suite = RedmineTestSuite()
    test_suite.run_all_tests()
    duration = time.time() - start_time
    
    logger.info(f"Test suite completed in {duration:.2f} seconds")
    
    # If tests passed, start the server in regular mode
    if test_suite.results["failed"] == 0:
        logger.info("All tests passed, starting server in regular mode...")
        return True
    else:
        logger.error(f"{test_suite.results['failed']} tests failed, not starting server")
        return False

if __name__ == "__main__":
    # Get configuration from environment variables
    server_mode = os.environ.get("SERVER_MODE", "live")
    test_project = os.environ.get("TEST_PROJECT", "")
    
    # Set up logging
    log_level_str = os.environ.get("LOG_LEVEL", "debug").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    
    logger = logging.getLogger("Main")
    
    # Run in test mode if SERVER_MODE is test and TEST_PROJECT is specified
    if server_mode.lower() == "test" and test_project:
        logger.info(f"Starting in TEST mode with project: {test_project}")
        tests_passed = run_test_suite()
        
        # Only proceed to server if tests pass
        if tests_passed:
            run_server()
    else:
        # Regular server mode
        run_server()
