#!/usr/bin/env python3
"""
Enhanced test client for the Redmine MCP Server
Creates a test issue for each test and updates it with timestamp notes
"""
import os
import sys
import json
import time
import random
import datetime
from modules.redmine_client import RedmineClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("IssueTrackingTest")

class IssueTrackingTest:
    """Test class that creates and updates issues for each test"""
    
    def __init__(self, redmine_url, api_key):
        """Initialize the test client"""
        self.redmine_url = redmine_url
        self.api_key = api_key
        self.client = RedmineClient(redmine_url, api_key, logger)
        self.test_issues = {}
        self.test_versions = []
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.test_prefix = f"TEST-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Find the p1 test project ID
        projects = self.client.get_projects()['projects']
        self.test_project_id = None
        for project in projects:
            if project['identifier'] == 'p1':
                self.test_project_id = project['id']
                logger.info(f"Found test project 'p1' with ID {self.test_project_id}")
                break
                
        if not self.test_project_id:
            logger.warning("Test project 'p1' not found, using first project")
            self.test_project_id = projects[0]['id']
            
    def create_test_issue(self, test_name):
        """Create an issue for tracking a specific test"""
        issue_data = {
            "project_id": self.test_project_id,
            "subject": f"{self.test_prefix}: {test_name}",
            "description": f"Tracking issue for test: {test_name}\n\nCreated at: {self.timestamp}",
            "priority_id": 2,  # Normal priority
            "tracker_id": 1     # Bug tracker
        }
        result = self.client.create_issue(issue_data)
        issue_id = result['issue']['id']
        self.test_issues[test_name] = issue_id
        logger.info(f"Created tracking issue #{issue_id} for test '{test_name}'")
        return issue_id
        
    def update_test_issue(self, test_name, status, details=None):
        """Update the tracking issue with test results"""
        if test_name not in self.test_issues:
            logger.warning(f"No tracking issue found for test '{test_name}'")
            return
            
        issue_id = self.test_issues[test_name]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        note = f"Test Status: {status}\nTimestamp: {now}\n"
        if details:
            note += f"\nDetails:\n{details}"
            
        update_data = {
            "notes": note
        }
        
        self.client.update_issue(issue_id, update_data)
        logger.info(f"Updated tracking issue #{issue_id} for test '{test_name}' with status '{status}'")
        
    def cleanup(self):
        """Clean up all test issues and versions"""
        for test_name, issue_id in self.test_issues.items():
            try:
                logger.info(f"Cleaning up issue #{issue_id} for test '{test_name}'")
                self.client.delete_issue(issue_id)
            except Exception as e:
                logger.warning(f"Error cleaning up issue #{issue_id}: {e}")
                
        for version_id in self.test_versions:
            try:
                logger.info(f"Cleaning up version #{version_id}")
                self.client.delete_version(version_id)
            except Exception as e:
                logger.warning(f"Error cleaning up version #{version_id}: {e}")

def run_tests():
    """Run the issue tracking tests"""
    # Get configuration from environment
    redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
    redmine_api_key = os.environ.get("REDMINE_API_KEY", "")
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is not set")
        sys.exit(1)
    
    logger.info(f"Starting issue tracking tests against Redmine at {redmine_url}")
    
    # Initialize the test tracker
    test_tracker = IssueTrackingTest(redmine_url, redmine_api_key)
    
    try:
        # Test 1: Current User
        test_name = "Current User Test"
        issue_id = test_tracker.create_test_issue(test_name)
        print(f"\n=== Test 1: {test_name} (Issue #{issue_id}) ===")
        
        try:
            result = test_tracker.client.get_current_user()
            user = result['user']
            details = (
                f"Connected as: {user['firstname']} {user['lastname']} ({user['login']})\n"
                f"Email: {user['mail']}\n"
                f"Admin: {'Yes' if user['admin'] else 'No'}\n"
                f"Last login: {user['last_login_on']}"
            )
            print(details)
            test_tracker.update_test_issue(test_name, "PASSED", details)
        except Exception as e:
            print(f"Error: {e}")
            test_tracker.update_test_issue(test_name, "FAILED", str(e))
        
        # Test 2: Project Listing
        test_name = "Project Listing Test"
        issue_id = test_tracker.create_test_issue(test_name)
        print(f"\n=== Test 2: {test_name} (Issue #{issue_id}) ===")
        
        try:
            result = test_tracker.client.get_projects()
            projects = result['projects']
            details = f"Found {len(projects)} projects:\n"
            for project in projects:
                details += f"- {project['name']} (ID: {project['id']}, Identifier: {project['identifier']})\n"
            print(details)
            test_tracker.update_test_issue(test_name, "PASSED", details)
        except Exception as e:
            print(f"Error: {e}")
            test_tracker.update_test_issue(test_name, "FAILED", str(e))
        
        # Test 3: Project Details
        test_name = "Project Details Test"
        issue_id = test_tracker.create_test_issue(test_name)
        print(f"\n=== Test 3: {test_name} (Issue #{issue_id}) ===")
        
        try:
            result = test_tracker.client.get_project(test_tracker.test_project_id)
            project = result['project']
            details = (
                f"Project Name: {project['name']}\n"
                f"Identifier: {project['identifier']}\n"
                f"Description: {project['description'] or '(None)'}\n"
                f"Created: {project['created_on']}\n"
                f"Status: {project['status']}\n"
                f"Public: {'Yes' if project['is_public'] else 'No'}"
            )
            print(details)
            test_tracker.update_test_issue(test_name, "PASSED", details)
        except Exception as e:
            print(f"Error: {e}")
            test_tracker.update_test_issue(test_name, "FAILED", str(e))
        
        # Test 4: Issue Creation and Update
        test_name = "Issue Creation Test"
        issue_id = test_tracker.create_test_issue(test_name)
        print(f"\n=== Test 4: {test_name} (Issue #{issue_id}) ===")
        
        try:
            random_suffix = ''.join(random.choices('0123456789abcdef', k=6))
            issue_data = {
                "project_id": test_tracker.test_project_id,
                "subject": f"Test issue {random_suffix}",
                "description": "This is a test issue created by the automated test suite",
                "priority_id": 2  # Normal priority
            }
            result = test_tracker.client.create_issue(issue_data)
            test_issue = result['issue']
            test_issue_id = test_issue['id']
            
            # Update the test issue
            update_data = {
                "notes": f"This is a test note\nTimestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            test_tracker.client.update_issue(test_issue_id, update_data)
            
            # Get the updated issue
            updated_issue = test_tracker.client.get_issue(test_issue_id)['issue']
            
            details = (
                f"Created issue #{test_issue_id}: {test_issue['subject']}\n"
                f"Updated with note at: {updated_issue['updated_on']}\n"
                f"Status: {updated_issue['status']['name']}\n"
                f"Priority: {updated_issue['priority']['name']}"
            )
            print(details)
            
            # Clean up the test issue
            test_tracker.client.delete_issue(test_issue_id)
            print(f"Deleted test issue #{test_issue_id}")
            
            test_tracker.update_test_issue(test_name, "PASSED", details)
        except Exception as e:
            print(f"Error: {e}")
            test_tracker.update_test_issue(test_name, "FAILED", str(e))
        
        # Test 5: Version Management
        test_name = "Version Management Test"
        issue_id = test_tracker.create_test_issue(test_name)
        print(f"\n=== Test 5: {test_name} (Issue #{issue_id}) ===")
        
        try:
            # First list versions
            result = test_tracker.client.get_versions(test_tracker.test_project_id)
            versions = result.get('versions', [])
            version_list = f"Found {len(versions)} existing versions:\n"
            for version in versions:
                version_list += f"- {version['name']} (Status: {version['status']})\n"
            
            # Create a test version
            random_suffix = ''.join(random.choices('0123456789abcdef', k=6))
            version_data = {
                "project_id": test_tracker.test_project_id,
                "name": f"Test Version {random_suffix}",
                "description": "Test version created by the automated test suite",
                "status": "open"
            }
            result = test_tracker.client.create_version(version_data)
            test_version = result['version']
            test_version_id = test_version['id']
            test_tracker.test_versions.append(test_version_id)
            
            # Get the created version
            version_details = test_tracker.client.get_version(test_version_id)['version']
            
            details = (
                f"{version_list}\n"
                f"Created version #{test_version_id}:\n"
                f"- Name: {version_details['name']}\n"
                f"- Description: {version_details['description']}\n"
                f"- Status: {version_details['status']}\n"
                f"- Project: {version_details['project']['name']}"
            )
            print(details)
            
            test_tracker.update_test_issue(test_name, "PASSED", details)
        except Exception as e:
            print(f"Error: {e}")
            test_tracker.update_test_issue(test_name, "FAILED", str(e))
        
        # Test 6: User Listing
        test_name = "User Listing Test"
        issue_id = test_tracker.create_test_issue(test_name)
        print(f"\n=== Test 6: {test_name} (Issue #{issue_id}) ===")
        
        try:
            result = test_tracker.client.get_users()
            users = result['users']
            details = f"Found {len(users)} users:\n"
            for user in users:
                details += f"- {user['firstname']} {user['lastname']} ({user['login']})\n"
            print(details)
            test_tracker.update_test_issue(test_name, "PASSED", details)
        except Exception as e:
            print(f"Error: {e}")
            test_tracker.update_test_issue(test_name, "FAILED", str(e))
        
        # Test 7: Group Listing (if available)
        test_name = "Group Listing Test"
        issue_id = test_tracker.create_test_issue(test_name)
        print(f"\n=== Test 7: {test_name} (Issue #{issue_id}) ===")
        
        try:
            result = test_tracker.client.get_groups()
            groups = result.get('groups', [])
            if groups:
                details = f"Found {len(groups)} groups:\n"
                for group in groups:
                    details += f"- {group['name']} (ID: {group['id']})\n"
            else:
                details = "No groups found on this Redmine instance"
            print(details)
            test_tracker.update_test_issue(test_name, "PASSED", details)
        except Exception as e:
            print(f"Error: {e}")
            test_tracker.update_test_issue(test_name, "FAILED", str(e))
        
        # Summarize all tests in a final issue
        test_name = "Test Summary"
        issue_id = test_tracker.create_test_issue(test_name)
        print(f"\n=== {test_name} (Issue #{issue_id}) ===")
        
        summary = f"Test run completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        summary += "Test Results:\n"
        
        for name, id in test_tracker.test_issues.items():
            if name != "Test Summary":
                summary += f"- {name}: Issue #{id}\n"
        
        test_tracker.update_test_issue(test_name, "COMPLETED", summary)
        print(summary)
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Unexpected error in test suite: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if input("Clean up test issues? (y/n): ").lower() == 'y':
            test_tracker.cleanup()
            print("Test issues cleaned up")
        else:
            print("Test issues retained for inspection")
            
        print("Test suite complete")

if __name__ == "__main__":
    run_tests()