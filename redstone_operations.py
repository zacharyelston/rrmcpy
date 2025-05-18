#!/usr/bin/env python3
"""
Redstone Redmine API Operations
Demonstrates various operations with the Redstone Redmine API
"""
import os
import logging
import json
import sys
import time
from redmine_api import RedmineAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("RedstoneOperations")

# Helper function to pretty print JSON
def print_json(data):
    print(json.dumps(data, indent=2))

def main():
    # Get API key from environment
    redmine_url = "https://redstone.redminecloud.net"
    redmine_api_key = os.environ.get("REDMINE_API_KEY")

    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is not set")
        sys.exit(1)

    # Initialize Redmine API client
    api = RedmineAPI(redmine_url, redmine_api_key, logger)
    
    print(f"Connected to Redstone Redmine at {redmine_url}")
    
    # Operation 1: Get current user
    print("\n=== Operation 1: Get Current User ===")
    try:
        result = api.get_current_user()
        print_json(result)
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
    
    # Operation 2: List projects
    print("\n=== Operation 2: List Projects ===")
    try:
        result = api.get_projects()
        print_json(result)
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
    
    # Operation 3: List issues
    print("\n=== Operation 3: List Issues ===")
    try:
        result = api.get_issues()
        print_json(result)
    except Exception as e:
        logger.error(f"Error listing issues: {e}")
    
    # Operation 4: Create a test issue in the first project
    print("\n=== Operation 4: Create Test Issue ===")
    try:
        # Get the first project
        projects = api.get_projects().get('projects', [])
        if projects:
            project_id = projects[0]['id']
            issue_data = {
                "project_id": project_id,
                "subject": f"Test issue created at {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "description": "This is a test issue created by the Redstone Operations script.",
                "priority_id": 2,  # Normal priority
                "tracker_id": 1    # Bug tracker
            }
            result = api.create_issue(issue_data)
            print_json(result)
            
            # Store the issue ID for the next operation
            issue_id = result.get('issue', {}).get('id')
            if issue_id:
                # Operation 5: Get issue details
                print(f"\n=== Operation 5: Get Issue Details (ID: {issue_id}) ===")
                try:
                    result = api.get_issue(issue_id)
                    print_json(result)
                except Exception as e:
                    logger.error(f"Error getting issue details: {e}")
                
                # Operation 6: Update the issue
                print(f"\n=== Operation 6: Update Issue (ID: {issue_id}) ===")
                try:
                    update_data = {
                        "notes": "This issue was updated by the Redstone Operations script."
                    }
                    result = api.update_issue(issue_id, update_data)
                    # Get the updated issue
                    result = api.get_issue(issue_id)
                    print_json(result)
                except Exception as e:
                    logger.error(f"Error updating issue: {e}")
        else:
            logger.warning("No projects found, skipping issue creation")
    except Exception as e:
        logger.error(f"Error in issue operations: {e}")
    
    # Operation 7: List users
    print("\n=== Operation 7: List Users ===")
    try:
        result = api.get_users()
        print_json(result)
    except Exception as e:
        logger.error(f"Error listing users: {e}")
    
    # Operation 8: List groups
    print("\n=== Operation 8: List Groups ===")
    try:
        result = api.get_groups()
        print_json(result)
    except Exception as e:
        logger.error(f"Error listing groups: {e}")
    
    print("\n=== All operations completed ===")

if __name__ == "__main__":
    main()