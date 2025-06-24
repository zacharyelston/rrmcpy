#!/usr/bin/env python3
"""
Test connection and retry capabilities of modular Redmine clients
"""
import os
import sys
import unittest
import logging
from unittest.mock import patch, MagicMock
import requests

# Add the parent directory to the path to access src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.users import UserClient
from src.connection_manager import ConnectionManager

class TestConnectionManager(unittest.TestCase):
    """Test connection functionality and resilience"""
    
    def setUp(self):
        """Set up test environment"""
        self.redmine_url = os.environ.get('REDMINE_URL', 'https://demo.redmine.org')
        self.redmine_api_key = os.environ.get('REDMINE_API_KEY', '')
        
        if not self.redmine_api_key:
            self.skipTest("REDMINE_API_KEY environment variable not set")
        
        # Set up logging
        logging.basicConfig(level=logging.DEBUG)
        
        self.client = UserClient(self.redmine_url, self.redmine_api_key)
    
    def test_health_check_success(self):
        """Test that health check works with valid connection"""
        # Test the health check functionality
        health = self.client.health_check()
        
        # Should return True for a working connection
        self.assertTrue(health)
    
    def test_connection_manager_configuration(self):
        """Test that connection settings can be configured"""
        # Configure connection settings
        self.client.configure_connection_settings(
            max_retries=5,
            base_delay=2.0,
            timeout=15.0
        )
        
        # Verify settings were applied
        cm = self.client.connection_manager
        self.assertEqual(cm.max_retries, 5)
        self.assertEqual(cm.base_delay, 2.0)
        self.assertEqual(cm.timeout, 15.0)
    
    def test_successful_request_no_retry(self):
        """Test that successful requests don't trigger retry logic"""
        # Make a normal request that should succeed
        result = self.client.get_current_user()
        
        # Should not be an error response
        self.assertFalse(result.get('error', False))
        self.assertIn('user', result)
    
    def test_retry_on_connection_error(self):
        """Test retry behavior when connection fails"""
        with patch.object(self.client.connection_manager.session, 'get') as mock_get:
            # Set up mock to fail first time, succeed second time
            mock_get.side_effect = [
                requests.exceptions.ConnectionError("Connection failed"),
                MagicMock(
                    status_code=200, 
                    content=b'{"user": {"id": 1}}', 
                    json=lambda: {"user": {"id": 1}},
                    headers={}
                )
            ]
            
            # Configure minimal retry settings for faster test
            self.client.connection_manager.max_retries = 2
            self.client.connection_manager.base_delay = 0.1
            self.client.connection_manager.max_delay = 1.0
            
            # Make request that should retry and succeed
            result = self.client.get_current_user()
            
            # Should succeed after retry
            self.assertIn('user', result)
            
            # Should have been called twice (initial + 1 retry)
            self.assertEqual(mock_get.call_count, 2)
    
    def test_max_retries_exhausted(self):
        """Test behavior when max retries are exhausted"""
        with patch.object(self.client.connection_manager.session, 'get') as mock_get:
            # Set up mock to always fail with a connection error
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            # Configure minimal retry settings for faster test
            self.client.connection_manager.max_retries = 1
            self.client.connection_manager.base_delay = 0.1
            
            # Make request that should fail after retries
            with self.assertRaises(requests.exceptions.ConnectionError):
                self.client.get_current_user()
                
            # Should have been called max_retries + 1 times (initial + retries)
            self.assertEqual(mock_get.call_count, 2)
    
    def test_delay_calculation(self):
        """Test exponential backoff delay calculation"""
        cm = ConnectionManager("https://test.com", "test_key")
        
        # Test delay calculation with default settings
        delay_0 = cm._calculate_delay(0)
        delay_1 = cm._calculate_delay(1)
        delay_2 = cm._calculate_delay(2)
        
        # Should increase with each attempt
        self.assertGreater(delay_1, delay_0 * 0.5)  # Account for jitter
        self.assertGreater(delay_2, delay_1 * 0.5)  # Account for jitter
        
        # Should all be reasonable values
        self.assertGreater(delay_0, 0)
        self.assertLess(delay_0, 5)  # Should be small for first retry
        self.assertLess(delay_2, cm.max_delay * 1.5)  # Should respect max delay
    
    def test_retryable_error_detection(self):
        """Test detection of retryable vs non-retryable errors"""
        cm = ConnectionManager("https://test.com", "test_key")
        
        # Test retryable errors
        connection_error = requests.exceptions.ConnectionError("Connection failed")
        timeout_error = requests.exceptions.Timeout("Request timed out")
        
        self.assertTrue(cm._is_retryable_error(connection_error))
        self.assertTrue(cm._is_retryable_error(timeout_error))
        
        # Test non-retryable errors
        auth_error = requests.exceptions.HTTPError()
        auth_error.response = MagicMock(status_code=401)
        
        not_found_error = requests.exceptions.HTTPError()
        not_found_error.response = MagicMock(status_code=404)
        
        self.assertFalse(cm._is_retryable_error(auth_error))
        self.assertFalse(cm._is_retryable_error(not_found_error))
        
        # Test retryable HTTP errors
        server_error = requests.exceptions.HTTPError()
        server_error.response = MagicMock(status_code=500)
        
        rate_limit_error = requests.exceptions.HTTPError()
        rate_limit_error.response = MagicMock(status_code=429)
        
        self.assertTrue(cm._is_retryable_error(server_error))
        self.assertTrue(cm._is_retryable_error(rate_limit_error))

if __name__ == '__main__':
    unittest.main()