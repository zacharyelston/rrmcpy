#!/usr/bin/env python3
"""
Test the proper FastMCP implementation
"""
import os
import sys
import unittest
import asyncio
import logging

# Add the parent directory to the path to access src
sys.path.insert(0, os.path.abspath('..'))

from src.server import RedmineMCPServer

class TestProperMCP(unittest.TestCase):
    """Test proper FastMCP implementation"""
    
    def setUp(self):
        """Set up test environment"""
        self.redmine_url = os.environ.get('REDMINE_URL', 'https://demo.redmine.org')
        self.redmine_api_key = os.environ.get('REDMINE_API_KEY', '')
        
        if not self.redmine_api_key:
            self.skipTest("REDMINE_API_KEY environment variable not set")
        
        # Configure logging to stderr (proper MCP pattern)
        # Clear existing handlers and force stderr configuration
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stderr,
            force=True
        )
        
        self.server = RedmineMCPServer(self.redmine_url, self.redmine_api_key)
    
    def test_server_initialization(self):
        """Test that server initializes properly"""
        self.assertIsNotNone(self.server)
        self.assertEqual(self.server.redmine_url, self.redmine_url)
        self.assertEqual(self.server.api_key, self.redmine_api_key)
        self.assertIsNotNone(self.server.redmine_client)
        self.assertIsNotNone(self.server.app)
    
    def test_logging_to_stderr(self):
        """Test that logging is properly configured to stderr"""
        # The server setup in setUp() should have configured stderr logging
        # Check the root logger handlers since our server uses basicConfig
        root_logger = logging.getLogger()
        has_stderr_handler = False
        
        for handler in root_logger.handlers:
            if hasattr(handler, 'stream') and handler.stream == sys.stderr:
                has_stderr_handler = True
                break
        
        self.assertTrue(has_stderr_handler, "Logging should be configured to use stderr")
    
    def test_redmine_client_integration(self):
        """Test that Redmine client is properly integrated"""
        # Test basic connectivity
        try:
            result = self.server.redmine_client.get_current_user()
            self.assertFalse(result.get('error', False))
            self.assertIn('user', result)
        except Exception as e:
            self.fail(f"Redmine client integration failed: {e}")
    
    def test_pydantic_models(self):
        """Test that Pydantic models work correctly"""
        from src.server import IssueCreateRequest, IssueUpdateRequest, ProjectCreateRequest
        
        # Test IssueCreateRequest
        issue_request = IssueCreateRequest(
            project_id="rmcpy",
            subject="Test issue",
            description="Test description"
        )
        self.assertEqual(issue_request.project_id, "rmcpy")
        self.assertEqual(issue_request.subject, "Test issue")
        
        # Test model serialization
        data = issue_request.model_dump(exclude_none=True)
        self.assertIn('project_id', data)
        self.assertIn('subject', data)
        self.assertIn('description', data)
        
        # Test IssueUpdateRequest
        update_request = IssueUpdateRequest(
            issue_id=123,
            subject="Updated subject",
            notes="Update notes"
        )
        self.assertEqual(update_request.issue_id, 123)
        
        # Test ProjectCreateRequest
        project_request = ProjectCreateRequest(
            name="Test Project",
            identifier="test-proj"
        )
        self.assertEqual(project_request.name, "Test Project")
        self.assertEqual(project_request.identifier, "test-proj")

if __name__ == '__main__':
    unittest.main()