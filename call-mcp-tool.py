#!/usr/bin/env python3
"""
MCP client to call a specific tool within the Redmine MCP Server
Used to test individual tools like redmine_health_check

This follows the MCP protocol for tool calls and should be run inside the container
"""
import argparse
import json
import logging
import os
import sys
import time

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("call-mcp-tool")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Call a specific tool in the Redmine MCP Server")
    parser.add_argument("tool_name", help="Name of the MCP tool to call (e.g., redmine_health_check)")
    parser.add_argument("--params", help="JSON string of parameters to pass to the tool", default="{}")
    parser.add_argument("--pretty", help="Pretty print the result", action="store_true")
    args = parser.parse_args()
    
    try:
        # Import the MCP server class
        from src.mcp_server import RedmineMCPServer
        
        # Get configuration from environment
        redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        redmine_api_key = os.environ.get('REDMINE_API_KEY')
        
        if not redmine_api_key:
            logger.error("REDMINE_API_KEY environment variable is required")
            return 1
        
        # Create server instance
        server = RedmineMCPServer(redmine_url, redmine_api_key)
        logger.info(f"Successfully created MCP Server instance")
        
        # Get the method to call
        tool_name = args.tool_name
        if not hasattr(server, tool_name):
            logger.error(f"Tool '{tool_name}' not found in MCP server")
            logger.info("Available tools:")
            for attr_name in dir(server):
                if attr_name.startswith("redmine_") and callable(getattr(server, attr_name)):
                    logger.info(f"  - {attr_name}")
            return 1
        
        # Parse parameters if provided
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON parameters: {args.params}")
            return 1
        
        # Call the tool method
        logger.info(f"Calling {tool_name} with params: {params}")
        method = getattr(server, tool_name)
        
        # Call with or without parameters based on parameter count
        if params:
            result = method(**params)
        else:
            result = method()
        
        # Parse and display result
        try:
            parsed_result = json.loads(result)
            if args.pretty:
                print(json.dumps(parsed_result, indent=2))
            else:
                print(result)
            logger.info(f"Successfully called {tool_name}")
            return 0
        except json.JSONDecodeError:
            logger.error(f"Tool returned invalid JSON: {result}")
            print(result)
            return 1
            
    except Exception as e:
        logger.error(f"Error calling tool: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
