#!/usr/bin/env python3
"""
Main entry point for the Redmine MCPServer
"""
import os
import logging
import sys
from mcp_server import RedmineMCPServer

if __name__ == "__main__":
    # Get configuration from environment variables
    # Use demo.redmine.org for testing in this environment
    redmine_url = os.environ.get("REDMINE_URL", "https://demo.redmine.org")
    redmine_api_key = os.environ.get("REDMINE_API_KEY", "af159c9b93c7c41a6b629de19b84f2d14e5854a4")
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
