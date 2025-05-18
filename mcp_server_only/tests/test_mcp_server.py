#!/usr/bin/env python3
"""
Tests for the Redmine MCP Server
"""
import pytest
import os
import json
import sys
import threading
import time
import io
from contextlib import redirect_stdout, redirect_stderr

# Add the parent directory to the path so we can import the server module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.fixed_mcp_server import RedmineMCPServer
from redmine_mcp_server import main

class TestMCPServer:
    """Tests for the MCP Server functionality"""
    
    @pytest.fixture
    def server(self):
        """Create an MCP server for testing"""
        # Get environment variables or use test values
        redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        redmine_api_key = os.environ.get('REDMINE_API_KEY', '')
        server_mode = 'test'
        
        if not redmine_api_key:
            pytest.skip("REDMINE_API_KEY environment variable is required for testing")
        
        # Create server
        server = RedmineMCPServer(redmine_url, redmine_api_key, server_mode)
        
        # Return server for testing
        yield server
        
        # Clean up
        server.stop()
    
    def test_server_initialization(self, server):
        """Test that the server initializes correctly"""
        assert server is not None
        assert server.redmine_url == os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        assert server.api_key == os.environ.get('REDMINE_API_KEY', '')
        assert server.mode == 'test'
        
    def test_server_start_stop(self, server):
        """Test starting and stopping the server"""
        # Start in a separate thread so it doesn't block
        server_thread = threading.Thread(target=server.start)
        server_thread.daemon = True
        server_thread.start()
        
        # Give the server time to start
        time.sleep(1)
        
        # Check that the server is running
        assert server_thread.is_alive()
        
        # Stop the server
        server.stop()
        
        # Give the server time to stop
        time.sleep(1)
        
        # Check that the server has stopped
        assert not server_thread.is_alive()
        
    def test_process_request(self, server):
        """Test processing a simple request"""
        # Create a test request
        request = {
            'method': 'GET',
            'path': '/users/current.json',
            'data': {}
        }
        
        # Process the request
        response = server.process_request(request)
        
        # Check the response
        assert response is not None
        assert 'user' in response
        assert 'login' in response['user']
        
    def test_invalid_request(self, server):
        """Test handling an invalid request"""
        # Create an invalid request
        request = {
            'method': 'GET',
            'path': '/invalid/endpoint',
            'data': {}
        }
        
        # Process the request
        response = server.process_request(request)
        
        # Check the response contains an error
        assert response is not None
        assert 'error' in response