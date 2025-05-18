#!/usr/bin/env python3
"""
Essential functionality test for Redmine MCP Server
Tests the core API endpoints using the MCP protocol
"""
import os
import json
import subprocess
import time
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def send_mcp_request(method, path, data=None, process=None):
    """
    Send an MCP request to a running server process
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        path: Path to request
        data: Optional data to send
        process: Optional subprocess.Popen instance (if None, a new one is created)
        
    Returns:
        Tuple of (response, process)
    """
    close_process = False
    if process is None:
        # Start a new server process
        process = subprocess.Popen(
            ['python', 'main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Give the server a moment to start
        time.sleep(1)
        close_process = True
    
    # Prepare the request
    request = {
        'method': method,
        'path': path,
        'data': data or {}
    }
    
    # Convert to JSON
    request_json = json.dumps(request)
    
    # Send the request and get the response
    if process.stdin:
        process.stdin.write(request_json + '\n')
        process.stdin.flush()
    
    response_line = ""
    if process.stdout:
        response_line = process.stdout.readline().strip()
    
    # Parse the response
    try:
        response = json.loads(response_line)
        if close_process:
            process.terminate()
            process.wait()
            return response, None
        return response, process
    except json.JSONDecodeError:
        logger.error(f"Failed to parse response: {response_line}")
        if close_process:
            process.terminate()
            process.wait()
            return None, None
        return None, process

def test_health_check():
    """Test the health check endpoint"""
    logger.info("Testing health check endpoint...")
    
    response, _ = send_mcp_request('GET', '/health')
    
    if response and response.get('status') == 200 and response.get('data', {}).get('status') == 'ok':
        logger.info("✅ Health check successful!")
        return True
    else:
        logger.error("❌ Health check failed")
        return False

def test_projects():
    """Test the projects endpoint"""
    logger.info("Testing projects endpoint...")
    
    response, _ = send_mcp_request('GET', '/projects')
    
    if response and response.get('status') == 200 and 'projects' in response.get('data', {}):
        logger.info("✅ Projects endpoint successful!")
        return True
    else:
        logger.error("❌ Projects endpoint failed")
        return False

def test_current_user():
    """Test the current user endpoint"""
    logger.info("Testing current user endpoint...")
    
    response, _ = send_mcp_request('GET', '/users/current')
    
    if response and response.get('status') == 200 and 'user' in response.get('data', {}):
        logger.info("✅ Current user endpoint successful!")
        return True
    else:
        logger.error("❌ Current user endpoint failed")
        return False

def main():
    """Run all tests"""
    # Check for API key
    if not os.environ.get('REDMINE_API_KEY'):
        logger.error("REDMINE_API_KEY environment variable is not set")
        return 1
    
    # Run tests
    health_check_passed = test_health_check()
    projects_passed = test_projects()
    current_user_passed = test_current_user()
    
    # Print summary
    logger.info("\n=== Test Summary ===")
    logger.info(f"Health Check: {'✅ PASSED' if health_check_passed else '❌ FAILED'}")
    logger.info(f"Projects Endpoint: {'✅ PASSED' if projects_passed else '❌ FAILED'}")
    logger.info(f"Current User Endpoint: {'✅ PASSED' if current_user_passed else '❌ FAILED'}")
    
    # Check overall result
    if health_check_passed and projects_passed and current_user_passed:
        logger.info("\n✅ All tests passed!")
        return 0
    else:
        logger.error("\n❌ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())