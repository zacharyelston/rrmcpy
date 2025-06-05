# API Specifications

This directory contains YAML specifications for the Redmine MCP tools and features. These specifications define the methods, parameters, and return types for each feature area, providing documentation for the API design.

## Purpose

These specifications serve as:
1. Documentation for the MCP interface
2. Reference for implementing server feature modules
3. Guidelines for client application development
4. Basis for generating API documentation

## Relationship to Codebase

These specifications are associated with the implementation in `/src/rmcpy/server/features/` and should be kept in sync with any API changes. When modifying a feature module, the corresponding YAML specification should be updated accordingly.

## File Structure

Each YAML file corresponds to a feature area in Redmine:

- `calendar.yaml`: Calendar functionality
- `custom_fields.yaml`: Custom field definitions
- `documents.yaml`: Document management
- `forums.yaml`: Forum functionality
- `gantt.yaml`: Gantt chart generation
- `groups.yaml`: User group management
- `index.yaml`: Index of available features
- `issues.yaml`: Issue tracking and management
- `news.yaml`: News articles and notifications
- `projects.yaml`: Project management
- `queries.yaml`: Saved queries and filters
- `repositories.yaml`: Source code repositories
- `time_entries.yaml`: Time tracking entries
- `users.yaml`: User account management
- `versions.yaml`: Version/milestone management
- `wiki.yaml`: Wiki page functionality

## Format

The YAML files follow a standard format with `mcpMethods` defining individual API methods, each containing:
- `name`: Method name
- `summary`: Brief description
- `parameters`: List of input parameters with types and requirements
- `returns`: Description of return value

## Usage

These specifications can be used for:
1. Reference during implementation
2. Validation of API consistency
3. Generation of documentation
4. Development of client applications

When implementing new features, refer to these specifications to ensure consistent API design and parameter handling.
