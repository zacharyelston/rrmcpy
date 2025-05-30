# Redmine MCP Server

[![Tests](https://img.shields.io/github/actions/workflow/status/zacharyelston/rrmcpy/build-and-test.yml?branch=main&label=tests&style=for-the-badge)](https://github.com/zacharyelston/rrmcpy/actions)

A robust Python-based MCP (Model Context Protocol) server for Redmine API integration. Designed for containerized deployment with STDIO communication and full MCP protocol compliance.

## Features

- **Complete Redmine API Coverage**: Issues, projects, users, groups, versions, and more
- **MCP Protocol Compliance**: Full support for MCP 2024-11-05 specification
- **STDIO Communication**: Secure communication via standard input/output (no network ports)
- **Robust Error Handling**: Standardized error responses with detailed logging
- **Automatic Reconnection**: Exponential backoff retry logic with health monitoring
- **Container-Ready**: Production-ready Docker deployment with minimal configuration
- **100% Test Coverage**: Comprehensive test suite with automated CI/CD

## Quick Start

### Prerequisites

- Redmine API key with appropriate permissions

### Using Docker (Recommended)

1. Build the Docker image:
```bash
docker build -t redmine-mcp-server .
```

2. Run the server:
```bash
docker run -e REDMINE_URL=https://your-redmine.com -e REDMINE_API_KEY=your-api-key redmine-mcp-server
```

### Local Testing

Use the provided testing utilities:
```bash
# Interactive Docker testing menu
./utils/test-docker.sh

# Basic connectivity test
python scripts/test-minimal.py
```

### Environment Variables

- `REDMINE_URL`: URL of your Redmine instance (default: https://redstone.redminecloud.net)
- `REDMINE_API_KEY`: Your Redmine API key (required)
- `SERVER_MODE`: Server mode, 'live' or 'test' (default: live)
- `LOG_LEVEL`: Logging level, 'debug', 'info', 'warning', or 'error' (default: info)

## Usage

The MCP server communicates using the MCP protocol over STDIO. It provides tools for Redmine API operations and integrates seamlessly with MCP clients like Claude Desktop.

### Available Tools

#### Issue Management
- `list_issues`: List issues with optional filtering by project, status, or assignee
- `get_issue`: Get detailed information about a specific issue
- `create_issue`: Create a new issue
- `update_issue`: Update an existing issue

#### Project Management
- `list_projects`: List all accessible projects
- `get_project`: Get detailed project information

#### User Management
- `get_current_user`: Get information about the authenticated user
- `list_users`: List all users (requires admin privileges)

#### System
- `health_check`: Verify Redmine connection and server status

## Architecture

### MCP Protocol Implementation
- **STDIO Transport**: Direct JSON-RPC communication via standard input/output
- **Protocol Compliance**: Full adherence to MCP 2024-11-05 specification
- **Error Handling**: Proper JSON-RPC error responses with detailed messages

### Reliability Features
- **Connection Management**: Automatic reconnection with exponential backoff retry logic
- **Health Monitoring**: Built-in health checks with connection status monitoring
- **Request Validation**: Input validation for all API operations

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
├── main.py                 # Main entry point
├── stdio_server.py         # MCP STDIO server implementation  
├── redmine_client.py       # Unified Redmine API client
├── base.py                 # Base client with error handling
├── connection_manager.py   # Automatic reconnection logic
├── issues.py              # Issue management
├── projects.py            # Project management
├── users.py               # User management
└── versions.py            # Version management

tests/
├── test_proper_mcp.py      # MCP implementation tests
├── test_error_handling.py  # Error handling validation
├── test_connection_manager.py # Connection reliability tests
└── test_logging.py         # Logging functionality tests

scripts/
├── test-minimal.py         # Basic connectivity test
├── redstone_demo.py        # Interactive Redmine demo
└── [utility scripts]      # Development and testing utilities

utils/
└── test-docker.sh          # Docker testing utility
```