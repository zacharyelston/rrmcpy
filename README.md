# Redmine MCP Server

A robust FastMCP server for Redmine API integration. This server uses standard input/output (STDIO) for communication rather than exposing network ports, making it ideal for secure integrations.

## Features

- Comprehensive Redmine API support (issues, projects, versions, users, groups)
- STDIO-based communication protocol (no network ports exposed)
- Test mode for automated validation
- Detailed logging and error reporting

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Redmine API key with appropriate permissions

### Running the Server

1. Set your Redmine API key as an environment variable:

```bash
export REDMINE_API_KEY=your-api-key-here
```

2. Run the server using the provided shell script:

```bash
./run_server.sh
```

### Using Docker

1. Build the Docker image:

```bash
docker build -t redmine-mcp-server .
```

2. Run the server with Docker:

```bash
docker run -e REDMINE_API_KEY=your-api-key-here redmine-mcp-server
```

### Environment Variables

- `REDMINE_URL`: URL of your Redmine instance (default: https://redstone.redminecloud.net)
- `SERVER_MODE`: Server mode, either "live" or "test" (default: live)
- `LOG_LEVEL`: Logging level (default: info)
- `TEST_PROJECT`: Project identifier for tests (default: p1)
- `REDMINE_API_KEY_FILE`: Path to a file containing your API key (for Docker Compose)

## Usage

The MCP server communicates using JSON messages over STDIO. Send requests to the server's standard input and read responses from its standard output.

### Example Request

```json
{
  "method": "GET",
  "path": "/issues",
  "data": {
    "params": {
      "project_id": 1,
      "status_id": "open"
    }
  }
}
```

### Example Response

```json
{
  "status": 200,
  "data": {
    "issues": [
      {
        "id": 123,
        "subject": "Sample issue",
        "description": "This is a sample issue",
        "status": {
          "id": 1,
          "name": "New"
        }
      }
    ],
    "total_count": 1,
    "offset": 0,
    "limit": 25
  }
}
```

## Supported Endpoints

### Issues

- `GET /issues`: List issues with optional filtering
- `GET /issues/{id}`: Get a specific issue
- `POST /issues`: Create a new issue
- `PUT /issues/{id}`: Update an existing issue
- `DELETE /issues/{id}`: Delete an issue

### Projects

- `GET /projects`: List projects with optional filtering
- `GET /projects/{id}`: Get a specific project
- `POST /projects`: Create a new project
- `PUT /projects/{id}`: Update an existing project
- `DELETE /projects/{id}`: Delete a project

### Versions

- `GET /projects/{id}/versions`: List versions for a project
- `GET /versions/{id}`: Get a specific version
- `POST /versions`: Create a new version
- `PUT /versions/{id}`: Update an existing version
- `DELETE /versions/{id}`: Delete a version

### Users

- `GET /users`: List users with optional filtering
- `GET /users/{id}`: Get a specific user
- `GET /users/current`: Get current user (based on API key)
- `POST /users`: Create a new user
- `PUT /users/{id}`: Update an existing user
- `DELETE /users/{id}`: Delete a user

### Groups

- `GET /groups`: List groups with optional filtering
- `GET /groups/{id}`: Get a specific group
- `POST /groups`: Create a new group
- `PUT /groups/{id}`: Update an existing group
- `DELETE /groups/{id}`: Delete a group
- `POST /groups/{id}/users`: Add a user to a group
- `DELETE /groups/{id}/users/{user_id}`: Remove a user from a group

## Testing

Run the automated tests to verify the server functionality:

```bash
docker-compose run --rm -e SERVER_MODE=test mcp-server
```

## Development

To run the server locally without Docker:

1. Install the required Python packages:

```bash
pip install -r docker-requirements.txt
```

2. Set the environment variables:

```bash
export REDMINE_API_KEY=your-api-key-here
export REDMINE_URL=https://redstone.redminecloud.net
export SERVER_MODE=live
export LOG_LEVEL=debug
```

3. Run the server:

```bash
python main.py
```

4. To run tests:

```bash
python test_essential.py
```