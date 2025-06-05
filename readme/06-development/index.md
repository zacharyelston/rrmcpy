# Development Guide

This guide provides information for developers contributing to the Redmine MCP Server.

## Project Structure

```
rrmcpy/
├── src/                    # Source code
│   ├── core/               # Core components
│   │   ├── client_manager.py
│   │   ├── service_manager.py
│   │   ├── tool_registry.py
│   │   └── tool_registrations.py
│   ├── services/           # Business logic services
│   ├── tools/              # MCP tool implementations
│   └── server.py           # Entry point
├── tests/                  # Test suite
├── docs/                   # Documentation
├── readme/                 # README chapters
└── scripts/                # Utility scripts
```

## Development Environment

For the best development experience:

1. Use Python 3.10+ with a dedicated virtual environment
2. Install fastmcp in editable mode
3. Run tests before submitting changes

For detailed setup instructions, see [README-python.md](../README-python.md).

## Testing

Run the test suite to verify your changes:

```bash
# Run all tests
python -m unittest discover -s tests

# Run specific test file
python -m unittest tests/test_mcp_server.py

# Run with test mode
python -m src.server --test
```

## Coding Standards

Follow these standards to maintain our "Keep It Simple" philosophy:

1. **Simple > Clever**: Choose clear, readable code over complex, clever solutions
2. **Small Pieces**: Create focused components that do one thing well
3. **Hide the Mess**: Use clean interfaces to encapsulate implementation details
4. **Documentation**: Include clear docstrings that explain the "what" and "why"
5. **Error Handling**: Use consistent error handling that's easy to understand
6. **Testing**: Write simple tests that verify functionality without complexity

## Adding New Tools

To add new MCP tools:

1. Start simple - implement the core functionality first
2. Use existing patterns in `client_manager.py` and `tool_registrations.py`
3. Add focused service methods if needed
4. Add tool implementation in `tool_registrations.py`
5. Register your new tool in the `register_all_tools()` method
6. Write tests for your new tool
7. Update the tool inventory in `readme/04-tools.md`

## Making Changes

1. Make small, incremental changes - one focused change at a time
2. Work methodically and validate each step before proceeding
3. Always run tests after each significant change
4. Ask yourself: "How could this be simpler?"
5. Remove complexity whenever possible

## Workflow

1. Create a new branch for your changes
2. Make small, focused commits with clear messages
3. Run tests to verify your changes
4. Submit a pull request with a clear description
5. Respond to code review feedback

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration. On each push:

1. Code is built and tested
2. Docker image is created
3. Tests run in a containerized environment
4. Updates README badges if tests pass