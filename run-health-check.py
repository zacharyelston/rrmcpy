#!/usr/bin/env python3
"""
Simple MCP client script to call the redmine_health_check tool
"""
import json
import logging
import os
import sys
import subprocess
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("run-health-check")

def main():
    """Run the MCP server and send a health check request"""
    try:
        # Start the MCP server in the background
        server_process = subprocess.Popen(
            ["python", "-m", "src.main"], 
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True
        )
        
        # Give the server a moment to initialize
        time.sleep(0.5)
        
        # Prepare health check request in MCP format
        request = {
            "id": "1",
            "method": "redmine_health_check",
            "params": {}
        }
        
        # Send the request
        server_process.stdin.write(json.dumps(request) + "\n")
        server_process.stdin.flush()
        
        # Read the response
        response = server_process.stdout.readline()
        result = json.loads(response)
        
        # Pretty print the result
        logger.info("Health Check Result:")
        print(json.dumps(result, indent=2))
        
        # Close the server
        server_process.stdin.close()
        server_process.terminate()
        server_process.wait(timeout=2)
        
    except Exception as e:
        logger.error(f"Error during health check: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
