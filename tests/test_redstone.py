#!/usr/bin/env python3
"""
Test script to verify connectivity to Redstone Redmine server
"""
import os
import logging
import sys
import json

# Add the parent directory to path so we can import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.redmine_api import RedmineAPI

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("RedstoneTest")

# Get API key from environment
redmine_url = "https://redstone.redminecloud.net"
redmine_api_key = os.environ.get("REDMINE_API_KEY")

if not redmine_api_key:
    logger.error("REDMINE_API_KEY environment variable is not set")
    sys.exit(1)

# Initialize Redmine API client
api = RedmineAPI(redmine_url, redmine_api_key, logger)

# Test endpoints (choose which one to run)
def test_current_user():
    logger.info("Testing current user endpoint...")
    try:
        result = api.get_current_user()
        print(json.dumps(result, indent=2))
        logger.info("Successfully retrieved current user data")
    except Exception as e:
        logger.error(f"Error getting current user: {e}")

def test_projects():
    logger.info("Testing projects endpoint...")
    try:
        result = api.get_projects()
        print(json.dumps(result, indent=2))
        logger.info(f"Successfully retrieved {len(result.get('projects', []))} projects")
    except Exception as e:
        logger.error(f"Error getting projects: {e}")

def test_issues():
    logger.info("Testing issues endpoint...")
    try:
        result = api.get_issues()
        print(json.dumps(result, indent=2))
        logger.info(f"Successfully retrieved {len(result.get('issues', []))} issues")
    except Exception as e:
        logger.error(f"Error getting issues: {e}")

if __name__ == "__main__":
    # Run tests
    test_current_user()
    test_projects()
    test_issues()