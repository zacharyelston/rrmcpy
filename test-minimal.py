#!/usr/bin/env python3
"""
Comprehensive test script to verify Docker container functionality
Tests all MCP tools to catch import and serialization issues
"""
import os
import sys
import json
from pydantic import BaseModel
sys.path.append('.')

from src.mcp_server import RedmineMCPServer, IssueCreateRequest, IssueUpdateRequest, ProjectCreateRequest

def test_json_serialization(data, source):
    """Test that a string is valid JSON"""
    try:
        if not isinstance(data, str):
            print(f"❌ {source} did not return a string, got {type(data).__name__}")
            return False
        json.loads(data)  # This will throw if not valid JSON
        print(f"✓ {source} returned valid JSON string")
        return True
    except Exception as e:
        print(f"❌ {source} failed JSON validation: {e}")
        return False

def main():
    # Get environment variables
    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    redmine_api_key = os.environ.get('REDMINE_API_KEY')
    
    if not redmine_api_key:
        print("Error: REDMINE_API_KEY environment variable not set")
        sys.exit(1)
    
    print(f"Testing connection to: {redmine_url}")
    test_failures = 0
    
    try:
        # Initialize server
        server = RedmineMCPServer(redmine_url, redmine_api_key)
        print("✓ FastMCP server initialized")
        
        # Test all MCP tool functions
        
        # 1. Test health check tool
        print("\nTesting redmine_health_check tool...")
        try:
            health_result = server.redmine_health_check()
            if not test_json_serialization(health_result, "redmine_health_check"):
                test_failures += 1
        except Exception as e:
            print(f"❌ redmine_health_check failed: {e}")
            test_failures += 1
        
        # 2. Test get current user tool
        print("\nTesting redmine_get_current_user tool...")
        try:
            user_result = server.redmine_get_current_user()
            if not test_json_serialization(user_result, "redmine_get_current_user"):
                test_failures += 1
        except Exception as e:
            print(f"❌ redmine_get_current_user failed: {e}")
            test_failures += 1
        
        # 3. Test list projects tool
        print("\nTesting redmine_list_projects tool...")
        try:
            projects_result = server.redmine_list_projects()
            if not test_json_serialization(projects_result, "redmine_list_projects"):
                test_failures += 1
            
            # Get a project_id for further tests
            projects = json.loads(projects_result)
            project_id = None
            if projects and len(projects) > 0:
                project_id = projects[0].get('identifier')
                print(f"  Using project_id: {project_id} for further tests")
        except Exception as e:
            print(f"❌ redmine_list_projects failed: {e}")
            test_failures += 1
        
        # 4. Test get project (if we have a project_id)
        if project_id:
            print("\nTesting redmine_get_project tool...")
            try:
                project_result = server.redmine_get_project(project_id)
                if not test_json_serialization(project_result, "redmine_get_project"):
                    test_failures += 1
            except Exception as e:
                print(f"❌ redmine_get_project failed: {e}")
                test_failures += 1
                
            # 5. Test list versions
            print("\nTesting redmine_list_versions tool...")
            try:
                versions_result = server.redmine_list_versions(project_id)
                if not test_json_serialization(versions_result, "redmine_list_versions"):
                    test_failures += 1
            except Exception as e:
                print(f"❌ redmine_list_versions failed: {e}")
                test_failures += 1
        
        # 6. Test list issues
        print("\nTesting redmine_list_issues tool...")
        try:
            issues_result = server.redmine_list_issues()
            if not test_json_serialization(issues_result, "redmine_list_issues"):
                test_failures += 1
                
            # Get an issue_id for further tests
            issues = json.loads(issues_result)
            issue_id = None
            if issues and len(issues) > 0:
                issue_id = issues[0].get('id')
                print(f"  Using issue_id: {issue_id} for further tests")
        except Exception as e:
            print(f"❌ redmine_list_issues failed: {e}")
            test_failures += 1
        
        # 7. Test get issue (if we have an issue_id)
        if issue_id:
            print("\nTesting redmine_get_issue tool...")
            try:
                issue_result = server.redmine_get_issue(issue_id)
                if not test_json_serialization(issue_result, "redmine_get_issue"):
                    test_failures += 1
            except Exception as e:
                print(f"❌ redmine_get_issue failed: {e}")
                test_failures += 1
        
        # 8. Test list users
        print("\nTesting redmine_list_users tool...")
        try:
            users_result = server.redmine_list_users()
            if not test_json_serialization(users_result, "redmine_list_users"):
                test_failures += 1
        except Exception as e:
            print(f"❌ redmine_list_users failed: {e}")
            test_failures += 1
        
        # 9. Test create project (READ-ONLY test to avoid side effects)
        print("\nValidating redmine_create_project tool initialization...")
        try:
            # Just check if the function exists and can be called with proper params
            if hasattr(server, 'redmine_create_project') and callable(server.redmine_create_project):
                print("✓ redmine_create_project accessible (not executed)")
            else:
                print("❌ redmine_create_project not accessible")
                test_failures += 1
        except Exception as e:
            print(f"❌ redmine_create_project validation failed: {e}")
            test_failures += 1
        
        # 10. Test create issue (READ-ONLY test to avoid side effects)
        print("\nValidating redmine_create_issue tool initialization...")
        try:
            # Just check if the function exists and can be called with proper params
            if hasattr(server, 'redmine_create_issue') and callable(server.redmine_create_issue):
                print("✓ redmine_create_issue accessible (not executed)")
            else:
                print("❌ redmine_create_issue not accessible")
                test_failures += 1
        except Exception as e:
            print(f"❌ redmine_create_issue validation failed: {e}")
            test_failures += 1
                
        # 11. Test update issue (READ-ONLY test to avoid side effects)
        print("\nValidating redmine_update_issue tool initialization...")
        try:
            # Just check if the function exists and can be called with proper params
            if hasattr(server, 'redmine_update_issue') and callable(server.redmine_update_issue):
                print("✓ redmine_update_issue accessible (not executed)")
            else:
                print("❌ redmine_update_issue not accessible")
                test_failures += 1
        except Exception as e:
            print(f"❌ redmine_update_issue validation failed: {e}")
            test_failures += 1
        
        # Report results
        print("\n=== Test Summary ===")
        if test_failures == 0:
            print("✅ All tests PASSED")
            print("Docker container test: SUCCESS")
        else:
            print(f"❌ {test_failures} tests FAILED")
            print("Docker container test: FAILED")
            sys.exit(1)
            
    except Exception as e:
        print(f"Docker container test: FAILED - {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()