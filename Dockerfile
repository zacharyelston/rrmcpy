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
ENV REDMINE_URL="https://redstone.redminecloud.net" \
    REDMINE_API_KEY="" \
    SERVER_MODE="live" \
    LOG_LEVEL="debug" \
    TEST_PROJECT="p1" \
    PYTHONPATH="/app"

# Create entrypoint script to handle both test and live modes
RUN echo '#!/bin/bash \n\
if [ "$SERVER_MODE" = "test" ]; then \n\
  echo "Running in TEST mode with project $TEST_PROJECT" \n\
  python -m tests.test_redstone \n\
else \n\
  echo "Running in LIVE mode" \n\
  python -m src.main \n\
fi' > /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh

# Run the application
ENTRYPOINT ["/app/docker-entrypoint.sh"]
