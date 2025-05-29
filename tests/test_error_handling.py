#!/usr/bin/env python3
"""
Test error handling capabilities of the Redmine MCP Server
"""
import os
import sys
import unittest
import logging

# Add the parent directory to the path to access src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.redmine_client import RedmineClient

class TestErrorHandling(unittest.TestCase):
    """Test comprehensive error handling functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        self.redmine_api_key = os.environ.get('REDMINE_API_KEY', '')
        
        if not self.redmine_api_key:
            self.skipTest("REDMINE_API_KEY environment variable not set")
        
        # Configure logging to capture error messages
        logging.basicConfig(level=logging.DEBUG)
        
        self.client = RedmineClient(self.redmine_url, self.redmine_api_key)
    
    def test_invalid_issue_creation_missing_fields(self):
        """Test error handling for missing required fields in issue creation"""
        # Try to create an issue without required fields
        invalid_data = {
            "description": "Test issue without required fields"
        }
        
        result = self.client.create_issue(invalid_data)
        
        # Should return an error response
        self.assertTrue(result.get('error', False))
        self.assertEqual(result.get('error_code'), 'VALIDATION_ERROR')
        self.assertIn('Missing required fields', result.get('message', ''))
        self.assertIn('project_id', result.get('message', ''))
        self.assertIn('subject', result.get('message', ''))
    
    def test_invalid_issue_creation_empty_subject(self):
        """Test error handling for empty subject in issue creation"""
        invalid_data = {
            "project_id": "rmcpy",
            "subject": "   "  # Empty/whitespace only subject
        }
        
        result = self.client.create_issue(invalid_data)
        
        # Should return an error response
        self.assertTrue(result.get('error', False))
        self.assertEqual(result.get('error_code'), 'VALIDATION_ERROR')
        self.assertIn('subject cannot be empty', result.get('message', ''))
    
    def test_invalid_issue_creation_wrong_types(self):
        """Test error handling for wrong data types in issue creation"""
        invalid_data = {
            "project_id": "rmcpy",
            "subject": "Test issue",
            "tracker_id": "not_an_integer"  # Should be int
        }
        
        result = self.client.create_issue(invalid_data)
        
        # Should return an error response
        self.assertTrue(result.get('error', False))
        self.assertEqual(result.get('error_code'), 'VALIDATION_ERROR')
        self.assertIn('must be of type', result.get('message', ''))
    
    def test_nonexistent_issue_access(self):
        """Test error handling when accessing a non-existent issue"""
        # Try to access an issue that doesn't exist
        result = self.client.get_issue(999999)
        
        # Should return an error response for not found
        if result.get('error', False):
            self.assertEqual(result.get('error_code'), 'NOT_FOUND')
    
    def test_error_response_structure(self):
        """Test that error responses have correct structure"""
        # Create a validation error
        invalid_data = {"description": "Missing required fields"}
        result = self.client.create_issue(invalid_data)
        
        # Check error response structure
        self.assertTrue(result.get('error', False))
        self.assertIn('error_code', result)
        self.assertIn('message', result)
        self.assertIn('status_code', result)
        self.assertIn('timestamp', result)
        
        # Verify timestamp format (ISO 8601)
        timestamp = result.get('timestamp', '')
        self.assertTrue(timestamp.endswith('Z'))
        self.assertIn('T', timestamp)
    
    def test_successful_operation_no_error(self):
        """Test that successful operations don't return error responses"""
        # Get current user (should succeed)
        result = self.client.get_current_user()
        
        # Should not be an error response
        self.assertFalse(result.get('error', False))
        self.assertIn('user', result)

if __name__ == '__main__':
    unittest.main()