#!/usr/bin/env python3
"""
Test script for Redmine roadmap and version tagging functionality
"""
import os
import sys
import json
import time
import random
import datetime
# Add the parent directory to path so we can import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.redmine_client import RedmineClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("RoadmapTest")

def test_roadmap_features():
    """Test the roadmap and version tagging features"""
    # Get configuration from environment
    redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
    redmine_api_key = os.environ.get("REDMINE_API_KEY", "")
    
    # For automated test environment
    if not redmine_api_key and os.path.exists('/run/secrets/REDMINE_API_KEY'):
        try:
            with open('/run/secrets/REDMINE_API_KEY', 'r') as f:
                redmine_api_key = f.read().strip()
        except Exception as e:
            logger.warning(f"Could not read REDMINE_API_KEY from secrets: {e}")
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is not set")
        return  # Return instead of exiting to allow pytest to continue with other tests
    
    logger.info(f"Starting roadmap tests against Redmine at {redmine_url}")
    
    # Initialize the client
    client = RedmineClient(redmine_url, redmine_api_key, logger)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_id = ''.join(random.choices('0123456789abcdef', k=6))
    test_id = f"TEST-{timestamp}-{random_id}"
    
    try:
        # Find the p1 test project
        projects = client.get_projects()['projects']
        test_project_id = None
        for project in projects:
            if project['identifier'] == 'p1':
                test_project_id = project['id']
                logger.info(f"Found test project 'p1' with ID {test_project_id}")
                break
                
        if not test_project_id:
            logger.warning("Test project 'p1' not found, using first project")
            test_project_id = projects[0]['id']
        
        # 1. Create a feature roadmap with multiple versions
        print("\n=== Creating Feature Roadmap ===")
        versions = []
        
        # Create version for current sprint
        current_sprint = {
            "name": f"Sprint {timestamp}-{random_id}-Current",
            "description": "Current sprint with active development tasks",
            "status": "open",
            "due_date": (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        }
        result = client.roadmap.create_roadmap_version(test_project_id, 
                                                    current_sprint["name"],
                                                    current_sprint["description"],
                                                    current_sprint["status"],
                                                    current_sprint["due_date"])
        current_version_id = result["version"]["id"]
        versions.append(current_version_id)
        logger.info(f"Created current sprint version: {result['version']['name']} (ID: {current_version_id})")
        
        # Create version for next milestone
        next_milestone = {
            "name": f"Milestone {timestamp}-{random_id}-Next",
            "description": "Next milestone for upcoming features",
            "status": "open",
            "due_date": (datetime.datetime.now() + datetime.timedelta(days=45)).strftime("%Y-%m-%d")
        }
        result = client.roadmap.create_roadmap_version(test_project_id, 
                                                    next_milestone["name"],
                                                    next_milestone["description"],
                                                    next_milestone["status"],
                                                    next_milestone["due_date"])
        next_version_id = result["version"]["id"]
        versions.append(next_version_id)
        logger.info(f"Created next milestone version: {result['version']['name']} (ID: {next_version_id})")
        
        # Create version for future release
        future_release = {
            "name": f"Release {timestamp}-{random_id}-Future",
            "description": "Future release with planned features",
            "status": "open",
            "due_date": (datetime.datetime.now() + datetime.timedelta(days=90)).strftime("%Y-%m-%d")
        }
        result = client.roadmap.create_roadmap_version(test_project_id, 
                                                   future_release["name"],
                                                   future_release["description"],
                                                   future_release["status"],
                                                   future_release["due_date"])
        future_version_id = result["version"]["id"]
        versions.append(future_version_id)
        logger.info(f"Created future release version: {result['version']['name']} (ID: {future_version_id})")
        
        # 2. Create issues for each milestone
        print("\n=== Creating Feature Issues for Roadmap ===")
        created_issues = []
        
        # Create issue for current sprint
        current_issue_data = {
            "project_id": test_project_id,
            "subject": f"{test_id}: Current Sprint Feature",
            "description": "This is a feature planned for the current sprint",
            "priority_id": 2,  # Normal priority
            "fixed_version_id": current_version_id  # Tag with version
        }
        result = client.create_issue(current_issue_data)
        current_issue_id = result["issue"]["id"]
        created_issues.append(current_issue_id)
        logger.info(f"Created issue #{current_issue_id} for current sprint")
        
        # Create issue for next milestone
        next_issue_data = {
            "project_id": test_project_id,
            "subject": f"{test_id}: Next Milestone Feature",
            "description": "This is a feature planned for the next milestone",
            "priority_id": 2,  # Normal priority
            "fixed_version_id": next_version_id  # Tag with version
        }
        result = client.create_issue(next_issue_data)
        next_issue_id = result["issue"]["id"]
        created_issues.append(next_issue_id)
        logger.info(f"Created issue #{next_issue_id} for next milestone")
        
        # Create issue for future release
        future_issue_data = {
            "project_id": test_project_id,
            "subject": f"{test_id}: Future Release Feature",
            "description": "This is a feature planned for a future release",
            "priority_id": 2,  # Normal priority
            "fixed_version_id": future_version_id  # Tag with version
        }
        result = client.create_issue(future_issue_data)
        future_issue_id = result["issue"]["id"]
        created_issues.append(future_issue_id)
        logger.info(f"Created issue #{future_issue_id} for future release")
        
        # 3. Demonstrate getting issues by version
        print("\n=== Getting Issues by Version ===")
        for version_id in versions:
            result = client.roadmap.get_issues_by_version(version_id)
            issues = result.get("issues", [])
            version_info = client.roadmap.get_version(version_id)["version"]
            print(f"Version: {version_info['name']} - Due: {version_info.get('due_date', 'None')}")
            print(f"Found {len(issues)} issues:")
            for issue in issues:
                print(f"  - #{issue['id']}: {issue['subject']}")
            print()
        
        # 4. Demonstrate updating a version (e.g., changing due date)
        print("\n=== Updating Version ===")
        updated_due_date = (datetime.datetime.now() + datetime.timedelta(days=21)).strftime("%Y-%m-%d")
        update_data = {
            "due_date": updated_due_date,
            "description": f"{current_sprint['description']} (Updated)"
        }
        client.roadmap.update_version(current_version_id, update_data)
        updated_version = client.roadmap.get_version(current_version_id)["version"]
        print(f"Updated version {updated_version['name']}:")
        print(f"  - Due date: {updated_version['due_date']}")
        print(f"  - Description: {updated_version['description']}")
        
        # 5. Demonstrate moving an issue between versions (re-tagging)
        print("\n=== Moving Issue Between Versions ===")
        # Move the current sprint issue to next milestone
        client.roadmap.tag_issue_with_version(current_issue_id, next_version_id)
        updated_issue = client.get_issue(current_issue_id)["issue"]
        print(f"Moved issue #{current_issue_id} from Current Sprint to Next Milestone")
        print(f"  - Issue: {updated_issue['subject']}")
        print(f"  - Now in version: {updated_issue['fixed_version']['name']}")
        
        # Ask user if they want to keep the test roadmap or clean up
        keep_roadmap = input("\nKeep the test roadmap items for reference? (y/n): ").lower() == 'y'
        
        if not keep_roadmap:
            print("\n=== Cleaning Up ===")
            # Delete created issues
            for issue_id in created_issues:
                client.delete_issue(issue_id)
                logger.info(f"Deleted issue #{issue_id}")
            
            # Delete created versions
            for version_id in versions:
                client.roadmap.delete_version(version_id)
                logger.info(f"Deleted version #{version_id}")
                
            print("All test roadmap items deleted")
        else:
            print("\nKeeping test roadmap items for reference")
            print("You can access these items in your Redmine project")
        
    except Exception as e:
        logger.error(f"Error in roadmap test: {e}")
        import traceback
        traceback.print_exc()
    
if __name__ == "__main__":
    test_roadmap_features()