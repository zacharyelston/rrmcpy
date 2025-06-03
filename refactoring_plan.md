# Redmine MCP Server Refactoring Plan

## Design Philosophy

Following the "Fighting Complexity" philosophy, this refactoring aims to:

1. **Simplify the code structure** by breaking the monolithic `server.py` into specialized modules
2. **Encapsulate complexity** through clear separation of concerns
3. **Apply SOLID principles** for improved maintainability
4. **Reduce layers of indirection** while maintaining clean interfaces
5. **Improve testability** through modular components

## Modular Architecture

The refactored server will consist of these key components:

### 1. ClientManager (`core/client_manager.py`)
- **Purpose**: Initialize and manage all Redmine API clients
- **Responsibilities**:
  - Initialize client connections to Redmine API
  - Manage client lifecycle and configuration
  - Provide centralized access to different clients (issues, projects, users, etc.)
- **Key methods**:
  - `initialize_clients()` - Create all client instances
  - `get_client(client_type)` - Get a specific client by type

### 2. ServiceManager (`core/service_manager.py`)
- **Purpose**: Initialize and manage service layer components
- **Responsibilities**:
  - Link clients to appropriate services
  - Manage service lifecycle
  - Provide centralized access to services
- **Key methods**:
  - `initialize_services()` - Create all service instances
  - `get_service(service_type)` - Get a specific service by type

### 3. ToolRegistry (`core/tool_registry.py`)
- **Purpose**: Handle MCP tool registration and execution
- **Responsibilities**:
  - Register tools with FastMCP
  - Manage tool execution flow
  - Provide consistent error handling for tools
- **Key methods**:
  - `register(tool_class, service)` - Register a tool with its service
  - `list_tool_names()` - Get list of registered tools

### 4. ToolRegistrations (`core/tool_registrations.py`)
- **Purpose**: Contain all tool registration implementations
- **Responsibilities**:
  - Define and register all MCP tools (issue, admin, version)
  - Implement parameter validation and error handling
  - Format tool responses consistently
- **Key methods**:
  - `register_issue_tools()` - Register issue management tools
  - `register_admin_tools()` - Register admin tools
  - `register_version_tools()` - Register version management tools

### 5. RedmineMCPServer (simplified `server.py`)
- **Purpose**: Main server class with clean orchestration logic
- **Responsibilities**:
  - Configure and initialize all components
  - Manage server lifecycle (startup, shutdown)
  - Handle container compatibility
- **Key methods**:
  - `initialize()` - Set up configuration and logging
  - `_initialize_components()` - Initialize all modular components
  - `run()` - Start the MCP server

## Implementation Steps

1. Create the modular components (already done):
   - `core/client_manager.py`
   - `core/service_manager.py`
   - `core/tool_registry.py`
   - `core/tool_registrations.py`

2. Refactor `server.py` to:
   - Import the new modular components
   - Replace direct client/service creation with managers
   - Simplify tool registration through ToolRegistrations
   - Update server initialization and run logic
   - Handle container compatibility correctly

3. Ensure consistent error handling and logging across all modules

4. Add appropriate tests for each module

## Migration Considerations

- Maintain compatibility with existing MCP tools and interfaces
- Keep consistent error handling and response formatting
- Ensure container-based deployments continue to work
- Preserve logging for debugging and tracing

This modular approach will significantly reduce complexity while maintaining all functionality, making the codebase easier to understand, maintain, and extend.
