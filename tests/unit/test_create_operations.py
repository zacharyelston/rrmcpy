#!/usr/bin/env python3
"""
Unit tests for create operations and 201 response handling
Tests use mocks - no actual API calls
"""
import os
import sys
import unittest
import json
from unittest.mock import Mock, patch, MagicMock
import requests

# Add the parent directory to the path to access src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.base import RedmineBaseClient
from src.issues import IssueClient
from src.projects import ProjectClient
from src.versions import VersionClient


class TestCreateOperations(unittest.TestCase):
    """Test 201 response handling for create operations"""
    
    def setUp(self):
        """Set up test client"""
        self.base_client = RedmineBaseClient()
        self.issue_client = IssueClient()
        self.project_client = ProjectClient()
        self.version_client = VersionClient()
    
    @patch('requests.request')
    def test_201_with_json_response(self, mock_request):
        """Test handling of 201 response with JSON body"""
        # Mock a 201 Created response with JSON body
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"issue": {"id": 1, "subject": "Test Issue"}}
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        # Make a create request
        result = self.base_client.post("/issues.json", {"issue": {"subject": "Test Issue"}})
        
        # Verify the response was processed correctly
        self.assertIn("issue", result)
        self.assertEqual(result["issue"]["id"], 1)
        self.assertEqual(result["issue"]["subject"], "Test Issue")
    
    @patch('requests.request')
    def test_201_with_location_header(self, mock_request):
        """Test handling of 201 response with Location header but no body"""
        # Mock a 201 Created response with Location header but empty body
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.side_effect = ValueError("No JSON body")
        mock_response.text = ""
        mock_response.headers = {"Location": "http://example.com/issues/42.json"}
        mock_request.return_value = mock_response
        
        # Make a create request
        result = self.base_client.post("/issues.json", {"issue": {"subject": "Test Issue"}})
        
        # Verify the ID was extracted from Location header
        self.assertIn("id", result)
        self.assertEqual(result["id"], 42)
    
    @patch('requests.request')
    def test_201_empty_response_fallback(self, mock_request):
        """Test handling of 201 response with no body and no Location header"""
        # Mock a 201 Created response with no body and no Location header
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.side_effect = ValueError("No JSON body")
        mock_response.text = ""
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        # Make a create request
        result = self.base_client.post("/issues.json", {"issue": {"subject": "Test Issue"}})
        
        # Verify a success response was returned
        self.assertIn("success", result)
        self.assertTrue(result["success"])
    
    def test_extract_id_from_location_variations(self):
        """Test ID extraction from various Location header formats"""
        # Test cases for different Location header formats
        test_cases = [
            ("http://example.com/issues/42", 42),
            ("http://example.com/issues/42.json", 42),
            ("http://example.com/projects/42", 42),
            ("http://example.com/versions/42.xml", 42),
            ("/issues/42", 42),
            ("/projects/42.json", 42),
        ]
        
        for location, expected_id in test_cases:
            # Test ID extraction
            extracted_id = self.base_client._extract_id_from_location(location)
            self.assertEqual(extracted_id, expected_id, f"Failed to extract ID from {location}")


if __name__ == '__main__':
    unittest.main()
