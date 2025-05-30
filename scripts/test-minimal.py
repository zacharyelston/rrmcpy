#!/usr/bin/env python3
"""
Minimal test script to verify Docker container functionality
"""
import os
import sys
sys.path.append('.')

from src.proper_mcp_server import RedmineMCPServer

def main():
    # Get environment variables
    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    redmine_api_key = os.environ.get('REDMINE_API_KEY')
    
    if not redmine_api_key:
        print("Error: REDMINE_API_KEY environment variable not set")
        sys.exit(1)
    
    print(f"Testing connection to: {redmine_url}")
    
    try:
        # Initialize server
        server = RedmineMCPServer(redmine_url, redmine_api_key)
        print("✓ FastMCP server initialized")
        
        # Test health check
        health = server.redmine_client.health_check()
        print(f"✓ Health check: {'PASS' if health else 'FAIL'}")
        
        if health:
            # Test basic operations
            user_result = server.redmine_client.get_current_user()
            if not user_result.get('error'):
                user = user_result.get('user', {})
                print(f"✓ Current user: {user.get('firstname', '')} {user.get('lastname', '')}")
            
            projects_result = server.redmine_client.get_projects()
            if not projects_result.get('error'):
                projects = projects_result.get('projects', [])
                print(f"✓ Projects accessible: {len(projects)}")
            
            print("Docker container test: SUCCESS")
        else:
            print("Docker container test: FAILED - health check failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"Docker container test: FAILED - {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()