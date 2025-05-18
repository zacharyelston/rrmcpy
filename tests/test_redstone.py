#!/usr/bin/env python3
"""
Test script to verify connectivity to Redstone Redmine server
"""
import os
import logging
import sys
import json
import unittest

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

class TestRedstoneConnection(unittest.TestCase):
    """Test connection to Redstone Redmine server"""

    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        # Get API key from environment
        cls.redmine_url = "https://redstone.redminecloud.net"
        cls.redmine_api_key = os.environ.get("REDMINE_API_KEY")
        
        if not cls.redmine_api_key:
            logger.error("REDMINE_API_KEY environment variable is not set")
            raise unittest.SkipTest("REDMINE_API_KEY environment variable is not set")
        
        # Initialize Redmine API client
        cls.api = RedmineAPI(cls.redmine_url, cls.redmine_api_key, logger)

    def test_current_user(self):
        """Test current user endpoint"""
        logger.info("Testing current user endpoint...")
        try:
            result = self.api.get_current_user()
            print(json.dumps(result, indent=2))
            logger.info("Successfully retrieved current user data")
            self.assertIn('user', result, "Response should contain user data")
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            self.fail(f"Error getting current user: {e}")

    def test_projects(self):
        """Test projects endpoint"""
        logger.info("Testing projects endpoint...")
        try:
            result = self.api.get_projects()
            print(json.dumps(result, indent=2))
            logger.info(f"Successfully retrieved {len(result.get('projects', []))} projects")
            self.assertIn('projects', result, "Response should contain projects data")
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            self.fail(f"Error getting projects: {e}")

    def test_issues(self):
        """Test issues endpoint"""
        logger.info("Testing issues endpoint...")
        try:
            result = self.api.get_issues()
            print(json.dumps(result, indent=2))
            logger.info(f"Successfully retrieved {len(result.get('issues', []))} issues")
            self.assertIn('issues', result, "Response should contain issues data")
        except Exception as e:
            logger.error(f"Error getting issues: {e}")
            self.fail(f"Error getting issues: {e}")

if __name__ == "__main__":
    unittest.main()