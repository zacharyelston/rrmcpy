# Redmine MCPServer

A Python/FastMCP-based MCPServer for Redmine that handles all Redmine APIs for issues, projects, versions, users, and groups. This server uses the MCP protocol with STDIO communication, making it ideal for loading in MCP clients via Docker.

## Features

- Seamless integration with Redmine API
- STDIO-based communication using the MCP protocol
- Support for all major Redmine features:
  - Issues management
  - Projects management
  - Versions management
  - Users management
  - Groups management
- Docker compatibility for easy deployment in MCP clients
- Configurable logging levels
- Support for "live" and "test" server modes

## Configuration

The server can be configured using the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `REDMINE_URL` | URL of the Redmine instance | `http://localhost:3000` |
| `REDMINE_API_KEY` | API key for Redmine authentication | (required) |
| `SERVER_MODE` | Server mode ('live' or 'test') | `live` |
| `LOG_LEVEL` | Logging level (debug, info, warning, error) | `info` |

## Usage with Docker

### Building the Docker Image

```shell
# Build the Docker image
docker build -t redmine-mcp-server .
```

### Running the Docker Container

To run the server using Docker:

```shell
docker run \
  -e REDMINE_URL="http://m1ni.local:3100" \
  -e REDMINE_API_KEY="af159c9b93c7c41a6b629de19b84f2d14e5854a4" \
  -e SERVER_MODE="live" \
  -e LOG_LEVEL="debug" \
  --name redmine-mcp-server \
  redmine-mcp-server
```

Since this is an MCP server that communicates via STDIO, you can also pipe commands to it:

```shell
echo '{"method": "GET", "path": "/health", "data": {}}' | docker run -i redmine-mcp-server
```

The default configuration values are pre-configured in the Docker image, but you can override them as shown above.

### Using with MCP Clients

This server is designed to be loaded into MCP clients. The MCP client will communicate with the server via STDIO, sending JSON requests and receiving JSON responses.
