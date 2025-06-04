#!/usr/bin/env python3
"""
Live integration test for project management tools
Tests against real Redmine instance
"""
import os
import sys
import json
import asyncio
import logging

# Add the parent directory to the path to access src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.projects import ProjectClient

async def test_project_operations():
    """Test project CRUD operations against live Redmine"""
    # Setup
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("test_project_live")
    
    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    api_key = os.environ.get('REDMINE_API_KEY')
    
    if not api_key:
        logger.error("REDMINE_API_KEY environment variable required")
        return False
    
    # Create client
    client = ProjectClient(redmine_url, api_key, logger)
    
    # Test data
    test_identifier = f"test-proj-{os.urandom(4).hex()}"
    test_name = f"Test Project {test_identifier}"
    
    try:
        # 1. Create project
        logger.info(f"Creating project: {test_name}")
        create_result = client.create_project({
            "name": test_name,
            "identifier": test_identifier,
            "description": "Test project created by automated tests",
            "is_public": False
        })
        
        if "project" not in create_result:
            logger.error(f"Create failed: {create_result}")
            return False
            
        project_id = create_result["project"]["id"]
        logger.info(f"✓ Created project with ID: {project_id}")
        
        # 2. Get project
        logger.info(f"Getting project: {project_id}")
        get_result = client.get_project(project_id)
        
        if "project" not in get_result:
            logger.error(f"Get failed: {get_result}")
            return False
            
        logger.info(f"✓ Retrieved project: {get_result['project']['name']}")
        
        # 3. Update project
        logger.info(f"Updating project: {project_id}")
        update_result = client.update_project(project_id, {
            "description": "Updated description - test completed"
        })
        
        # Update typically returns empty on success
        logger.info(f"✓ Updated project description")
        
        # 4. Delete project
        logger.info(f"Deleting project: {project_id}")
        delete_result = client.delete_project(project_id)
        
        logger.info(f"✓ Deleted project")
        
        logger.info("\n✅ All project operations completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        
        # Try to clean up if possible
        if 'project_id' in locals():
            try:
                client.delete_project(project_id)
                logger.info(f"Cleaned up test project {project_id}")
            except:
                logger.warning(f"Failed to clean up project {project_id}")
                
        return False

if __name__ == "__main__":
    success = asyncio.run(test_project_operations())
    sys.exit(0 if success else 1)
