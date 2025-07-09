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
The tools are registered through `tool_registrations.py` which organizes them by category:
- Issue management tools - CRUD operations for issues
- Project management tools - Full project lifecycle management
- Version management tools - Roadmap and version control
- Wiki management tools - Wiki page operations
- Template system tools - Issue templates and subtask creation
- Administrative tools - Health checks and system information

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

### Available Tools (29 Total)

#### Issue Management (5 tools)
1. `redmine-create-issue` - Create new issues with full parameter support
2. `redmine-get-issue` - Retrieve issue details by ID
3. `redmine-list-issues` - List issues with filtering options
4. `redmine-update-issue` - Update existing issues
5. `redmine-delete-issue` - Delete issues

#### Project Management (6 tools)
6. `redmine-list-projects` - List all available projects
7. `redmine-create-project` - Create new projects with validation
8. `redmine-update-project` - Update project attributes
9. `redmine-delete-project` - Delete projects by ID or identifier
10. `redmine-archive-project` - Archive a project (set status to archived)
11. `redmine-unarchive-project` - Unarchive a project (set status to active)

#### Version Management (6 tools)
12. `redmine-list-versions` - List versions for a project
13. `redmine-get-version` - Get version details by ID
14. `redmine-create-version` - Create new versions
15. `redmine-update-version` - Update version attributes
16. `redmine-delete-version` - Delete versions
17. `redmine-get-issues-by-version` - Get issues for a specific version

#### Wiki Management (5 tools)
18. `redmine-list-wiki-pages` - List wiki pages in a project
19. `redmine-get-wiki-page` - Get wiki page content
20. `redmine-create-wiki-page` - Create new wiki pages
21. `redmine-update-wiki-page` - Update existing wiki pages
22. `redmine-delete-wiki-page` - Delete wiki pages

#### Template System (4 tools)
23. `redmine-use-template` - Create issues from templates with placeholders
24. `redmine-create-subtasks` - Create standard subtasks for a parent issue
25. `redmine-list-templates` - List available templates
26. `redmine-list-issue-templates` - List issue templates from Templates project

#### Administrative Tools (3 tools)
27. `redmine-health-check` - Check Redmine connection health
28. `redmine-version-info` - Get server version and environment info
29. `redmine-current-user` - Get current authenticated user information

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
┌─────────────────────────────────────────────────────────────────────┐
│                         MCP Server (29 Tools)                       │
├─────────────────────────────────────────────────────────────────────┤
│          FastMCP Integration & Tool Registration System             │
├─────────────────────────────────────────────────────────────────────┤
│                        Tool Registry Layer                          │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│ │ Issue Tools  │ │Project Tools │ │Version Tools │ │ Wiki Tools │ │
│ │  (5 tools)   │ │  (6 tools)   │ │  (6 tools)   │ │ (5 tools)  │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
│ ┌──────────────┐ ┌──────────────┐                                  │
│ │Template Tools│ │ Admin Tools  │                                  │
│ │  (4 tools)   │ │  (3 tools)   │                                  │
│ └──────────────┘ └──────────────┘                                  │
├─────────────────────────────────────────────────────────────────────┤
│                        Service Layer                                │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│ │Issue Service │ │Project Svc   │ │Wiki Service  │ │Template Svc│ │
│ └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│                      API Client Layer                               │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│ │Issue Client  │ │Project Client│ │Roadmap Client│ │Wiki Client │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│                    Core Infrastructure                              │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│ │Configuration │ │Error Handling│ │   Logging    │ │Client Mgr  │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                      ┌─────────────────┐
                      │  Redmine API    │
                      └─────────────────┘
```

This modular architecture provides a robust, maintainable, and extensible foundation for the Redmine MCP Server.