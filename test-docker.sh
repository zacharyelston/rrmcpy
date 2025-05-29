#!/bin/bash

# Local Docker Testing Script for Redmine MCP Server
# Reads configuration from .env file for easy testing

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}Redmine MCP Server - Local Docker Testing${NC}"
echo "=========================================="

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please create a .env file with the following variables:"
    echo ""
    echo "REDMINE_URL=https://your-redmine-instance.com"
    echo "REDMINE_API_KEY=your_api_key_here"
    echo "LOG_LEVEL=debug"
    echo "SERVER_MODE=live"
    echo ""
    exit 1
fi

# Load environment variables from .env file
echo -e "${YELLOW}Loading configuration from .env file...${NC}"
export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)

# Validate required environment variables
if [ -z "$REDMINE_URL" ]; then
    echo -e "${RED}Error: REDMINE_URL not set in .env file${NC}"
    exit 1
fi

if [ -z "$REDMINE_API_KEY" ]; then
    echo -e "${RED}Error: REDMINE_API_KEY not set in .env file${NC}"
    exit 1
fi

# Set default values
LOG_LEVEL=${LOG_LEVEL:-info}
SERVER_MODE=${SERVER_MODE:-live}

echo "Configuration:"
echo "  Redmine URL: $REDMINE_URL"
echo "  Log Level: $LOG_LEVEL"
echo "  Server Mode: $SERVER_MODE"
echo ""

# Build Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t redmine-mcp-server:local . || {
    echo -e "${RED}Failed to build Docker image${NC}"
    exit 1
}

echo -e "${GREEN}Docker image built successfully${NC}"
echo ""

# Function to run tests
run_tests() {
    echo -e "${YELLOW}Running unit tests...${NC}"
    docker run --rm \
        -e REDMINE_URL="$REDMINE_URL" \
        -e REDMINE_API_KEY="$REDMINE_API_KEY" \
        -e LOG_LEVEL="$LOG_LEVEL" \
        --entrypoint="" \
        redmine-mcp-server:local \
        python -m pytest tests/test_proper_mcp.py tests/test_error_handling.py tests/test_logging.py -v
}

# Function to run health check
run_health_check() {
    echo -e "${YELLOW}Running health check...${NC}"
    docker run --rm \
        -e REDMINE_URL="$REDMINE_URL" \
        -e REDMINE_API_KEY="$REDMINE_API_KEY" \
        -e LOG_LEVEL="$LOG_LEVEL" \
        --entrypoint="" \
        redmine-mcp-server:local \
        python -c "
import os
import sys
sys.path.append('.')
from src.proper_mcp_server import RedmineMCPServer

# Test server initialization and health
try:
    server = RedmineMCPServer(os.environ['REDMINE_URL'], os.environ['REDMINE_API_KEY'])
    health = server.redmine_client.health_check()
    print(f'Health check: {\"PASS\" if health else \"FAIL\"}')
    
    # Test basic operations
    user_result = server.redmine_client.get_current_user()
    if not user_result.get('error'):
        user = user_result.get('user', {})
        print(f'Current user: {user.get(\"firstname\", \"\")} {user.get(\"lastname\", \"\")}')
    
    projects_result = server.redmine_client.get_projects()
    if not projects_result.get('error'):
        projects = projects_result.get('projects', [])
        print(f'Projects accessible: {len(projects)}')
    
    print('Docker container test: SUCCESS')
except Exception as e:
    print(f'Docker container test: FAILED - {e}')
    sys.exit(1)
"
}

# Function to run interactive container
run_interactive() {
    echo -e "${YELLOW}Starting interactive container...${NC}"
    echo "You can now test MCP operations directly"
    echo "Press Ctrl+C to exit"
    echo ""
    
    docker run -it --rm \
        -e REDMINE_URL="$REDMINE_URL" \
        -e REDMINE_API_KEY="$REDMINE_API_KEY" \
        -e LOG_LEVEL="$LOG_LEVEL" \
        -e SERVER_MODE="$SERVER_MODE" \
        --entrypoint="/bin/bash" \
        redmine-mcp-server:local
}

# Function to run server in test mode
run_server_test_mode() {
    echo -e "${YELLOW}Running server in test mode...${NC}"
    echo "This will run the FastMCP server with test validation"
    echo ""
    
    docker run --rm \
        -e REDMINE_URL="$REDMINE_URL" \
        -e REDMINE_API_KEY="$REDMINE_API_KEY" \
        -e LOG_LEVEL="$LOG_LEVEL" \
        -e SERVER_MODE="test" \
        redmine-mcp-server:local
}

# Main menu
while true; do
    echo ""
    echo "Select test option:"
    echo "1) Run unit tests"
    echo "2) Run health check"
    echo "3) Run server in test mode"
    echo "4) Interactive container shell"
    echo "5) Exit"
    echo ""
    
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            run_tests
            ;;
        2)
            run_health_check
            ;;
        3)
            run_server_test_mode
            ;;
        4)
            run_interactive
            ;;
        5)
            echo -e "${GREEN}Exiting...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option. Please select 1-5.${NC}"
            ;;
    esac
done