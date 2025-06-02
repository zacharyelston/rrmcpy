#!/usr/bin/env python3
"""
Direct test of the Redmine client response handling
"""
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.redmine_client import RedmineClient
from src.proper_mcp_server import IssueCreateRequest
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

def test_response_handling():
    """Test how responses are handled at different levels"""
    
    # Set up client
    redmine_url = "https://redstone.redminecloud.net"
    api_key = "dc0b97c2830924b6653b4325f155b1caeaad983d"
    
    client = RedmineClient(redmine_url, api_key)
    
    print("\n=== Testing List Issues Response ===", file=sys.stderr)
    
    # Test list issues
    params = {"limit": 3, "project_id": "p1"}
    result = client.get_issues(params)
    
    print(f"Result type: {type(result)}", file=sys.stderr)
    print(f"Result keys: {result.keys()}", file=sys.stderr)
    
    issues = result.get('issues', [])
    print(f"Issues type: {type(issues)}", file=sys.stderr)
    print(f"Issues length: {len(issues)}", file=sys.stderr)
    
    # Try different serialization approaches
    print("\n=== Testing Serialization ===", file=sys.stderr)
    
    # Direct return
    print(f"Direct issues: {issues}", file=sys.stderr)
    
    # JSON round-trip
    json_str = json.dumps(issues)
    print(f"JSON string length: {len(json_str)}", file=sys.stderr)
    issues_from_json = json.loads(json_str)
    print(f"Issues from JSON type: {type(issues_from_json)}", file=sys.stderr)
    
    # Test what FastMCP might see
    print("\n=== Testing FastMCP-like handling ===", file=sys.stderr)
    
    # Simulate what the tool function returns
    def simulate_list_tool():
        result = client.get_issues(params)
        return result.get('issues', [])
    
    tool_result = simulate_list_tool()
    print(f"Tool result type: {type(tool_result)}", file=sys.stderr)
    print(f"Tool result: {tool_result}", file=sys.stderr)
    
    print("\n=== Testing Create Issue Response ===", file=sys.stderr)
    
    # Don't actually create an issue, just test with cached response
    mock_create_response = {
        "issue": {
            "id": 999,
            "project": {"id": 1, "name": "p1"},
            "subject": "Test Issue",
            "description": "Test Description"
        }
    }
    
    issue_data = mock_create_response.get('issue', {})
    print(f"Issue data type: {type(issue_data)}", file=sys.stderr)
    print(f"Issue data: {issue_data}", file=sys.stderr)
    
    # Test empty dict
    empty_response = {}
    issue_from_empty = empty_response.get('issue', {})
    print(f"\nEmpty response issue: {issue_from_empty}", file=sys.stderr)
    print(f"Empty response issue type: {type(issue_from_empty)}", file=sys.stderr)

if __name__ == "__main__":
    test_response_handling()
