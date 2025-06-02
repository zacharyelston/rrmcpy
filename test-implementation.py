#!/usr/bin/env python3
"""
Comprehensive test script for Redmine MCP Server implementation
Tests the single Windsurf-compatible instance method implementation
"""
import argparse
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("test-implementation")

# Import both server implementations
try:
    from src.mcp_server import RedmineMCPServer
except ImportError as e:
    logger.error(f"Failed to import server implementation: {e}")
    logger.error("Make sure you're running this script from the project root directory")
    sys.exit(1)


def validate_json_response(response: str, context: str) -> Dict[str, Any]:
    """Validate that a response is valid JSON and not an error"""
    try:
        result = json.loads(response)
        if isinstance(result, dict) and "error" in result:
            logger.error(f"Error in {context}: {result['error']}")
            return result
        logger.info(f"Valid JSON response from {context}")
        return result
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON response from {context}: {response[:100]}...")
        return {"error": "Invalid JSON response"}


def test_server(server_cls, name: str) -> bool:
    """
    Test a specific server implementation
    
    Args:
        server_cls: Server class to test
        name: Name of the implementation for logging
        
    Returns:
        True if all tests pass, False otherwise
    """
    # Get configuration from environment
    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    redmine_api_key = os.environ.get('REDMINE_API_KEY')
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is required")
        return False
    
    logger.info(f"Testing {name} implementation with URL: {redmine_url}")
    
    # Create server instance
    try:
        server = server_cls(redmine_url, redmine_api_key)
        logger.info(f"Successfully created {name} server instance")
    except Exception as e:
        logger.error(f"Failed to create server instance: {e}")
        return False
    
    # Test all tools
    all_tests_passed = True
    
    # 1. Test health check
    try:
        logger.info("Testing health_check...")
        health_response = server.redmine_health_check()
        health_data = validate_json_response(health_response, "health_check")
        if health_data.get("status") != "healthy":
            logger.error(f"Unhealthy status: {health_data}")
            all_tests_passed = False
    except Exception as e:
        logger.error(f"Health check error: {e}")
        all_tests_passed = False
    
    # 2. Test current user
    try:
        logger.info("Testing get_current_user...")
        user_response = server.redmine_get_current_user()
        user_data = validate_json_response(user_response, "get_current_user")
        if "id" not in user_data:
            logger.error(f"Invalid user data: {user_data}")
            all_tests_passed = False
        else:
            logger.info(f"Current user: {user_data.get('login')} (ID: {user_data.get('id')})")
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        all_tests_passed = False
    
    # 3. Test list projects
    try:
        logger.info("Testing list_projects...")
        projects_response = server.redmine_list_projects()
        projects_data = validate_json_response(projects_response, "list_projects")
        if not isinstance(projects_data, list):
            logger.error(f"Invalid projects data: {projects_data}")
            all_tests_passed = False
        else:
            logger.info(f"Found {len(projects_data)} projects")
            # Test first project if available
            if projects_data:
                first_project = projects_data[0]
                project_id = first_project.get("identifier")
                
                # 4. Test get project
                try:
                    logger.info(f"Testing get_project with ID: {project_id}...")
                    project_response = server.redmine_get_project(project_id)
                    project_data = validate_json_response(project_response, "get_project")
                    if project_data.get("identifier") != project_id:
                        logger.error(f"Project ID mismatch: {project_data}")
                        all_tests_passed = False
                    else:
                        logger.info(f"Project name: {project_data.get('name')}")
                        
                        # 5. Test list versions for this project
                        try:
                            logger.info(f"Testing list_versions for project: {project_id}...")
                            versions_response = server.redmine_list_versions(project_id)
                            versions_data = validate_json_response(versions_response, "list_versions")
                            if not isinstance(versions_data, list):
                                logger.error(f"Invalid versions data: {versions_data}")
                                all_tests_passed = False
                            else:
                                logger.info(f"Found {len(versions_data)} versions for project {project_id}")
                        except Exception as e:
                            logger.error(f"List versions error: {e}")
                            all_tests_passed = False
                        
                        # 6. Test list issues for this project
                        try:
                            logger.info(f"Testing list_issues for project: {project_id}...")
                            issues_response = server.redmine_list_issues(project_id=project_id, limit=5)
                            issues_data = validate_json_response(issues_response, "list_issues")
                            if not isinstance(issues_data, list):
                                logger.error(f"Invalid issues data: {issues_data}")
                                all_tests_passed = False
                            else:
                                logger.info(f"Found {len(issues_data)} issues for project {project_id}")
                                
                                # 7. Test get issue if any issues exist
                                if issues_data:
                                    first_issue = issues_data[0]
                                    issue_id = first_issue.get("id")
                                    
                                    try:
                                        logger.info(f"Testing get_issue with ID: {issue_id}...")
                                        issue_response = server.redmine_get_issue(issue_id)
                                        issue_data = validate_json_response(issue_response, "get_issue")
                                        if issue_data.get("id") != issue_id:
                                            logger.error(f"Issue ID mismatch: {issue_data}")
                                            all_tests_passed = False
                                        else:
                                            logger.info(f"Issue subject: {issue_data.get('subject')}")
                                    except Exception as e:
                                        logger.error(f"Get issue error: {e}")
                                        all_tests_passed = False
                        except Exception as e:
                            logger.error(f"List issues error: {e}")
                            all_tests_passed = False
                except Exception as e:
                    logger.error(f"Get project error: {e}")
                    all_tests_passed = False
    except Exception as e:
        logger.error(f"List projects error: {e}")
        all_tests_passed = False
    
    # 8. Test list users
    try:
        logger.info("Testing list_users...")
        users_response = server.redmine_list_users()
        users_data = validate_json_response(users_response, "list_users")
        if not isinstance(users_data, list) and not (isinstance(users_data, dict) and "error" in users_data):
            logger.error(f"Invalid users data: {users_data}")
            all_tests_passed = False
        else:
            if isinstance(users_data, list):
                logger.info(f"Found {len(users_data)} users")
            else:
                # This is expected as not all users have admin privileges
                logger.info("List users requires admin privileges - error is expected if not admin")
    except Exception as e:
        logger.error(f"List users error: {e}")
        all_tests_passed = False
    
    # Final status
    if all_tests_passed:
        logger.info(f"✅ All tests PASSED for {name} implementation")
    else:
        logger.error(f"❌ Some tests FAILED for {name} implementation")
    
    return all_tests_passed


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Test Redmine MCP server implementation")
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("TESTING MCP SERVER IMPLEMENTATION")
    logger.info("=" * 80)
    result = test_server(RedmineMCPServer, "MCP Server")
    
    # Summary
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    logger.info(f"MCP Server Implementation: {'✅ PASSED' if result else '❌ FAILED'}")
    
    if not result:
        sys.exit(1)


if __name__ == "__main__":
    main()
