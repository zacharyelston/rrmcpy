#!/usr/bin/env python3
"""
Test MCP server issue creation to debug the empty response
"""
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.proper_mcp_server import RedmineMCPServer
from src.proper_mcp_server import IssueCreateRequest

def test_mcp_server():
    """Test the MCP server directly"""
    print("\n=== Testing MCP Server Direct ===")
    
    redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
    api_key = os.environ.get("REDMINE_API_KEY", "")
    
    if not api_key:
        print("REDMINE_API_KEY not set!")
        return
    
    # Create server instance
    server = RedmineMCPServer(redmine_url, api_key)
    
    # Test the tool directly
    print("\nTesting redmine_create_issue tool...")
    
    # Create request
    request = IssueCreateRequest(
        project_id="p1",
        subject="Test via MCP direct",
        description="Testing MCP server directly"
    )
    
    # Find the tool
    for tool_name, tool_func in server.app._tool_map.items():
        if tool_name == "redmine_create_issue":
            print(f"Found tool: {tool_name}")
            try:
                result = tool_func(request)
                print(f"Tool result type: {type(result)}")
                print(f"Tool result: {json.dumps(result, indent=2)}")
            except Exception as e:
                print(f"Error calling tool: {e}")
                import traceback
                traceback.print_exc()
            break

if __name__ == "__main__":
    # Set environment variables
    os.environ["REDMINE_URL"] = "https://redstone.redminecloud.net"
    os.environ["REDMINE_API_KEY"] = "dc0b97c2830924b6653b4325f155b1caeaad983d"
    
    test_mcp_server()
