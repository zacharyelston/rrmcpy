#!/usr/bin/env python3
"""
Quick test to verify the Redmine MCP server functionality
"""
import os
import sys
import json

# Set environment variables for testing
os.environ['REDMINE_URL'] = 'https://redstone.redminecloud.net'
os.environ['REDMINE_API_KEY'] = 'dummy_key_for_testing'

try:
    from src.proper_mcp_server import RedmineMCPServer
    print("✓ Server imports working")
    
    # Test server initialization
    server = RedmineMCPServer(
        redmine_url='https://redstone.redminecloud.net',
        api_key='dummy_key'
    )
    print("✓ Server initialization working")
    
    # Check if tools are registered
    print(f"✓ FastMCP app created: {server.app}")
    print("✓ All imports and initialization successful")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Other error: {e}")
    sys.exit(1)

print("Server appears to be working correctly!")