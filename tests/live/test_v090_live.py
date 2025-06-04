#!/usr/bin/env python3
"""
Live integration tests for v0.9.0 critical bug fixes
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
from src.versions import VersionClient


def generate_test_id():
    """Generate a unique test ID"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


class TestLiveCreateOperations:
    """Live tests for 201 response handling"""
    
    @classmethod
    def setup_class(cls):
        """Set up test clients with real API"""
        redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        api_key = os.environ.get('REDMINE_API_KEY')
        
        if not api_key:
            pytest.skip("REDMINE_API_KEY environment variable required")
            
        cls.issue_client = IssueClient(redmine_url, api_key)
        cls.project_client = ProjectClient(redmine_url, api_key)
        cls.version_client = VersionClient(redmine_url, api_key)
        cls.test_project_id = "rrmcpy"  # Using the rrmcpy project
        cls.created_resources = []
    
    @classmethod
    def teardown_class(cls):
        """Clean up created resources"""
        for resource_type, resource_id in cls.created_resources:
            try:
                if resource_type == "issue":
                    cls.issue_client.delete_issue(resource_id)
                elif resource_type == "project":
                    cls.project_client.delete_project(resource_id)
                elif resource_type == "version":
                    cls.version_client.delete_version(resource_id)
            except:
                pass  # Ignore cleanup errors
    
    def test_create_issue_201_response(self):
        """Test that create issue handles 201 response correctly"""
        test_id = generate_test_id()
        issue_data = {
            "project_id": self.test_project_id,
            "subject": f"Test Issue 201 Response - {test_id}",
            "description": "Testing 201 response handling for v0.9.0"
        }
        
        # Create issue
        result = self.issue_client.create_issue(issue_data)
        
        # Verify response contains created issue
        assert "issue" in result, f"Response missing 'issue' key: {result}"
        assert "id" in result["issue"], f"Issue missing 'id': {result}"
        assert result["issue"]["subject"] == issue_data["subject"]
        
        # Track for cleanup
        self.created_resources.append(("issue", result["issue"]["id"]))
        
        print(f"✓ Created issue #{result['issue']['id']} successfully")
    
    def test_create_version_201_response(self):
        """Test that create version handles 201 response correctly"""
        test_id = generate_test_id()
        version_data = {
            "project_id": self.test_project_id,
            "name": f"Test Version {test_id}",
            "description": "Testing version creation for v0.9.0",
            "status": "open",
            "sharing": "none"
        }
        
        # Create version
        result = self.version_client.create_version(version_data)
        
        # Verify response
        assert "version" in result, f"Response missing 'version' key: {result}"
        assert "id" in result["version"], f"Version missing 'id': {result}"
        assert result["version"]["name"] == version_data["name"]
        
        # Track for cleanup
        self.created_resources.append(("version", result["version"]["id"]))
        
        print(f"✓ Created version #{result['version']['id']} successfully")
    
    def test_create_with_location_header(self):
        """Test ID extraction from Location header"""
        test_id = generate_test_id()
        issue_data = {
            "project_id": self.test_project_id,
            "subject": f"Test Location Header - {test_id}",
            "description": "Testing Location header ID extraction"
        }
        
        # Create issue (Redmine returns Location header)
        result = self.issue_client.create_issue(issue_data)
        
        # Should have extracted ID correctly
        assert "issue" in result
        assert "id" in result["issue"]
        assert isinstance(result["issue"]["id"], int)
        
        # Track for cleanup
        self.created_resources.append(("issue", result["issue"]["id"]))
        
        print(f"✓ Location header ID extraction working")


class TestLiveProjectTools:
    """Live tests for project management tools"""
    
    @classmethod
    def setup_class(cls