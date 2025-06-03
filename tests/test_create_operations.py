#!/usr/bin/env python3
"""
Tests for create operations in Redmine API client
Specifically tests the fix for empty responses in create operations

Note: These tests require a real Redmine server to run against.
Set REDMINE_URL and REDMINE_API_KEY environment variables before running.
"""
import os
import sys
import unittest
import logging
import json
from requests import Response

# Add the parent directory to the path to access src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.base import RedmineBaseClient

class TestCreateOperations(unittest.TestCase):
    """Test the fix for empty responses in create operations"""
    
    @classmethod
    def setUpClass(cls):
        """Set up environment for all tests"""
        # Check for required environment variables
        cls.redmine_url = os.environ.get('REDMINE_URL')
        cls.api_key = os.environ.get('REDMINE_API_KEY')
        
        if not cls.redmine_url or not cls.api_key:
            raise unittest.SkipTest(
                "REDMINE_URL and REDMINE_API_KEY environment variables must be set to run these tests"
            )
    
    def setUp(self):
        """Set up test environment with actual clients"""
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("TestCreateOperations")
        
        # Create client using real connection to Redmine
        self.base_client = RedmineBaseClient(self.redmine_url, self.api_key, self.logger)
    
    def test_extract_id_from_location(self):
        """Test the helper method that extracts IDs from Location headers"""
        # Create a simple Response-like object with a Location header
        class MockResponse:
            def __init__(self, headers):
                self.headers = headers
        
        # Test absolute URL
        response = MockResponse({"Location": f"{self.redmine_url}/issues/42.json"})
        result = self.base_client._extract_id_from_location(response)
        self.assertEqual(result, 42, "Should extract ID 42 from absolute URL Location header")
        
        # Test relative URL
        response = MockResponse({"Location": "/issues/123"})
        result = self.base_client._extract_id_from_location(response)
        self.assertEqual(result, 123, "Should extract ID 123 from relative URL Location header")
        
        # Test no Location header
        response = MockResponse({})
        result = self.base_client._extract_id_from_location(response)
        self.assertIsNone(result, "Should return None when no Location header is present")
    
    def test_create_issue_with_minimal_data(self):
        """Test creating an issue with minimal data against real server"""
        # This test creates a real issue in the server
        self.logger.info("Creating test issue with minimal data")
        
        # First get a project to work with
        projects = self.base_client.make_request("GET", "projects.json")
        if not projects or "projects" not in projects or not projects["projects"]:
            self.skipTest("No projects available to test issue creation")
        
        # Get the first project's ID
        project_id = projects["projects"][0]["id"]
        
        # Get trackers to use a valid tracker ID
        trackers = self.base_client.make_request("GET", "trackers.json")
        if not trackers or "trackers" not in trackers or not trackers["trackers"]:
            self.skipTest("No trackers available to test issue creation")
        
        # Get the first tracker ID
        tracker_id = trackers["trackers"][0]["id"]
        
        # Get issue statuses to use a valid status ID
        statuses = self.base_client.make_request("GET", "issue_statuses.json")
        if not statuses or "issue_statuses" not in statuses or not statuses["issue_statuses"]:
            self.skipTest("No issue statuses available to test issue creation")
        
        # Get the first status ID
        status_id = statuses["issue_statuses"][0]["id"]
        
        # Create a uniquely identifiable test issue with all required fields
        test_subject = f"Test Issue - Automated Testing {os.urandom(4).hex()}"
        issue_data = {
            "issue": {
                "project_id": project_id,
                "tracker_id": tracker_id,
                "status_id": status_id,
                "subject": test_subject,
                "description": "This is a test issue created by automated tests. It can be deleted."
            }
        }
        
        # Make the request to create an issue
        result = self.base_client.make_request("POST", "issues.json", issue_data)
        
        # Verify successful creation and returned data
        self.assertIn("issue", result, "Response should contain issue data")
        self.assertIn("id", result["issue"], "Response should include issue ID")
        self.assertEqual(result["issue"]["subject"], test_subject, "Issue should have the subject we specified")
        
        # Clean up - delete the test issue if possible
        try:
            issue_id = result["issue"]["id"]
            self.logger.info(f"Cleaning up test issue ID: {issue_id}")
            self.base_client.make_request("DELETE", f"issues/{issue_id}.json")
        except Exception as e:
            self.logger.warning(f"Cleanup failed for issue {issue_id if 'issue_id' in locals() else 'unknown'}: {e}")
    
    def test_create_version_with_date(self):
        """Test creating a version with a date field against real server"""
        # First get a project to work with
        projects = self.base_client.make_request("GET", "projects.json")
        
        if not projects or "projects" not in projects or not projects["projects"]:
            self.skipTest("No projects available to test version creation")
        
        # Get the first project ID
        project_id = projects["projects"][0]["id"]
        
        # Create a uniquely identifiable test version
        test_name = f"TestVersion-{os.urandom(4).hex()}"
        version_data = {
            "version": {
                "name": test_name,
                "description": "This is a test version created by automated tests.",
                "status": "open",
                "due_date": "2025-12-31"
            }
        }
        
        # Make the request to create a version
        result = self.base_client.make_request(
            "POST", f"projects/{project_id}/versions.json", version_data
        )
        
        # Verify successful creation and returned data
        self.assertIn("version", result, "Response should contain version data")
        self.assertIn("id", result["version"], "Response should include version ID")
        self.assertEqual(result["version"]["name"], test_name, "Version should have the name we specified")
        self.assertEqual(result["version"]["due_date"], "2025-12-31", "Version should have the due date we specified")
        
        # Clean up - delete the test version if possible
        try:
            version_id = result["version"]["id"]
            self.logger.info(f"Cleaning up test version ID: {version_id}")
            self.base_client.make_request("DELETE", f"versions/{version_id}.json")
        except Exception as e:
            self.logger.warning(f"Cleanup failed for version {version_id if 'version_id' in locals() else 'unknown'}: {e}")
    
    def test_error_handling(self):
        """Test error handling for various scenarios"""
        # Test 404 Not Found - our base client returns error info in dict, not exception
        result = self.base_client.make_request("GET", "nonexistent_resource.json")
        self.assertTrue(result.get("error", False), "Should indicate error for 404")
        self.assertEqual(result.get("status_code"), 404, "Should return 404 status code")
        
        # Test invalid data format / missing required fields
        result = self.base_client.make_request("POST", "issues.json", {"invalid_format": True})
        self.assertTrue(result.get("error", False), "Should indicate error for invalid data")
        self.assertEqual(result.get("status_code"), 422, "Should return 422 status code")
        self.assertIn("validation", result.get("error_code", "").lower(), "Error code should indicate validation error")
        
        # Modified test to check if we can access a specific endpoint that requires 
        # higher authorization - we'll look for a restricted admin endpoint
        # Try accessing an admin endpoint which should fail even with valid API key
        # because our test user likely doesn't have admin rights
        result = self.base_client.make_request("GET", "admin/info.json")
        
        # Verify error data - should indicate either 403 Forbidden or 404 Not Found
        self.assertTrue(result.get("error", False), "Should indicate error for restricted access")
        
        # Either 403 or 404 is acceptable depending on server configuration
        self.assertIn(result.get("status_code"), [403, 404], 
                   "Should return either 403 or 404 status code for restricted access")

if __name__ == '__main__':
    unittest.main()
