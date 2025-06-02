#!/usr/bin/env python3
"""
Test script to understand MCP response format
Run this and pipe to a file to see the actual MCP protocol messages
"""
import os
import sys
import json

# Simulate what an MCP server sends to stdout
def send_mcp_response(id, result):
    """Send a properly formatted MCP response"""
    response = {
        "jsonrpc": "2.0",
        "id": id,
        "result": result
    }
    # MCP uses newline-delimited JSON
    print(json.dumps(response))
    sys.stdout.flush()

def test_responses():
    """Test different response formats"""
    
    # Test 1: Simple dict response
    send_mcp_response(1, {
        "type": "dict",
        "data": {"key": "value", "number": 42}
    })
    
    # Test 2: List response
    send_mcp_response(2, {
        "type": "list",
        "data": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ]
    })
    
    # Test 3: Empty dict
    send_mcp_response(3, {})
    
    # Test 4: Complex nested response
    send_mcp_response(4, {
        "issue": {
            "id": 123,
            "project": {"id": 1, "name": "Test"},
            "subject": "Test Issue"
        }
    })

if __name__ == "__main__":
    # Don't use logging - it would interfere
    print("Testing MCP response formats...", file=sys.stderr)
    test_responses()
