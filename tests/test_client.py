#!/usr/bin/env python3
"""
Test client for the Redmine MCP Server
"""
import socket
import json
import sys

def send_mcp_request(host, port, method, path, data=None):
    """
    Send an MCP request to the server
    
    Args:
        host: Host to connect to
        port: Port to connect to
        method: HTTP method (GET, POST, PUT, DELETE)
        path: Path to request
        data: Optional data to send
        
    Returns:
        Response from the server
    """
    # Create a socket and connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    
    # Prepare the request
    request = {
        'method': method,
        'path': path,
        'data': data or {}
    }
    
    # Send the request
    s.send(json.dumps(request).encode('utf-8'))
    
    # Receive the response
    response = s.recv(4096).decode('utf-8')
    
    # Close the socket
    s.close()
    
    # Parse and return the response
    return json.loads(response)

if __name__ == "__main__":
    # Default parameters
    host = 'localhost'
    port = 5000
    method = 'GET'
    path = '/health'
    data = None
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        method = sys.argv[1]
    if len(sys.argv) > 2:
        path = sys.argv[2]
    if len(sys.argv) > 3:
        try:
            data = json.loads(sys.argv[3])
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON data: {sys.argv[3]}")
            sys.exit(1)
    
    # Send the request and print the response
    try:
        response = send_mcp_request(host, port, method, path, data)
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)