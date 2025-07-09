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

RUN mkdir -p /app/logs
VOLUME ["/app/logs"]

# Copy application code
COPY src/ /app/src/

# Copy tests
COPY tests/ /app/tests/
COPY pytest.ini /app/

# This is a modular FastMCP server that communicates via STDIO
# No port exposure needed

# Set environment variables - these are the defaults but can be overridden
# Note: REDMINE_API_KEY should be provided at runtime for security
ENV REDMINE_URL="https://redstone.redminecloud.net" \
    SERVER_MODE="live" \
    LOG_LEVEL="INFO" \
    MCP_TRANSPORT="stdio" \
    PYTHONPATH="/app"

# Run the modular MCP server directly
CMD ["sh", "-c", "python -m src.server 2>/app/logs/debug.log"]
