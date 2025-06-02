#!/usr/bin/env python3
"""
Test to understand FastMCP response handling
"""
import os
import sys
import json
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastmcp import FastMCP
from fastmcp.tools.tool import _convert_to_content
from mcp.types import TextContent

async def test_response_conversion():
    """Test how FastMCP converts different response types"""
    
    print("\n=== Testing FastMCP Response Conversion ===\n")
    
    # Test 1: Dict response
    dict_result = {"id": 123, "name": "Test Issue", "status": "New"}
    content = _convert_to_content(dict_result)
    print(f"Dict result: {dict_result}")
    print(f"Converted content type: {type(content)}")
    print(f"Content: {content}")
    print(f"Content[0].text: {content[0].text if content else 'No content'}")
    print()
    
    # Test 2: List response
    list_result = [
        {"id": 1, "name": "Issue 1"},
        {"id": 2, "name": "Issue 2"}
    ]
    content = _convert_to_content(list_result)
    print(f"List result: {list_result}")
    print(f"Converted content type: {type(content)}")
    print(f"Content: {content}")
    print(f"Content[0].text: {content[0].text if content else 'No content'}")
    print()
    
    # Test 3: String response
    str_result = "Simple string response"
    content = _convert_to_content(str_result)
    print(f"String result: {str_result}")
    print(f"Converted content type: {type(content)}")
    print(f"Content: {content}")
    print()
    
    # Test 4: Empty dict
    empty_dict = {}
    content = _convert_to_content(empty_dict)
    print(f"Empty dict result: {empty_dict}")
    print(f"Converted content type: {type(content)}")
    print(f"Content: {content}")
    print(f"Content[0].text: {content[0].text if content else 'No content'}")
    print()
    
    # Test 5: None
    none_result = None
    content = _convert_to_content(none_result)
    print(f"None result: {none_result}")
    print(f"Converted content type: {type(content)}")
    print(f"Content: {content}")
    print()
    
    # Now test with a real FastMCP server
    print("\n=== Testing with FastMCP Server ===\n")
    
    mcp = FastMCP("Test Server")
    
    @mcp.tool()
    def return_dict() -> dict:
        """Returns a dict"""
        return {"status": "success", "data": {"id": 42, "name": "Test"}}
    
    @mcp.tool()
    def return_list() -> list:
        """Returns a list"""
        return [{"id": 1}, {"id": 2}, {"id": 3}]
    
    @mcp.tool()
    def return_empty_dict() -> dict:
        """Returns an empty dict"""
        return {}
    
    # Simulate tool calls
    print("Testing return_dict tool:")
    result = await mcp._mcp_call_tool("return_dict", {})
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    if result and hasattr(result[0], 'text'):
        print(f"Result text: {result[0].text}")
    print()
    
    print("Testing return_list tool:")
    result = await mcp._mcp_call_tool("return_list", {})
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    if result and hasattr(result[0], 'text'):
        print(f"Result text: {result[0].text}")
    print()
    
    print("Testing return_empty_dict tool:")
    result = await mcp._mcp_call_tool("return_empty_dict", {})
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    if result and hasattr(result[0], 'text'):
        print(f"Result text: {result[0].text}")
    print()

if __name__ == "__main__":
    asyncio.run(test_response_conversion())
