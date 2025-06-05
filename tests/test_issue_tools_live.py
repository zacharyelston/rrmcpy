#!/usr/bin/env python3
"""
Live integration tests for issue management tools, specifically tracker updates.
Tests against a real Redmine instance.
"""
import os
import sys
import pytest
import logging
import time # For unique subject

# Add the parent directory to the path to access src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.issues import IssueClient # Assuming IssueClient is in src.issues

# Tracker IDs for testing (assuming standard Redmine setup)
# You might want to fetch these dynamically or ensure they are standard in your instance
# From MEMORY: Bug: 1, Feature: 2, Support: 3
INITIAL_TRACKER_ID = 1  # Bug
NEW_TRACKER_ID = 2      # Feature
TEST_PROJECT_ID = "1"   # Project P1 as specified by user

@pytest.mark.live # Marking as a live test as per pytest.ini
@pytest.mark.integration # Marking as an integration test
@pytest.mark.skipif(
    not os.environ.get('REDMINE_API_KEY'),
    reason="REDMINE_API_KEY environment variable required for live tests"
)
def test_issue_tracker_update():
    """Test that an issue's tracker_id can be updated."""
    logger = logging.getLogger("test_issue_tracker_update_live")
    logging.basicConfig(level=logging.INFO) # Ensure logs are visible

    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    api_key = os.environ.get('REDMINE_API_KEY')

    client = IssueClient(redmine_url, api_key, logger)

    issue_id = None
    unique_subject = f"Test Issue - Tracker Update - {int(time.time())}"

    try:
        # 1. Create a new issue with the initial tracker
        logger.info(f"Creating issue '{unique_subject}' in project '{TEST_PROJECT_ID}' with tracker '{INITIAL_TRACKER_ID}'")
        create_payload = {
            "project_id": TEST_PROJECT_ID,
            "subject": unique_subject,
            "description": "Temporary issue for testing tracker update.",
            "tracker_id": INITIAL_TRACKER_ID
        }
        create_result = client.create_issue(create_payload)
        
        assert "issue" in create_result, f"Create issue failed: {create_result}"
        issue_id = create_result["issue"]["id"]
        assert create_result["issue"]["tracker"]["id"] == INITIAL_TRACKER_ID, \
            f"Initial tracker ID mismatch. Expected {INITIAL_TRACKER_ID}, got {create_result['issue']['tracker']['id']}"
        logger.info(f"✓ Created issue ID: {issue_id} with tracker ID: {INITIAL_TRACKER_ID}")

        # 2. Update the issue's tracker_id
        logger.info(f"Updating issue ID: {issue_id} to tracker ID: {NEW_TRACKER_ID}")
        update_payload = {
            "tracker_id": NEW_TRACKER_ID
        }
        # The update_issue method in IssueClient might return the updated issue or just a status.
        # Assuming it returns the updated issue or that an empty successful response is okay.
        # The actual MCP tool returns a JSON string, but client.update_issue might be different.
        # For now, we'll assume it doesn't error out.
        client.update_issue(issue_id, update_payload) 
        logger.info(f"✓ Update call for issue ID: {issue_id} completed.")

        # 3. Get the issue again to verify the tracker update
        logger.info(f"Getting updated issue ID: {issue_id}")
        get_result = client.get_issue(issue_id)
        
        assert "issue" in get_result, f"Get issue failed after update: {get_result}"
        updated_tracker_id = get_result["issue"]["tracker"]["id"]
        assert updated_tracker_id == NEW_TRACKER_ID, \
            f"Tracker ID not updated. Expected {NEW_TRACKER_ID}, got {updated_tracker_id}"
        logger.info(f"✓ Issue ID: {issue_id} successfully updated to tracker ID: {updated_tracker_id}")

        logger.info("\n✅ Issue tracker update test completed successfully!")

    except Exception as e:
        logger.error(f"Error during test_issue_tracker_update: {e}")
        raise # Re-raise the exception for pytest

    finally:
        # 4. Clean up: Delete the test issue
        if issue_id:
            try:
                logger.info(f"Cleaning up: Deleting issue ID: {issue_id}")
                client.delete_issue(issue_id)
                logger.info(f"✓ Deleted issue ID: {issue_id}")
            except Exception as e:
                logger.warning(f"Failed to clean up (delete) issue ID {issue_id}: {e}")
