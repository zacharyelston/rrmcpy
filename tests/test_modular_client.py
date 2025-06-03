#!/usr/bin/env python3
"""
Test client for the modular Redmine MCP Server
"""
import os
import sys
import json
import time
import random
# Add the parent directory to path so we can import src modules
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.users import UserClient
from src.projects import ProjectClient
from src.issues import IssueClient
from src.groups import GroupClient
from src.versions import VersionClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("MCPClientTest")

def main():
    """Test the modular Redmine client directly"""
    print("Starting direct Redmine client test...")
    
    # Get configuration from environment
    redmine_url = os.environ.get("REDMINE_URL", "https://demo.redmine.org")
    redmine_api_key = os.environ.get("REDMINE_API_KEY", "")
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is not set")
        sys.exit(1)
    
    # Initialize client
    logger.info(f"Connecting to Redmine at {redmine_url}")
    user_client = UserClient(redmine_url, redmine_api_key, logger)
    project_client = ProjectClient(redmine_url, redmine_api_key, logger)
    issue_client = IssueClient(redmine_url, redmine_api_key, logger)
    group_client = GroupClient(redmine_url, redmine_api_key, logger)
    version_client = VersionClient(redmine_url, redmine_api_key, logger)
    
    try:
        # Test 1: Check connection and get current user
        print("\n=== Test 1: Current User ===")
        result = user_client.get_current_user()
        user = result['user']
        print(f"Connected as: {user['firstname']} {user['lastname']} ({user['login']})")
        print(f"Email: {user['mail']}")
        print(f"Admin: {'Yes' if user['admin'] else 'No'}")
        
        # Test 2: Get projects
        print("\n=== Test 2: Projects ===")
        result = project_client.get_projects()
        projects = result['projects']
        print(f"Found {len(projects)} projects:")
        for project in projects:
            print(f"  - {project['name']} (ID: {project['id']}, Identifier: {project['identifier']})")
        
        # Find p1 test project
        test_project_id = None
        for project in projects:
            if project['identifier'] == 'p1':
                test_project_id = project['id']
                break
        
        if not test_project_id:
            print("Test project 'p1' not found, using first project")
            test_project_id = projects[0]['id']
            
        print(f"Using project ID {test_project_id} for testing")
        
        # Test 3: Create issue in test project
        print("\n=== Test 3: Create Issue ===")
        random_suffix = ''.join(random.choices('0123456789abcdef', k=6))
        issue_data = {
            "project_id": test_project_id,
            "subject": f"Test issue from modular client {random_suffix}",
            "description": "This is a test issue created by the modular client",
            "priority_id": 2  # Normal priority
        }
        result = issue_client.create_issue(issue_data)
        new_issue = result['issue']
        new_issue_id = new_issue['id']
        print(f"Created issue #{new_issue_id}: {new_issue['subject']}")
        
        # Test 4: Get issue details
        print("\n=== Test 4: Get Issue ===")
        result = issue_client.get_issue(new_issue_id)
        issue = result['issue']
        print(f"Issue #{issue['id']}: {issue['subject']}")
        print(f"Status: {issue['status']['name']}")
        print(f"Priority: {issue['priority']['name']}")
        
        # Test 5: Update issue
        print("\n=== Test 5: Update Issue ===")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        update_data = {
            "notes": f"This is a test note from the modular client\nTimestamp: {timestamp}"
        }
        issue_client.update_issue(new_issue_id, update_data)
        print(f"Updated issue #{new_issue_id} with a note")
        
        # Test 6: Get project details
        print("\n=== Test 6: Project Details ===")
        result = project_client.get_project(test_project_id)
        project = result['project']
        print(f"Project: {project['name']}")
        print(f"Description: {project['description'] or '(None)'}")
        print(f"Created: {project['created_on']}")
        
        # Test 7: Versions
        print("\n=== Test 7: Versions ===")
        try:
            result = version_client.get_versions(test_project_id)
            versions = result.get('versions', [])
            print(f"Found {len(versions)} versions:")
            for version in versions:
                print(f"  - {version['name']} (Status: {version['status']})")
            
            # Create a test version
            version_data = {
                "project_id": test_project_id,
                "name": f"Test Version {random_suffix}",
                "description": "Test version created by modular client",
                "status": "open"
            }
            result = version_client.create_version(version_data)
            new_version = result['version']
            new_version_id = new_version['id']
            print(f"Created version #{new_version_id}: {new_version['name']}")
            
            # Clean up the test version
            version_client.delete_version(new_version_id)
            print(f"Deleted test version #{new_version_id}")
        except Exception as e:
            print(f"Version tests failed: {e}")
        
        # Clean up
        print("\n=== Cleaning Up ===")
        issue_client.delete_issue(new_issue_id)
        print(f"Deleted test issue #{new_issue_id}")
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"Error in test client: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Test client complete.")

if __name__ == "__main__":
    main()