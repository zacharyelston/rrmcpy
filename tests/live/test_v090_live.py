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
    def setup_class(cls):
        """Set up test clients with real API"""
        redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        api_key = os.environ.get('REDMINE_API_KEY')
        
        if not api_key:
            pytest.skip("REDMINE_API_KEY environment variable required")
            
        cls.project_client = ProjectClient(redmine_url, api_key)
        cls.created_resources = []
    
    @classmethod
    def teardown_class(cls):
        """Clean up created resources"""
        for resource_type, resource_id in cls.created_resources:
            try:
                if resource_type == "project":
                    cls.project_client.delete_project(resource_id)
            except:
                pass  # Ignore cleanup errors
    
    def test_project_lifecycle(self):
        """Test complete project lifecycle (create/update/delete)"""
        test_id = generate_test_id()
        
        # Create project
        project_data = {
            "name": f"Test Project {test_id}",
            "identifier": f"test-{test_id}",
            "description": "Testing project lifecycle for v0.9.0",
            "is_public": True
        }
        
        result = self.project_client.create_project(project_data)
        
        # Verify response
        assert "project" in result, f"Response missing 'project' key: {result}"
        assert "id" in result["project"], f"Project missing 'id': {result}"
        assert result["project"]["name"] == project_data["name"]
        
        project_id = result["project"]["id"]
        self.created_resources.append(("project", project_id))
        
        print(f"✓ Created project #{project_id} successfully")
        
        # Update project
        update_data = {
            "description": "Updated description for testing"
        }
        
        update_result = self.project_client.update_project(project_id, update_data)
        assert update_result.get("success") is not False, f"Update failed: {update_result}"
        
        # Get project to verify update
        get_result = self.project_client.get_project(project_id)
        assert "project" in get_result, f"Response missing 'project' key: {get_result}"
        assert get_result["project"]["description"] == update_data["description"]
        
        print(f"✓ Updated project #{project_id} successfully")
    
    def test_parent_child_projects(self):
        """Test parent-child project relationships"""
        parent_id = generate_test_id()
        child_id = generate_test_id()
        
        # Create parent project
        parent_data = {
            "name": f"Parent Project {parent_id}",
            "identifier": f"parent-{parent_id}",
            "description": "Parent project for testing",
            "is_public": True
        }
        
        parent_result = self.project_client.create_project(parent_data)
        assert "project" in parent_result, f"Response missing 'project' key: {parent_result}"
        
        parent_project_id = parent_result["project"]["id"]
        self.created_resources.append(("project", parent_project_id))
        
        # Create child project
        child_data = {
            "name": f"Child Project {child_id}",
            "identifier": f"child-{child_id}",
            "description": "Child project for testing",
            "is_public": True,
            "parent_id": parent_project_id
        }
        
        child_result = self.project_client.create_project(child_data)
        assert "project" in child_result, f"Response missing 'project' key: {child_result}"
        
        child_project_id = child_result["project"]["id"]
        self.created_resources.append(("project", child_project_id))
        
        # Verify parent-child relationship
        get_result = self.project_client.get_project(child_project_id)
        assert "project" in get_result, f"Response missing 'project' key: {get_result}"
        assert "parent" in get_result["project"], f"Child project missing 'parent' key: {get_result}"
        assert get_result["project"]["parent"]["id"] == parent_project_id
        
        print(f"✓ Parent-child project relationship verified")
    
    def test_list_projects(self):
        """Test listing projects with the redmine-list-projects tool"""
        # Get all projects
        result = self.project_client.get_projects()
        
        # Verify response structure
        assert "projects" in result, f"Response missing 'projects' key: {result}"
        assert isinstance(result["projects"], list), f"Projects is not a list: {result}"
        assert len(result["projects"]) > 0, "No projects returned"
        
        # Verify project structure
        project = result["projects"][0]
        assert "id" in project, f"Project missing 'id': {project}"
        assert "name" in project, f"Project missing 'name': {project}"
        assert "identifier" in project, f"Project missing 'identifier': {project}"
        
        print(f"✓ Listed {len(result['projects'])} projects successfully")
        
        # Test with include parameter
        include_result = self.project_client.get_projects({"include": "trackers"})
        
        # Verify included associations
        assert "projects" in include_result, f"Response missing 'projects' key: {include_result}"
        if len(include_result["projects"]) > 0:
            project = include_result["projects"][0]
            # Some projects might not have trackers, so we don't assert this
            if "trackers" in project:
                assert isinstance(project["trackers"], list), f"Trackers is not a list: {project}"
                print(f"✓ Included trackers in project listing successfully")
                
    def test_project_archive_unarchive(self):
        """Test project archive and unarchive functionality"""
        test_id = generate_test_id()
        
        # Create a project to test with
        project_data = {
            "name": f"Archive Test Project {test_id}",
            "identifier": f"archive-test-{test_id}",
            "description": "Testing project archive/unarchive for v0.9.0",
            "is_public": True
        }
        
        result = self.project_client.create_project(project_data)
        
        # Verify response
        assert "project" in result, f"Response missing 'project' key: {result}"
        assert "id" in result["project"], f"Project missing 'id': {result}"
        
        project_id = result["project"]["id"]
        self.created_resources.append(("project", project_id))
        
        print(f"✓ Created project #{project_id} for archive testing")
        
        # Check if current user has admin permissions by attempting to archive
        archive_result = self.project_client.archive_project(project_id)
        
        # If we get an authorization error, skip the rest of the test
        if archive_result.get("error_code") in ["AUTHORIZATION_ERROR", "FORBIDDEN"]:
            print(f"⚠️ Skipping archive/unarchive test: User lacks admin permissions")
            pytest.skip("User lacks admin permissions for archive/unarchive operations")
            return
            
        # No permission error, continue with test
        assert archive_result.get("success") is not False, f"Archive failed: {archive_result}"
        
        # Get project to verify archive status
        get_result = self.project_client.get_project(project_id)
        assert "project" in get_result, f"Response missing 'project' key: {get_result}"
        
        # If we can still access the project, check its status
        if "status" in get_result["project"]:
            # In RedMica, archived projects have status=9
            # If the API returns a different status code, adapt the test accordingly
            archived_status = get_result["project"]["status"]
            assert archived_status != 1, f"Project not archived, status is still active: {archived_status}"
            print(f"✓ Project #{project_id} archived successfully with status {archived_status}")
        else:
            print(f"✓ Project #{project_id} archived successfully (status not available)")
        
        # Unarchive the project
        unarchive_result = self.project_client.unarchive_project(project_id)
        assert unarchive_result.get("success") is not False, f"Unarchive failed: {unarchive_result}"
        
        # Get project to verify unarchive status
        get_result = self.project_client.get_project(project_id)
        assert "project" in get_result, f"Response missing 'project' key: {get_result}"
        
        # If we can still access the project, check its status
        if "status" in get_result["project"]:
            # Active projects should have status=1
            active_status = get_result["project"]["status"]
            assert active_status == 1, f"Project not unarchived, status: {active_status}"
            print(f"✓ Project #{project_id} unarchived successfully with status {active_status}")
        else:
            print(f"✓ Project #{project_id} unarchived successfully (status not available)")
        
        print(f"✓ Archive/unarchive API endpoints verified successfully")


class TestLiveErrorHandling:
    """Live tests for error handling"""
    
    @classmethod
    def setup_class(cls):
        """Set up test clients with real API"""
        redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        api_key = os.environ.get('REDMINE_API_KEY')
        
        if not api_key:
            pytest.skip("REDMINE_API_KEY environment variable required")
            
        cls.issue_client = IssueClient(redmine_url, api_key)
        cls.project_client = ProjectClient(redmine_url, api_key)
        cls.bad_client = IssueClient(redmine_url, "bad_key")
    
    def test_validation_error(self):
        """Test validation error handling"""
        # Empty data should cause validation error
        result = self.issue_client.create_issue({})
        
        # Should get structured error
        assert result.get("error") is True or "errors" in result
        
        if result.get("error") is True:
            assert "error_code" in result
            assert result["error_code"] in ["VALIDATION_ERROR", "BAD_REQUEST"]
            assert "status_code" in result
            assert result["status_code"] in [400, 422]
        else:
            # Redmine API might return errors array instead
            assert "errors" in result
            assert isinstance(result["errors"], list)
        
        print(f"✓ Validation error handled correctly")
    
    def test_not_found_error(self):
        """Test 404 error handling"""
        # Non-existent ID should cause 404
        result = self.issue_client.get_issue(999999999)
        
        # Should get structured error
        assert result.get("error") is True
        assert "error_code" in result
        assert result["error_code"] in ["NOT_FOUND", "RESOURCE_NOT_FOUND"]
        assert "status_code" in result
        assert result["status_code"] == 404
        
        print(f"✓ 404 Not Found error handled correctly")
    
    def test_authentication_error(self):
        """Test authentication error handling"""
        # Bad API key should cause 401
        result = self.bad_client.get_issue(1)
        
        # Should get structured error
        assert result.get("error") is True
        assert "error_code" in result
        assert result["error_code"] in ["AUTHENTICATION_ERROR", "UNAUTHORIZED"]
        assert "status_code" in result
        assert result["status_code"] == 401
        
        print(f"✓ 401 Authentication error handled correctly")
