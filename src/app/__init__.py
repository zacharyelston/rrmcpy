"""
Flask application package initialization
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