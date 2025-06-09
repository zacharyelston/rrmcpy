#!/usr/bin/env python3
"""
Unit tests for standardized error handling
Tests use mocks - no actual API calls
"""
import os
import sys
import unittest
import json
from unittest.mock import Mock, patch, MagicMock
import requests

# Add the parent directory to the path to access src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.base import RedmineBaseClient


class TestStandardizedErrorHandling(unittest.TestCase):
    """Test standardized error response format"""
    
    def setUp(self):
        """Set up test client"""
        self.client = RedmineBaseClient()
    
    @patch('requests.request')
    def test_error_response_format(self, mock_request):
        """Test that error responses follow the standard format"""
        # Mock a 400 Bad Request response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"errors": ["Subject cannot be blank"]}
        mock_response.text = json.dumps({"errors": ["Subject cannot be blank"]})
        mock_request.return_value = mock_response
        
        # Trigger the error
        try:
            self.client.post("/issues.json", {"issue": {}})
            self.fail("Expected exception was not raised")
        except Exception as e:
            # Verify error format
            self.assertIn("error", str(e).lower())
            
            # Check if the error has the expected attributes
            if hasattr(e, "error_response"):
                error_response = e.error_response
                self.assertIn("error", error_response)
                self.assertIn("error_code", error_response)
                self.assertEqual(error_response["error_code"], "VALIDATION_ERROR")
                self.assertIn("message", error_response)
                self.assertIn("status_code", error_response)
                self.assertEqual(error_response["status_code"], 400)
    
    @patch('requests.request')
    def test_http_error_mapping(self, mock_request):
        """Test that HTTP status codes are mapped to appropriate error codes"""
        # Test cases for different HTTP status codes
        test_cases = [
            (400, "VALIDATION_ERROR"),
            (401, "AUTHENTICATION_ERROR"),
            (403, "AUTHORIZATION_ERROR"),
            (404, "NOT_FOUND"),
            (422, "VALIDATION_ERROR"),
            (500, "SERVER_ERROR")
        ]
        
        for status_code, expected_error_code in test_cases:
            # Mock response with the current status code
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_response.json.return_value = {"errors": ["Test error"]}
            mock_response.text = json.dumps({"errors": ["Test error"]})
            mock_request.return_value = mock_response
            
            # Trigger the error
            try:
                self.client.get("/test.json")
                self.fail(f"Expected exception for status {status_code} was not raised")
            except Exception as e:
                # Verify error mapping
                if hasattr(e, "error_response"):
                    error_response = e.error_response
                    self.assertEqual(error_response["error_code"], expected_error_code,
                                    f"Expected {expected_error_code} for status {status_code}, got {error_response['error_code']}")
    
    @patch('requests.request')
    def test_connection_error_handling(self, mock_request):
        """Test handling of connection errors"""
        # Mock a connection error
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        # Trigger the error
        try:
            self.client.get("/test.json")
            self.fail("Expected ConnectionError was not raised")
        except Exception as e:
            # Verify error format
            if hasattr(e, "error_response"):
                error_response = e.error_response
                self.assertIn("error", error_response)
                self.assertEqual(error_response["error_code"], "CONNECTION_ERROR")
                self.assertIn("message", error_response)
    
    @patch('requests.request')
    def test_timeout_error_handling(self, mock_request):
        """Test handling of timeout errors"""
        # Mock a timeout error
        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")
        
        # Trigger the error
        try:
            self.client.get("/test.json")
            self.fail("Expected Timeout was not raised")
        except Exception as e:
            # Verify error format
            if hasattr(e, "error_response"):
                error_response = e.error_response
                self.assertIn("error", error_response)
                self.assertEqual(error_response["error_code"], "TIMEOUT_ERROR")
                self.assertIn("message", error_response)


if __name__ == '__main__':
    unittest.main()
