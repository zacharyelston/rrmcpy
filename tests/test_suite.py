#!/usr/bin/env python3
"""
Automated test suite for Redmine MCPServer
Runs a series of tests against a specified test project
"""
import os
import logging
import json
import sys
import time
import random
import string
from datetime import datetime
from redmine_api import RedmineAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("TestSuite")

class RedmineTestSuite:
    """Test suite for Redmine MCPServer"""
    
    def __init__(self):
        # Get configuration from environment variables
        self.redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
        self.redmine_api_key = os.environ.get("REDMINE_API_KEY", "")
        self.server_mode = os.environ.get("SERVER_MODE", "test")
        self.test_project = os.environ.get("TEST_PROJECT", "p1")
        
        # Check if API key is available
        if not self.redmine_api_key:
            logger.error("REDMINE_API_KEY environment variable is not set")
            sys.exit(1)
        
        # Initialize API client
        self.api = RedmineAPI(self.redmine_url, self.redmine_api_key, logger)
        
        # Track test results
        self.results = {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "tests": []
        }
        
        # Data for cleanup
        self.created_issues = []
        self.created_projects = []
        self.created_versions = []
    
    def generate_test_data(self, prefix=""):
        """Generate random test data with timestamp"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}_{random_str}_{timestamp}"
    
    def run_test(self, test_name, test_func):
        """Run a test and record the result"""
        self.results["total"] += 1
        logger.info(f"Running test: {test_name}")
        
        start_time = time.time()
        try:
            test_func()
            duration = time.time() - start_time
            self.results["passed"] += 1
            status = "PASSED"
            logger.info(f"✅ Test {test_name} PASSED ({duration:.2f}s)")
        except Exception as e:
            duration = time.time() - start_time
            self.results["failed"] += 1
            status = "FAILED"
            logger.error(f"❌ Test {test_name} FAILED: {e} ({duration:.2f}s)")
        
        self.results["tests"].append({
            "name": test_name,
            "status": status,
            "duration": f"{duration:.2f}s"
        })
    
    def find_test_project(self):
        """Find the test project by identifier"""
        logger.info(f"Looking for test project: {self.test_project}")
        try:
            # Get all projects
            projects = self.api.get_projects().get('projects', [])
            
            # Find project by identifier
            for project in projects:
                if project.get('identifier') == self.test_project:
                    logger.info(f"Found test project: {project['name']} (ID: {project['id']})")
                    return project['id']
            
            logger.warning(f"Test project '{self.test_project}' not found")
            return None
        except Exception as e:
            logger.error(f"Error finding test project: {e}")
            return None
    
    def run_all_tests(self):
        """Run all tests in the test suite"""
        logger.info(f"Starting test suite in {self.server_mode} mode")
        logger.info(f"Redmine URL: {self.redmine_url}")
        logger.info(f"Test project: {self.test_project}")
        
        # Find the test project
        self.test_project_id = self.find_test_project()
        if not self.test_project_id and self.test_project != "auto_create":
            logger.error(f"Cannot proceed without test project")
            return
        
        # Run the tests
        self.run_test("Test Authentication", self.test_authentication)
        self.run_test("Test Get Projects", self.test_get_projects)
        
        if self.test_project_id:
            self.run_test("Test Project Details", self.test_project_details)
            self.run_test("Test Create Issue", self.test_create_issue)
            self.run_test("Test Update Issue", self.test_update_issue)
            self.run_test("Test Create Version", self.test_create_version)
        
        self.run_test("Test Get Users", self.test_get_users)
        self.run_test("Test Current User", self.test_current_user)
        
        # Clean up if in test mode
        if self.server_mode.lower() == "test":
            self.cleanup()
        
        # Print results
        self.print_results()
    
    def cleanup(self):
        """Clean up resources created during tests"""
        logger.info("Cleaning up resources created during tests...")
        
        # Delete created issues
        for issue_id in self.created_issues:
            try:
                logger.info(f"Deleting test issue {issue_id}")
                self.api.delete_issue(issue_id)
            except Exception as e:
                logger.warning(f"Error deleting issue {issue_id}: {e}")
        
        # Delete created versions
        for version_id in self.created_versions:
            try:
                logger.info(f"Deleting test version {version_id}")
                self.api.delete_version(version_id)
            except Exception as e:
                logger.warning(f"Error deleting version {version_id}: {e}")
        
        # Delete created projects (only if auto-created)
        if self.test_project == "auto_create":
            for project_id in self.created_projects:
                try:
                    logger.info(f"Deleting test project {project_id}")
                    self.api.delete_project(project_id)
                except Exception as e:
                    logger.warning(f"Error deleting project {project_id}: {e}")
    
    def print_results(self):
        """Print test results summary"""
        logger.info("\n----- TEST RESULTS -----")
        logger.info(f"Total tests: {self.results['total']}")
        logger.info(f"Passed: {self.results['passed']}")
        logger.info(f"Failed: {self.results['failed']}")
        logger.info("-----------------------")
        
        # Print individual test results
        for test in self.results["tests"]:
            status_symbol = "✅" if test["status"] == "PASSED" else "❌"
            logger.info(f"{status_symbol} {test['name']}: {test['status']} ({test['duration']})")
        
        # Print overall pass/fail
        if self.results["failed"] == 0:
            logger.info("\n✅ ALL TESTS PASSED ✅")
        else:
            logger.info(f"\n❌ {self.results['failed']} TESTS FAILED ❌")
    
    # === TEST METHODS ===
    
    def test_authentication(self):
        """Test authentication with Redmine API"""
        result = self.api.get_current_user()
        assert result and 'user' in result, "Authentication failed"
    
    def test_get_projects(self):
        """Test getting the list of projects"""
        result = self.api.get_projects()
        assert result and 'projects' in result, "Failed to get projects"
        assert isinstance(result['projects'], list), "Projects not returned as list"
    
    def test_project_details(self):
        """Test getting project details"""
        if not self.test_project_id:
            logger.warning("No test project ID available, skipping project details test")
            return
            
        result = self.api.get_project(self.test_project_id)
        assert result and 'project' in result, "Failed to get project details"
        assert result['project']['id'] == self.test_project_id, "Project ID mismatch"
    
    def test_create_issue(self):
        """Test creating an issue"""
        if not self.test_project_id:
            logger.warning("No test project ID available, skipping issue creation test")
            return
            
        issue_data = {
            "project_id": self.test_project_id,
            "subject": f"Test issue - {self.generate_test_data('MCPServer')}",
            "description": "This is a test issue created by the Redmine MCPServer test suite.",
            "priority_id": 2,  # Normal priority
            "tracker_id": 1    # Bug tracker
        }
        
        result = self.api.create_issue(issue_data)
        assert result and 'issue' in result, "Failed to create issue"
        
        issue_id = result['issue']['id']
        self.created_issues.append(issue_id)
        
        # Verify the issue was created
        issue = self.api.get_issue(issue_id)
        assert issue and 'issue' in issue, "Failed to get created issue"
        assert issue['issue']['subject'] == issue_data['subject'], "Issue subject mismatch"
    
    def test_update_issue(self):
        """Test updating an issue"""
        # Create an issue if needed
        if not self.created_issues:
            self.test_create_issue()
        
        issue_id = self.created_issues[0]
        update_data = {
            "notes": "Updated by test suite",
            "done_ratio": 50
        }
        
        # Update the issue
        self.api.update_issue(issue_id, update_data)
        
        # Verify the update
        updated_issue = self.api.get_issue(issue_id)
        assert updated_issue and 'issue' in updated_issue, "Failed to get updated issue"
        assert updated_issue['issue']['done_ratio'] == 50, "Issue done_ratio not updated"
    
    def test_create_version(self):
        """Test creating a version"""
        if not self.test_project_id:
            logger.warning("No test project ID available, skipping version creation test")
            return
            
        try:
            # Get project versions first to check if the API is available
            project_versions = self.api.get_versions(self.test_project_id)
            
            # If we're here, versions API is available
            version_data = {
                "project_id": self.test_project_id,
                "name": f"Version {self.generate_test_data('v')}",
                "description": "Test version created by MCPServer test suite",
                "status": "open"
            }
            
            result = self.api.create_version(version_data)
            assert result and 'version' in result, "Failed to create version"
            
            version_id = result['version']['id']
            self.created_versions.append(version_id)
            
            # Verify the version was created
            version = self.api.get_version(version_id)
            assert version and 'version' in version, "Failed to get created version"
            assert version['version']['name'] == version_data['name'], "Version name mismatch"
        except Exception as e:
            # Check if this is a 404 error which means versions API isn't available
            if '404' in str(e) or 'Not Found' in str(e):
                logger.warning("Versions API not available in this Redmine instance - skipping test")
                # Skip test without failing
                return
            else:
                # For other errors, re-raise
                raise
    
    def test_get_users(self):
        """Test getting the list of users"""
        result = self.api.get_users()
        assert result and 'users' in result, "Failed to get users"
        assert isinstance(result['users'], list), "Users not returned as list"
    
    def test_current_user(self):
        """Test getting current user details"""
        result = self.api.get_current_user()
        assert result and 'user' in result, "Failed to get current user"
        assert 'login' in result['user'], "User login not found"
        assert 'api_key' in result['user'], "API key not found in user details"

if __name__ == "__main__":
    test_suite = RedmineTestSuite()
    test_suite.run_all_tests()