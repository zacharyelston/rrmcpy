#!/usr/bin/env python3
"""
Comprehensive test suite for v0.9.0 critical bug fixes
Tests cover:
1. Create operations (201 response handling)
2. Project management tools
3. Standardized error handling
"""
import os
import sys
import unittest
import json
from unittest.mock import Mock, patch, MagicMock
import requests

# Add the parent directory to the path to access src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.base import RedmineBaseClient
from src.issues import IssueClient
from src.projects import ProjectClient
from src.core.tool_registrations import ToolRegistrations
from fastmcp import FastMCP


class TestCreateOperations(unittest.TestCase):
    """Test 201 response handling for create operations"""
    
    def setUp(self):
        """Set up test client"""
        self.base_client = RedmineBaseClient("https://test.redmine.org", "test_key")
    
    def test_201_with_json_response(self):
        """Test handling of 201 response with JSON body"""
        # Mock response with JSON content
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.content = b'{"issue": {"id": 123, "subject": "Test"}}'
        mock_response.json.return_value = {"issue": {"id": 123, "subject": "Test"}}
        mock_response.raise_for_status = Mock()
        
        with patch.object(self.base_client.connection_manager, 'make_request', return_value=mock_response):
            result = self.base_client.make_request("POST", "issues.json", data={"issue": {"subject": "Test"}})
        
        # Should return the created resource
        self.assertIn("issue", result)
        self.assertEqual(result["issue"]["id"], 123)
    
    def test_201_with_location_header(self):
        """Test handling of 201 response with Location header but no body"""
        # Mock response with Location header
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.content = b''
        mock_response.headers = {"Location": "https://test.redmine.org/issues/456.json"}
        mock_response.raise_for_status = Mock()
        
        with patch.object(self.base_client.connection_manager, 'make_request', return_value=mock_response):
            result = self.base_client.make_request("POST", "issues.json", data={"issue": {"subject": "Test"}})
        
        # Should extract ID from Location header
        self.assertIn("id", result)
        self.assertEqual(result["id"], 456)
        self.assertTrue(result["success"])
    
    def test_201_empty_response_fallback(self):
        """Test handling of 201 response with no body and no Location header"""
        # Mock response with nothing
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.content = b''
        mock_response.headers = {}
        mock_response.raise_for_status = Mock()
        
        with patch.object(self.base_client.connection_manager, 'make_request', return_value=mock_response):
            result = self.base_client.make_request("POST", "issues.json", data={"issue": {"subject": "Test"}})
        
        # Should return success with status code
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 201)
    
    def test_extract_id_from_location_variations(self):
        """Test ID extraction from various Location header formats"""
        test_cases = [
            ("https://example.com/issues/789.json", 789),
            ("/issues/101", 101),
            ("http://redmine.org/projects/test/issues/202.xml", 202),
            ("/versions/303/", 303),
            ("https://example.com/issues/abc", None),  # Non-numeric
            ("", None),  # Empty
        ]
        
        for location, expected_id in test_cases:
            mock_response = Mock()
            mock_response.headers = {"Location": location}
            result = self.base_client._extract_id_from_location(mock_response)
            self.assertEqual(result, expected_id, f"Failed for location: {location}")


class TestProjectTools(unittest.TestCase):
    """Test project management tools implementation"""
    
    def setUp(self):
        """Set up test environment"""
        self.mcp = FastMCP("Test")
        self.mock_client_manager = Mock()
        self.mock_project_client = Mock()
        self.mock_client_manager.get_client.return_value = self.mock_project_client
        
        self.tool_registrations = ToolRegistrations(
            mcp=self.mcp,
            client_manager=self.mock_client_manager
        )
    
    def test_project_tools_registered(self):
        """Test that all project tools are registered"""
        self.tool_registrations.register_project_tools()
        
        expected_tools = [
            "redmine-create-project",
            "redmine-update-project",
            "redmine-delete-project"
        ]
        
        for tool in expected_tools:
            self.assertIn(tool, self.tool_registrations._registered_tools)
    
    def test_create_project_validation(self):
        """Test create project parameter validation"""
        self.tool_registrations.register_project_tools()
        
        # Get the registered tool function
        create_tool = None
        for name, tool in self.mcp._tools.items():
            if name == "redmine-create-project":
                create_tool = tool.fn
                break
        
        self.assertIsNotNone(create_tool)
        
        # Test with missing required parameters
        import asyncio
        result = asyncio.run(create_tool(name="", identifier="test"))
        result_data = json.loads(result)
        
        self.assertIn("error", result_data)
        self.assertEqual(result_data["error"], "name and identifier are required")
    
    def test_update_project_validation(self):
        """Test update project parameter validation"""
        self.tool_registrations.register_project_tools()
        
        # Get the registered tool function
        update_tool = None
        for name, tool in self.mcp._tools.items():
            if name == "redmine-update-project":
                update_tool = tool.fn
                break
        
        self.assertIsNotNone(update_tool)
        
        # Test with no update fields
        import asyncio
        result = asyncio.run(update_tool(project_id="test"))
        result_data = json.loads(result)
        
        self.assertIn("error", result_data)
        self.assertEqual(result_data["error"], "No update fields provided")


class TestStandardizedErrorHandling(unittest.TestCase):
    """Test standardized error response format"""
    
    def setUp(self):
        """Set up test client"""
        self.base_client = RedmineBaseClient("https://test.redmine.org", "test_key")
    
    def test_error_response_format(self):
        """Test that error responses follow the standard format"""
        error = self.base_client._create_error_response(
            error_code="TEST_ERROR",
            error_message="This is a test error",
            status_code=400
        )
        
        # Check required fields
        self.assertTrue(error["error"])
        self.assertEqual(error["error_code"], "TEST_ERROR")
        self.assertEqual(error["message"], "This is a test error")
        self.assertEqual(error["status_code"], 400)
        self.assertIn("timestamp", error)
        
        # Check timestamp format
        self.assertTrue(error["timestamp"].endswith("Z"))
        self.assertIn("T", error["timestamp"])
    
    def test_http_error_mapping(self):
        """Test that HTTP status codes are mapped to appropriate error codes"""
        test_cases = [
            (401, "AUTHENTICATION_ERROR", "Invalid API key or insufficient permissions"),
            (403, "AUTHORIZATION_ERROR", "Access forbidden - check user permissions"),
            (404, "NOT_FOUND", "Resource not found"),
            (422, "VALIDATION_ERROR", "Invalid data provided"),
            (500, "SERVER_ERROR", "Redmine server error"),
        ]
        
        for status_code, expected_code, expected_msg_part in test_cases:
            # Mock HTTP error response
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_response.text = "Error details"
            
            error = requests.exceptions.HTTPError()
            error.response = mock_response
            
            result = self.base_client._handle_request_error(
                error, "POST", "https://test.redmine.org/test", {}
            )
            
            self.assertEqual(result["error_code"], expected_code)
            self.assertIn(expected_msg_part, result["message"])
            self.assertEqual(result["status_code"], status_code)
    
    def test_connection_error_handling(self):
        """Test handling of connection errors"""
        error = requests.exceptions.ConnectionError("Connection refused")
        result = self.base_client._handle_request_error(
            error, "GET", "https://test.redmine.org/test", {}
        )
        
        self.assertEqual(result["error_code"], "CONNECTION_ERROR")
        self.assertIn("Failed to connect", result["message"])
        self.assertEqual(result["status_code"], 503)
    
    def test_timeout_error_handling(self):
        """Test handling of timeout errors"""
        error = requests.exceptions.Timeout("Request timed out")
        result = self.base_client._handle_request_error(
            error, "GET", "https://test.redmine.org/test", {}
        )
        
        self.assertEqual(result["error_code"], "TIMEOUT_ERROR")
        self.assertIn("timed out", result["message"])
        self.assertEqual(result["status_code"], 504)


class TestIntegration(unittest.TestCase):
    """Integration tests for all v0.9.0 fixes"""
    
    @unittest.skipIf(not os.environ.get('REDMINE_API_KEY'), 
                     "REDMINE_API_KEY environment variable required for integration tests")
    def test_full_project_lifecycle(self):
        """Test complete project lifecycle with all fixes"""
        redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        api_key = os.environ.get('REDMINE_API_KEY')
        
        project_client = ProjectClient(redmine_url, api_key)
        issue_client = IssueClient(redmine_url, api_key)
        
        test_id = os.urandom(4).hex()
        project_data = {
            "name": f"Test Project {test_id}",
            "identifier": f"test-proj-{test_id}",
            "description": "Integration test project",
            "is_public": False
        }
        
        try:
            # Test create operation (201 handling)
            create_result = project_client.create_project(project_data)
            self.assertIn("project", create_result)
            self.assertIn("id", create_result["project"])
            project_id = create_result["project"]["id"]
            
            # Test update operation
            update_result = project_client.update_project(
                project_id,
                {"description": "Updated description"}
            )
            self.assertIn("success", update_result)
            
            # Test error handling with invalid issue creation
            invalid_issue = {"subject": ""}  # Missing project_id and empty subject
            error_result = issue_client.create_issue(invalid_issue)
            self.assertTrue(error_result.get("error", False))
            self.assertIn("error_code", error_result)
            self.assertIn("message", error_result)
            
            # Cleanup
            project_client.delete_project(project_id)
            
        except Exception as e:
            # Cleanup on failure
            if 'project_id' in locals():
                try:
                    project_client.delete_project(project_id)
                except:
                    pass
            raise e


def suite():
    """Create test suite"""
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_suite.addTest(unittest.makeSuite(TestCreateOperations))
    test_suite.addTest(unittest.makeSuite(TestProjectTools))
    test_suite.addTest(unittest.makeSuite(TestStandardizedErrorHandling))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
