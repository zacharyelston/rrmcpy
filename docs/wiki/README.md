# Redmine MCP Server Wiki

Welcome to the comprehensive documentation for the Redmine MCP Server project. This wiki provides detailed information for both users and developers.

## Quick Navigation

### For Users
- [Installation Guide](installation.md) - Get started with setup and configuration
- [Tool Reference](tools/README.md) - Complete MCP tool documentation
- [Configuration Guide](configuration.md) - Environment variables and settings
- [Examples](examples/README.md) - Working examples and tutorials

### For Developers
- [Architecture Overview](architecture/README.md) - System design and patterns
- [API Documentation](api/README.md) - Internal APIs and schemas
- [Development Guide](development/README.md) - Contributing and testing
- [Extension Guide](extensions/README.md) - Adding new features

### Resources
- [FAQ](faq.md) - Common questions and troubleshooting
- [Changelog](../CHANGELOG.md) - Version history and updates
- [Roadmap](../ROADMAP.md) - Future development plans

## Project Status

**Current Version**: Production Ready  
**MCP Compatibility**: Full FastMCP compliance  
**Redmine Support**: All major versions  
**Test Coverage**: Comprehensive with authentic data validation

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
export REDMINE_URL="https://your-redmine.com"
export REDMINE_API_KEY="your-api-key"

# Run server
python fastmcp_server.py
```

## Available Tools

- `redmine-create-issue` - Create new issues
- `redmine-get-issue` - Get issue details  
- `redmine-list-issues` - List and filter issues
- `redmine-update-issue` - Update existing issues
- `redmine-delete-issue` - Delete issues
- `redmine-health-check` - Check connectivity
- `redmine-get-current-user` - Get user information

## Support

For questions or issues:
1. Check the [FAQ](faq.md)
2. Review [troubleshooting guides](troubleshooting.md)
3. Open an issue on GitHub
4. Consult the [API documentation](api/README.md)

---

*This documentation is automatically updated with each release.*