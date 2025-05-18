#!/usr/bin/env python3
"""
Script to create a 'Features' issue in Redmine with subtasks for remaining features
"""
import os
import sys
import time
from datetime import datetime

# Add the src directory to the path so we can import from it
sys.path.insert(0, os.path.abspath('.'))

# Make sure we can access the RedmineClient (or other appropriate classes)
try:
    from src.redmine_client import RedmineClient
except ImportError:
    try:
        # Try another possible location based on your repository structure
        from src.issues import IssueClient
        RedmineClient = None
    except ImportError:
        print("Error: Could not import RedmineClient or IssueClient. Make sure your src structure is correct.")
        sys.exit(1)

def main():
    # Get Redmine API credentials from environment
    redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
    redmine_api_key = os.environ.get("REDMINE_API_KEY")
    
    if not redmine_api_key:
        print("Error: REDMINE_API_KEY environment variable not set")
        sys.exit(1)
    
    # Project identifier
    project_id = "rmcpy"  # Change if your project has a different identifier
    
    print(f"Creating issues in Redmine project '{project_id}'...")
    
    # Initialize the client
    if RedmineClient:
        client = RedmineClient(redmine_url, redmine_api_key)
    else:
        client = IssueClient(redmine_url, redmine_api_key)
    
    # Create the main "Features" issue
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    main_issue_data = {
        "project_id": project_id,
        "subject": "Features - Redmine MCP Server Roadmap",
        "description": f"""# Redmine MCP Server Feature Roadmap

This issue tracks the development roadmap for the Redmine MCP Server.

## Overview
The Redmine MCP Server provides a standardized interface for interacting with Redmine through the MCP protocol, which uses STDIO for communication instead of network ports.

## Status
Created: {timestamp}
""",
        "tracker_id": 2,  # Feature tracker (adjust if your Redmine uses different tracker IDs)
        "priority_id": 2  # Normal priority
    }
    
    try:
        main_response = client.create_issue(main_issue_data)
        main_issue_id = main_response.get("issue", {}).get("id")
        if not main_issue_id:
            print("Error: Failed to get ID from the created main issue")
            sys.exit(1)
            
        print(f"Created main 'Features' issue with ID {main_issue_id}")
        
        # Create subtasks for remaining features
        subtasks = [
            {
                "subject": "Implement comprehensive error handling",
                "description": """# Error Handling Implementation

## Description
Implement robust error handling across all API endpoints to ensure graceful failure and helpful error messages.

## Tasks
- Add exception handling to all API methods
- Create standardized error response format
- Implement logging of errors with appropriate detail levels
- Add validation of input parameters
"""
            },
            {
                "subject": "Add comprehensive logging",
                "description": """# Logging Enhancements

## Description
Implement detailed logging throughout the application with configurable log levels.

## Tasks
- Add structured logging to all components
- Create log rotation configuration
- Implement different log levels (DEBUG, INFO, WARN, ERROR)
- Add contextual information to log entries (timestamp, component, request ID)
"""
            },
            {
                "subject": "Implement automatic reconnection for dropped Redmine connections",
                "description": """# Automatic Reconnection

## Description
Add capability to automatically reconnect to Redmine if the connection is dropped or times out.

## Tasks
- Implement connection pool with retry logic
- Add exponential backoff for failed connections
- Create health check mechanism to verify Redmine connectivity
- Properly handle and surface connection state to clients
"""
            },
            {
                "subject": "Add support for file attachments",
                "description": """# File Attachment Support

## Description
Implement support for uploading and downloading file attachments through the MCP interface.

## Tasks
- Create file upload endpoint
- Implement download functionality
- Add support for different file types
- Implement proper error handling for file operations
"""
            },
            {
                "subject": "Create comprehensive API documentation",
                "description": """# API Documentation

## Description
Create detailed API documentation explaining all available endpoints and their parameters.

## Tasks
- Document all API endpoints
- Create usage examples
- Add parameter descriptions and validation rules
- Generate HTML/Markdown documentation
"""
            }
        ]
        
        for idx, subtask in enumerate(subtasks, 1):
            subtask_data = {
                "project_id": project_id,
                "subject": subtask["subject"],
                "description": subtask["description"],
                "tracker_id": 2,  # Feature tracker
                "priority_id": 2,  # Normal priority
                "parent_issue_id": main_issue_id  # Link to main issue as parent
            }
            
            sub_response = client.create_issue(subtask_data)
            subtask_id = sub_response.get("issue", {}).get("id")
            
            if subtask_id:
                print(f"Created subtask {idx}/{len(subtasks)}: {subtask['subject']} (ID: {subtask_id})")
            else:
                print(f"Error creating subtask {idx}/{len(subtasks)}")
            
            # Small delay to avoid hitting API rate limits
            time.sleep(1)
        
        print(f"\nCompleted: Created main 'Features' issue (#{main_issue_id}) with {len(subtasks)} subtasks")
        
    except Exception as e:
        print(f"Error creating issues: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()