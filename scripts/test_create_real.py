#!/usr/bin/env python3
"""
Test script for verifying the create operations fix against a real Redmine server
"""
import os
import sys
import logging
import json
import dotenv
from datetime import datetime

# Add the parent directory to path so we can import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from src.projects import ProjectClient
from src.issues import IssueClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("CreateOperationsTest")

def setup_environment():
    """Setup environment variables for testing"""
    # Try to load from .env file if it exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        logger.info(f"Loading environment from {env_file}")
        dotenv.load_dotenv(env_file)
    
    # Get connection details from environment
    redmine_url = os.environ.get("REDMINE_URL", "")
    redmine_api_key = os.environ.get("REDMINE_API_KEY", "")
    
    # For automated test environment
    if not redmine_api_key and os.path.exists('/run/secrets/REDMINE_API_KEY'):
        try:
            with open('/run/secrets/REDMINE_API_KEY', 'r') as f:
                redmine_api_key = f.read().strip()
        except Exception as e:
            logger.warning(f"Could not read REDMINE_API_KEY from secrets: {e}")
    
    return redmine_url, redmine_api_key

def main():
    """Test create operations with real Redmine server"""
    # Setup environment variables
    redmine_url, redmine_api_key = setup_environment()
    
    if not redmine_url or not redmine_api_key:
        logger.error("REDMINE_URL and REDMINE_API_KEY environment variables must be set")
        logger.error("Please create a .env file with these variables or set them in your environment")
        sys.exit(1)
    
    logger.info(f"Connecting to Redmine at {redmine_url}")
    
    # Initialize clients
    project_client = ProjectClient(redmine_url, redmine_api_key, logger)
    issue_client = IssueClient(redmine_url, redmine_api_key, logger)
    
    # Find test project (or create one if needed)
    test_project_id = find_or_create_test_project(project_client)
    if not test_project_id:
        logger.error("Could not find or create test project")
        sys.exit(1)
    
    # Test issue creation
    test_issue_creation(issue_client, test_project_id)
    
def find_or_create_test_project(project_client):
    """Find a test project or create one if needed"""
    # Try to find a project named "MCP Test Project"
    logger.info("Looking for test project...")
    projects = project_client.get_projects()
    
    if 'projects' not in projects:
        logger.error("Failed to get projects list")
        return None
    
    for project in projects['projects']:
        if project['name'] == "MCP Test Project":
            logger.info(f"Found test project with ID: {project['id']}")
            return project['id']
    
    # Create test project if it doesn't exist
    logger.info("Test project not found, creating new one...")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    new_project = {
        "name": "MCP Test Project",
        "identifier": f"mcp-test-{timestamp}",
        "description": "Test project for MCP create operations"
    }
    
    result = project_client.create_project(new_project)
    print("Create project result:", json.dumps(result, indent=2))
    
    # Check if result contains the created project ID
    if 'project' in result and 'id' in result['project']:
        logger.info(f"Created test project with ID: {result['project']['id']}")
        return result['project']['id']
    elif 'id' in result:  # With our fix, empty responses return ID from Location header
        logger.info(f"Created test project with ID: {result['id']} (from Location header)")
        return result['id']
    else:
        logger.error("Failed to create test project")
        return None

def test_issue_creation(issue_client, project_id):
    """Test issue creation with empty response handling"""
    # Create a test issue
    logger.info(f"Creating test issue in project {project_id}")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_issue = {
        "project_id": project_id,
        "subject": f"Test issue created at {timestamp}",
        "description": "This is a test issue to verify the create operations fix"
    }
    
    result = issue_client.create_issue(new_issue)
    print("Create issue result:", json.dumps(result, indent=2))
    
    # Verify the result
    if 'issue' in result and 'id' in result['issue']:
        logger.info(f"Successfully created issue with ID: {result['issue']['id']} (full response)")
        issue_id = result['issue']['id']
        success = True
    elif 'id' in result:  # With our fix, empty responses return ID from Location header
        logger.info(f"Successfully created issue with ID: {result['id']} (from Location header)")
        issue_id = result['id']
        success = True
    else:
        logger.error("Failed to create test issue or ID not found in response")
        success = False
    
    if success:
        # Verify we can retrieve the issue
        verify_result = issue_client.get_issue(issue_id)
        if 'issue' in verify_result and verify_result['issue']['id'] == issue_id:
            logger.info("Verification succeeded! We can retrieve the created issue.")
        else:
            logger.error("Verification failed! Could not retrieve the created issue.")

if __name__ == "__main__":
    main()
