# Redmine MCP Server

A Python/FastMCP-based MCPServer for Redmine that runs in Docker and handles all Redmine APIs for issues, projects, versions, users, and groups.

## Overview

This project provides a server that exposes Redmine functionality through the MCP (Message Communication Protocol) interface. It communicates using standard input/output (STDIO) rather than network ports, making it ideal for integration with other MCP-compatible systems.

## Features

- **Full Redmine API Support**: Access all Redmine features including issues, projects, versions, users, and groups
- **STDIO Communication**: Uses standard input/output for communication rather than network ports
- **Docker Support**: Runs in a Docker container with configurable environment variables
- **Modular Architecture**: Well-organized codebase with separate modules for different Redmine features
- **Automated Testing**: Includes test suite for verifying functionality against a test project
- **Roadmap Management**: Tools for creating and managing feature roadmaps using Redmine versions

## Installation

### Prerequisites

- Docker
- Redmine instance with API access
- Redmine API key

### Docker Setup

Build the Docker image:

```bash
docker build -t redmine-mcp-server .
```

Run the container:

```bash
docker run -e REDMINE_URL="https://your-redmine-instance.com" \
           -e REDMINE_API_KEY="your-api-key" \
           -e SERVER_MODE="live" \
           redmine-mcp-server
```

### Environment Variables

- `REDMINE_URL`: URL of your Redmine instance
- `REDMINE_API_KEY`: API key for authentication
- `SERVER_MODE`: Server mode (`live` or `test`)
- `TEST_PROJECT`: Project identifier for test mode (default: `p1`)
- `LOG_LEVEL`: Logging level (default: `debug`)

## Usage

### Direct Python Usage

You can use the Redmine client directly in your Python code:

```python
from modules.redmine_client import RedmineClient

# Initialize the client
client = RedmineClient(
    base_url="https://your-redmine-instance.com",
    api_key="your-api-key"
)

# Get all projects
projects = client.get_projects()

# Create an issue
issue_data = {
    "project_id": 1,
    "subject": "Test issue",
    "description": "This is a test issue"
}
new_issue = client.create_issue(issue_data)
```

### MCP Client Usage

For integration with MCP systems, use the MCP client:

```python
from modules.mcp_client import MCPClient

# Initialize the client (pointing to the server script)
client = MCPClient(["python", "main.py"])

# Start the server process
client.start_server()

# Send requests
response = client.health_check()
projects = client.get_projects()

# Create an issue
issue_data = {
    "project_id": 1,
    "subject": "Test issue from MCP",
    "description": "This is a test issue created by the MCP client"
}
response = client.create_issue(issue_data)

# Clean up
client.stop_server()
```

## Testing

### Automated Tests

Run the test suite against your Redmine instance:

```bash
export REDMINE_URL="https://your-redmine-instance.com"
export REDMINE_API_KEY="your-api-key"
export TEST_PROJECT="p1"
export SERVER_MODE="test"

python test_suite.py
```

### Docker Test Mode

Run the container in test mode:

```bash
docker run -e REDMINE_URL="https://your-redmine-instance.com" \
           -e REDMINE_API_KEY="your-api-key" \
           -e SERVER_MODE="test" \
           -e TEST_PROJECT="p1" \
           redmine-mcp-server
```

## Project Structure

- `main.py`: Entry point for the server
- `src/`: Core server components
  - `mcp_server.py`: FastMCP server implementation using instance methods
  - `redmine_client.py`: Unified Redmine API client
  - `base.py`: Base client with error handling and connection management
- `tests/`: Test suite for validation
  - `test-implementation.py`: Validation script for server implementation
- `test_suite.py`: Automated test suite
- `test_roadmap.py`: Roadmap functionality tests
- `mcp_client_demo.py`: Demo of the MCP client
- `.github/workflows/`: GitHub Actions for CI/CD

## Roadmap Feature

The roadmap functionality allows you to:

1. Create versions (sprints, milestones, releases)
2. Tag issues with versions
3. Get issues by version
4. Build a complete product roadmap

Example roadmap creation:

```python
from modules.redmine_client import RedmineClient

# Initialize client
client = RedmineClient(redmine_url, redmine_api_key)

# Create a version roadmap
client.roadmap.create_roadmap_version(
    project_id=1,
    name="Sprint 2023-06",
    description="June sprint with key features",
    status="open",
    due_date="2023-06-30"
)

# Tag an issue with the version
client.roadmap.tag_issue_with_version(issue_id=123, version_id=456)

# Get all issues for a version
issues = client.roadmap.get_issues_by_version(version_id=456)
```

## CI/CD with GitHub Actions

This project includes GitHub Actions workflows for:

1. Automated building
2. Running tests
3. Integration testing
4. Docker image publishing

## License

MIT

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.