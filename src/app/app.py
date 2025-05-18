"""
Redmine MCP Server Web UI
Provides a simple web interface for monitoring and controlling the MCP Server
"""
from flask import Flask
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__,
            static_folder="../../static",
            template_folder="../../templates")

app.secret_key = os.environ.get("SESSION_SECRET", "redmine-mcp-server-dev-key")

# Import routes after app is created to avoid circular imports
from src.app import routes

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)