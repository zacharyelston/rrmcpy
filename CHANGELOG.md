# Changelog

All notable changes to the Redmine MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project management tools: `redmine-create-project`, `redmine-update-project`, `redmine-delete-project`
- Comprehensive test suite for project management tools
- Live integration tests for project operations
- Automated cleanup workflow for branches and PRs
- Scripts for cleaning up badge update PRs

### Changed
- Updated GitHub Actions workflow to commit badge updates directly instead of creating PRs
- README now shows 17 tools instead of 14

### Fixed
- Badge update workflow no longer creates accumulating PRs
- Create operations bug (201 response handling) - already fixed in codebase

## [0.9.0] - In Progress

### Fixed
- Create operations now properly handle 201 Created responses
- Created resources are now returned to clients
- Location header ID extraction implemented

### Added
- Project management tools implementation
- Test coverage for create operations

## [0.8.0] - 2025-06-04

### Added
- Initial modular architecture implementation
- Core infrastructure with ClientManager, ServiceManager, ToolRegistrations
- Issue management tools (create, read, update, delete, list)
- Version management tools
- Health check and version info tools
- Current user authentication tool
- Docker support with test mode
- Comprehensive error handling system
- Configuration management system
- FastMCP integration

### Architecture
- Implemented "Built for Clarity" design philosophy
- SOLID principles applied throughout
- Clear separation of concerns
- Modular, testable components
