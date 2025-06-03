#!/usr/bin/env python3
"""
Production entry point for Redmine MCP Server
"""
import sys
import os
import asyncio

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server import main

if __name__ == "__main__":
    asyncio.run(main())