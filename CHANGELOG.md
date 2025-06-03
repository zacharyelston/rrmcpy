# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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