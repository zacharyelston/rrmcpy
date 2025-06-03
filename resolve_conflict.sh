#!/bin/bash
# Script to resolve the stdio_server.py conflict

echo "Resolving Git conflict for stdio_server.py..."

# Remove the conflicted file since we've consolidated into mcp_server.py
git rm src/stdio_server.py

# Stage all changes
git add .

# Commit the resolution
git commit -m "Remove stdio_server.py - consolidated into single mcp_server.py

- Removed duplicate stdio server implementation
- All functionality now handled by src/mcp_server.py using FastMCP
- Fixed JSON response handling for proper MCP tool responses
- Consolidated architecture maintains modular design"

echo "Conflict resolved. You can now push the changes."
echo "Run: git push origin HEAD"