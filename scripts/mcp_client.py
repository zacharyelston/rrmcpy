#!/usr/bin/env python3
"""
Simple MCP client for testing the modular Redmine MCPServer
"""
import sys
import json
import subprocess
import argparse
import os

def send_mcp_request(tool_name, arguments=None):
    """
    Send an MCP tool request to the Redmine MCPServer
    
    Args:
        tool_name: Name of the MCP tool to call (e.g., "redmine-health-check")
        arguments: Optional dictionary of tool arguments
        
    Returns:
        Response from the server
    """
    # Prepare the MCP tool call request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }
    
    # Convert to JSON
    request_json = json.dumps(request)
    
    # Use subprocess to pipe the request to the MCPServer
    process = subprocess.Popen(
        ['python', 'main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    
    # Send the request and get the response
    stdout, stderr = process.communicate(input=request_json)
    
    if process.returncode != 0:
        return {'error': 'Server error', 'stderr': stderr, 'stdout': stdout}
    
    # Extract the JSON response from the output
    lines = stdout.splitlines()
    for line in lines:
        try:
            response = json.loads(line)
            if "result" in response:
                return response["result"]
            elif "error" in response:
                return {"error": response["error"]}
        except json.JSONDecodeError:
            continue
    
    # If no valid JSON was found, return the raw output
    return {'error': 'Invalid response', 'output': stdout, 'stderr': stderr}

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Simple MCP client for testing the modular Redmine MCPServer')
    parser.add_argument('tool', help='MCP tool name (e.g., redmine-health-check, redmine-list-issues)')
    parser.add_argument('--args', help='JSON arguments for the tool')
    
    args = parser.parse_args()
    
    # Parse the arguments if provided
    arguments = None
    if args.args:
        try:
            arguments = json.loads(args.args)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON arguments: {args.args}")
            sys.exit(1)
    
    # Send the request
    response = send_mcp_request(args.tool, arguments)
    
    # Print the response
    print(json.dumps(response, indent=2))

if __name__ == '__main__':
    main()