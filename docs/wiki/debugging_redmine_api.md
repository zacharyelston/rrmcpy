# Debugging Redmine API Issues: Wiki Page Creation Case Study

This document outlines the process of diagnosing and fixing inconsistent Textile formatting in wiki pages created via the Redmine API. It serves as a reference for debugging similar API-related issues in the future.

## Background

**Issue #698**: Wiki pages created via the Redmine MCP Server API had inconsistent Textile formatting compared to pages created through the web UI.

**Root Cause**: The issue was related to the HTTP method used to create wiki pages. Our implementation was using POST as the primary method with PUT as a fallback, but the standard Redmine API actually uses PUT as the preferred method for wiki page creation.

## Investigation Process

### 1. Identify the Problem

- Wiki pages created via API showed plain text instead of formatted Textile
- The issue was reproducible and occurred consistently
- Pages updated via the API worked correctly, only creation was affected

### 2. Analyze the Code

We first examined the implementation of wiki page creation in `src/wiki/client.py`:

```python
def create_wiki_page(self, project_id: str, title: str, text: str, ...):
    # Initial implementation used POST with a fallback to PUT
    standard_endpoint = f"/projects/{project_id}/wiki.json"
    # Try POST method first
    try:
        response = self.make_request('POST', standard_endpoint, data=page_data)
        # Handle response...
    except Exception as e:
        # Fallback to PUT
        fallback_endpoint = f"/projects/{project_id}/wiki/{title}.json"
        response = self.make_request('PUT', fallback_endpoint, data=page_data)
        # Handle response...
```

### 3. Create Diagnostic Tools

We created a diagnostic script (`diagnostic_wiki.py`) to test both POST and PUT methods against the Redmine API:

```python
#!/usr/bin/env python3
import os
import requests
import logging
import json

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_redmine_api():
    # Get credentials from environment variables
    redmine_url = os.environ.get('REDMINE_URL')
    api_key = os.environ.get('REDMINE_API_KEY')
    
    if not redmine_url or not api_key:
        logger.error("Missing required environment variables")
        return
    
    headers = {
        'Content-Type': 'application/json',
        'X-Redmine-API-Key': api_key
    }
    
    # Test data for wiki page
    project_id = 'rrmcpy'
    page_title = 'ApiTestPage'
    page_data = {
        'wiki_page': {
            'title': page_title,
            'text': 'h1. Test Heading\n\nThis is a *bold* text.',
            'comments': 'API diagnostic test'
        }
    }
    
    # Test POST endpoint
    post_url = f"{redmine_url}/projects/{project_id}/wiki.json"
    logger.info(f"Testing POST to {post_url}")
    try:
        post_response = requests.post(post_url, headers=headers, json=page_data)
        logger.info(f"POST Status Code: {post_response.status_code}")
        logger.info(f"POST Response: {post_response.text}")
    except Exception as e:
        logger.error(f"POST request failed: {str(e)}")
    
    # Test PUT endpoint
    put_url = f"{redmine_url}/projects/{project_id}/wiki/{page_title}.json"
    logger.info(f"Testing PUT to {put_url}")
    try:
        put_response = requests.put(put_url, headers=headers, json=page_data)
        logger.info(f"PUT Status Code: {put_response.status_code}")
        logger.info(f"PUT Response: {put_response.text}")
    except Exception as e:
        logger.error(f"PUT request failed: {str(e)}")

if __name__ == "__main__":
    test_redmine_api()
```

### 4. Run Tests in Container Environment

We used Docker to test our diagnostic script with proper environment variables:

```bash
# Build the Docker image
docker build -t redmine-mcp-server:test .

# Run the diagnostic script with proper environment variables
docker run --rm --env-file .env -e LOG_LEVEL=DEBUG -v "$(pwd)":/app \
    redmine-mcp-server:test python diagnostic_wiki.py
```

### 5. Analyze the Results

The diagnostic tests revealed:
- POST to `/projects/{project_id}/wiki.json` returned 404 Not Found
- PUT to `/projects/{project_id}/wiki/{page_title}.json` returned 201 Created

After checking the [official Redmine API documentation](https://www.redmine.org/projects/redmine/wiki/Rest_WikiPages), we confirmed that PUT is indeed the standard method for wiki page creation.

## The Solution

### 1. Create a Feature Branch

```bash
git checkout -b fix/wiki-put-method-priority
```

### 2. Modify the Code

We updated `src/wiki/client.py` to prioritize PUT over POST:

```python
def create_wiki_page(self, project_id: str, title: str, text: str, ...):
    # Use PUT method first (standard according to Redmine API docs)
    standard_endpoint = f"/projects/{project_id}/wiki/{title}.json"
    try:
        response = self.make_request('PUT', standard_endpoint, data=page_data)
        # Handle response...
    except Exception as e:
        # Fallback to POST for backward compatibility
        fallback_endpoint = f"/projects/{project_id}/wiki.json"
        response = self.make_request('POST', fallback_endpoint, data=page_data)
        # Handle response...
```

### 3. Update Unit Tests

We updated the unit tests in `tests/unit/test_wiki_client.py` to match our implementation change:

- Changed test_create_wiki_page_success to expect PUT method
- Renamed test_create_wiki_page_post_failure_put_fallback to test_create_wiki_page_put_failure_post_fallback
- Updated test assertions to check for PUT first, then POST

### 4. Run Unit Tests

```bash
docker run --rm --env-file .env -e LOG_LEVEL=DEBUG -v "$(pwd)":/app \
    redmine-mcp-server:test python -m pytest tests/unit/test_wiki_client.py -v
```

### 5. Create Integration Test

We created an integration test script (`test_wiki_integration.py`) to verify the solution:

```python
#!/usr/bin/env python3
import os
import logging
import sys
import json
from datetime import datetime

# Configure logging and imports...

def main():
    # Get environment variables
    redmine_url = os.environ.get('REDMINE_URL')
    api_key = os.environ.get('REDMINE_API_KEY')
    
    # Create test page with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    page_name = f"TestPage_{timestamp}"
    project_id = "rrmcpy"
    
    # Create wiki page and check the method used
    client = WikiClient(redmine_url, api_key)
    result = client.create_wiki_page(
        project_id=project_id,
        title=page_name,
        text="h1. Test Wiki Page\n\nThis is a test page...",
        comments="Integration test for PUT method priority"
    )
    
    # Verify results
    if result.get('method_used') == 'PUT':
        logger.info("SUCCESS: Page created using PUT method as expected")
    else:
        logger.warning(f"WARNING: Page created using {result.get('method_used')} method")

if __name__ == "__main__":
    main()
```

### 6. Run Integration Test

```bash
docker run --rm --env-file .env -e LOG_LEVEL=DEBUG -v "$(pwd)":/app \
    redmine-mcp-server:test python test_wiki_integration.py
```

### 7. Commit Changes

```bash
git add src/wiki/client.py tests/unit/test_wiki_client.py
git commit -m "fix: reverse wiki page creation method priority to use PUT first, POST as fallback based on Redmine API standards"
```

## Lessons Learned

1. **Check the API Documentation First**: Always refer to the official documentation for standard API behaviors.
   
2. **Use Diagnostic Scripts**: Create isolated scripts to test API behavior outside the main application.
   
3. **Container-Based Testing**: Use Docker containers with proper environment variables to ensure consistent testing.
   
4. **Maintain Backward Compatibility**: Implement fallbacks for alternative methods to ensure robustness.
   
5. **Update Tests with Implementation**: Make sure to update all unit tests when changing method behaviors.
   
6. **Integration Test for Validation**: Always perform integration tests against the real API to confirm that the solution works as expected.

## Related Issues

- **Issue #698**: Original bug report for Textile formatting inconsistencies
- **Issue #711**: Investigation finding that PUT is the correct method for wiki page creation

## References

- [Redmine REST API - Wiki Pages](https://www.redmine.org/projects/redmine/wiki/Rest_WikiPages)
- [RFC 7231 - HTTP Methods](https://tools.ietf.org/html/rfc7231#section-4.3)
