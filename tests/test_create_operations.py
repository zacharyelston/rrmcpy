#!/usr/bin/env python3
"""
Tests for create operations in Redmine API client
Specifically tests the fix for empty responses in create operations
"""
import os
import sys
import unittest
import logging
from unittest import mock
from requests import Response

# Add the parent directory to the path to access src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.base import RedmineBaseClient
from src.issues import IssueClient
from src.projects import ProjectClient

class TestCreateOperations(unittest.TestCase):
    """Test the fix for empty responses in create operations"""
    
    def setUp(self):
        """Set up test environment with mock clients"""
        self.redmine_url = "https://example.redmine.org"
        self.api_key = "test_api_key"
        
        # Configure logging to capture debugging info
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("TestCreateOperations")
        
        # Create clients
        self.base_client = RedmineBaseClient(self.redmine_url, self.api_key, self.logger)
        self.issue_client = IssueClient(self.redmine_url, self.api_key, self.logger)
        self.project_client = ProjectClient(self.redmine_url, self.api_key, self.logger)
    
    def test_extract_id_from_location(self):
        """Test the helper method that extracts IDs from Location headers"""
        # Create a mock response with a Location header
        mock_response = mock.Mock(spec=Response)
        mock_response.headers = {"Location": "https://example.redmine.org/issues/42.json"}
        
        # Extract ID from Location
        result = self.base_client._extract_id_from_location(mock_response)
        self.assertEqual(result, 42, "Should extract ID 42 from Location header")
        
        # Test with different Location format
        mock_response.headers = {"Location": "/issues/123"}
        result = self.base_client._extract_id_from_location(mock_response)
        self.assertEqual(result, 123, "Should extract ID 123 from Location header without extension")
        
        # Test with no Location header
        mock_response.headers = {}
        result = self.base_client._extract_id_from_location(mock_response)
        self.assertIsNone(result, "Should return None when no Location header is present")
        
    @mock.patch('src.base.ConnectionManager')
    def test_create_with_empty_response(self, mock_cm):
        """Test handling of empty response bodies in create operations"""
        # Set up mock response with 201 status but empty content
        mock_response = mock.Mock(spec=Response)
        mock_response.status_code = 201
        mock_response.content = b""  # Empty response body
        mock_response.headers = {"Location": "/issues/42.json"}
        
        # Configure the mock connection manager
        mock_cm.return_value.make_request.return_value = mock_response
        
        # Make a create request that would result in a 201 with empty body
        result = self.base_client.make_request("POST", "issues.json", {"issue": {"subject": "Test"}})
        
        # Verify the result includes the ID from Location and success flag
        self.assertEqual(result["id"], 42, "Should include ID extracted from Location header")
        self.assertTrue(result["success"], "Should indicate success")
    
    @mock.patch('src.base.ConnectionManager')
    def test_create_with_response_content(self, mock_cm):
        """Test handling of responses with content in create operations"""
        # Set up mock response with 201 status and content
        mock_response = mock.Mock(spec=Response)
        mock_response.status_code = 201
        mock_response.content = b'{"issue": {"id": 42, "subject": "Test"}}'
        mock_response.json.return_value = {"issue": {"id": 42, "subject": "Test"}}
        
        # Configure the mock connection manager
        mock_cm.return_value.make_request.return_value = mock_response
        
        # Make a create request that returns response content
        result = self.base_client.make_request("POST", "issues.json", {"issue": {"subject": "Test"}})
        
        # Verify the result contains the full response data
        self.assertEqual(result["issue"]["id"], 42, "Should return the issue data")
        self.assertEqual(result["issue"]["subject"], "Test", "Should return all issue fields")
    
    @mock.patch('src.base.ConnectionManager')
    def test_create_no_location_header(self, mock_cm):
        """Test handling of create operations with no Location header"""
        # Set up mock response with 201 status, empty content, but no Location header
        mock_response = mock.Mock(spec=Response)
        mock_response.status_code = 201
        mock_response.content = b""
        mock_response.headers = {}
        
        # Configure the mock connection manager
        mock_cm.return_value.make_request.return_value = mock_response
        
        # Make a create request
        result = self.base_client.make_request("POST", "issues.json", {"issue": {"subject": "Test"}})
        
        # Verify we get a basic success response
        self.assertTrue(result["success"], "Should indicate success")
        self.assertEqual(result["status_code"], 201, "Should include status code")
        self.assertNotIn("id", result, "Should not include ID when no Location header")

if __name__ == '__main__':
    unittest.main()
