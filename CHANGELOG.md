# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2025-06-03

### Added
- Complete modular architecture with core infrastructure modules (config, errors, logging)
- Service layer for business logic separation from API clients
- Tool registry system with plugin-like architecture for extensible functionality
- Comprehensive issue management tools with validation and error handling
- Administrative tools for health checking and user information
- Centralized configuration management with type-safe environment variable handling
- Standardized error handling with custom exception classes
- Production-ready server implementation with real Redmine API integration

### Changed
- Major restructure from monolithic to modular architecture
- Separated concerns into core/, services/, and tools/ modules
- Updated FastMCP integration with proper tool registration
- Enhanced logging for better debugging and monitoring
- Improved documentation with detailed architecture guide

### Fixed
- Tool registration issues with FastMCP parameter handling
- Import dependencies in modular architecture
- Service layer initialization and dependency injection
- Error handling and response formatting throughout the system

### Removed
- Legacy testing files after successful modular architecture validation
- Completed todo-now.md implementation plan

## [1.2.0] - 2025-06-02

### Removed
- `src/stdio_server.py` - Eliminated redundant STDIO server implementation (340 lines)
- Duplicate tool definitions and manual JSON-RPC protocol handling

### Changed
- Renamed `src/proper_mcp_server.py` to `src/mcp_server.py` for clarity
- Updated `src/main.py` to use consolidated FastMCP server
- FastMCP.run() is now called synchronously (removed async wrapper)

### Fixed
- Server implementation duplication causing maintenance overhead
- Inconsistent tool definitions between server implementations
- Unnecessary complexity in transport handling

### Technical Notes
- FastMCP natively supports STDIO transport as default
- Transport options: STDIO (default), SSE, streamable-HTTP
- Reduced codebase size by ~15%
- Single source of truth for MCP server implementation