#!/usr/bin/env python3
"""
Dedicated test script for testing Redmine issue creation
This specifically tests the redmine_create_issue functionality
"""
import json
import logging
import os
import sys
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("test-create-issue")

# Import server implementation
try:
    from src.mcp_server import RedmineMCPServer, IssueCreateRequest
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

def main():
    """Main entry point for testing issue creation"""
    # Get configuration from environment
    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    redmine_api_key = os.environ.get('REDMINE_API_KEY')
    test_project = os.environ.get('TEST_PROJECT', 'budget')
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is required")
        sys.exit(1)
    
    logger.info(f"Testing issue creation with URL: {redmine_url}")
    
    # Create server instance
    try:
        server = RedmineMCPServer(redmine_url, redmine_api_key)
        logger.info("Successfully created MCP Server instance")
    except Exception as e:
        logger.error(f"Failed to create server instance: {e}")
        sys.exit(1)
    
    # 1. First verify the project exists
    try:
        logger.info(f"Verifying project {test_project} exists...")
        project_response = server.redmine_get_project(test_project)
        project_data = validate_json_response(project_response, "get_project")
        
        if "error" in project_data:
            logger.error(f"Project {test_project} not found or not accessible")
            sys.exit(1)
            
        logger.info(f"Project found: {project_data.get('name')}")
    except Exception as e:
        logger.error(f"Error verifying project: {e}")
        sys.exit(1)
    
    # 2. Create a test issue
    try:
        logger.info("Creating test issue...")
        # Create an issue request
        issue_data = IssueCreateRequest(
            project_id=test_project,
            subject="Test Issue - " + os.environ.get('USER', 'automated test'),
            description="This is a test issue created via MCP Server to verify functionality.",
            priority_id=4  # Normal priority
        )
        
        # Call the create_issue method
        logger.info("Calling redmine_create_issue...")
        create_response = server.redmine_create_issue(issue_data)
        
        # Validate response
        issue_data = validate_json_response(create_response, "create_issue")
        
        if "error" in issue_data:
            logger.error("Failed to create issue")
            sys.exit(1)
        
        # Verify the response has the expected structure
        if not issue_data.get("id"):
            logger.error("Created issue response missing ID field")
            logger.error(f"Response: {json.dumps(issue_data, indent=2)}")
            sys.exit(1)
            
        issue_id = issue_data.get("id")
        logger.info(f"Successfully created issue with ID: {issue_id}")
        
        # 3. Verify issue can be retrieved
        logger.info(f"Verifying issue can be retrieved with ID: {issue_id}")
        get_response = server.redmine_get_issue(issue_id)
        get_data = validate_json_response(get_response, "get_issue")
        
        if "error" in get_data:
            logger.error(f"Failed to retrieve newly created issue: {issue_id}")
            sys.exit(1)
            
        logger.info(f"Successfully retrieved issue: {get_data.get('subject')}")
        logger.info("✅ Issue creation test PASSED")
        
    except Exception as e:
        logger.error(f"Error during issue creation test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
