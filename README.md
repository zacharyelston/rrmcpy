# Redmine MCP Server

![Tests Passing](https://img.shields.io/badge/tests-passing-brightgreen)

A Model Context Protocol (MCP) server that enables AI assistants to interact with Redmine project management.

## Quick Start

```bash
# Set environment variables
export REDMINE_URL="https://your-redmine-instance.com"
export REDMINE_API_KEY="your-api-key-here"

# Install dependencies
pip install -e /path/to/fastmcp
pip install -r requirements.txt

# Run server
python -m src.server
```

**Note:** Requires Python 3.10+ due to fastmcp dependency.

## Features

- Modular architecture with clear separation of concerns
- 17+ MCP tools for Redmine interaction
- Compatible with any MCP client framework
- Comprehensive test suite and CI pipeline
- Follows "Keep It Simple" design principles

## Documentation

The documentation is organized into chapters for easier navigation:

1. [Overview](./readme/01-overview.md) - Project overview and requirements
2. [Installation](./readme/02-installation.md) - Setup instructions for different environments
3. [Configuration](./readme/03-configuration.md) - Environment variables and settings
4. [Tool Inventory](./readme/04-tools.md) - Available and planned MCP tools
5. [Design Philosophy](./readme/05-philosophy.md) - "Keep It Simple" principles
6. [Development Guide](./readme/06-development.md) - For contributors
7. [Troubleshooting](./readme/07-troubleshooting.md) - Common issues and solutions
8. [Security](./readme/08-security.md) - Credential management and security best practices

## Security Notice

This server requires your Redmine API credentials. Always store them securely:

- Use environment variables instead of hardcoding credentials
- For development, store credentials in a `.env` file (add to `.gitignore`)
- For CI/CD pipelines, use repository secrets
- For container deployments, use secure environment injection

See the [Security chapter](./readme/08-security.md) for detailed best practices.