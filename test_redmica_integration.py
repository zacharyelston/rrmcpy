#!/usr/bin/env python3
"""
Simple test script to validate Redmica API integration
"""
import os
import requests
import json

# Use the same values as our MCP server
REDMINE_URL = "http://localhost:3000"
REDMINE_API_KEY = "1fb3759d9dfe0851c626c4dd312c62fce6f91050"

def test_projects_api():
    """Test the projects API endpoint"""
    headers = {'X-Redmine-API-Key': REDMINE_API_KEY, 'Content-Type': 'application/json'}
    url = f"{REDMINE_URL}/projects.json"
    
    print(f"Testing Projects API: GET {url}")
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Projects found: {len(data.get('projects', []))}")
        for project in data.get('projects', []):
            print(f" - {project.get('name')} ({project.get('identifier')})")
    else:
        print(f"Error: {response.text}")

def test_search_api():
    """Test the search API endpoint"""
    headers = {'X-Redmine-API-Key': REDMINE_API_KEY, 'Content-Type': 'application/json'}
    query = "test"
    url = f"{REDMINE_URL}/search.json?q={query}"
    
    print(f"\nTesting Search API: GET {url}")
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Search results for '{query}': {data.get('total_count', 0)} found")
        for result in data.get('results', []):
            print(f" - {result.get('title')} ({result.get('type')})")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("=== Redmica API Integration Test ===")
    test_projects_api()
    test_search_api()
    print("=== Test Complete ===")
