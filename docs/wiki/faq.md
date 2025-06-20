# Frequently Asked Questions

## General Questions

### What is the Redmine MCP Server?
The Redmine MCP Server is a Model Context Protocol (MCP) server that provides programmatic access to Redmine project management systems. It exposes Redmine functionality as standardized MCP tools that can be used by AI assistants like Claude or custom applications.

### What MCP clients are supported?
The server works with any MCP-compliant client including:
- Claude Desktop
- Custom MCP clients
- Development environments (Jupyter, VS Code)
- Command-line MCP tools

### Which Redmine versions are supported?
The server supports Redmine 4.0+ with REST API enabled. It has been tested with:
- Redmine 4.2.x
- Redmine 5.0.x
- Redmine 5.1.x

## Installation and Setup

### How do I get a Redmine API key?
1. Log into your Redmine instance
2. Navigate to "My account" → "API access key"
3. Click "Show" to reveal your API key
4. Copy the key for configuration

### Can I use multiple Redmine instances?
Currently, each server instance connects to one Redmine instance. For multiple instances, run separate MCP server processes with different configurations.

### Do I need administrator access to Redmine?
No, regular user access is sufficient. The API key permissions determine available operations. However, some operations (like user management) may require elevated permissions.

## Configuration Issues

### Why am I getting "Invalid API key" errors?
- Verify the API key is correctly copied without extra spaces
- Check that the API key belongs to an active user account
- Ensure the user has appropriate permissions for the operations
- Confirm the Redmine instance has REST API enabled

### How do I fix "Connection refused" errors?
- Verify the REDMINE_URL is accessible from your network
- Check if the Redmine server is running
- Ensure firewall settings allow outbound connections
- Try accessing the URL in a web browser

### What if my Redmine uses self-signed certificates?
Set up proper SSL verification or configure your environment to handle self-signed certificates. The server enforces HTTPS for security.

## Tool Usage

### Why do some tools return empty responses?
This was a known issue in earlier versions that has been resolved. Ensure you're using the latest version where create operations return complete JSON data.

### How do I handle large numbers of issues?
Use pagination parameters:
- `limit`: Control number of results per request
- `offset`: Skip to specific starting position
- Process in batches to avoid overwhelming the server

### Can I create custom fields in issues?
The current implementation supports standard Redmine fields. Custom field support depends on your Redmine configuration and may require API client extensions.

## Development and Integration

### How do I add new tools?
1. Create a new `@mcp.tool()` decorated function in `fastmcp_server.py`
2. Implement parameter validation and error handling
3. Add corresponding API client methods if needed
4. Follow existing patterns for consistency

### Can I modify the server for my organization?
Yes, the server is designed for customization. Key extension points:
- Additional tool functions
- Custom authentication methods
- Enhanced error handling
- Organization-specific workflows

### How do I test my changes?
The server includes comprehensive testing:
- Unit tests for individual components
- Integration tests with authentic Redmine data
- Health check validation
- Example scripts for manual testing

## Performance and Scaling

### What are typical response times?
- Simple operations (get issue): 100-300ms
- Create operations: 200-500ms
- List operations: 300-1000ms (depends on result size)
- Bulk operations: Linear scaling with item count

### How many concurrent requests can it handle?
The server is designed for typical MCP usage patterns (single-user, sequential operations). For high-concurrency scenarios, consider:
- Multiple server instances
- Connection pooling
- Rate limiting
- Caching strategies

### Can I use it in production?
Yes, the server is production-ready with:
- Comprehensive error handling
- Authentication security
- Logging and monitoring
- Container deployment support

## Troubleshooting

### The server won't start
1. Check Python version (3.8+ required)
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Ensure environment variables are set correctly
4. Check for port conflicts or permission issues

### Tools are not working correctly
1. Run health check: `redmine-health-check`
2. Verify API key permissions in Redmine
3. Check server logs for detailed error messages
4. Test with simple operations first

### Container or development environment issues
The server includes special handling for container environments:
- Install `nest_asyncio` for Jupyter/VS Code compatibility
- Use the container-compatible entry points
- Check event loop conflict resolution

## Security Concerns

### How secure is the API key transmission?
- API keys are sent in HTTP headers over HTTPS
- Keys are never logged in plaintext
- Environment variable storage is recommended
- Regular key rotation is advised

### What data is logged?
- Operational events (startup, tool execution)
- Error conditions and debugging information
- Request metadata (not content)
- No sensitive data like API keys or issue content

### Can I restrict tool access?
Tool access is controlled by Redmine permissions associated with the API key. Use role-based access control in Redmine to limit operations.

## Migration and Upgrades

### How do I upgrade from the complex server implementation?
The simple FastMCP implementation provides identical functionality:
1. Replace complex `src/mcp_server.py` with `fastmcp_server.py`
2. Update MCP client configuration
3. Test all tools work correctly
4. Remove unused complex architecture files

### Will my existing MCP client configuration work?
Yes, tool names and functionality remain identical. Only the server implementation has been simplified.

## Getting Help

### Where can I find more documentation?
- [Tool Reference](tools/README.md) - Complete tool documentation
- [Architecture Guide](architecture/README.md) - System design details
- [Examples](examples/README.md) - Working code samples
- [Configuration Guide](configuration.md) - Setup and tuning

### How do I report issues?
1. Check this FAQ and troubleshooting guides
2. Verify your configuration and permissions
3. Collect relevant error messages and logs
4. Open an issue on the project repository with detailed information

### Can I contribute to the project?
Yes, contributions are welcome:
- Follow existing code patterns and style
- Include tests for new functionality
- Update documentation for changes
- Submit pull requests with clear descriptions