# Redmine MCP Server (No Web UI)

A robust Python-based MCPServer for Redmine, engineered to provide comprehensive API management and testing capabilities. This version contains only the core MCP server functionality with STDIO communication, without the web interface.

## Key Components

- FastMCP framework for Redmine API interactions
- STDIO-based communication protocol 
- Automated workflow testing
- Dynamic roadmap and issue tracking
- Modular client architecture for extensible API handling

## Usage

The MCP Server can be started using:

```
python main.py
```

The server accepts environment variables for configuration:

- `REDMINE_URL`: URL to the Redmine instance (default: https://redstone.redminecloud.net)
- `REDMINE_API_KEY`: API key for authentication
- `SERVER_MODE`: Mode of operation (live, test)
- `LOG_LEVEL`: Logging level (debug, info, warning, error)

## MCP Client Usage

Communication with the MCP server happens through standard input/output (STDIO). Here's an example client request:

```python
import json
import sys

# Send request to server
request = {
    "method": "GET",
    "path": "/users/current.json",
    "data": {}
}
print(json.dumps(request), flush=True)

# Read response from server
response = json.loads(sys.stdin.readline().strip())
print(f"Response: {response}")
```

## Architecture

The server is organized into modules for different Redmine functionality:

- Issues management
- Project operations
- User and group handling
- Roadmap and versions

Each module provides a clean API to interact with the corresponding Redmine functionality.