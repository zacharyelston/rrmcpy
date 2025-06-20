# Tool: redmine-health-check

**Description**: Verifies connectivity and authentication with the Redmine server to ensure the MCP server is properly configured.

## Parameters

None - this tool requires no input parameters.

## Returns

JSON string containing health status information and connection details.

## Example Usage

### Basic Health Check
```python
result = await mcp.call_tool("redmine-health-check")
```

## Response Example

### Healthy Connection
```json
{
  "healthy": true,
  "status": "Connected"
}
```

### Connection Failure
```json
{
  "healthy": false,
  "status": "Disconnected"
}
```

## Error Scenarios

- **Invalid URL**: "Health check failed: Invalid Redmine URL format"
- **Network unreachable**: "Health check failed: Connection timeout"
- **Authentication failed**: "Health check failed: Invalid API key"
- **Server error**: "Health check failed: Redmine server returned error 500"

## Use Cases

### Server Startup Validation
Verify configuration before processing requests:
```python
health = await mcp.call_tool("redmine-health-check")
if "healthy": true in health:
    print("Server ready for operations")
else:
    print("Configuration issue detected")
```

### Monitoring Integration
Regular health checks for system monitoring:
```python
# Check every 5 minutes
import asyncio

async def monitor_health():
    while True:
        result = await mcp.call_tool("redmine-health-check")
        log_health_status(result)
        await asyncio.sleep(300)
```

### Troubleshooting
Diagnose connection issues:
```python
result = await mcp.call_tool("redmine-health-check")
if "Disconnected" in result:
    # Check environment variables
    # Verify network connectivity
    # Validate API key permissions
```

## Configuration Dependencies

This tool validates:
- `REDMINE_URL` environment variable
- `REDMINE_API_KEY` environment variable
- Network connectivity to Redmine server
- API key authentication and permissions

## Notes

- Health check performs minimal API request to verify connectivity
- Does not modify any data in Redmine
- Results indicate overall system readiness
- Use for automated monitoring and startup validation