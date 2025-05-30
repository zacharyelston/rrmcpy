FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Copy requirements and install dependencies
COPY docker-requirements.txt .
RUN pip install --no-cache-dir -r docker-requirements.txt

# Create directory structure
RUN mkdir -p /app/src /app/tests

# Copy application code
COPY src/ /app/src/
COPY run_server.sh /app/

# Copy tests
COPY tests/ /app/tests/

# This is a FastMCP server that communicates via STDIO
# No port exposure needed

# Set environment variables - these are the defaults but can be overridden
# Note: REDMINE_API_KEY should be provided at runtime for security
ENV REDMINE_URL="https://redstone.redminecloud.net" \
    SERVER_MODE="live" \
    LOG_LEVEL="debug" \
    TEST_PROJECT="p1" \
    PYTHONPATH="/app"

# Simple entrypoint to run the MCPServer
CMD ["python", "-m", "src.main"]
