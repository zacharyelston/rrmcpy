# Redmine MCP Server

[![Tests](https://img.shields.io/github/actions/workflow/status/zacharyelston/rrmcpy/build-and-test.yml?branch=main&label=tests&style=for-the-badge)](https://github.com/zacharyelston/rrmcpy/actions)

A robust Python-based MCP (Model Context Protocol) server for Redmine API integration. Built with FastMCP and designed for containerized deployment with STDIO communication.


## Features

- **Comprehensive Redmine API Coverage**: Complete support for issues, projects, versions, users, and groups
- **FastMCP Protocol Compliance**: Proper MCP tool registration with Pydantic type validation
- **STDIO Communication**: Secure communication via standard input/output (no network ports)
- **Robust Error Handling**: Standardized error responses with detailed logging
- **Automatic Reconnection**: Exponential backoff retry logic with health monitoring
- **Container-Ready**: Docker deployment with minimal configuration

## Quick Start

### Prerequisites

- Redmine API key with appropriate permissions

### Using Docker (Recommended)

1. Build the Docker image:

```bash
docker build -t redmine-mcp-server .
```

2. Run the server with Docker:

```bash
docker run -e REDMINE_API_KEY=your-api-key-here redmine-mcp-server
```

### Environment Variables

- `REDMINE_URL`: URL of your Redmine instance (default: https://redstone.redminecloud.net)
- `REDMINE_API_KEY`: Your Redmine API key (required)
- `SERVER_MODE`: Server mode, 'live' or 'test' (default: live)
- `LOG_LEVEL`: Logging level, 'debug', 'info', 'warning', or 'error' (default: info)

## Usage

The MCP server communicates using the FastMCP protocol over STDIO. It provides MCP tools for Redmine API operations with proper Pydantic type validation.

### Available MCP Tools

#### Issue Management
- `list_issues`: List issues with optional filtering by project, status, or assignee
- `get_issue`: Get detailed information about a specific issue
- `create_issue`: Create a new issue with Pydantic validation
- `update_issue`: Update an existing issue

#### Project Management
- `list_projects`: List all accessible projects
- `get_project`: Get detailed project information including trackers and categories
- `create_project`: Create a new project

#### User Management
- `get_current_user`: Get information about the authenticated user
- `list_users`: List all users (requires admin privileges)

#### Version Management
- `list_versions`: List versions for a specific project

#### Health Check
- `health_check`: Verify Redmine connection and server status

## Architecture

### FastMCP Implementation
- **Proper Tool Registration**: Uses `@app.tool()` decorators following FastMCP best practices
- **Pydantic Models**: Type-safe request/response handling with automatic validation
- **STDERR Logging**: Logs are properly directed to stderr to avoid interfering with MCP protocol

### Error Handling & Reliability
- **Standardized Error Responses**: Consistent error format with timestamps and error codes
- **Connection Management**: Automatic reconnection with exponential backoff retry logic
- **Health Monitoring**: Built-in health checks with connection status caching

## Testing

Run the test suite to verify functionality:

```bash
python -m pytest tests/ -v
```

Test specific components:
```bash
# Test FastMCP implementation
python -m pytest tests/test_proper_mcp.py -v

# Test error handling
python -m pytest tests/test_error_handling.py -v

# Test connection reliability
python -m pytest tests/test_connection_manager.py -v
```

## Development

### Local Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export REDMINE_API_KEY=your-api-key-here
export REDMINE_URL=https://your-redmine-instance.com
export LOG_LEVEL=debug
```

3. Run the server:
```bash
python -m src.main
```

### Project Structure
```
src/
├── main.py                 # Entry point with proper FastMCP patterns
├── proper_mcp_server.py    # FastMCP server implementation
├── redmine_client.py       # Unified Redmine API client
├── base.py                 # Base client with error handling
├── connection_manager.py   # Automatic reconnection logic
└── [feature modules]       # Individual API feature implementations

tests/
├── test_proper_mcp.py      # FastMCP implementation tests
├── test_error_handling.py  # Error handling validation
└── test_connection_manager.py # Connection reliability tests
```