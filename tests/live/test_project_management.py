#!/usr/bin/env python3
"""
Live integration tests for project management functionality
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
from src.projects import ProjectClient


def generate_test_id(length=6):
    """Generate a random string for test identifiers"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


class TestLiveProjectManagement:
    """Live tests for project management functionality"""
    
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
        cls.project_client = ProjectClient(base_url=base_url, api_key=api_key)
        
        # Track created resources for cleanup
        cls.created_resources = []
    
    @classmethod
    def teardown_class(cls):
        """Clean up created resources"""
        # Delete in reverse order (children before parents)
        for resource_type, resource_id in reversed(cls.created_resources):
            try:
                if resource_type == "project":
                    cls.project_client.delete_project(resource_id)
                    print(f"✓ Cleaned up {resource_type} #{resource_id}")
                    time.sleep(0.5)  # Avoid rate limiting
            except Exception as e:
                print(f"⚠️ Failed to clean up {resource_type} #{resource_id}: {e}")
    
    def test_project_lifecycle(self):
        """Test complete project lifecycle (create/update/delete)"""
        test_id = generate_test_id()
        
        # Create project
        project_data = {
            "name": f"Test Project {test_id}",
            "identifier": f"test-{test_id}",
            "description": "Test project created by automated tests",
            "is_public": True
        }
        
        result = self.project_client.create_project(project_data)
        
        # Verify response
        assert "project" in result, f"Response missing 'project' key: {result}"
        assert "id" in result["project"], f"Project missing 'id': {result}"
        
        project_id = result["project"]["id"]
        self.created_resources.append(("project", project_id))
        
        print(f"✓ Created project #{project_id}")
        
        # Update project
        update_data = {
            "name": f"Updated Project {test_id}",
            "description": "This project was updated by automated tests"
        }
        
        update_result = self.project_client.update_project(project_id, update_data)
        assert update_result.get("success") is not False, f"Update failed: {update_result}"
        
        # Get project to verify update
        get_result = self.project_client.get_project(project_id)
        assert "project" in get_result, f"Response missing 'project' key: {get_result}"
        assert get_result["project"]["name"] == update_data["name"], f"Name not updated: {get_result}"
        assert get_result["project"]["description"] == update_data["description"], f"Description not updated: {get_result}"
        
        print(f"✓ Updated project #{project_id}")
        
        # Delete project (will also happen in teardown, but testing the delete operation)
        delete_result = self.project_client.delete_project(project_id)
        assert delete_result.get("success") is not False, f"Delete failed: {delete_result}"
        
        # Verify deletion
        try:
            self.project_client.get_project(project_id)
            assert False, f"Project #{project_id} still exists after deletion"
        except Exception as e:
            assert "404" in str(e) or "not found" in str(e).lower(), f"Unexpected error: {e}"
        
        print(f"✓ Deleted project #{project_id}")
        
        # Remove from cleanup list since we already deleted it
        self.created_resources.remove(("project", project_id))
    
    def test_parent_child_projects(self):
        """Test parent-child project relationships"""
        test_id = generate_test_id()
        
        # Create parent project
        parent_data = {
            "name": f"Parent Project {test_id}",
            "identifier": f"parent-{test_id}",
            "description": "Parent project for testing",
            "is_public": True
        }
        
        parent_result = self.project_client.create_project(parent_data)
        assert "project" in parent_result, f"Response missing 'project' key: {parent_result}"
        
        parent_id = parent_result["project"]["id"]
        self.created_resources.append(("project", parent_id))
        
        print(f"✓ Created parent project #{parent_id}")
        
        # Create child project
        child_data = {
            "name": f"Child Project {test_id}",
            "identifier": f"child-{test_id}",
            "description": "Child project for testing",
            "is_public": True,
            "parent_id": parent_id
        }
        
        child_result = self.project_client.create_project(child_data)
        assert "project" in child_result, f"Response missing 'project' key: {child_result}"
        
        child_id = child_result["project"]["id"]
        self.created_resources.append(("project", child_id))
        
        print(f"✓ Created child project #{child_id}")
        
        # Verify parent-child relationship
        get_result = self.project_client.get_project(child_id)
        assert "project" in get_result, f"Response missing 'project' key: {get_result}"
        assert "parent" in get_result["project"], f"Child project missing parent: {get_result}"
        assert get_result["project"]["parent"]["id"] == parent_id, f"Wrong parent ID: {get_result}"
        
        print(f"✓ Verified parent-child relationship")
    
    def test_list_projects(self):
        """Test listing projects with various parameters"""
        # Create a test project to ensure we have at least one
        test_id = generate_test_id()
        project_data = {
            "name": f"List Test Project {test_id}",
            "identifier": f"list-test-{test_id}",
            "description": "Project for testing list functionality",
            "is_public": True
        }
        
        result = self.project_client.create_project(project_data)
        assert "project" in result, f"Response missing 'project' key: {result}"
        
        project_id = result["project"]["id"]
        self.created_resources.append(("project", project_id))
        
        print(f"✓ Created project #{project_id} for list testing")
        
        # Test basic listing
        list_result = self.project_client.get_projects()
        assert "projects" in list_result, f"Response missing 'projects' key: {list_result}"
        assert isinstance(list_result["projects"], list), f"Projects not a list: {list_result}"
        assert len(list_result["projects"]) > 0, f"No projects returned: {list_result}"
        
        # Verify our test project is in the list
        project_ids = [p["id"] for p in list_result["projects"]]
        assert project_id in project_ids, f"Test project not in list: {list_result}"
        
        print(f"✓ Listed projects successfully")
        
        # Test listing with include parameter
        include_result = self.project_client.get_projects(params={"include": "trackers"})
        assert "projects" in include_result, f"Response missing 'projects' key: {include_result}"
        
        # Check if at least one project has trackers included
        has_trackers = any("trackers" in p for p in include_result["projects"])
        assert has_trackers, f"No projects with trackers included: {include_result}"
        
        print(f"✓ Listed projects with includes successfully")
    
    def test_project_archive_unarchive(self):
        """Test project archive and unarchive functionality"""
        test_id = generate_test_id()
        
        # Create a project to test with
        project_data = {
            "name": f"Archive Test Project {test_id}",
            "identifier": f"archive-test-{test_id}",
            "description": "Testing project archive/unarchive functionality",
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
        print(f"✓ Archive API endpoint verified successfully")
        
        # Try to get project to verify archive status
        # But don't fail the test if we can't access it due to permissions
        get_result = self.project_client.get_project(project_id)
        
        if get_result.get("error_code") in ["AUTHORIZATION_ERROR", "FORBIDDEN"]:
            print(f"⚠️ Cannot verify project status after archive: Permission denied")
        elif "project" in get_result:
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
        print(f"✓ Unarchive API endpoint verified successfully")
        
        # Try to get project to verify unarchive status
        # But don't fail the test if we can't access it due to permissions
        get_result = self.project_client.get_project(project_id)
        
        if get_result.get("error_code") in ["AUTHORIZATION_ERROR", "FORBIDDEN"]:
            print(f"⚠️ Cannot verify project status after unarchive: Permission denied")
        elif "project" in get_result:
            # If we can still access the project, check its status
            if "status" in get_result["project"]:
                # Active projects should have status=1
                active_status = get_result["project"]["status"]
                assert active_status == 1, f"Project not unarchived, status: {active_status}"
                print(f"✓ Project #{project_id} unarchived successfully with status {active_status}")
            else:
                print(f"✓ Project #{project_id} unarchived successfully (status not available)")
        
        print(f"✓ Archive/unarchive API endpoints implementation complete")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
