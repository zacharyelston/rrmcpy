#!/usr/bin/env python3
"""
Interactive demo for Redstone Redmine API
This script provides direct interaction with your Redstone Redmine instance
"""
import os
import logging
import json
import sys
from redmine_api import RedmineAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("RedstoneDemo")

# Get API key from environment
redmine_url = "https://redstone.redminecloud.net"
redmine_api_key = os.environ.get("REDMINE_API_KEY")

if not redmine_api_key:
    logger.error("REDMINE_API_KEY environment variable is not set")
    sys.exit(1)

# Initialize Redmine API client
api = RedmineAPI(redmine_url, redmine_api_key, logger)

# Helper function to pretty print JSON
def print_json(data):
    print(json.dumps(data, indent=2))

def menu():
    """Display the menu of available actions"""
    print("\n=== Redstone Redmine Demo ===")
    print("1. Get Current User")
    print("2. List Projects")
    print("3. List Issues")
    print("4. Create a Test Issue")
    print("5. Get Issue Details")
    print("6. List Users")
    print("7. List Groups")
    print("0. Exit")
    return input("Enter your choice: ")

def get_current_user():
    """Get the current user information"""
    try:
        result = api.get_current_user()
        print("\nCurrent User:")
        print_json(result)
    except Exception as e:
        logger.error(f"Error getting current user: {e}")

def list_projects():
    """List all projects"""
    try:
        result = api.get_projects()
        projects = result.get('projects', [])
        print(f"\nProjects ({len(projects)}):")
        print_json(result)
    except Exception as e:
        logger.error(f"Error getting projects: {e}")

def list_issues():
    """List all issues"""
    try:
        result = api.get_issues()
        issues = result.get('issues', [])
        print(f"\nIssues ({len(issues)}):")
        print_json(result)
    except Exception as e:
        logger.error(f"Error getting issues: {e}")

def create_test_issue():
    """Create a test issue"""
    try:
        # Get the available projects to select
        projects = api.get_projects().get('projects', [])
        if not projects:
            print("No projects available to create an issue")
            return
        
        print("\nAvailable Projects:")
        for i, project in enumerate(projects):
            print(f"{i+1}. {project['name']} (ID: {project['id']})")
        
        selection = input("Select a project number: ")
        try:
            project_index = int(selection) - 1
            if project_index < 0 or project_index >= len(projects):
                raise ValueError()
            project_id = projects[project_index]['id']
        except (ValueError, IndexError):
            print("Invalid selection")
            return
        
        # Create the issue
        issue_data = {
            "project_id": project_id,
            "subject": "Test issue created from MCP Demo",
            "description": "This is a test issue created from the Redstone Redmine MCP Demo script.",
            "priority_id": 2,  # Normal priority
            "tracker_id": 1  # Bug tracker
        }
        
        result = api.create_issue(issue_data)
        print("\nIssue Created:")
        print_json(result)
    except Exception as e:
        logger.error(f"Error creating issue: {e}")

def get_issue_details():
    """Get details of a specific issue"""
    try:
        issue_id = input("Enter issue ID: ")
        try:
            issue_id = int(issue_id)
        except ValueError:
            print("Invalid issue ID")
            return
        
        result = api.get_issue(issue_id)
        print(f"\nIssue {issue_id} Details:")
        print_json(result)
    except Exception as e:
        logger.error(f"Error getting issue details: {e}")

def list_users():
    """List all users"""
    try:
        result = api.get_users()
        users = result.get('users', [])
        print(f"\nUsers ({len(users)}):")
        print_json(result)
    except Exception as e:
        logger.error(f"Error getting users: {e}")

def list_groups():
    """List all groups"""
    try:
        result = api.get_groups()
        groups = result.get('groups', [])
        print(f"\nGroups ({len(groups)}):")
        print_json(result)
    except Exception as e:
        logger.error(f"Error getting groups: {e}")

def main():
    """Main function to handle user interaction"""
    print(f"Connected to Redstone Redmine at {redmine_url}")
    
    while True:
        choice = menu()
        
        if choice == '0':
            print("Exiting...")
            break
        elif choice == '1':
            get_current_user()
        elif choice == '2':
            list_projects()
        elif choice == '3':
            list_issues()
        elif choice == '4':
            create_test_issue()
        elif choice == '5':
            get_issue_details()
        elif choice == '6':
            list_users()
        elif choice == '7':
            list_groups()
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()