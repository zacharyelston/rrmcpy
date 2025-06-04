#!/usr/bin/env python3
"""
Live integration test for project management tools
Tests against real Redmine instance
"""
import os
import sys
import pytest
import logging

# Add the parent directory to the path to access src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.projects import ProjectClient

@pytest.mark.skipif(
    not os.environ.get('REDMINE_API_KEY'),
    reason="REDMINE_API_KEY environment variable required for live tests"
)
def test_project_operations():
    """Test project CRUD operations against live Redmine"""
    # Setup
    logger = logging.getLogger("test_project_live")
    
    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    api_key = os.environ.get('REDMINE_API_KEY')
    
    # Create client
    client = ProjectClient(redmine_url, api_key, logger)
    
    # Test data
    test_identifier = f"test-proj-{os.urandom(4).hex()}"
    test_name = f"Test Project {test_identifier}"
    
    project_id = None
    try:
        # 1. Create project
        logger.info(f"Creating project: {test_name}")
        create_result = client.create_project({
            "name": test_name,
            "identifier": test_identifier,
            "description": "Test project created by automated tests",
            "is_public": False
        })
        
        assert "project" in create_result, f"Create failed: {create_result}"
        project_id = create_result["project"]["id"]
        logger.info(f"✓ Created project with ID: {project_id}")
        
        # 2. Get project
        logger.info(f"Getting project: {project_id}")
        get_result = client.get_project(project_id)
        
        assert "project" in get_result, f"Get failed: {get_result}"
        assert get_result['project']['name'] == test_name
        logger.info(f"✓ Retrieved project: {get_result['project']['name']}")
        
        # 3. Update project
        logger.info(f"Updating project: {project_id}")
        update_result = client.update_project(project_id, {
            "description": "Updated description - test completed"
        })
        
        # Update typically returns empty on success
        logger.info(f"✓ Updated project description")
        
        # Verify update by getting project again
        get_updated = client.get_project(project_id)
        assert get_updated['project']['description'] == "Updated description - test completed"
        
        # 4. Delete project
        logger.info(f"Deleting project: {project_id}")
        delete_result = client.delete_project(project_id)
        
        logger.info(f"✓ Deleted project")
        
        logger.info("\n✅ All project operations completed successfully!")
        
    except Exception as e:
        # Try to clean up if possible
        if project_id:
            try:
                client.delete_project(project_id)
                logger.info(f"Cleaned up test project {project_id}")
            except:
                logger.warning(f"Failed to clean up project {project_id}")
        
        # Re-raise the exception so pytest knows the test failed
        raise e

if __name__ == "__main__":
    # Allow running as a standalone script for local testing
    if not os.environ.get('REDMINE_API_KEY'):
        print("REDMINE_API_KEY environment variable required")
        sys.exit(1)
    
    # Run the test function directly
    try:
        test_project_operations()
        print("Test passed!")
        sys.exit(0)
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
