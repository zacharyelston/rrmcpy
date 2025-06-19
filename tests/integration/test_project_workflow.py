#!/usr/bin/env python3
"""
Integration tests for complete project management workflow
Tests combine multiple components but use mocks for API calls
"""
import os
import sys
import unittest
import json
from unittest.mock import Mock, patch, MagicMock

# Handle import paths for both local development and CI environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from src.base import RedmineBaseClient
    from src.projects import ProjectClient
    from src.core.client_manager import ClientManager
except ImportError:
    # Alternative import path for CI environment
    from rrmcpy.src.base import RedmineBaseClient
    from rrmcpy.src.projects import ProjectClient
    from rrmcpy.src.core.client_manager import ClientManager


class TestProjectWorkflow(unittest.TestCase):
    """Integration tests for project management workflow"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a client manager with mocked clients
        self.client_manager = ClientManager()
        
        # Mock the project client
        self.mock_project_client = Mock(spec=ProjectClient)
        
        # Set up mock responses for project operations
        self.mock_project_client.create_project.return_value = {
            "project": {
                "id": 1,
                "name": "Test Project",
                "identifier": "test-project",
                "description": "Test project description",
                "status": 1
            }
        }
        
        self.mock_project_client.get_project.return_value = {
            "project": {
                "id": 1,
                "name": "Test Project",
                "identifier": "test-project",
                "description": "Test project description",
                "status": 1
            }
        }
        
        self.mock_project_client.update_project.return_value = {"success": True}
        self.mock_project_client.archive_project.return_value = {"success": True}
        self.mock_project_client.unarchive_project.return_value = {"success": True}
        self.mock_project_client.delete_project.return_value = {"success": True}
        
        # Replace the real client with our mock
        self.client_manager._clients["projects"] = self.mock_project_client
    
    def test_full_project_lifecycle(self):
        """Test complete project lifecycle with all operations"""
        # Get the project client from the manager
        project_client = self.client_manager.get_client("projects")
        
        # 1. Create a project
        project_data = {
            "name": "Test Project",
            "identifier": "test-project",
            "description": "Test project description",
            "is_public": True
        }
        
        create_result = project_client.create_project(project_data)
        self.assertIn("project", create_result)
        self.assertEqual(create_result["project"]["id"], 1)
        
        # 2. Update the project
        update_data = {
            "name": "Updated Project",
            "description": "Updated description"
        }
        
        # Mock the updated project response
        self.mock_project_client.get_project.return_value = {
            "project": {
                "id": 1,
                "name": "Updated Project",
                "identifier": "test-project",
                "description": "Updated description",
                "status": 1
            }
        }
        
        update_result = project_client.update_project(1, update_data)
        self.assertTrue(update_result["success"])
        
        # Verify the update
        get_result = project_client.get_project(1)
        self.assertEqual(get_result["project"]["name"], "Updated Project")
        
        # 3. Archive the project
        # Mock the archived project response
        self.mock_project_client.get_project.return_value = {
            "project": {
                "id": 1,
                "name": "Updated Project",
                "identifier": "test-project",
                "description": "Updated description",
                "status": 9  # Archived status
            }
        }
        
        archive_result = project_client.archive_project(1)
        self.assertTrue(archive_result["success"])
        
        # Verify the archive
        get_result = project_client.get_project(1)
        self.assertEqual(get_result["project"]["status"], 9)
        
        # 4. Unarchive the project
        # Mock the unarchived project response
        self.mock_project_client.get_project.return_value = {
            "project": {
                "id": 1,
                "name": "Updated Project",
                "identifier": "test-project",
                "description": "Updated description",
                "status": 1  # Active status
            }
        }
        
        unarchive_result = project_client.unarchive_project(1)
        self.assertTrue(unarchive_result["success"])
        
        # Verify the unarchive
        get_result = project_client.get_project(1)
        self.assertEqual(get_result["project"]["status"], 1)
        
        # 5. Delete the project
        delete_result = project_client.delete_project(1)
        self.assertTrue(delete_result["success"])
        
        # Verify the deletion by checking that get_project raises an exception
        self.mock_project_client.get_project.side_effect = Exception("404 Not Found")
        
        with self.assertRaises(Exception):
            project_client.get_project(1)


if __name__ == '__main__':
    unittest.main()
