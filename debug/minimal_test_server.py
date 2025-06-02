#!/usr/bin/env python3
"""
Minimal test server to debug MCP response issues
"""
from fastmcp import FastMCP

mcp = FastMCP("Debug Test Server")

@mcp.tool()
def test_dict() -> dict:
    """Returns a simple dict"""
    return {"status": "success", "value": 42}

@mcp.tool()
def test_list() -> list:
    """Returns a simple list"""
    return [{"id": 1}, {"id": 2}, {"id": 3}]

@mcp.tool()
def test_string() -> str:
    """Returns a simple string"""
    return "Hello from test server!"

@mcp.tool()
def test_empty() -> dict:
    """Returns an empty dict"""
    return {}

if __name__ == "__main__":
    print("Starting debug test server...")
    mcp.run()
