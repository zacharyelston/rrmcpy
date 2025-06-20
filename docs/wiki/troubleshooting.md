# Troubleshooting Guide

## Connection Issues

### Connection Refused
**Symptoms**: Server fails to connect to Redmine
**Solutions**:
```bash
# Test network connectivity
curl -I https://your-redmine.com

# Verify environment variables
echo $REDMINE_URL
echo $REDMINE_API_KEY

# Check server accessibility
python -c "
import requests
response = requests.get('$REDMINE_URL')
print(f'Status: {response.status_code}')
"
```

### Authentication Failures
**Symptoms**: "Invalid API key" or "Unauthorized" errors
**Solutions**:
```bash
# Validate API key format
python -c "
import os
key = os.getenv('REDMINE_API_KEY')
print(f'Key length: {len(key) if key else 0}')
print(f'Key format valid: {key and len(key) >= 32 if key else False}')
"

# Test API key directly
curl -H "X-Redmine-API-Key: $REDMINE_API_KEY" \
     $REDMINE_URL/users/current.json
```

### SSL Certificate Issues
**Symptoms**: SSL verification errors
**Solutions**:
```python
# For development only - disable SSL verification
import os
os.environ['PYTHONHTTPSVERIFY'] = '0'

# Better solution - add certificate to trust store
# Contact your system administrator
```

## Server Startup Issues

### Import Errors
**Symptoms**: Module not found errors
**Solutions**:
```bash
# Install missing dependencies
pip install -r requirements.txt

# Verify Python path
python -c "
import sys
print('Python path:')
for path in sys.path:
    print(f'  {path}')
"

# Check specific imports
python -c "
try:
    from fastmcp import FastMCP
    print('FastMCP: OK')
except ImportError as e:
    print(f'FastMCP error: {e}')
"
```

### Environment Variable Issues
**Symptoms**: Configuration validation failures
**Solutions**:
```bash
# Check all required variables
python -c "
import os
required = ['REDMINE_URL', 'REDMINE_API_KEY']
for var in required:
    value = os.getenv(var)
    print(f'{var}: {\"SET\" if value else \"MISSING\"}')
"

# Validate URL format
python -c "
import os
from urllib.parse import urlparse
url = os.getenv('REDMINE_URL')
parsed = urlparse(url) if url else None
print(f'URL valid: {bool(parsed and parsed.scheme and parsed.netloc)}')
"
```

### Event Loop Conflicts
**Symptoms**: "Already running asyncio in this thread"
**Solutions**:
```bash
# Install container compatibility
pip install nest_asyncio

# Use container-compatible server
python container_server.py

# Alternative: use configuration wrapper
python mcp_config_example.py
```

## Tool Execution Issues

### Empty or Unexpected Responses
**Symptoms**: Tools return "{}" or error messages
**Solutions**:
```python
# Test basic connectivity first
result = await mcp.call_tool("redmine-health-check")
print("Health check:", result)

# Verify tool registration
result = await mcp.list_tools()
print("Available tools:", [tool["name"] for tool in result])

# Test with minimal parameters
result = await mcp.call_tool(
    "redmine-get-current-user"
)
print("User info:", result)
```

### Permission Denied Errors
**Symptoms**: 403 Forbidden or access denied messages
**Solutions**:
```python
# Check user permissions
user_info = await mcp.call_tool("redmine-get-current-user")
user_data = json.loads(user_info)["user"]

# Review group memberships
groups = [group["name"] for group in user_data.get("groups", [])]
print("User groups:", groups)

# Check project memberships
memberships = user_data.get("memberships", [])
for membership in memberships:
    project = membership["project"]["name"]
    roles = [role["name"] for role in membership["roles"]]
    print(f"Project {project}: {roles}")
```

### Parameter Validation Errors
**Symptoms**: "Invalid parameter" or validation failures
**Solutions**:
```python
# Check parameter types and values
await mcp.call_tool(
    "redmine-create-issue",
    project_id="1",  # String, not integer
    subject="Test issue",
    description="Test description"
)

# Verify project exists
try:
    # List issues in project first
    result = await mcp.call_tool(
        "redmine-list-issues",
        project_id="your-project-id",
        limit=1
    )
    print("Project accessible")
except Exception as e:
    print(f"Project issue: {e}")
```

## Performance Issues

### Slow Response Times
**Symptoms**: Operations take longer than expected
**Solutions**:
```bash
# Increase timeout for slow networks
export REDMINE_TIMEOUT="90"

# Enable debug logging to identify bottlenecks
export MCP_LOG_LEVEL="DEBUG"

# Test network latency
ping your-redmine-server.com
```

### Memory or Resource Issues
**Symptoms**: Out of memory or resource exhaustion
**Solutions**:
```python
# Process large datasets in batches
async def process_issues_efficiently():
    offset = 0
    batch_size = 25
    
    while True:
        result = await mcp.call_tool(
            "redmine-list-issues",
            limit=batch_size,
            offset=offset
        )
        
        issues_data = json.loads(result)
        issues = issues_data.get("issues", [])
        
        if not issues:
            break
            
        # Process batch
        for issue in issues:
            # Process individual issue
            pass
        
        offset += batch_size
        await asyncio.sleep(0.1)  # Brief pause
```

## Development Environment Issues

### Jupyter Notebook Problems
**Symptoms**: Event loop or import issues in notebooks
**Solutions**:
```python
# Install compatibility package
!pip install nest_asyncio

# Apply nested event loop support
import nest_asyncio
nest_asyncio.apply()

# Use asyncio.create_task instead of asyncio.run
import asyncio
task = asyncio.create_task(main())
```

### VS Code Integration Issues
**Symptoms**: Server won't start in VS Code terminal
**Solutions**:
```bash
# Use full Python path
/usr/bin/python3 fastmcp_server.py

# Check terminal environment
env | grep REDMINE

# Use integrated terminal settings
# Settings → Terminal → Integrated → Env
```

### Docker Container Issues
**Symptoms**: Container deployment failures
**Solutions**:
```dockerfile
# Ensure proper environment variable passing
ENV REDMINE_URL=https://your-redmine.com
ENV REDMINE_API_KEY=your-api-key

# Use proper container entry point
CMD ["python", "fastmcp_server.py"]
```

## Data and API Issues

### Inconsistent Data
**Symptoms**: Different results from same API calls
**Solutions**:
```python
# Verify data consistency
issue_1 = await mcp.call_tool("redmine-get-issue", issue_id=123)
issue_2 = await mcp.call_tool("redmine-get-issue", issue_id=123)

# Check for concurrent modifications
import time
time.sleep(1)  # Brief delay between calls
```

### Rate Limiting
**Symptoms**: 429 Too Many Requests errors
**Solutions**:
```python
# Add delays between requests
import asyncio

async def rate_limited_operation():
    for i in range(10):
        result = await mcp.call_tool("redmine-list-issues", limit=5, offset=i*5)
        await asyncio.sleep(0.5)  # 500ms between requests
```

## Debugging Techniques

### Enable Detailed Logging
```bash
export MCP_LOG_LEVEL="DEBUG"
python fastmcp_server.py 2>&1 | tee debug.log
```

### Trace Network Requests
```python
import logging
import http.client

# Enable HTTP debug logging
http.client.HTTPConnection.debuglevel = 1
logging.basicConfig(level=logging.DEBUG)
```

### Isolate Issues
```python
# Test individual components
from src.issues import IssueClient

client = IssueClient(url, api_key)

# Test basic connectivity
print("Health:", client.health_check())

# Test simple operation
result = client.get_issues({"limit": 1})
print("Issues:", len(result.get("issues", [])))
```

### Validate Configuration
```python
from mcp_config_example import validate_configuration, setup_logging

# Run configuration validation
setup_logging()
if validate_configuration():
    print("Configuration valid")
else:
    print("Configuration errors detected")
```

## Getting Additional Help

### Collect Diagnostic Information
Before seeking help, gather:
- Error messages and stack traces
- Server logs with DEBUG level enabled
- Environment variable values (redacted)
- Python and dependency versions
- Network connectivity test results

### Diagnostic Script
```bash
#!/bin/bash
echo "=== Redmine MCP Server Diagnostics ==="
echo "Python version: $(python --version)"
echo "FastMCP installed: $(pip show fastmcp | grep Version || echo 'Not installed')"
echo "Environment variables:"
echo "  REDMINE_URL: ${REDMINE_URL:0:20}..."
echo "  REDMINE_API_KEY: ${REDMINE_API_KEY:0:8}..."
echo "Network connectivity:"
curl -I -s --connect-timeout 5 "$REDMINE_URL" || echo "Connection failed"
echo "=== End Diagnostics ==="
```