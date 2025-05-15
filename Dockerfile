FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install dependencies
COPY docker-requirements.txt .
RUN pip install --no-cache-dir -r docker-requirements.txt

# Copy application code
COPY main.py redmine_api.py mcp_server.py models.py ./

# Make main.py executable
RUN chmod +x main.py

# This is a FastMCP server that communicates via STDIO
# No port exposure needed

# Run the application
CMD ["python", "main.py"]

# When building the Docker image, these environment variables can be overridden
# Default values are set in main.py
ENV REDMINE_URL="http://m1ni.local:3100" \
    REDMINE_API_KEY="af159c9b93c7c41a6b629de19b84f2d14e5854a4" \
    SERVER_MODE="live" \
    LOG_LEVEL="debug"
