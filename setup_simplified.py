#!/usr/bin/env python3
"""
Simplified validation project setup script
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
logger = logging.getLogger("SetupSimplified")

def main():
    # Get configuration from environment
    redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
    redmine_api_key = os.environ.get("REDMINE_API_KEY", "")
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is not set")
        sys.exit(1)
    
    # Initialize client
    client = RedmineClient(redmine_url, redmine_api_key, logger)
    
    # Find v1 project
    projects = client.get_projects()['projects']
    v1_project = None
    for project in projects:
        if project['identifier'] == 'v1':
            v1_project = project
            logger.info(f"Found v1 project (ID: {v1_project['id']})")
            break
    
    if not v1_project:
        logger.error("v1 project not found")
        sys.exit(1)
    
    # Create master validation issue
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
    
    # Module issue IDs (either already created or we need to find them)
    module_issues = []
    
    try:
        # Check if validation_issues.json exists
        if os.path.exists('validation_issues.json'):
            with open('validation_issues.json', 'r') as f:
                data = json.load(f)
                for module in data.get('modules', []):
                    module_issues.append(module)
        else:
            # Find issues by subject pattern
            result = client.get_issues({'project_id': v1_project['id']})
            issues = result.get('issues', [])
            
            for issue in issues:
                subject = issue['subject']
                if subject.startswith("Validate: "):
                    module_name = subject[len("Validate: "):]
                    # Derive module identifier from name
                    module_id = module_name.split()[0].lower()
                    module_issues.append({
                        "module": module_id,
                        "issue_id": issue['id'],
                        "name": module_name
                    })
    except Exception as e:
        logger.error(f"Error finding module issues: {e}")
    
    # Update master issue with links to module issues
    note = "# Validation Issues\n\n"
    for issue in module_issues:
        note += f"- #{issue['issue_id']} - {issue['name']}\n"
    
    update_data = {
        "notes": note
    }
    client.update_issue(master_issue_id, update_data)
    
    # Save validation issues to file
    validation_data = {
        "project_id": v1_project['id'],
        "master_issue_id": master_issue_id,
        "modules": module_issues
    }
    
    with open('validation_issues.json', 'w') as f:
        json.dump(validation_data, f, indent=2)
    
    logger.info("Saved validation issues to validation_issues.json")
    logger.info(f"Master issue: #{master_issue_id}")

if __name__ == "__main__":
    main()