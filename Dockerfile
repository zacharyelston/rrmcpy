FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install dependencies
COPY docker-requirements.txt .
RUN pip install --no-cache-dir -r docker-requirements.txt

# Create directory structure
RUN mkdir -p /app/src /app/tests

# Copy application code
COPY src/ /app/src/

# Copy tests
COPY tests/ /app/tests/

# Make script executable
RUN chmod +x /app/run_mcp_server.py

# This is a FastMCP server that communicates via STDIO
# No port exposure needed

# Set environment variables - these are the defaults but can be overridden
ENV REDMINE_URL="https://redstone.redminecloud.net" \
    REDMINE_API_KEY="" \
    SERVER_MODE="live" \
    LOG_LEVEL="debug" \
    TEST_PROJECT="p1"

# Create entrypoint script to handle both test and live modes
RUN echo '#!/bin/bash \n\
if [ "$SERVER_MODE" = "test" ]; then \n\
  echo "Running in TEST mode with project $TEST_PROJECT" \n\
  python tests/test_suite.py \n\
else \n\
  echo "Running in LIVE mode" \n\
  python run_mcp_server.py \n\
fi' > /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh

# Run the application
ENTRYPOINT ["/app/docker-entrypoint.sh"]
