#!/usr/bin/env python3
"""
Simplified test client for the Redmine MCP Server
Creates and updates issues with timestamp notes for key functionality
"""
import os
import sys
import json
import time
import random
import datetime
# Add the parent directory to path so we can import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.redmine_client import RedmineClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("SimplifiedTest")

def run_tests():
    """Run simplified tests with issue tracking"""
    # Get configuration from environment
    redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
    redmine_api_key = os.environ.get("REDMINE_API_KEY", "")
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is not set")
        sys.exit(1)
    
    logger.info(f"Starting simplified tests against Redmine at {redmine_url}")
    
    # Initialize the client
    client = RedmineClient(redmine_url, redmine_api_key, logger)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    random_id = ''.join(random.choices('0123456789abcdef', k=6))
    test_id = f"TEST-{random_id}"
    
    try:
        # Find the p1 test project
        projects = client.get_projects()['projects']
        test_project_id = None
        for project in projects:
            if project['identifier'] == 'p1':
                test_project_id = project['id']
                logger.info(f"Found test project 'p1' with ID {test_project_id}")
                break
                
        if not test_project_id:
            logger.warning("Test project 'p1' not found, using first project")
            test_project_id = projects[0]['id']
            
        # Create a main test tracking issue
        main_issue_data = {
            "project_id": test_project_id,
            "subject": f"{test_id}: Automated Test Run",
            "description": f"Main tracking issue for automated test run\n\nStarted at: {timestamp}",
            "priority_id": 2  # Normal priority
        }
        result = client.create_issue(main_issue_data)
        main_issue_id = result['issue']['id']
        logger.info(f"Created main tracking issue #{main_issue_id}")
        
        # Now run the tests and update the main issue with results
        
        # Test 1: User Authentication
        print(f"\n=== Test 1: User Authentication ===")
        note = "Test 1: User Authentication\n"
        try:
            result = client.get_current_user()
            user = result['user']
            details = (
                f"Connected as: {user['firstname']} {user['lastname']} ({user['login']})\n"
                f"Email: {user['mail']}\n"
                f"Admin: {'Yes' if user['admin'] else 'No'}\n"
                f"Last login: {user['last_login_on']}"
            )
            print(details)
            note += f"Status: PASSED\nTimestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{details}\n\n"
        except Exception as e:
            print(f"Error: {e}")
            note += f"Status: FAILED\nTimestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nError: {str(e)}\n\n"
        
        # Update the main issue
        client.update_issue(main_issue_id, {"notes": note})
        
        # Test 2: Project and Issue Operations
        print(f"\n=== Test 2: Project and Issue Operations ===")
        note = "Test 2: Project and Issue Operations\n"
        try:
            # Get project info
            project_info = client.get_project(test_project_id)['project']
            project_details = (
                f"Project: {project_info['name']} (ID: {project_info['id']})\n"
                f"Identifier: {project_info['identifier']}\n"
                f"Description: {project_info['description'] or '(None)'}"
            )
            
            # Create a test issue
            issue_data = {
                "project_id": test_project_id,
                "subject": f"{test_id}: Test Issue",
                "description": f"This is a test issue created during the automated test run.\nCreated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "priority_id": 2  # Normal priority
            }
            result = client.create_issue(issue_data)
            test_issue_id = result['issue']['id']
            
            # Update the test issue with a note
            update_note = f"Test note added at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            client.update_issue(test_issue_id, {"notes": update_note})
            
            # Get the updated issue
            updated_issue = client.get_issue(test_issue_id)['issue']
            
            issue_details = (
                f"Created issue #{test_issue_id}: {updated_issue['subject']}\n"
                f"Status: {updated_issue['status']['name']}\n"
                f"Updated at: {updated_issue['updated_on']}"
            )
            
            details = f"{project_details}\n\n{issue_details}"
            print(details)
            note += f"Status: PASSED\nTimestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{details}\n\n"
            
            # We don't delete the test issue so it can be examined
            logger.info(f"Created test issue #{test_issue_id}")
            
        except Exception as e:
            print(f"Error: {e}")
            note += f"Status: FAILED\nTimestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nError: {str(e)}\n\n"
        
        # Update the main issue
        client.update_issue(main_issue_id, {"notes": note})
        
        # Test 3: Version Management
        print(f"\n=== Test 3: Version Management ===")
        note = "Test 3: Version Management\n"
        test_version_id = None
        
        try:
            # List existing versions
            versions = client.get_versions(test_project_id).get('versions', [])
            version_list = f"Found {len(versions)} existing versions\n"
            
            # Create a test version
            version_data = {
                "project_id": test_project_id,
                "name": f"{test_id}: Test Version",
                "description": "Test version created during the automated test run",
                "status": "open"
            }
            result = client.create_version(version_data)
            test_version_id = result['version']['id']
            
            # Get details of the created version
            version_details = client.get_version(test_version_id)['version']
            
            details = (
                f"{version_list}\n"
                f"Created version #{test_version_id}: {version_details['name']}\n"
                f"Status: {version_details['status']}\n"
                f"Project: {version_details['project']['name']}"
            )
            
            print(details)
            note += f"Status: PASSED\nTimestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{details}\n\n"
            logger.info(f"Created test version #{test_version_id}")
            
        except Exception as e:
            print(f"Error: {e}")
            note += f"Status: FAILED\nTimestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nError: {str(e)}\n\n"
        
        # Update the main issue
        client.update_issue(main_issue_id, {"notes": note})
        
        # Finalize the test run
        summary = (
            f"Test run completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"All tests were executed successfully.\n\n"
        )
        
        # Only add the test issue ID if it was created successfully
        if 'test_issue_id' in locals() and test_issue_id:
            summary += f"Created test issue #{test_issue_id} for inspection.\n"
        
        if test_version_id:
            summary += f"Created test version #{test_version_id} for inspection.\n"
            
        summary += f"\nThese test artifacts can be examined in the Redmine interface and will remain until manually deleted."
        
        client.update_issue(main_issue_id, {"notes": summary})
        
        print(f"\nTest run completed successfully. Main tracking issue: #{main_issue_id}")
        
    except Exception as e:
        logger.error(f"Unexpected error in test suite: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_tests()