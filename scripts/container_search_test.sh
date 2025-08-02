#!/bin/bash
# container_search_test.sh - Run MCP search test non-interactively in a container
# Usage: ./scripts/container_search_test.sh [query]
#
# This script runs a search test in a non-interactive Docker container
# using the MCP client to interact with the Redmine MCP server.
# It sets SERVER_MODE=live to ensure real API calls are made.

set -e

# Default search query if none provided
SEARCH_QUERY=${1:-"zealot"}

# Script directory (for relative paths)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment variables from .env file if it exists
if [ -f "$REPO_ROOT/.env" ]; then
    echo "Loading environment variables from .env file"
    # Extract environment variables from .env file
    REDMINE_URL="$(grep REDMINE_URL "$REPO_ROOT/.env" | cut -d= -f2)"
    REDMINE_API_KEY="$(grep REDMINE_API_KEY "$REPO_ROOT/.env" | cut -d= -f2)"
    LOG_LEVEL="$(grep LOG_LEVEL "$REPO_ROOT/.env" | cut -d= -f2 || echo 'debug')"
else
    echo "No .env file found in repository root. Using environment variables from shell."
fi

echo "Running MCP search test in container with query: $SEARCH_QUERY"

# Get git commit hash for environment variable
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Use the specific Docker image that we know works
DOCKER_IMAGE="redmine-mcp-server:feature-766-enhance-search-functionality"

# Create a temporary Python script for running the search
cat > "$REPO_ROOT/scripts/temp_search.py" << EOF
#!/usr/bin/env python3
from scripts.mcp_client import send_mcp_request
import json

# Execute the search with the given query
result = send_mcp_request('redmine-search', {'query': "$SEARCH_QUERY"})
print(json.dumps(result, indent=2))
EOF

chmod +x "$REPO_ROOT/scripts/temp_search.py"

# Run the test in a non-interactive container
docker run --rm \
  -v "$REPO_ROOT:/app" \
  -e REDMINE_URL="${REDMINE_URL}" \
  -e REDMINE_API_KEY="${REDMINE_API_KEY}" \
  -e LOG_LEVEL="${LOG_LEVEL:-debug}" \
  -e SERVER_MODE="live" \
  -e GIT_COMMIT="${GIT_COMMIT}" \
  --name "rmcp-search-test-$(date +%s)" \
  "${DOCKER_IMAGE}" \
  python /app/scripts/temp_search.py

# Clean up the temporary script
rm "$REPO_ROOT/scripts/temp_search.py"

# Exit with the status of the last command
exit $?
