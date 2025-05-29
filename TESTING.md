# Local Docker Testing Guide

This guide explains how to test the Redmine MCP Server locally using Docker.

## Setup

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Configure your environment:**
   Edit `.env` with your Redmine credentials:
   ```bash
   REDMINE_URL=https://your-redmine-instance.com
   REDMINE_API_KEY=your_actual_api_key
   LOG_LEVEL=debug
   SERVER_MODE=live
   ```

3. **Get your Redmine API key:**
   - Log into your Redmine instance
   - Go to "My account" → "API access key"
   - Copy the key to your `.env` file

## Running Tests

Execute the testing script:
```bash
./test-docker.sh
```

## Test Options

The script provides several testing modes:

### 1. Unit Tests
Runs the complete test suite inside the Docker container:
- FastMCP implementation tests
- Error handling validation
- Logging system verification

### 2. Health Check
Performs a quick connectivity test:
- Verifies Redmine connection
- Tests authentication
- Lists accessible projects

### 3. Test Mode Server
Runs the server in test mode:
- Validates configuration
- Tests core functionality
- Runs with your authentic Redmine data

### 4. Interactive Shell
Opens a shell inside the container for manual testing:
- Direct access to the server environment
- Run custom commands
- Debug issues interactively

## Example Output

Successful health check:
```
Health check: PASS
Current user: John Doe
Projects accessible: 5
Docker container test: SUCCESS
```

## Troubleshooting

**Permission denied:**
```bash
chmod +x test-docker.sh
```

**API key issues:**
- Verify the key in your Redmine account settings
- Ensure the user has API access enabled
- Check the Redmine URL is correct

**Connection problems:**
- Verify network connectivity to your Redmine instance
- Check if Redmine requires VPN access
- Confirm the URL format (include https://)

## Security Notes

- Never commit `.env` files to version control
- Keep API keys secure and rotate them regularly
- Use read-only API keys when possible for testing