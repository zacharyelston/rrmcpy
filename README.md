# Redmine MCP Server

<!-- test-status-badge -->\n[![Tests](https://img.shields.io/github/actions/workflow/status/zacharyelston/rrmcpy/build-and-test.yml?branch=main&label=tests&style=for-the-badge)](https://github.com/zacharyelston/rrmcpy/actions)\n

A production-ready Python MCP Server for Redmine with a highly modular architecture designed to fight complexity, featuring comprehensive API management, robust error handling, and an extensible tool registry system.

## Features

- **Fighting Complexity Architecture**: Designed with separation of concerns and clear component boundaries
- **Comprehensive Issue Management**: Full CRUD operations with validation and error handling
- **Centralized Configuration**: Type-safe environment variable handling with validation
- **Tool Registry System**: Plugin-like architecture for extensible functionality
- **Robust Error Handling**: Standardized exceptions and consistent error responses
- **Production-Ready**: Health checking, logging, and connection management
- **Testability**: Dedicated testing module for automated validation

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
./test-docker.sh

# Test mode (validates configuration, tool registry, health check, and authentication)
python src/server.py --test

# Create real issue test
python scripts/test_create_real.py
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

The server features a modern modular architecture that follows the "Fighting Complexity" design philosophy with clear separation of concerns:

### Core Server (`src/server.py`)
- **RedmineMCPServer**: Main orchestration class with simplified logic
- **Initialization Flow**: Configuration → logging → clients → services → tools → run
- **Test Mode**: Comprehensive validation with health checks and tool verification

### Core Infrastructure (`src/core/`)
- **ClientManager**: Centralized management of all Redmine API clients
- **ServiceManager**: Manages service layer with client dependencies
- **ToolRegistrations**: Implementation of all MCP tools with consistent patterns
- **Configuration**: Type-safe environment variable handling with validation
- **Error Handling**: Standardized exceptions and consistent error responses
- **Logging**: Centralized logging configuration with stderr output for MCP compatibility
- **ToolTester**: Dedicated module for test mode validation

### API Clients
- **Base Client**: Common HTTP functionality and authentication
- **Specialized Clients**: Issues, projects, users, groups, versions, roadmap
- **Error Handling**: Consistent response format across all endpoints

### Design Philosophy
The architecture follows key software design principles:
- **SOLID**: Single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion
- **DRY**: Don't repeat yourself
- **KISS**: Keep it simple
- **YAGNI**: You aren't gonna need it

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
├── server.py                # Main MCP server with modular architecture
├── core/                    # Core infrastructure
│   ├── config.py           # Configuration management
│   ├── errors.py           # Error handling
│   ├── logging.py          # Logging setup
│   ├── client_manager.py   # Client initialization and management
│   ├── service_manager.py  # Service layer management
│   ├── tool_registrations.py # Tool implementation and registration
│   └── tool_test.py        # Test mode validation
├── services/                # Business logic layer
│   └── [service modules]   # Specialized service modules
└── [api clients]           # API client modules (issues, projects, versions, etc.)
```

### Refactoring Documentation
Detailed information about the modular architecture and refactoring approach can be found in [refactoring_plan.md](refactoring_plan.md).