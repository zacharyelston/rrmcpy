"""
Unified Redmine API Client
Combines all feature modules into a single client
"""
import logging
from typing import Optional

from src.base import RedmineBaseClient
from src.issues import IssueClient
from src.projects import ProjectClient
from src.versions import VersionClient
from src.users import UserClient
from src.groups import GroupClient
from src.roadmap import RoadmapClient


class RedmineClient:
    """
    Unified client for all Redmine API functionality
    Combines all feature-specific modules into a single client
    """
    def __init__(self, base_url: str, api_key: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the Redmine API client
        
        Args:
            base_url: The base URL of the Redmine instance
            api_key: The API key for authentication
            logger: Optional logger instance for logging
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize feature-specific clients
        self.issues = IssueClient(base_url, api_key, logger)
        self.projects = ProjectClient(base_url, api_key, logger)
        self.versions = VersionClient(base_url, api_key, logger)
        self.users = UserClient(base_url, api_key, logger)
        self.groups = GroupClient(base_url, api_key, logger)
        self.roadmap = RoadmapClient(base_url, api_key, logger)
    
    # ===== Issues API =====
    
    def get_issues(self, params=None):
        """Get a list of issues with optional filtering"""
        return self.issues.get_issues(params)
    
    def get_issue(self, issue_id, include=None):
        """Get a specific issue by ID with optional includes"""
        return self.issues.get_issue(issue_id, include)
    
    def create_issue(self, issue_data):
        """Create a new issue"""
        return self.issues.create_issue(issue_data)
    
    def update_issue(self, issue_id, issue_data):
        """Update an existing issue"""
        return self.issues.update_issue(issue_id, issue_data)
    
    def delete_issue(self, issue_id):
        """Delete an issue"""
        return self.issues.delete_issue(issue_id)
    
    # ===== Projects API =====
    
    def get_projects(self, params=None):
        """Get a list of projects with optional filtering"""
        return self.projects.get_projects(params)
    
    def get_project(self, project_id, include=None):
        """Get a specific project by ID with optional includes"""
        return self.projects.get_project(project_id, include)
    
    def create_project(self, project_data):
        """Create a new project"""
        return self.projects.create_project(project_data)
    
    def update_project(self, project_id, project_data):
        """Update an existing project"""
        return self.projects.update_project(project_id, project_data)
    
    def delete_project(self, project_id):
        """Delete a project"""
        return self.projects.delete_project(project_id)
    
    # ===== Versions API =====
    
    def get_versions(self, project_id):
        """Get versions for a project"""
        return self.versions.get_versions(project_id)
    
    def get_version(self, version_id):
        """Get a specific version by ID"""
        return self.versions.get_version(version_id)
    
    def create_version(self, version_data):
        """Create a new version"""
        return self.versions.create_version(version_data)
    
    def update_version(self, version_id, version_data):
        """Update an existing version"""
        return self.versions.update_version(version_id, version_data)
    
    def delete_version(self, version_id):
        """Delete a version"""
        return self.versions.delete_version(version_id)
    
    # ===== Users API =====
    
    def get_users(self, params=None):
        """Get a list of users with optional filtering"""
        return self.users.get_users(params)
    
    def get_user(self, user_id, include=None):
        """Get a specific user by ID with optional includes"""
        return self.users.get_user(user_id, include)
    
    def create_user(self, user_data):
        """Create a new user"""
        return self.users.create_user(user_data)
    
    def update_user(self, user_id, user_data):
        """Update an existing user"""
        return self.users.update_user(user_id, user_data)
    
    def delete_user(self, user_id):
        """Delete a user"""
        return self.users.delete_user(user_id)
    
    def get_current_user(self):
        """Get the current user (based on API key)"""
        return self.users.get_current_user()
    
    # ===== Groups API =====
    
    def get_groups(self, params=None):
        """Get a list of groups with optional filtering"""
        return self.groups.get_groups(params)
    
    def get_group(self, group_id, include=None):
        """Get a specific group by ID with optional includes"""
        return self.groups.get_group(group_id, include)
    
    def create_group(self, group_data):
        """Create a new group"""
        return self.groups.create_group(group_data)
    
    def update_group(self, group_id, group_data):
        """Update an existing group"""
        return self.groups.update_group(group_id, group_data)
    
    def delete_group(self, group_id):
        """Delete a group"""
        return self.groups.delete_group(group_id)
    
    def add_user_to_group(self, group_id, user_id):
        """Add a user to a group"""
        return self.groups.add_user_to_group(group_id, user_id)
    
    def remove_user_from_group(self, group_id, user_id):
        """Remove a user from a group"""
        return self.groups.remove_user_from_group(group_id, user_id)
    
    # ===== Connection Management =====
    
    def health_check(self):
        """Check the health of the Redmine connection"""
        return self.issues.health_check()
    
    def configure_connection_settings(self, **kwargs):
        """Configure connection retry and timeout settings"""
        self.issues.configure_connection_settings(**kwargs)


# Main entry point for the MCP server
def main():
    """Main entry point for the Redmine MCP Server"""
    import os
    import sys
    import logging
    import argparse
    from src.fixed_mcp_server import RedmineMCPServer
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the Redmine MCP Server')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--project', type=str, default='p1', help='Test project identifier')
    args = parser.parse_args()
    
    # Get environment variables or use defaults
    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    redmine_api_key = os.environ.get('REDMINE_API_KEY', '')
    server_mode = 'test' if args.test else os.environ.get('SERVER_MODE', 'live')
    
    # Configure logging level
    log_level = os.environ.get('LOG_LEVEL', 'debug').upper()
    numeric_level = getattr(logging, log_level, logging.DEBUG)
    logger.setLevel(numeric_level)
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is required")
        sys.exit(1)
    
    # Initialize and start the server
    logger.info(f"Starting Redmine MCP Server in {server_mode} mode")
    logger.info(f"Connecting to Redmine at {redmine_url}")
    
    if server_mode == 'test':
        test_project = os.environ.get('TEST_PROJECT', args.project)
        logger.info(f"Test mode enabled - will run tests against project: {test_project}")
        # Import the test suite only if needed
        from tests.test_suite import RedmineTestSuite
        test_suite = RedmineTestSuite()
        test_suite.run_all_tests()
        test_suite.print_results()
        sys.exit(0)
    else:
        # Run the server in live mode
        logger.info("Starting Redmine MCP Server using STDIO")
        server = RedmineMCPServer(redmine_url, redmine_api_key, server_mode, logger)
        try:
            server.start()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
            server.stop()
        except Exception as e:
            logger.error(f"Server error: {e}")
            server.stop()
            sys.exit(1)