# Redmine MCP Server Test Suite

This directory contains tests for the Redmine MCP Server, organized according to the "Built for Clarity" design philosophy.

## Test Organization

Tests are organized into three main categories:

### 1. Unit Tests (`tests/unit/`)

Unit tests focus on testing individual components in isolation, using mocks for dependencies. These tests are fast, reliable, and help verify the behavior of specific functions or classes.

- `test_create_operations.py` - Tests for 201 response handling in create operations
- `test_error_handling.py` - Tests for standardized error handling
- `test_project_tools.py` - Tests for project management tools

### 2. Integration Tests (`tests/integration/`)

Integration tests verify that multiple components work together correctly. These tests still use mocks for external dependencies but test the interaction between internal components.

- `test_project_workflow.py` - Tests for complete project management workflow

### 3. Live Tests (`tests/live/`)

Live tests run against an actual Redmine/RedMica instance and verify that the system works correctly in a real environment. These tests require valid Redmine API credentials.

- `test_create_operations.py` - Live tests for create operations
- `test_error_handling.py` - Live tests for error handling
- `test_project_management.py` - Live tests for project management functionality

## Running Tests

### Running Unit Tests

```bash
python -m pytest tests/unit
```

### Running Integration Tests

```bash
python -m pytest tests/integration
```

### Running Live Tests

Live tests require valid Redmine API credentials:

```bash
export REDMINE_URL=https://your-redmine-instance.com
export REDMINE_API_KEY=your-api-key
python -m pytest tests/live
```

## Test Design Principles

Following the "Built for Clarity" design philosophy, our tests are:

1. **Focused** - Each test file focuses on a specific functionality
2. **Readable** - Test names and organization clearly communicate what's being tested
3. **Maintainable** - Tests are organized by functionality, not by version or release
4. **Independent** - Tests can run in isolation and don't depend on each other
5. **Thorough** - We test both success and error cases

## Adding New Tests

When adding new tests:

1. Place unit tests in `tests/unit/`
2. Place integration tests in `tests/integration/`
3. Place live tests in `tests/live/`
4. Name test files according to the functionality they test, not by version
5. Follow the existing patterns for setup, teardown, and test organization
