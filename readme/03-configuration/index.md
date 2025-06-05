# Configuration

## Environment Variables

The server uses the following environment variables for configuration:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDMINE_URL` | Yes | `https://demo.redmine.org` | URL of the Redmine instance |
| `REDMINE_API_KEY` | Yes | None | API key for Redmine access |
| `REDMINE_TIMEOUT` | No | `30` | Request timeout in seconds |
| `REDMINE_MAX_RETRIES` | No | `3` | Maximum number of retry attempts |
| `REDMINE_RETRY_DELAY` | No | `1.0` | Delay between retries in seconds |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `SERVER_MODE` | No | `live` | Server mode (live, test) |
| `SERVER_TRANSPORT` | No | `stdio` | MCP transport (stdio, http) |
| `TEST_PROJECT` | No | `p1` | Project ID used for tests |

## Secure Credential Management

For security, prefer environment variables over hardcoded values for your API key:

```bash
# Set environment variables before running the server
export REDMINE_URL="https://your-redmine-instance.com"
export REDMINE_API_KEY="your-api-key-here"

# Run the server
python -m src.server
```

## MCP Server Configuration

For MCP server configuration examples, see [MCP Servers Examples](../docs/mcp-servers-examples.md).
