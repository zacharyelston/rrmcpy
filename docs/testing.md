# Testing Guide

This guide explains how to test the modular Redmine MCP Server locally.

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

### 1. Native Python Testing
Run the modular server directly:
```bash
# Set environment variables
export REDMINE_API_KEY=your-api-key-here
export REDMINE_URL=https://your-redmine-instance.com

# Run the server
python main.py
```

### 2. Docker Testing
Test with containerized environment:
```bash
./test-docker.sh
```

### 3. Modular Component Testing
Test individual components:
- Core infrastructure (config, errors, logging)
- Service layer with business logic
- Tool registry system
- Individual MCP tools

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