#!/usr/bin/env python3
"""
Tests for project management tools in Redmine MCP server
"""
import os
import sys
import unittest
import json
import logging
from unittest.mock import Mock, patch

# Add the parent directory to the path to access src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.tool_registrations import ToolRegistrations
from fastmcp import FastMCP

class TestProjectTools(unittest.TestCase):
    """Test the project management tools"""
    
    def setUp(self):
        """Set up test environment"""
        # Configure logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("TestProjectTools")
        
        # Create mock MCP instance
        self.mcp = FastMCP()
        
        # Create mock client manager with project client
        self.mock_project_client = Mock()
        self.mock_client_manager = Mock()
        self.mock_client_manager.get_client.return_value = self.mock_project_client
        
        # Create mock service manager
        self.mock_service_manager = Mock()
        
        # Create tool registrations instance
        self.tool_registrations = ToolRegistrations(
            self.mcp,
            self.mock_client_manager,
            self.mock_service_manager,
            self.logger
        )
    
    def test_register_project_tools(self):
        """Test that project tools are registered correctly"""
        # Register project tools
        self.tool_registrations.register_project_tools()
        
        # Check that tools were registered
        expected_tools = [
            "redmine-create-project",
            "redmine-update-project", 
            "redmine-delete-project"
        ]
        
        for tool in expected_tools:
            self.assertIn(tool, self.tool_registrations._registered_tools)
    
    def test_create_project_tool(self):
        """Test the create project tool"""
        # Mock the create_project response
        self.mock_project_client.create_project.return_value = {
            "project": {
                "id": 123,
                "name": "Test Project",
                "identifier": "test-project",
                "description": "Test Description",
                "is_public": True
            }
        }
        
        # Register the tools
        self.tool_registrations.register_project_tools()
        
        # Test that tool was registered
        self.assertIn("redmine-create-project", self.tool_registrations._registered_tools)
        
        # Verify the client was called correctly when we would invoke the tool
        # Since we can't easily invoke the tool directly in tests, we test the registration
        self.mock_client_manager.get_client.assert_called_with('projects')
    
    def test_create_project_calls_client(self):
        """Test that create project calls the client correctly"""
        # Register the tools
        self.tool_registrations.register_project_tools()
        
        # Test that the project client was retrieved
        self.mock_client_manager.get_client.assert_called_with('projects')
        
        # Test that tool was registered
        self.assertIn("redmine-create-project", self.tool_registrations._registered_tools)
    
    def test_update_project_registration(self):
        """Test the update project tool registration"""
        # Register the tools
        self.tool_registrations.register_project_tools()
        
        # Test that tool was registered
        self.assertIn("redmine-update-project", self.tool_registrations._registered_tools)
    
    def test_delete_project_registration(self):
        """Test the delete project tool registration"""
        # Register the tools
        self.tool_registrations.register_project_tools()
        
        # Test that tool was registered
        self.assertIn("redmine-delete-project", self.tool_registrations._registered_tools)
    
    def test_all_project_tools_registered(self):
        """Test that all project tools are registered when calling register_all_tools"""
        # Register all tools
        self.tool_registrations.register_all_tools()
        
        # Check that project tools were registered
        project_tools = [
            "redmine-create-project",
            "redmine-update-project", 
            "redmine-delete-project"
        ]
        
        for tool in project_tools:
            self.assertIn(tool, self.tool_registrations._registered_tools)

if __name__ == '__main__':
    unittest.main()
