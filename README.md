# Redmine MCP Server

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

