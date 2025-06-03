#!/usr/bin/env python3
"""
Test core features of the Redmine API through MCP
"""
import os
import sys
import logging
import pytest

# Add the parent directory to path so we can import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.redmine_client import RedmineClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("CoreFeaturesTest")

def setup_api_key():
    """Setup API key from environment or secrets"""
    redmine_api_key = os.environ.get("REDMINE_API_KEY", "")
    
    # For automated test environment
    if not redmine_api_key and os.path.exists('/run/secrets/REDMINE_API_KEY'):
        try:
            with open('/run/secrets/REDMINE_API_KEY', 'r') as f:
                redmine_api_key = f.read().strip()
        except Exception as e:
            logger.warning(f"Could not read REDMINE_API_KEY from secrets: {e}")
    
    return redmine_api_key

@pytest.mark.skipif(not setup_api_key(), reason="REDMINE_API_KEY not available")
def test_current_user():
    """Test current user endpoint"""
    redmine_url = os.environ.get("REDMINE_URL", "https://demo.redmine.org")
    redmine_api_key = setup_api_key()
    
    logger.info(f"Connecting to Redmine at {redmine_url}")
    client = RedmineClient(redmine_url, redmine_api_key, logger)
    
    # Test current user
    logger.info("Testing current user...")
    user = client.get_current_user()
    logger.info(f"Logged in as: {user['user']['firstname']} {user['user']['lastname']} ({user['user']['login']})")
    
    assert 'user' in user, "User information not found in response"
    assert 'login' in user['user'], "Login field not found in user information"

@pytest.mark.skipif(not setup_api_key(), reason="REDMINE_API_KEY not available")
def test_projects():
    """Test projects endpoint"""
    redmine_url = os.environ.get("REDMINE_URL", "https://demo.redmine.org")
    redmine_api_key = setup_api_key()
    
    logger.info(f"Connecting to Redmine at {redmine_url}")
    client = RedmineClient(redmine_url, redmine_api_key, logger)
    
    # Test projects
    logger.info("Testing projects...")
    projects = client.get_projects()
    logger.info(f"Found {len(projects['projects'])} projects")
    
    assert 'projects' in projects, "Projects information not found in response"
    assert len(projects['projects']) > 0, "No projects found"
    
@pytest.mark.skipif(not setup_api_key(), reason="REDMINE_API_KEY not available")
def test_issues():
    """Test issues endpoint"""
    redmine_url = os.environ.get("REDMINE_URL", "https://demo.redmine.org")
    redmine_api_key = setup_api_key()
    test_project = os.environ.get("TEST_PROJECT", "p1")
    
    logger.info(f"Connecting to Redmine at {redmine_url}")
    client = RedmineClient(redmine_url, redmine_api_key, logger)
    
    # Find test project
    projects = client.get_projects()
    test_project_id = None
    for project in projects['projects']:
        if project['identifier'] == test_project:
            test_project_id = project['id']
            logger.info(f"Found test project '{test_project}' with ID {test_project_id}")
            break
    
    # Skip if test project not found
    if not test_project_id:
        logger.warning(f"Test project '{test_project}' not found, skipping issue tests")
        pytest.skip(f"Test project {test_project} not found")
        return
    
    # Test issues
    logger.info("Testing issues...")
    issues = client.get_issues({'project_id': test_project_id})
    logger.info(f"Found {len(issues.get('issues', []))} issues in project")
    
    assert 'issues' in issues, "Issues information not found in response"