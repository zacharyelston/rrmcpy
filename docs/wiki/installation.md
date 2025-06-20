# Installation Guide

This guide covers setting up the Redmine MCP Server in various environments.

## Prerequisites

- Python 3.8 or higher
- Access to a Redmine instance
- Valid Redmine API key
- Network connectivity to Redmine server

## Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd redmine-mcp-server
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
export REDMINE_URL="https://your-redmine-instance.com"
export REDMINE_API_KEY="your-api-key-here"
```

### 3. Run Server
```bash
python fastmcp_server.py
```

## Installation Methods

### Standard Python Installation

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Required Packages
- `fastmcp` - MCP server framework
- `requests` - HTTP client
- `pydantic` - Data validation
- `nest_asyncio` - Container compatibility

#### Optional Packages
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting

### Container Installation

#### Using Docker
```bash
docker build -t redmine-mcp-server .
docker run -e REDMINE_URL="https://your-redmine.com" \
           -e REDMINE_API_KEY="your-key" \
           redmine-mcp-server
```

#### Development Container
For VS Code or similar environments:
```bash
pip install nest_asyncio
python fastmcp_server.py
```

## Configuration

### Environment Variables

#### Required
- `REDMINE_URL` - Full URL to your Redmine instance
- `REDMINE_API_KEY` - Valid API key with appropriate permissions

#### Optional
- `MCP_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `MCP_SERVER_MODE` - Server mode (live, debug, test)
- `REDMINE_TIMEOUT` - Request timeout in seconds (default: 30)

### API Key Setup

#### Obtaining API Key
1. Log into your Redmine instance
2. Go to "My account" → "API access key"
3. Click "Show" to reveal your API key
4. Copy the key for configuration

#### Testing API Key
```python
from src.issues import IssueClient
client = IssueClient("https://your-redmine.com", "your-key")
print("Connected" if client.health_check() else "Failed")
```

## MCP Client Integration

### Claude Desktop
Add to `~/.claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "redmine": {
      "command": "python",
      "args": ["/path/to/fastmcp_server.py"],
      "env": {
        "REDMINE_URL": "https://your-redmine.com",
        "REDMINE_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Custom MCP Client
```python
import asyncio
from mcp_client import MCPClient

async def main():
    client = MCPClient("python", ["/path/to/fastmcp_server.py"])
    await client.connect()
    
    result = await client.call_tool("redmine-health-check")
    print(result)
```

## Verification

### Test Connection
```bash
python -c "
import os
from src.issues import IssueClient
client = IssueClient(os.getenv('REDMINE_URL'), os.getenv('REDMINE_API_KEY'))
print('✓ Connected' if client.health_check() else '✗ Connection failed')
"
```

### Test MCP Tools
```python
result = await mcp.call_tool("redmine-health-check")
# Should return: {"healthy": true, "status": "Connected"}
```

## Troubleshooting

### Common Issues

#### Connection Refused
- Verify REDMINE_URL is accessible
- Check firewall and network settings
- Ensure Redmine server is running

#### Authentication Failed
- Validate API key is correct
- Check API key permissions in Redmine
- Verify user account is active

#### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version compatibility
- Verify virtual environment activation

#### Container Issues
- Install nest_asyncio: `pip install nest_asyncio`
- Use container-compatible entry point: `python container_server.py`

### Debug Mode
```bash
export MCP_LOG_LEVEL="DEBUG"
python fastmcp_server.py
```

### Health Check
```python
import asyncio
from mcp_config_example import validate_configuration

# Test configuration
if validate_configuration():
    print("Configuration valid")
else:
    print("Configuration issues detected")
```

## Performance Optimization

### Connection Settings
```bash
export REDMINE_TIMEOUT="60"
export REDMINE_MAX_RETRIES="3"
```

### Logging Configuration
```bash
export MCP_LOG_LEVEL="WARNING"  # Reduce log verbosity
```

## Security Considerations

- Store API keys securely (environment variables, key management systems)
- Use HTTPS for Redmine connections
- Limit API key permissions to required operations only
- Regularly rotate API keys
- Monitor API usage and access logs