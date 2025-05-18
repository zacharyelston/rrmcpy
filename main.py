#!/usr/bin/env python3
"""Entry point for Replit

This file serves two purposes:
1. As an entry point for the MCPServer when executed directly
2. As an import point for the Flask app when imported by gunicorn

The Flask app is imported from app.py to support the workflow.
"""
from redmine_mcp_server import main
from app import app  # Import the Flask app to satisfy gunicorn

if __name__ == '__main__':
    main()