FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY docker-requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r docker-requirements.txt

# Copy application code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV REDMINE_URL=https://redstone.redminecloud.net
# REDMINE_API_KEY will be provided at runtime
ENV SERVER_MODE=live
ENV LOG_LEVEL=info

# Run as non-root user
RUN useradd -m mcp
USER mcp

# Run the MCP server
CMD ["python", "redmine_mcp_server.py"]