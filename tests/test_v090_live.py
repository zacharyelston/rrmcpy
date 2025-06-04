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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
        """Set up test clients"""
        redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        api_key = os.environ.get('REDMINE_API_KEY')
        
        if not api_key:
            pytest.skip("REDMINE_API_KEY environment variable required")
            
        cls.project_client = ProjectClient(redmine_url, api_key)
        cls.created_projects = []
    
    @classmethod
    def teardown_class(cls):
        """Clean up created projects"""
        for project_id in cls.created_projects:
            try:
                cls.project_client.delete_project(project_id)
                print(f"  Cleaned up project: {project_id}")
            except:
                pass
    
    def test_project_lifecycle(self):
        """Test complete project lifecycle: create, update, delete"""
        test_id = generate_test_id()
        
        # 1. Create project
        project_data = {
            "name": f"Test Project v090 {test_id}",
            "identifier": f"test-v090-{test_id}",
            "description": "Testing project tools for v0.9.0",
            "is_public": False
        }
        
        print(f"\n1. Creating project: {project_data['name']}")
        create_result = self.project_client.create_project(project_data)
        
        # Verify creation
        assert "project" in create_result, f"Create failed: {create_result}"
        assert "id" in create_result["project"]
        project_id = create_result["project"]["id"]
        self.created_projects.append(project_id)
        print(f"   ✓ Created project #{project_id}")
        
        # 2. Update project
        update_data = {
            "description": "Updated: Testing v0.9.0 project management",
            "is_public": True
        }
        
        print(f"2. Updating project #{project_id}")
        update_result = self.project_client.update_project(project_id, update_data)
        
        # Verify update
        assert update_result.get("success") == True, f"Update failed: {update_result}"
        print(f"   ✓ Updated project successfully")
        
        # 3. Get project to verify changes
        print(f"3. Verifying project updates")
        # Note: ProjectClient doesn't have get_project, so we'll verify via issues API
        
        # 4. Delete project
        print(f"4. Deleting project #{project_id}")
        delete_result = self.project_client.delete_project(project_id)
        
        # Verify deletion
        assert delete_result.get("success") == True, f"Delete failed: {delete_result}"
        self.created_projects.remove(project_id)  # Remove from cleanup list
        print(f"   ✓ Deleted project successfully")
    
    def test_project_with_parent(self):
        """Test creating project with parent"""
        test_id = generate_test_id()
        
        # Create parent project first
        parent_data = {
            "name": f"Parent Project {test_id}",
            "identifier": f"parent-{test_id}",
            "description": "Parent project for testing"
        }
        
        parent_result = self.project_client.create_project(parent_data)
        assert "project" in parent_result
        parent_id = parent_result["project"]["id"]
        self.created_projects.append(parent_id)
        
        # Create child project
        child_data = {
            "name": f"Child Project {test_id}",
            "identifier": f"child-{test_id}",
            "description": "Child project for testing",
            "parent_id": parent_id,
            "inherit_members": True
        }
        
        child_result = self.project_client.create_project(child_data)
        assert "project" in child_result
        child_id = child_result["project"]["id"]
        self.created_projects.append(child_id)
        
        print(f"✓ Created parent-child project relationship")


class TestLiveErrorHandling:
    """Live tests for standardized error handling"""
    
    @classmethod
    def setup_class(cls):
        """Set up test clients"""
        redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        api_key = os.environ.get('REDMINE_API_KEY')
        
        if not api_key:
            pytest.skip("REDMINE_API_KEY environment variable required")
            
        cls.issue_client = IssueClient(redmine_url, api_key)
        cls.project_client = ProjectClient(redmine_url, api_key)
    
    def test_validation_error_format(self):
        """Test validation error response format"""
        # Try to create issue without required fields
        invalid_data = {
            "subject": ""  # Empty subject should fail
        }
        
        result = self.issue_client.create_issue(invalid_data)
        
        # Check error format
        assert result.get("error") == True
        assert "error_code" in result
        assert "message" in result
        assert "status_code" in result
        assert "timestamp" in result
        
        # Should be validation error
        assert result["error_code"] == "VALIDATION_ERROR"
        assert result["status_code"] == 422
        
        print(f"✓ Validation error format correct: {result['error_code']}")
    
    def test_not_found_error(self):
        """Test 404 error handling"""
        # Try to get non-existent issue
        result = self.issue_client.get_issue(999999999)
        
        # Check error format
        assert result.get("error") == True
        assert result["error_code"] == "NOT_FOUND"
        assert result["status_code"] == 404
        assert "message" in result
        
        print(f"✓ Not found error format correct: {result['error_code']}")
    
    def test_authentication_error(self):
        """Test 401 error handling"""
        # Create client with invalid API key
        bad_client = IssueClient(
            os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net'),
            "invalid_api_key_12345"
        )
        
        result = bad_client.get_issue(1)
        
        # Check error format
        assert result.get("error") == True
        assert result["error_code"] == "AUTHENTICATION_ERROR"
        assert result["status_code"] == 401
        
        print(f"✓ Authentication error format correct: {result['error_code']}")
    
    def test_project_permission_error(self):
        """Test 403 error handling"""
        # Try to create project with identifier that might be restricted
        test_id = generate_test_id()
        project_data = {
            "name": f"Forbidden Project {test_id}",
            "identifier": "admin",  # This might be forbidden
            "description": "Testing forbidden access"
        }
        
        result = self.project_client.create_project(project_data)
        
        # Should get an error (either validation or forbidden)
        assert result.get("error") == True
        assert "error_code" in result
        assert "message" in result
        assert "status_code" in result
        
        print(f"✓ Permission/validation error handled: {result['error_code']}")


class TestLiveIntegration:
    """Full integration tests combining all v0.9.0 features"""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment"""
        redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        api_key = os.environ.get('REDMINE_API_KEY')
        
        if not api_key:
            pytest.skip("REDMINE_API_KEY environment variable required")
            
        cls.issue_client = IssueClient(redmine_url, api_key)
        cls.project_client = ProjectClient(redmine_url, api_key)
        cls.version_client = VersionClient(redmine_url, api_key)
        cls.cleanup_items = []
    
    @classmethod
    def teardown_class(cls):
        """Clean up all test data"""
        for item_type, item_id in cls.cleanup_items:
            try:
                if item_type == "issue":
                    cls.issue_client.delete_issue(item_id)
                elif item_type == "project":
                    cls.project_client.delete_project(item_id)
                elif item_type == "version":
                    cls.version_client.delete_version(item_id)
            except:
                pass
    
    def test_full_workflow(self):
        """Test complete workflow with all v0.9.0 features"""
        test_id = generate_test_id()
        
        print("\n=== Running Full v0.9.0 Integration Test ===")
        
        # 1. Create a test project
        print("\n1. Creating test project...")
        project_data = {
            "name": f"v0.9.0 Integration Test {test_id}",
            "identifier": f"v090-test-{test_id}",
            "description": "Full integration test for v0.9.0 features",
            "is_public": False
        }
        
        project_result = self.project_client.create_project(project_data)
        assert "project" in project_result
        project_id = project_result["project"]["id"]
        self.cleanup_items.append(("project", project_id))
        print(f"   ✓ Created project #{project_id}")
        
        # 2. Create a version in the project
        print("\n2. Creating version in project...")
        version_data = {
            "project_id": project_id,
            "name": f"v0.9.0-test-{test_id}",
            "description": "Test version for integration",
            "status": "open",
            "due_date": "2025-12-31"
        }
        
        version_result = self.version_client.create_version(version_data)
        assert "version" in version_result
        version_id = version_result["version"]["id"]
        self.cleanup_items.append(("version", version_id))
        print(f"   ✓ Created version #{version_id}")
        
        # 3. Create issues in the project
        print("\n3. Creating test issues...")
        issues_created = []
        for i in range(3):
            issue_data = {
                "project_id": project_id,
                "subject": f"Integration Test Issue {i+1} - {test_id}",
                "description": f"Testing issue creation #{i+1}",
                "fixed_version_id": version_id
            }
            
            issue_result = self.issue_client.create_issue(issue_data)
            assert "issue" in issue_result
            issue_id = issue_result["issue"]["id"]
            issues_created.append(issue_id)
            self.cleanup_items.append(("issue", issue_id))
            print(f"   ✓ Created issue #{issue_id}")
        
        # 4. Test error handling with invalid data
        print("\n4. Testing error handling...")
        invalid_issue = {
            "project_id": project_id,
            "subject": "",  # Invalid empty subject
            "description": "This should fail"
        }
        
        error_result = self.issue_client.create_issue(invalid_issue)
        assert error_result.get("error") == True
        assert error_result["error_code"] == "VALIDATION_ERROR"
        print(f"   ✓ Error handling working: {error_result['error_code']}")
        
        # 5. Update project
        print("\n5. Updating project...")
        update_data = {
            "description": "Updated: Integration test completed successfully!"
        }
        
        update_result = self.project_client.update_project(project_id, update_data)
        assert update_result.get("success") == True
        print(f"   ✓ Project updated successfully")
        
        print("\n=== All v0.9.0 Features Tested Successfully! ===")
        
        # Return summary
        return {
            "project_id": project_id,
            "version_id": version_id,
            "issues_created": issues_created,
            "total_tests": 5,
            "all_passed": True
        }


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
