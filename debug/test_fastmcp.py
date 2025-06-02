#!/usr/bin/env python3
"""
Simple FastMCP test to verify response handling
"""
import os
import sys
import json
from typing import Dict, List, Any
from mcp.server import FastMCP
from pydantic import BaseModel, Field

# Simple test server
app = FastMCP("Test Server")

class TestRequest(BaseModel):
    name: str = Field(description="Test name")
    value: int = Field(description="Test value")

@app.tool()
def test_dict_response() -> Dict[str, Any]:
    """Test returning a dictionary"""
    return {
        "status": "success",
        "data": {
            "id": 123,
            "name": "Test Item",
            "nested": {
                "key": "value"
            }
        }
    }

@app.tool()
def test_list_response() -> List[Dict[str, Any]]:
    """Test returning a list"""
    return [
        {"id": 1, "name": "Item 1"},
        {"id": 2, "name": "Item 2"},
        {"id": 3, "name": "Item 3"}
    ]

@app.tool()
def test_with_request(request: TestRequest) -> Dict[str, Any]:
    """Test with request parameter"""
    return {
        "received": {
            "name": request.name,
            "value": request.value
        },
        "processed": True
    }

@app.tool()
def test_empty_dict() -> Dict[str, Any]:
    """Test returning empty dict"""
    return {}

@app.tool()
def test_empty_list() -> List[Dict[str, Any]]:
    """Test returning empty list"""
    return []

if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    
    print("Starting test FastMCP server...", file=sys.stderr)
    print("Available tools:", file=sys.stderr)
    for tool_name in app._tool_map.keys():
        print(f"  - {tool_name}", file=sys.stderr)
    
    app.run(transport="stdio")
