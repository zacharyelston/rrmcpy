# Redmine MCP Server

<!-- test-status-badge -->
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen?style=for-the-badge)](https://github.com/actions)

A Python/FastMCP-based MCPServer for Redmine that runs in Docker and handles all Redmine APIs.

See docs/README.md for full documentation.

## Quick Start

```bash
# Build Docker image
docker build -t redmine-mcp-server .

# Run in live mode
docker run -e REDMINE_URL="https://your-redmine-instance.com" \
           -e REDMINE_API_KEY="your-api-key" \
           -e SERVER_MODE="live" \
           redmine-mcp-server

# Run in test mode
docker run -e REDMINE_URL="https://your-redmine-instance.com" \
           -e REDMINE_API_KEY="your-api-key" \
           -e SERVER_MODE="test" \
           -e TEST_PROJECT="p1" \
           redmine-mcp-server
```

## Project Structure

- `src/`: Main source code
- `tests/`: Test files
- `scripts/`: Utility scripts
- `docs/`: Documentation

## Test Status

| Module | Status | Last Updated |
|--------|--------|-------------|
| Redmine Connectivity | ✅ Passing | May 18, 2025 |
| Issues API | ✅ Passing | May 18, 2025 |
| Projects API | ✅ Passing | May 18, 2025 |
| Versions API | ✅ Passing | May 18, 2025 |
| Users API | ✅ Passing | May 18, 2025 |
| Groups API | ✅ Passing | May 18, 2025 |
| MCP Protocol | ✅ Passing | May 18, 2025 |

Last run: `May 18, 2025` - All tests are passing!

