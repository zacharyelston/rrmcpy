# Python Setup Guide for Redmine MCP Server

## Quick Start (No Docker)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export REDMINE_URL="https://your-redmine-instance.com"
export REDMINE_API_KEY="your-api-key-here"
```

### 3. Run the Server
```bash
# Simple FastMCP approach (recommended)
python fastmcp_server.py

# Or with configuration wrapper
python mcp_config_example.py

# Or complex implementation
python src/mcp_server.py
```

## Configuration Options

### Environment Variables
- `REDMINE_URL` - Your Redmine instance URL (required)
- `REDMINE_API_KEY` - Your Redmine API key (required)
- `MCP_SERVER_MODE` - Server mode: live, debug, test (default: live)
- `MCP_LOG_LEVEL` - Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
- `MCP_SERVER_TYPE` - Implementation: fastmcp, complex (default: fastmcp)

### Python Integration Example
```python
import os
from fastmcp_server import main
import asyncio

# Configure environment
os.environ['REDMINE_URL'] = 'https://your-redmine.com'
os.environ['REDMINE_API_KEY'] = 'your-key'

# Run server
asyncio.run(main())
```

## MCP Client Connection

### Claude Desktop Configuration
Add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "redmine": {
      "command": "python",
      "args": ["/path/to/fastmcp_server.py"],
      "env": {
        "REDMINE_URL": "https://your-redmine.com",
        "REDMINE_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Direct Python Usage
```python
# Test server functionality
from src.issues import IssueClient

client = IssueClient(
    base_url="https://your-redmine.com",
    api_key="your-api-key"
)

# Test connection
health = client.health_check()
print(f"Connection: {'OK' if health else 'Failed'}")

# Create an issue
issue_data = {
    "project_id": "project1",
    "subject": "Test Issue",
    "description": "Created via Python"
}
result = client.create_issue(issue_data)
print(f"Created issue: {result['issue']['id']}")
```

## Available Tools

- `redmine-create-issue` - Create new issues
- `redmine-get-issue` - Get issue details
- `redmine-list-issues` - List and filter issues
- `redmine-update-issue` - Update existing issues
- `redmine-delete-issue` - Delete issues
- `redmine-health-check` - Check server connectivity
- `redmine-get-current-user` - Get authenticated user info

## Troubleshooting

### Connection Issues
```python
# Test Redmine connectivity
from src.issues import IssueClient
client = IssueClient(url, api_key)
if client.health_check():
    print("Connection successful")
else:
    print("Check URL and API key")
```

### Container Environments
For Jupyter, VS Code, or other container environments:
```bash
pip install nest_asyncio
```

The server automatically handles event loop conflicts in container environments.