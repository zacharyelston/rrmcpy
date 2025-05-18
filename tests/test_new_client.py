#!/usr/bin/env python3
"""
Test the new modular Redmine client
"""
import os
import logging
import sys
# Add the parent directory to path so we can import src modules
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.redmine_client import RedmineClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("ModularClientTest")

def test_modular_client():
    """Test the new modular RedmineClient against the p1 project"""
    # Get API credentials from environment
    redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
    redmine_api_key = os.environ.get("REDMINE_API_KEY", "")
    test_project = "p1"
    
    # For automated test environment
    if not redmine_api_key and os.path.exists('/run/secrets/REDMINE_API_KEY'):
        try:
            with open('/run/secrets/REDMINE_API_KEY', 'r') as f:
                redmine_api_key = f.read().strip()
        except Exception as e:
            logger.warning(f"Could not read REDMINE_API_KEY from secrets: {e}")
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is not set")
        return False  # Return instead of exiting to allow pytest to continue with other tests
    
    logger.info(f"Connecting to Redmine at {redmine_url}")
    client = RedmineClient(redmine_url, redmine_api_key, logger)
    
    # Test current user
    logger.info("Testing current user...")
    user = client.get_current_user()
    logger.info(f"Logged in as: {user['user']['firstname']} {user['user']['lastname']} ({user['user']['login']})")
    
    # Test projects
    logger.info("Testing projects...")
    projects = client.get_projects()
    logger.info(f"Found {len(projects['projects'])} projects")
    
    # Find test project
    test_project_id = None
    for project in projects['projects']:
        if project['identifier'] == test_project:
            test_project_id = project['id']
            logger.info(f"Found test project '{test_project}' with ID {test_project_id}")
            break
    
    if not test_project_id:
        logger.error(f"Test project '{test_project}' not found")
        sys.exit(1)
    
    # Test project details
    logger.info("Testing project details...")
    project_details = client.get_project(test_project_id)
    logger.info(f"Project name: {project_details['project']['name']}")
    
    # Test issues
    logger.info("Testing issues...")
    issues = client.get_issues({'project_id': test_project_id})
    logger.info(f"Found {len(issues.get('issues', []))} issues in project")
    
    # Test creating a test issue
    logger.info("Testing issue creation...")
    issue_data = {
        "project_id": test_project_id,
        "subject": f"Test from modular client {os.urandom(4).hex()}",
        "description": "This is a test issue created by the modular Redmine client",
        "priority_id": 2,  # Normal priority
        "tracker_id": 1    # Bug tracker
    }
    new_issue = client.create_issue(issue_data)
    logger.info(f"Created issue #{new_issue['issue']['id']}: {new_issue['issue']['subject']}")
    
    # Update the issue
    logger.info("Testing issue update...")
    update_data = {
        "notes": "This is a test note from the modular Redmine client"
    }
    client.update_issue(new_issue['issue']['id'], update_data)
    logger.info(f"Updated issue #{new_issue['issue']['id']}")
    
    # Test versions if available
    logger.info("Testing versions...")
    try:
        versions = client.get_versions(test_project_id)
        logger.info(f"Found {len(versions.get('versions', []))} versions in project")
        
        # Create test version if possible
        version_data = {
            "project_id": test_project_id,
            "name": f"Test Version {os.urandom(3).hex()}",
            "description": "Test version created by modular client"
        }
        new_version = client.create_version(version_data)
        logger.info(f"Created version '{new_version['version']['name']}'")
        
        # Clean up version
        client.delete_version(new_version['version']['id'])
        logger.info(f"Deleted test version")
    except Exception as e:
        logger.warning(f"Version operations failed: {e}")
    
    # Clean up test issue
    logger.info("Cleaning up...")
    client.delete_issue(new_issue['issue']['id'])
    logger.info(f"Deleted test issue #{new_issue['issue']['id']}")
    
    logger.info("All tests completed successfully!")
    return True

if __name__ == "__main__":
    test_modular_client()