# Redmine MCP Server

<!-- test-status-badge -->\n[![Tests](https://img.shields.io/github/actions/workflow/status/zacharyelston/rrmcpy/build-and-test.yml?branch=main&label=tests&style=for-the-badge)](https://github.com/zacharyelston/rrmcpy/actions)\n

[![Tests](https://img.shields.io/github/actions/workflow/status/zacharyelston/rrmcpy/build-and-test.yml?branch=main&label=tests&style=for-the-badge)](https://github.com/zacharyelston/rrmcpy/actions)

A production-ready Python MCP Server for Redmine with modular architecture, featuring comprehensive API management, robust error handling, and extensible tool registry system.

## Features

- **Modular Architecture**: Separated core infrastructure, service layer, and tool registry for maintainability
- **Comprehensive Issue Management**: Full CRUD operations with validation and error handling
- **Centralized Configuration**: Type-safe environment variable handling with validation
- **Tool Registry System**: Plugin-like architecture for extensible functionality
- **Robust Error Handling**: Standardized exceptions and consistent error responses
- **Production-Ready**: Health checking, logging, and connection management

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
- `SERVER_MODE`: Server mode - 'live', 'test', or 'debug' (default: live)
- `LOG_LEVEL`: Logging level - 'DEBUG', 'INFO', 'WARNING', or 'ERROR' (default: INFO)
- `MCP_TRANSPORT`: Transport protocol - 'stdio', 'sse', or 'streamable-http' (default: stdio)

## Usage

The MCP server communicates using the MCP protocol over STDIO. It provides tools for Redmine API operations and integrates seamlessly with MCP clients like Claude Desktop.

### Available Tools

#### Issue Management
- `redmine-create-issue`: Create new issues with validation
- `redmine-get-issue`: Retrieve issue details by ID with optional includes
- `redmine-list-issues`: List issues with filtering and pagination
- `redmine-update-issue`: Update existing issues with notes
- `redmine-delete-issue`: Delete issues

#### Administrative
- `redmine-health-check`: Check Redmine connection health
- `redmine-get-current-user`: Get current authenticated user information

## Architecture

The server features a modern modular architecture with clear separation of concerns:

### Core Infrastructure (`src/core/`)
- **Configuration Management**: Type-safe environment variable handling with validation
- **Error Handling**: Standardized exceptions and consistent error responses
- **Logging**: Centralized logging configuration with stderr output for MCP compatibility

### Service Layer (`src/services/`)
- **Business Logic**: Separated from API clients with proper validation
- **Input Validation**: Data cleaning and type checking
- **Response Formatting**: Consistent success/error response structure

### Tool Registry (`src/tools/`)
- **Plugin Architecture**: Extensible tool system with registry pattern
- **Tool Isolation**: Each tool can be tested and developed independently
- **Dynamic Registration**: Tools are automatically registered with FastMCP

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

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
export LOG_LEVEL=DEBUG
```

3. Run the server:
```bash
python main.py
```

### Project Structure
```
src/
├── mcp_server.py           # Main MCP server with modular architecture
├── core/                   # Core infrastructure
│   ├── config.py          # Configuration management
│   ├── errors.py          # Error handling
│   └── logging.py         # Logging setup
├── services/               # Business logic layer
│   ├── base_service.py    # Base service class
│   └── issue_service.py   # Issue management service
├── tools/                  # Tool registry system
│   ├── registry.py        # Tool registry
│   ├── base_tool.py       # Base tool interface
│   ├── issue_tools.py     # Issue management tools
│   └── admin_tools.py     # Administrative tools
└── [api clients]          # Existing API client modules
```