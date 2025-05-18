#!/usr/bin/env python3
"""
Simple MCP client for testing the Redmine MCPServer
"""
import json
import sys
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def send_mcp_request(method, path, data=None):
    """
    Send an MCP request to the Redmine MCPServer
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        path: Path to request
        data: Optional data to send
        
    Returns:
        Response from the server
    """
    if data is None:
        data = {}
    
    # Create MCP request
    request = {
        "method": method,
        "path": path,
        "data": data
    }
    
    # Send request to server
    logger.debug(f"Sending MCP request: {request}")
    print(json.dumps(request), flush=True)
    
    # Read response from server
    response_line = sys.stdin.readline().strip()
    if not response_line:
        return {"status": "error", "message": "No response from server"}
    
    try:
        response = json.loads(response_line)
        logger.debug(f"Received MCP response: {response}")
        return response
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding response: {e}")
        return {"status": "error", "message": f"Invalid response: {response_line}"}

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MCP Client for Redmine MCP Server")
    parser.add_argument("--method", default="GET", choices=["GET", "POST", "PUT", "DELETE"],
                        help="HTTP method")
    parser.add_argument("--path", required=True, help="API path to request")
    parser.add_argument("--data", help="JSON data to send")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Parse JSON data if provided
    data = {}
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON data: {e}")
            sys.exit(1)
    
    # Send request
    response = send_mcp_request(args.method, args.path, data)
    
    # Print response
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main()