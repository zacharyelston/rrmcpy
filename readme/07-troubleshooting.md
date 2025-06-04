# Troubleshooting

Common issues and their solutions when working with the Redmine MCP Server.

## Environment Issues

### Python Version Errors

**Error**: `ERROR: Package 'fastmcp' requires a different Python: 3.9.x not in '>=3.10'`

**Solution**: Install and use Python 3.10 or later:
```bash
# Check your version
python --version

# Install newer Python version if needed (example using pyenv)
pyenv install 3.10.12
pyenv local 3.10.12
```

### Package Installation Failures

**Error**: `No matching distribution found for fastmcp`

**Solution**: Install from GitHub or local path:
```bash
# From local path
pip install -e /path/to/fastmcp

# From GitHub
pip install -e git+https://github.com/jlowin/fastmcp.git#egg=fastmcp
```

## Configuration Issues

### API Key Authentication Failures

**Error**: `401 Unauthorized` or `API key is invalid or missing`

**Solution**: Check your API key and permissions:
1. Verify `REDMINE_API_KEY` is set correctly
2. Confirm the key has appropriate permissions in Redmine
3. Check for trailing spaces or line breaks in the key

### URL Configuration

**Error**: `Failed to connect to Redmine server at https://example.com`

**Solution**:
1. Ensure `REDMINE_URL` points to the correct Redmine instance
2. Check network connectivity to the server
3. Verify the Redmine instance is online and the API is enabled

## Runtime Issues

### Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'fastmcp'`

**Solution**:
1. Verify fastmcp is installed: `pip list | grep fastmcp`
2. Install fastmcp if missing
3. Check if you're using the correct Python environment

### Transport Issues

**Error**: `RuntimeError: Event loop is already running`

**Solution**: This typically occurs in containerized environments:
1. Use the container compatibility mode
2. Set `SERVER_TRANSPORT=stdio` explicitly
3. Avoid running multiple event loops simultaneously

## Server Issues

### Server Not Starting

**Error**: `Connection refused` or server not responding

**Solution**:
1. Check if another instance is already running
2. Verify your environment variables
3. Look for error messages in logs
4. Try running with debug logging: `LOG_LEVEL=DEBUG`

### Tool Registration Failures

**Error**: `Failed to register MCP tool`

**Solution**:
1. Check for syntax errors in tool implementations
2. Verify that dependencies are properly initialized
3. Run in test mode to validate tool registrations: `python -m src.server --test`

## For More Help

If you encounter persistent issues:

1. Check GitHub issues for similar problems
2. Run with debug logging for more information
3. Submit a detailed bug report with environment information
