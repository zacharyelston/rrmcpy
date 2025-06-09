#!/usr/bin/env python3
"""
Live integration tests for error handling functionality
Tests run against actual Redmine API - no mocks!
"""
import os
import sys
import time
import random
import string
import pytest

# Add the parent directory to the path to access src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.base import RedmineBaseClient
from src.issues import IssueClient
from src.projects import ProjectClient


def generate_test_id(length=6):
    """Generate a random string for test identifiers"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


class TestLiveErrorHandling:
    """Live tests for error handling"""
    
    @classmethod
    def setup_class(cls):
        """Set up test clients with real API"""
        # Check for required environment variables
        required_vars = ['REDMINE_URL', 'REDMINE_API_KEY']
        for var in required_vars:
            if not os.environ.get(var):
                pytest.skip(f"Environment variable {var} not set")
        
        # Get environment variables
        base_url = os.environ.get('REDMINE_URL')
        api_key = os.environ.get('REDMINE_API_KEY')
        
        # Initialize clients
        cls.base_client = RedmineBaseClient(base_url=base_url, api_key=api_key)
        cls.issue_client = IssueClient(base_url=base_url, api_key=api_key)
        cls.project_client = ProjectClient(base_url=base_url, api_key=api_key)
        
        # Create a test project for issue operations
        test_id = generate_test_id()
        project_data = {
            "name": f"Error Test Project {test_id}",
            "identifier": f"error-test-{test_id}",
            "description": "Project for testing error handling",
            "is_public": True
        }
        
        result = cls.project_client.create_project(project_data)
        cls.test_project_id = result["project"]["id"]
        print(f"✓ Created test project #{cls.test_project_id}")
    
    @classmethod
    def teardown_class(cls):
        """Clean up test resources"""
        try:
            cls.project_client.delete_project(cls.test_project_id)
            print(f"✓ Cleaned up test project #{cls.test_project_id}")
        except Exception as e:
            print(f"⚠️ Failed to clean up test project: {e}")
    
    def test_validation_error(self):
        """Test validation error handling"""
        # Try to create an issue without required fields
        invalid_issue = {
            "project_id": self.test_project_id,
            # Missing required 'subject' field
        }
        
        try:
            self.issue_client.create_issue(invalid_issue)
            assert False, "Expected validation error but request succeeded"
        except Exception as e:
            error_str = str(e)
            assert "400" in error_str or "validation" in error_str.lower(), f"Unexpected error: {error_str}"
            
            # Check if the error response has the expected format
            if hasattr(e, "error_response"):
                error_response = e.error_response
                assert "error" in error_response, f"Missing 'error' key in response: {error_response}"
                assert "error_code" in error_response, f"Missing 'error_code' key: {error_response}"
                assert error_response["error_code"] == "VALIDATION_ERROR", f"Wrong error code: {error_response}"
        
        print("✓ Validation error handled correctly")
    
    def test_not_found_error(self):
        """Test 404 error handling"""
        # Try to get a non-existent project
        non_existent_id = 999999
        
        try:
            self.project_client.get_project(non_existent_id)
            assert False, "Expected 404 error but request succeeded"
        except Exception as e:
            error_str = str(e)
            assert "404" in error_str or "not found" in error_str.lower(), f"Unexpected error: {error_str}"
            
            # Check if the error response has the expected format
            if hasattr(e, "error_response"):
                error_response = e.error_response
                assert "error" in error_response, f"Missing 'error' key in response: {error_response}"
                assert "error_code" in error_response, f"Missing 'error_code' key: {error_response}"
                assert error_response["error_code"] == "NOT_FOUND", f"Wrong error code: {error_response}"
        
        print("✓ Not found error handled correctly")
    
    def test_authentication_error(self):
        """Test authentication error handling"""
        # Create a client with invalid API key
        invalid_client = RedmineBaseClient(api_key="invalid_key")
        
        try:
            # Try to access a protected resource
            invalid_client.get("/projects.json")
            assert False, "Expected authentication error but request succeeded"
        except Exception as e:
            error_str = str(e)
            assert "401" in error_str or "unauthorized" in error_str.lower(), f"Unexpected error: {error_str}"
            
            # Check if the error response has the expected format
            if hasattr(e, "error_response"):
                error_response = e.error_response
                assert "error" in error_response, f"Missing 'error' key in response: {error_response}"
                assert "error_code" in error_response, f"Missing 'error_code' key: {error_response}"
                assert error_response["error_code"] == "AUTHENTICATION_ERROR", f"Wrong error code: {error_response}"
        
        print("✓ Authentication error handled correctly")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
