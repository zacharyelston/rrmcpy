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

# Get current git branch for container labeling
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
CURRENT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

echo -e "${GREEN}Redmine MCP Server - Local Docker Testing${NC}"
echo "=========================================="
echo "Branch: $CURRENT_BRANCH"
echo "Commit: $CURRENT_COMMIT"
echo ""

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

# Create branch-specific image tag
BRANCH_TAG=$(echo "$CURRENT_BRANCH" | sed 's/[^a-zA-Z0-9._-]/-/g')
IMAGE_NAME="redmine-mcp-server:$BRANCH_TAG"
IMAGE_NAME_WITH_COMMIT="redmine-mcp-server:$BRANCH_TAG-$CURRENT_COMMIT"

# Build Docker image with branch-specific tags
echo -e "${YELLOW}Building Docker image with branch labeling...${NC}"
echo "Image tags: $IMAGE_NAME, $IMAGE_NAME_WITH_COMMIT"
docker build \
    -t "$IMAGE_NAME" \
    -t "$IMAGE_NAME_WITH_COMMIT" \
    -t "redmine-mcp-server:latest" \
    --label "branch=$CURRENT_BRANCH" \
    --label "commit=$CURRENT_COMMIT" \
    --label "build-date=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    . || {
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
        --name "rmcp-test-$BRANCH_TAG-$(date +%s)" \
        --entrypoint="" \
        "$IMAGE_NAME" \
        python -m pytest tests/test_mcp_server.py tests/test_error_handling.py tests/test_logging.py -v
}

# Function to run health check
run_health_check() {
    echo -e "${YELLOW}Running health check...${NC}"
    docker run --rm \
        -e REDMINE_URL="$REDMINE_URL" \
        -e REDMINE_API_KEY="$REDMINE_API_KEY" \
        -e LOG_LEVEL="$LOG_LEVEL" \
        --name "rmcp-health-$BRANCH_TAG-$(date +%s)" \
        --entrypoint="" \
        redmine-mcp-server:local \
        python -c "
import sys, os
sys.path.insert(0, '/app/src')
from mcp_server import RedmineMCPServer
from core.config import Config

config = Config()
try:
    server = RedmineMCPServer(config)
    print('✓ MCP Server initialized successfully')
    print('✓ Health check: PASS')
    exit(0)
except Exception as e:
    print(f'✗ Health check: FAIL - {e}')
    exit(1)
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
        --name "rmcp-interactive-$BRANCH_TAG-$(date +%s)" \
        --entrypoint="/bin/bash" \
        "$IMAGE_NAME"
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
        --name "rmcp-server-$BRANCH_TAG-$(date +%s)" \
        "$IMAGE_NAME"
}

# Function to list branch versions
list_branch_versions() {
    echo -e "${YELLOW}Available Redmine MCP Server images:${NC}"
    echo ""
    docker images redmine-mcp-server --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}\t{{.Size}}" | head -20
    echo ""
    echo "Image labels (showing branch and commit info):"
    docker images redmine-mcp-server -q | head -10 | while read image_id; do
        branch=$(docker inspect "$image_id" --format '{{index .Config.Labels "branch"}}' 2>/dev/null || echo "unknown")
        commit=$(docker inspect "$image_id" --format '{{index .Config.Labels "commit"}}' 2>/dev/null || echo "unknown")
        build_date=$(docker inspect "$image_id" --format '{{index .Config.Labels "build-date"}}' 2>/dev/null || echo "unknown")
        tag=$(docker inspect "$image_id" --format '{{index .RepoTags 0}}' 2>/dev/null || echo "unknown")
        echo "  $tag -> Branch: $branch, Commit: $commit, Built: $build_date"
    done
    echo ""
}

# Main menu
while true; do
    echo ""
    echo "Select test option:"
    echo "1) Run unit tests"
    echo "2) Run health check"
    echo "3) Run server in test mode"
    echo "4) Interactive container shell"
    echo "5) List branch versions"
    echo "6) Exit"
    echo ""
    
    read -p "Enter your choice (1-6): " choice
    
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
            list_branch_versions
            ;;
        6)
            echo -e "${GREEN}Exiting...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option. Please select 1-6.${NC}"
            ;;
    esac
done