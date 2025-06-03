# Redmine MCP Server - Modular Architecture

## Overview

The Redmine MCP Server has been completely restructured using a modular architecture that separates concerns, improves maintainability, and enables better testing. The new architecture follows industry best practices with clear separation between configuration, business logic, and tool implementations.

## Architecture Components

### Core Infrastructure (`src/core/`)

**Configuration Management (`config.py`)**
- Centralized environment variable handling with validation
- Type-safe configuration classes for different concerns
- Support for multiple server modes (live, test, debug)

**Error Handling (`errors.py`)**
- Standardized exception classes for different error types
- Consistent error response formatting across all modules
- Proper error context and traceability

**Logging (`logging.py`)**
- Centralized logging configuration using stderr for MCP compatibility
- Structured logging with proper context
- Environment-based log level configuration

### Service Layer (`src/services/`)

**Base Service (`base_service.py`)**
- Abstract base class with common validation and error handling
- Standardized response formatting
- Shared business logic patterns

**Issue Service (`issue_service.py`)**
- Business logic for issue management operations
- Input validation and data cleaning
- Error handling and response formatting

### Tool Registry System (`src/tools/`)

**Tool Registry (`registry.py`)**
- Plugin-like architecture for tool management
- Dynamic tool registration and execution
- Health checking and tool discovery

**Base Tool (`base_tool.py`)**
- Abstract interface for all MCP tools
- Standardized tool definition and execution
- Error handling and safety wrappers

**Tool Implementations**
- `issue_tools.py` - Complete issue management tools
- `admin_tools.py` - Health checking and user information tools

## Key Benefits

1. **Separation of Concerns** - Clear boundaries between configuration, business logic, and tool implementations
2. **Testability** - Each component can be tested in isolation with proper mocking
3. **Maintainability** - Modular structure makes code easier to understand and modify
4. **Extensibility** - New tools and services can be added without affecting existing code
5. **Error Handling** - Consistent error handling and reporting across all components
6. **Configuration** - Centralized and validated configuration management

## Current Implementation Status

### Completed Components
- ✅ Core infrastructure (config, errors, logging)
- ✅ Service layer with business logic separation
- ✅ Tool registry system with plugin architecture
- ✅ Complete issue management tools
- ✅ Administrative tools for health checking
- ✅ FastMCP integration with proper tool registration
- ✅ Comprehensive test suite validation
- ✅ Production-ready server implementation

### Available Tools
1. `redmine-create-issue` - Create new issues with validation
2. `redmine-get-issue` - Retrieve issue details by ID
3. `redmine-list-issues` - List issues with filtering options
4. `redmine-update-issue` - Update existing issues
5. `redmine-delete-issue` - Delete issues
6. `redmine-health-check` - Check Redmine connection health
7. `redmine-get-current-user` - Get current user information

## Usage

### Running the Server
```bash
# Production mode with STDIO transport
python main.py

# Test mode
SERVER_MODE=test python main.py
```

### Environment Configuration
```bash
REDMINE_URL=https://your-redmine.example.com
REDMINE_API_KEY=your_api_key_here
SERVER_MODE=live|test|debug
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
MCP_TRANSPORT=stdio|sse|streamable-http
```

### Testing
```bash
# Test modular architecture
python test_modular_server.py

# Test complete server functionality
python test_mcp_server.py
```

## Future Enhancements

The modular architecture provides a solid foundation for future enhancements:

1. **Additional Tools** - Easy to add project, user, and group management tools
2. **Enhanced Services** - Additional business logic and validation layers
3. **Plugin System** - External plugin support for custom functionality
4. **Advanced Configuration** - Multi-environment configuration support
5. **Performance Optimization** - Caching and connection pooling
6. **Monitoring** - Enhanced observability and metrics collection

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server                               │
├─────────────────────────────────────────────────────────────┤
│  FastMCP Integration & Tool Registration                    │
├─────────────────────────────────────────────────────────────┤
│                  Tool Registry                              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│  │   Issue Tools   │ │   Admin Tools   │ │ Future Tools │  │
│  └─────────────────┘ └─────────────────┘ └──────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                  Service Layer                              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│  │ Issue Service   │ │ Future Services │ │ Base Service │  │
│  └─────────────────┘ └─────────────────┘ └──────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                API Client Layer                             │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│  │ Issue Client    │ │ Other Clients   │ │ Base Client  │  │
│  └─────────────────┘ └─────────────────┘ └──────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                Core Infrastructure                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│  │ Configuration   │ │ Error Handling  │ │   Logging    │  │
│  └─────────────────┘ └─────────────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Redmine API     │
                    └─────────────────┘
```

This modular architecture provides a robust, maintainable, and extensible foundation for the Redmine MCP Server.