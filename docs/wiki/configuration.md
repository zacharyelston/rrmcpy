# Configuration Guide

Complete reference for configuring the Redmine MCP Server for different environments and use cases.

## Environment Variables

### Required Configuration

| Variable | Description | Example | Notes |
|----------|-------------|---------|-------|
| `REDMINE_URL` | Full URL to Redmine instance | `https://redmine.company.com` | Must include protocol (https/http) |
| `REDMINE_API_KEY` | Valid API access key | `a1b2c3d4e5f6789...` | Obtain from Redmine user settings |

### Optional Configuration

| Variable | Default | Description | Valid Values |
|----------|---------|-------------|--------------|
| `MCP_LOG_LEVEL` | `INFO` | Logging verbosity | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `MCP_SERVER_MODE` | `live` | Server operation mode | `live`, `debug`, `test` |
| `REDMINE_TIMEOUT` | `30` | Request timeout (seconds) | Any positive integer |
| `REDMINE_MAX_RETRIES` | `3` | Failed request retry count | 0-10 recommended |

## Configuration Methods

### Environment File (.env)
```bash
# .env file
REDMINE_URL=https://your-redmine.com
REDMINE_API_KEY=your-api-key-here
MCP_LOG_LEVEL=INFO
MCP_SERVER_MODE=live
```

Load with:
```bash
source .env
python fastmcp_server.py
```

### Shell Export
```bash
export REDMINE_URL="https://your-redmine.com"
export REDMINE_API_KEY="your-api-key-here"
python fastmcp_server.py
```

### Programmatic Configuration
```python
import os
os.environ['REDMINE_URL'] = 'https://your-redmine.com'
os.environ['REDMINE_API_KEY'] = 'your-api-key'

from mcp_config_example import main
asyncio.run(main())
```

## Server Modes

### Live Mode (Production)
```bash
export MCP_SERVER_MODE="live"
```
- Full functionality enabled
- Startup health checks required
- All API operations available
- Recommended for production use

### Debug Mode (Development)
```bash
export MCP_SERVER_MODE="debug"
export MCP_LOG_LEVEL="DEBUG"
```
- Verbose logging enabled
- Additional error information
- Performance metrics logged
- Request/response details shown

### Test Mode (Validation)
```bash
export MCP_SERVER_MODE="test"
```
- Runs validation tests only
- No persistent server operation
- Configuration and connectivity verification
- Returns test results and exits

## Redmine API Configuration

### API Key Permissions
Required permissions for full functionality:
- View issues
- Add issues
- Edit issues
- Delete issues (if using delete operations)
- View projects
- View users

### API Key Security
```bash
# Restrict permissions to minimum required
# Use project-specific API keys when possible
# Rotate keys regularly
# Monitor API usage in Redmine logs
```

### Connection Settings
```bash
# For slow networks
export REDMINE_TIMEOUT="60"

# For unreliable connections
export REDMINE_MAX_RETRIES="5"

# For high-latency environments
export REDMINE_TIMEOUT="120"
export REDMINE_MAX_RETRIES="3"
```

## Logging Configuration

### Log Levels

#### DEBUG
```bash
export MCP_LOG_LEVEL="DEBUG"
```
- All HTTP requests and responses
- Internal state changes
- Performance timing
- Error stack traces

#### INFO (Default)
```bash
export MCP_LOG_LEVEL="INFO"
```
- Server startup/shutdown
- Tool execution summary
- Connection status changes
- Important operational events

#### WARNING
```bash
export MCP_LOG_LEVEL="WARNING"
```
- Configuration issues
- Retry attempts
- Deprecated feature usage
- Performance concerns

#### ERROR
```bash
export MCP_LOG_LEVEL="ERROR"
```
- Failed operations only
- Critical errors
- Authentication failures
- System errors

### Log Output
```python
# Customize logging in code
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp_server.log')
    ]
)
```

## Docker Configuration

### Dockerfile Environment
```dockerfile
ENV REDMINE_URL=https://your-redmine.com
ENV REDMINE_API_KEY=your-api-key
ENV MCP_LOG_LEVEL=INFO
```

### Docker Compose
```yaml
version: '3.8'
services:
  redmine-mcp:
    build: .
    environment:
      - REDMINE_URL=https://your-redmine.com
      - REDMINE_API_KEY=your-api-key
      - MCP_LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
```

### Runtime Configuration
```bash
docker run -e REDMINE_URL="https://your-redmine.com" \
           -e REDMINE_API_KEY="your-key" \
           -e MCP_LOG_LEVEL="DEBUG" \
           redmine-mcp-server
```

## MCP Client Configuration

### Claude Desktop Config
```json
{
  "mcpServers": {
    "redmine": {
      "command": "python",
      "args": ["/path/to/fastmcp_server.py"],
      "env": {
        "REDMINE_URL": "https://your-redmine.com",
        "REDMINE_API_KEY": "your-api-key",
        "MCP_LOG_LEVEL": "WARNING"
      }
    }
  }
}
```

### Custom Client Configuration
```python
import subprocess
import json

# Configure environment for MCP server
env = {
    "REDMINE_URL": "https://your-redmine.com",
    "REDMINE_API_KEY": "your-api-key",
    "MCP_LOG_LEVEL": "INFO"
}

# Start MCP server process
process = subprocess.Popen(
    ["python", "fastmcp_server.py"],
    env=env,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE
)
```

## Validation and Testing

### Configuration Validation
```python
from mcp_config_example import validate_configuration
if validate_configuration():
    print("Configuration valid")
else:
    print("Check environment variables")
```

### Connection Testing
```python
from src.issues import IssueClient
import os

client = IssueClient(
    os.getenv('REDMINE_URL'),
    os.getenv('REDMINE_API_KEY')
)

if client.health_check():
    print("Redmine connection successful")
else:
    print("Connection failed - check configuration")
```

### Full System Test
```bash
export REDMINE_URL="https://your-redmine.com"
export REDMINE_API_KEY="your-key"
export MCP_SERVER_MODE="test"
python fastmcp_server.py
```

## Performance Tuning

### Network Optimization
```bash
# Increase timeout for slow networks
export REDMINE_TIMEOUT="90"

# Reduce retries for fast-fail behavior
export REDMINE_MAX_RETRIES="1"

# Optimize for high-latency connections
export REDMINE_TIMEOUT="180"
export REDMINE_MAX_RETRIES="2"
```

### Logging Optimization
```bash
# Reduce log volume in production
export MCP_LOG_LEVEL="WARNING"

# Disable debug logging
export MCP_LOG_LEVEL="INFO"
```

## Security Best Practices

### API Key Management
- Store in secure key management systems
- Use environment-specific keys
- Implement key rotation procedures
- Monitor API usage patterns

### Network Security
- Use HTTPS for all Redmine connections
- Implement network access controls
- Monitor connection attempts
- Use VPN for sensitive environments

### Access Control
- Limit API key permissions
- Use project-specific access when possible
- Implement role-based restrictions
- Regular access audits