#!/usr/bin/env python3
"""
Simple test script for the Redmine MCP Server
This script tests the basic functionality of the MCP server
"""
import json
import subprocess
import time
import sys

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    
    # Prepare the request
    request = {
        'method': 'GET',
        'path': '/health',
        'data': {}
    }
    
    # Convert to JSON
    request_json = json.dumps(request)
    
    # Start the server process
    process = subprocess.Popen(
        ['python', 'main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give the server a moment to start
    time.sleep(1)
    
    try:
        # Send the request
        if process.stdin:
            process.stdin.write(request_json + '\n')
            process.stdin.flush()
        
        # Read the response
        response_line = ""
        if process.stdout:
            response_line = process.stdout.readline().strip()
        
        try:
            response = json.loads(response_line)
            print(f"Response: {json.dumps(response, indent=2)}")
            
            # Check if the response is valid
            if response.get('status') == 200 and response.get('data', {}).get('status') == 'ok':
                print("✅ Health check successful!")
                return True
            else:
                print("❌ Health check failed: Invalid response")
                return False
                
        except json.JSONDecodeError:
            print(f"❌ Health check failed: Invalid JSON response: {response_line}")
            return False
            
    finally:
        # Terminate the server
        process.terminate()
        process.wait()

def main():
    """Run all tests"""
    success = test_health_check()
    
    if success:
        print("\nAll tests passed! 🎉")
        return 0
    else:
        print("\nSome tests failed. 😢")
        return 1

if __name__ == '__main__':
    sys.exit(main())