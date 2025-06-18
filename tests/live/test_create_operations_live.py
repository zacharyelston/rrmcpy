#!/usr/bin/env python3
"""
Test for create operations with real Redmine server
Verifies that our fix for empty responses in create operations works correctly
"""
import os
import sys
import logging
import pytest
import dotenv
from datetime import datetime

# Add the parent directory to path so we can import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
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
    logger.info(f"Create project result: {result}")
    
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

@pytest.mark.skipif(not os.environ.get("REDMINE_API_KEY"), reason="REDMINE_API_KEY not available")
def test_create_operations():
    """Test create operations with empty response handling"""
    # Setup environment variables
    redmine_url, redmine_api_key = setup_environment()
    
    if not redmine_url or not redmine_api_key:
        pytest.skip("REDMINE_URL and REDMINE_API_KEY environment variables must be set")
    
    logger.info(f"Connecting to Redmine at {redmine_url}")
    
    # Initialize clients
    project_client = ProjectClient(redmine_url, redmine_api_key, logger)
    issue_client = IssueClient(redmine_url, redmine_api_key, logger)
    
    # Find test project (or create one if needed)
    test_project_id = find_or_create_test_project(project_client)
    assert test_project_id is not None, "Could not find or create test project"
    
    # Test issue creation
    logger.info(f"Creating test issue in project {test_project_id}")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_issue = {
        "project_id": test_project_id,
        "subject": f"Test issue created at {timestamp}",
        "description": "This is a test issue to verify the create operations fix"
    }
    
    result = issue_client.create_issue(new_issue)
    logger.info(f"Create issue result: {result}")
    
    # Verify the result
    if 'issue' in result and 'id' in result['issue']:
        issue_id = result['issue']['id']
        logger.info(f"Successfully created issue with ID: {issue_id} (full response)")
        success = True
    elif 'id' in result:  # With our fix, empty responses return ID from Location header
        issue_id = result['id']
        logger.info(f"Successfully created issue with ID: {issue_id} (from Location header)")
        success = True
    else:
        logger.error("Failed to create test issue or ID not found in response")
        success = False
    
    assert success, "Failed to create issue"
    
    # Verify we can retrieve the issue
    verify_result = issue_client.get_issue(issue_id)
    assert 'issue' in verify_result and verify_result['issue']['id'] == issue_id, "Cannot retrieve created issue"
    logger.info("Verification succeeded! We can retrieve the created issue.")
