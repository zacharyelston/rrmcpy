#!/usr/bin/env python3
"""
Test the MCP server tools directly
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.proper_mcp_server import RedmineMCPServer, IssueCreateRequest

def test_mcp_tools():
    """Test MCP tools directly"""
    redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
    api_key = os.environ.get("REDMINE_API_KEY", "")
    
    if not api_key:
        print("Set REDMINE_API_KEY!")
        return
    
    # Create server instance
    server = RedmineMCPServer(redmine_url, api_key)
    
    # Access the registered tools through the app
    # The tools are registered in _register_tools() but we need to call them directly
    
    # First, let's call health check
    print("\n=== Testing health check ===")
    # Since tools are registered as functions on the app, we need to find them
    # FastMCP stores tools in the app's tool registry
    
    # Actually, let me test the underlying client directly
    print("\n=== Testing underlying client ===")
    issue_data = {
        "project_id": "p1",
        "subject": "Test from MCP layer",
        "description": "Testing MCP layer"
    }
    
    result = server.redmine_client.create_issue(issue_data)
    print(f"Direct client result: {result}")
    
    # Now test through the MCP tool function
    print("\n=== Testing through MCP tool ===")
    request = IssueCreateRequest(
        project_id="p1",
        subject="Test from MCP tool function",
        description="Testing MCP tool function"
    )
    
    # The tools are methods that were decorated with @app.tool()
    # We need to find the actual function
    # In FastMCP, tools are stored in app._tools
    for tool_name, tool_info in server.app._tools.items():
        print(f"Found tool: {tool_name}")
    
    # Get the create issue tool
    if "redmine_create_issue" in server.app._tools:
        create_issue_tool = server.app._tools["redmine_create_issue"]["handler"]
        print(f"\nCalling create_issue tool...")
        try:
            result = create_issue_tool(request)
            print(f"Tool result: {result}")
        except Exception as e:
            print(f"Error calling tool: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_mcp_tools()
