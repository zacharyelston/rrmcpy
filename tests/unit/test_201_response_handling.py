#!/usr/bin/env python3
"""
Integration tests for create operations and 201 response handling
Tests make real API calls to the Redmine server
"""
import os
import sys
import unittest
import time
from datetime import datetime

# Handle import paths for both local development and CI environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from src.base import RedmineBaseClient
    from src.issues import IssueClient
    from src.projects import ProjectClient
    from src.versions import VersionClient
except ImportError:
    # Alternative import path for CI environment
    from rrmcpy.src.base import RedmineBaseClient
    from rrmcpy.src.issues import IssueClient
    from rrmcpy.src.projects import ProjectClient
    from rrmcpy.src.versions import VersionClient


class TestCreateOperations(unittest.TestCase):
    """Test 201 response handling for create operations with real API calls"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client and test data"""
        # Get configuration from environment
        cls.base_url = os.getenv('REDMINE_URL')
        cls.api_key = os.getenv('REDMINE_API_KEY')
        
        if not cls.base_url or not cls.api_key:
            raise unittest.SkipTest("REDMINE_URL and REDMINE_API_KEY environment variables must be set")
        
        # Initialize clients with configuration
        cls.base_client = RedmineBaseClient(base_url=cls.base_url, api_key=cls.api_key)
        cls.issue_client = IssueClient(base_url=cls.base_url, api_key=cls.api_key)
        cls.project_client = ProjectClient(base_url=cls.base_url, api_key=cls.api_key)
        cls.version_client = VersionClient(base_url=cls.base_url, api_key=cls.api_key)
        
        # Create a test project
        project_data = {
            "project": {
                "name": f"Test Project {int(time.time())}",
                "identifier": f"test-project-{int(time.time())}",
                "description": "Temporary project for testing"
            }
        }
        result = cls.project_client.create_project(project_data)
        if not result.get('success', False):
            raise unittest.SkipTest(f"Failed to create test project: {result}")
        cls.test_project_id = result['project']['id']
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        if hasattr(cls, 'test_project_id'):
            # Delete the test project
            cls.project_client.delete_project(cls.test_project_id)
    
    def test_create_issue_with_json_response(self):
        """Test creating an issue and verify the response contains the created issue"""
        # Create a test issue
        issue_data = {
            "issue": {
                "project_id": self.test_project_id,
                "subject": f"Test Issue {datetime.now().isoformat()}",
                "description": "This is a test issue"
            }
        }
        
        # Make the API call
        result = self.issue_client.create_issue(issue_data)
        
        # Verify the response
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertIn("issue", result)
        self.assertIn("id", result["issue"])
        
        # Store the issue ID for cleanup
        self.test_issue_id = result["issue"]["id"]
    
    def test_create_project_version(self):
        """Test creating a project version and verify the response"""
        version_data = {
            "version": {
                "name": f"Test Version {datetime.now().isoformat()}",
                "project_id": self.test_project_id,
                "status": "open"
            }
        }
        
        # Make the API call
        result = self.version_client.create_version(version_data)
        
        # Verify the response
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertIn("version", result)
        self.assertIn("id", result["version"])
        
        # Store the version ID for cleanup
        self.test_version_id = result["version"]["id"]
    
    def test_extract_id_from_location(self):
        """Test ID extraction from Location header"""
        # Create a mock response object with Location header
        class MockResponse:
            def __init__(self, location):
                self.headers = {'Location': location}
        
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
            response = MockResponse(location)
            extracted_id = self.base_client._extract_id_from_location(response)
            self.assertEqual(extracted_id, expected_id, f"Failed to extract ID from {location}")


if __name__ == '__main__':
    unittest.main()
