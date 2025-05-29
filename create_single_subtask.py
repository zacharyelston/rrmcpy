#!/usr/bin/env python3
"""
Script to create a single subtask for the Features issue in Redmine
"""
import os
import sys
import argparse
from datetime import datetime

# Add the src directory to the path so we can import from it
sys.path.insert(0, os.path.abspath('.'))

# Make sure we can access the RedmineClient
try:
    from src.redmine_client import RedmineClient
except ImportError:
    try:
        from src.issues import IssueClient
        RedmineClient = None
    except ImportError:
        print("Error: Could not import RedmineClient or IssueClient.")
        sys.exit(1)

def create_subtask(parent_id, subject, description, project_id="rmcpy"):
    """Create a single subtask for a parent issue"""
    # Get Redmine API credentials from environment
    redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
    redmine_api_key = os.environ.get("REDMINE_API_KEY")
    
    if not redmine_api_key:
        print("Error: REDMINE_API_KEY environment variable not set")
        sys.exit(1)
    
    # Initialize the client
    if RedmineClient:
        client = RedmineClient(redmine_url, redmine_api_key)
    else:
        client = IssueClient(redmine_url, redmine_api_key)
    
    subtask_data = {
        "project_id": project_id,
        "subject": subject,
        "description": description,
        "tracker_id": 2,  # Feature tracker
        "priority_id": 2,  # Normal priority
        "parent_issue_id": parent_id  # Link to main issue as parent
    }
    
    try:
        response = client.create_issue(subtask_data)
        subtask_id = response.get("issue", {}).get("id")
        
        if subtask_id:
            print(f"Created subtask: {subject} (ID: {subtask_id})")
            return subtask_id
        else:
            print(f"Error creating subtask: {subject}")
            return None
            
    except Exception as e:
        print(f"Error creating subtask: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Create a subtask for a Redmine issue')
    parser.add_argument('--parent', type=int, required=True, help='Parent issue ID')
    parser.add_argument('--subject', type=str, required=True, help='Subject of the subtask')
    parser.add_argument('--description', type=str, required=True, help='Description of the subtask')
    parser.add_argument('--project', type=str, default="rmcpy", help='Project identifier')
    
    args = parser.parse_args()
    
    create_subtask(args.parent, args.subject, args.description, args.project)

if __name__ == "__main__":
    main()