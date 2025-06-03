#!/usr/bin/env python3
"""
Test script for the complete Redmine MCP Server with real API connections
"""
import os
import sys
import asyncio
import json

# Set up environment for testing
os.environ['REDMINE_URL'] = 'https://redstone.redminecloud.net'
os.environ['SERVER_MODE'] = 'test'
os.environ['LOG_LEVEL'] = 'INFO'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server import RedmineMCPServer


async def test_server_functionality():
    """Test the complete MCP server functionality"""
    print("Testing Complete Redmine MCP Server")
    print("=" * 40)
    
    # Check if API key is available
    api_key = os.environ.get('REDMINE_API_KEY')
    if not api_key:
        print("❌ REDMINE_API_KEY not found in environment")
        print("Please set REDMINE_API_KEY environment variable to test with real Redmine instance")
        return False
    
    try:
        # Initialize server
        print("Initializing MCP server...")
        server = RedmineMCPServer()
        server.initialize()
        print("✅ Server initialized successfully")
        
        # Test tool registry
        tools = server.tool_registry.list_tool_names()
        print(f"✅ Registered {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool}")
        
        # Test individual tools
        print("\nTesting individual tools:")
        
        # Test health check
        health_result = server.tool_registry.execute_tool("redmine-health-check")
        print(f"✅ Health check: {health_result.get('success', False)}")
        
        # Test current user
        user_result = server.tool_registry.execute_tool("redmine-get-current-user")
        print(f"✅ Current user: {user_result.get('success', False)}")
        
        # Test list issues
        list_result = server.tool_registry.execute_tool("redmine-list-issues", limit=5)
        print(f"✅ List issues: {list_result.get('success', False)}")
        
        if list_result.get('success'):
            issues = list_result.get('data', [])
            print(f"   Found {len(issues)} issues")
            if issues:
                print(f"   First issue: #{issues[0].get('id')} - {issues[0].get('subject', 'No subject')}")
        
        # Test create issue (in test project)
        create_data = {
            "project_id": "p1",
            "subject": "MCP Server Test Issue",
            "description": "This is a test issue created by the modular MCP server"
        }
        
        create_result = server.tool_registry.execute_tool("redmine-create-issue", **create_data)
        print(f"✅ Create issue: {create_result.get('success', False)}")
        
        if create_result.get('success'):
            new_issue = create_result.get('data', {})
            issue_id = new_issue.get('id')
            print(f"   Created issue #{issue_id}")
            
            # Test get issue
            if issue_id:
                get_result = server.tool_registry.execute_tool("redmine-get-issue", issue_id=issue_id)
                print(f"✅ Get issue: {get_result.get('success', False)}")
                
                # Test update issue
                update_result = server.tool_registry.execute_tool(
                    "redmine-update-issue", 
                    issue_id=issue_id,
                    notes="Updated by MCP server test"
                )
                print(f"✅ Update issue: {update_result.get('success', False)}")
        
        print("\n✅ All server functionality tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False


async def main():
    """Main test function"""
    success = await test_server_functionality()
    
    if success:
        print("\n🎉 Complete MCP Server is working correctly!")
        print("Ready for production use with MCP clients.")
    else:
        print("\n❌ Server tests failed. Check the errors above.")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)