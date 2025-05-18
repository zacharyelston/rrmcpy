#!/usr/bin/env python3
"""
Add a note to a specific Redmine issue with a timestamp
"""
import os
import logging
import sys
import datetime
from redmine_api import RedmineAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("IssueNoteAdder")

def add_note_to_issue(issue_id, note_text):
    """Add a note to a specific issue"""
    # Get configuration from environment variables
    redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
    redmine_api_key = os.environ.get("REDMINE_API_KEY", "")
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is not set")
        sys.exit(1)
    
    logger.info(f"Connecting to Redmine at {redmine_url}")
    api = RedmineAPI(redmine_url, redmine_api_key, logger)
    
    # Add timestamp to the note
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    note_with_timestamp = f"{note_text}\n\nTimestamp: {timestamp}"
    
    # Create update data with the note
    update_data = {
        "notes": note_with_timestamp
    }
    
    # Update the issue
    try:
        logger.info(f"Adding note to issue #{issue_id}")
        api.update_issue(issue_id, update_data)
        logger.info(f"Successfully added note to issue #{issue_id}")
        
        # Get and display the updated issue
        issue = api.get_issue(issue_id)
        if issue and 'issue' in issue:
            logger.info(f"Issue #{issue_id} - {issue['issue'].get('subject', 'No subject')}")
            logger.info(f"Status: {issue['issue'].get('status', {}).get('name', 'Unknown')}")
            logger.info(f"Last updated: {issue['issue'].get('updated_on', 'Unknown')}")
            return True
    except Exception as e:
        logger.error(f"Error adding note to issue: {e}")
        return False
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        # If no issue ID provided, default to issue #1
        issue_id = 1
    else:
        issue_id = int(sys.argv[1])
    
    # Default note text
    note_text = "This note was added by the Redmine MCPServer"
    
    # Allow custom note text as second argument
    if len(sys.argv) >= 3:
        note_text = sys.argv[2]
    
    add_note_to_issue(issue_id, note_text)