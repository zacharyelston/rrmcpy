#!/usr/bin/env python3
"""
Demo for using the MCP Client to interact with Redmine MCP Server
"""
import os
import sys
import time
import json
import random
import logging
from modules.mcp_client import MCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("MCPClientDemo")

def print_json(data):
    """Print JSON data in a readable format"""
    print(json.dumps(data, indent=2))

def demo_mcp_client():
    """Demo the MCP client functionality"""
    # Command to start the MCP server
    server_command = ["python", "main.py"]
    
    # Initialize the MCP client
    client = MCPClient(server_command, logger)
    
    try:
        # Start the server
        client.start_server()
        
        # Give the server time to start
        time.sleep(2)
        
        print("=== MCP Client Demo ===")
        
        # 1. Check server health
        print("\n1. Checking server health...")
        response = client.health_check()
        if response.get('status') == 200:
            print("Server is healthy!")
            print_json(response.get('data', {}))
        else:
            print("Server health check failed")
            print_json(response)
            return
        
        # 2. Get current user
        print("\n2. Getting current user...")
        response = client.get_current_user()
        if response.get('status') == 200:
            user = response.get('data', {}).get('user', {})
            print(f"Current user: {user.get('firstname')} {user.get('lastname')} ({user.get('login')})")
        else:
            print("Failed to get current user")
            print_json(response)
        
        # 3. Get projects
        print("\n3. Getting projects...")
        response = client.get_projects()
        if response.get('status') == 200:
            projects = response.get('data', {}).get('projects', [])
            print(f"Found {len(projects)} projects:")
            for project in projects:
                print(f"  - {project.get('name')} (ID: {project.get('id')}, Identifier: {project.get('identifier')})")
            
            # If no projects found, exit
            if not projects:
                print("No projects found, exiting demo")
                return
                
            # Use the first project for further operations
            test_project_id = projects[0].get('id')
            test_project_name = projects[0].get('name')
            print(f"\nUsing project '{test_project_name}' (ID: {test_project_id}) for demo")
        else:
            print("Failed to get projects")
            print_json(response)
            return
        
        # 4. Create a test issue
        print("\n4. Creating a test issue...")
        random_suffix = ''.join(random.choices('0123456789abcdef', k=6))
        issue_data = {
            "project_id": test_project_id,
            "subject": f"Test issue from MCP client {random_suffix}",
            "description": "This is a test issue created by the MCP client demo",
            "priority_id": 2  # Normal priority
        }
        response = client.create_issue(issue_data)
        if response.get('status') == 201:
            issue = response.get('data', {}).get('issue', {})
            issue_id = issue.get('id')
            print(f"Created issue #{issue_id}: {issue.get('subject')}")
        else:
            print("Failed to create issue")
            print_json(response)
            return
        
        # 5. Get the created issue
        print(f"\n5. Getting issue #{issue_id}...")
        response = client.get_issue(issue_id)
        if response.get('status') == 200:
            issue = response.get('data', {}).get('issue', {})
            print(f"Issue #{issue.get('id')}: {issue.get('subject')}")
            print(f"  - Status: {issue.get('status', {}).get('name')}")
            print(f"  - Created: {issue.get('created_on')}")
        else:
            print(f"Failed to get issue #{issue_id}")
            print_json(response)
        
        # 6. Update the issue
        print(f"\n6. Updating issue #{issue_id}...")
        update_data = {
            "notes": f"This is a note added by the MCP client demo at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        }
        response = client.update_issue(issue_id, update_data)
        if response.get('status') == 200:
            print(f"Updated issue #{issue_id} with a note")
        else:
            print(f"Failed to update issue #{issue_id}")
            print_json(response)
        
        # 7. Get project versions
        print(f"\n7. Getting versions for project {test_project_name}...")
        response = client.get_versions(test_project_id)
        if response.get('status') == 200:
            versions = response.get('data', {}).get('versions', [])
            print(f"Found {len(versions)} versions:")
            for version in versions:
                print(f"  - {version.get('name')} (ID: {version.get('id')}, Status: {version.get('status')})")
            
            # If versions found, tag the issue with the first version
            if versions:
                version_id = versions[0].get('id')
                version_name = versions[0].get('name')
                
                print(f"\n8. Tagging issue #{issue_id} with version '{version_name}'...")
                response = client.tag_issue_with_version(issue_id, version_id)
                if response.get('status') == 200:
                    print(f"Tagged issue #{issue_id} with version '{version_name}'")
                else:
                    print(f"Failed to tag issue #{issue_id} with version")
                    print_json(response)
        else:
            print(f"Failed to get versions for project {test_project_name}")
            print_json(response)
        
        # 9. Clean up (delete the test issue)
        print(f"\n9. Cleaning up (deleting issue #{issue_id})...")
        response = client.delete_issue(issue_id)
        if response.get('status') == 200:
            print(f"Deleted issue #{issue_id}")
        else:
            print(f"Failed to delete issue #{issue_id}")
            print_json(response)
        
        print("\nMCP Client Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in MCP client demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Stop the server
        client.stop_server()
        print("\nServer stopped.")

if __name__ == "__main__":
    demo_mcp_client()