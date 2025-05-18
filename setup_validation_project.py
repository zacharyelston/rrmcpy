#!/usr/bin/env python3
"""
Script to set up validation project structure in Redmine
Creates a subproject under p1 called 'v1' for validation
Creates issues for each module to track validation status
"""
import os
import sys
import logging
import json
from modules.redmine_client import RedmineClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("ValidationSetup")

def setup_validation_project():
    """Set up validation project structure in Redmine"""
    # Get configuration from environment
    redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
    redmine_api_key = os.environ.get("REDMINE_API_KEY", "")
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is not set")
        sys.exit(1)
    
    logger.info(f"Connecting to Redmine at {redmine_url}")
    client = RedmineClient(redmine_url, redmine_api_key, logger)
    
    try:
        # 1. Find the p1 project
        logger.info("Looking for p1 project...")
        projects = client.get_projects()['projects']
        p1_project = None
        for project in projects:
            if project['identifier'] == 'p1':
                p1_project = project
                logger.info(f"Found p1 project (ID: {p1_project['id']})")
                break
        
        if not p1_project:
            logger.error("Could not find p1 project")
            sys.exit(1)
        
        # 2. Check if v1 subproject already exists
        logger.info("Checking for existing v1 subproject...")
        v1_project = None
        for project in projects:
            if project['identifier'] == 'v1':
                v1_project = project
                logger.info(f"Found existing v1 project (ID: {v1_project['id']})")
                break
        
        # 3. Create v1 subproject if it doesn't exist
        if not v1_project:
            logger.info("Creating v1 subproject...")
            project_data = {
                "name": "Validation",
                "identifier": "v1",
                "description": "Validation project for rrmcpy",
                "is_public": True,
                "parent_id": p1_project['id']
            }
            result = client.create_project(project_data)
            v1_project = result['project']
            logger.info(f"Created v1 project (ID: {v1_project['id']})")
        
        # 4. Define modules to validate
        modules = [
            {"name": "Base Client", "identifier": "base", "description": "Base client functionality"},
            {"name": "Issues Module", "identifier": "issues", "description": "Issue-related operations"},
            {"name": "Projects Module", "identifier": "projects", "description": "Project-related operations"},
            {"name": "Versions Module", "identifier": "versions", "description": "Version-related operations"},
            {"name": "Users Module", "identifier": "users", "description": "User-related operations"},
            {"name": "Groups Module", "identifier": "groups", "description": "Group-related operations"},
            {"name": "Roadmap Module", "identifier": "roadmap", "description": "Roadmap and version tagging functionality"},
            {"name": "MCP Protocol", "identifier": "mcp", "description": "MCP protocol implementation"}
        ]
        
        # 5. Create issues for each module
        created_issues = []
        for module in modules:
            logger.info(f"Creating issue for {module['name']}...")
            issue_data = {
                "project_id": v1_project['id'],
                "subject": f"Validate: {module['name']}",
                "description": f"Validation tracking for {module['identifier']} module.\n\n"
                               f"{module['description']}\n\n"
                               f"This issue will be updated by the test suite to track validation status.",
                "tracker_id": 1,  # Bug tracker
                "priority_id": 2  # Normal priority
            }
            result = client.create_issue(issue_data)
            issue_id = result['issue']['id']
            created_issues.append({
                "module": module['identifier'],
                "issue_id": issue_id,
                "name": module['name']
            })
            logger.info(f"Created issue #{issue_id} for {module['name']}")
            
            # Add initial note
            update_data = {
                "notes": "Issue created for validation tracking. This issue will be updated by the test suite."
            }
            client.update_issue(issue_id, update_data)
        
        # 6. Create a master validation issue
        logger.info("Creating master validation issue...")
        master_issue_data = {
            "project_id": v1_project['id'],
            "subject": "Master Validation Status",
            "description": "Master issue for tracking overall validation status.\n\n"
                          "This issue tracks the validation status for all modules.",
            "tracker_id": 1,  # Bug tracker
            "priority_id": 2  # Normal priority
        }
        result = client.create_issue(master_issue_data)
        master_issue_id = result['issue']['id']
        logger.info(f"Created master validation issue #{master_issue_id}")
        
        # Add note with links to validation issues
        note = "# Validation Issues\n\n"
        for issue in created_issues:
            note += f"- #{issue['issue_id']} - {issue['name']}\n"
        
        update_data = {
            "notes": note
        }
        client.update_issue(master_issue_id, update_data)
        
        # 7. Save issue IDs to a file for reference
        logger.info("Saving issue IDs to validation_issues.json...")
        validation_data = {
            "project_id": v1_project['id'],
            "master_issue_id": master_issue_id,
            "modules": created_issues
        }
        
        with open('validation_issues.json', 'w') as f:
            json.dump(validation_data, f, indent=2)
        
        logger.info("Validation project setup complete!")
        logger.info(f"Project: {v1_project['name']} (ID: {v1_project['id']})")
        logger.info(f"Master issue: #{master_issue_id}")
        logger.info("Module issues:")
        for issue in created_issues:
            logger.info(f"  {issue['module']}: #{issue['issue_id']}")
        
    except Exception as e:
        logger.error(f"Error setting up validation project: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    setup_validation_project()