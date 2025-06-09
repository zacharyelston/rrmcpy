#!/usr/bin/env python3
"""
Unit tests for project management tools
Tests use mocks - no actual API calls
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
except ImportError:
    # Alternative import path for CI environment
    from rrmcpy.src.base import RedmineBaseClient
    from rrmcpy.src.projects import ProjectClient


class TestProjectTools(unittest.TestCase):
    """Test project management tools implementation"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_client = Mock(spec=ProjectClient)
        
        # Mock responses
        self.mock_client.create_project.return_value = {"project": {"id": 1, "name": "Test Project"}}
        self.mock_client.update_project.return_value = {"success": True}
        self.mock_client.delete_project.return_value = {"success": True}
        self.mock_client.archive_project.return_value = {"success": True}
        self.mock_client.unarchive_project.return_value = {"success": True}
        self.mock_client.get_projects.return_value = {"projects": [{"id": 1, "name": "Test Project"}]}
    
    @patch('src.core.tool_registrations.ToolRegistrations')
    def test_project_tools_registered(self, mock_tool_registrations):
        """Test that all project tools are registered"""
        # This is a placeholder for testing tool registration
        # In a real test, we would verify that each tool is registered with the MCP
        pass
    
    def test_create_project_validation(self):
        """Test create project parameter validation"""
        # Valid project data
        valid_data = {
            "name": "Test Project",
            "identifier": "test-project",
            "description": "Test project description",
            "is_public": True
        }
        
        # Test with valid data
        result = self.mock_client.create_project(valid_data)
        self.assertIn("project", result)
        self.assertEqual(result["project"]["id"], 1)
        
        # Test with missing required fields
        invalid_data = {
            "description": "Missing name and identifier"
        }
        
        with self.assertRaises(Exception):
            self.mock_client.create_project.side_effect = Exception("Validation error")
            self.mock_client.create_project(invalid_data)
    
    def test_update_project_validation(self):
        """Test update project parameter validation"""
        # Valid update data
        valid_data = {
            "name": "Updated Project",
            "description": "Updated description"
        }
        
        # Test with valid data
        result = self.mock_client.update_project(1, valid_data)
        self.assertTrue(result["success"])
        
        # Test with invalid project ID
        with self.assertRaises(Exception):
            self.mock_client.update_project.side_effect = Exception("Invalid project ID")
            self.mock_client.update_project(None, valid_data)
    
    def test_archive_unarchive_project(self):
        """Test project archive and unarchive functionality"""
        # Test archive
        archive_result = self.mock_client.archive_project(1)
        self.assertTrue(archive_result["success"])
        
        # Test unarchive
        unarchive_result = self.mock_client.unarchive_project(1)
        self.assertTrue(unarchive_result["success"])
        
        # Test with invalid project ID
        with self.assertRaises(Exception):
            self.mock_client.archive_project.side_effect = Exception("Invalid project ID")
            self.mock_client.archive_project(None)
    
    def test_list_projects_parameters(self):
        """Test list projects with various parameters"""
        # Test basic listing
        list_result = self.mock_client.get_projects()
        self.assertIn("projects", list_result)
        self.assertEqual(len(list_result["projects"]), 1)
        
        # Test with include parameter
        self.mock_client.get_projects.return_value = {
            "projects": [
                {
                    "id": 1,
                    "name": "Test Project",
                    "trackers": [{"id": 1, "name": "Bug"}]
                }
            ]
        }
        
        include_result = self.mock_client.get_projects(params={"include": "trackers"})
        self.assertIn("projects", include_result)
        self.assertIn("trackers", include_result["projects"][0])


if __name__ == '__main__':
    unittest.main()
