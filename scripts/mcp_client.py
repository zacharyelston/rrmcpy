#!/usr/bin/env python3
"""
Simple MCP client for testing the Redmine MCPServer
"""
import sys
import json
import subprocess
import argparse

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
    # Prepare the request
    request = {
        'method': method,
        'path': path,
        'data': data or {}
    }
    
    # Convert to JSON
    request_json = json.dumps(request)
    
    # Use subprocess to pipe the request to the MCPServer
    process = subprocess.Popen(
        ['python', 'main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send the request and get the response
    stdout, stderr = process.communicate(input=request_json)
    
    # Extract the JSON response from the output
    lines = stdout.splitlines()
    for line in lines:
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            pass
    
    # If no valid JSON was found, return the raw output
    return {'error': 'Invalid response', 'output': stdout, 'stderr': stderr}

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Simple MCP client for testing the Redmine MCPServer')
    parser.add_argument('method', choices=['GET', 'POST', 'PUT', 'DELETE'], help='HTTP method')
    parser.add_argument('path', help='Path to request')
    parser.add_argument('--data', help='JSON data to send')
    
    args = parser.parse_args()
    
    # Parse the data if provided
    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON data: {args.data}")
            sys.exit(1)
    
    # Send the request
    response = send_mcp_request(args.method, args.path, data)
    
    # Print the response
    print(json.dumps(response, indent=2))

if __name__ == '__main__':
    main()