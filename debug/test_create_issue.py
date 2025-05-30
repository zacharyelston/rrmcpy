#!/usr/bin/env python3
"""
Debug script to test issue creation and see actual response
"""
import os
import sys
import json
import requests

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.redmine_client import RedmineClient
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_raw_api():
    """Test the raw API to see what it returns"""
    print("\n=== Testing Raw Redmine API ===")
    
    redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
    api_key = os.environ.get("REDMINE_API_KEY", "")
    
    if not api_key:
        print("REDMINE_API_KEY not set!")
        return
    
    # Test raw API call
    headers = {
        'X-Redmine-API-Key': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    issue_data = {
        "issue": {
            "project_id": "p1",
            "subject": "Debug test issue - raw API",
            "description": "Testing raw API response"
        }
    }
    
    url = f"{redmine_url}/issues.json"
    
    print(f"Making POST request to: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(issue_data, indent=2)}")
    
    response = requests.post(url, headers=headers, json=issue_data)
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Content Length: {len(response.content)}")
    print(f"Response Text: '{response.text}'")
    
    if response.content:
        try:
            json_data = response.json()
            print(f"Response JSON: {json.dumps(json_data, indent=2)}")
        except:
            print("Could not parse response as JSON")

def test_client():
    """Test using the RedmineClient"""
    print("\n=== Testing RedmineClient ===")
    
    redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
    api_key = os.environ.get("REDMINE_API_KEY", "")
    
    if not api_key:
        print("REDMINE_API_KEY not set!")
        return
    
    client = RedmineClient(redmine_url, api_key)
    
    issue_data = {
        "project_id": "p1",
        "subject": "Debug test issue - client",
        "description": "Testing client response"
    }
    
    print("Creating issue via client...")
    result = client.create_issue(issue_data)
    print(f"Client result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    test_raw_api()
    test_client()
