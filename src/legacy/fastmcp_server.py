#!/usr/bin/env python3
"""
Pure FastMCP implementation for Redmine MCP Server
Following FastMCP best practices without custom tool registry layers
"""
import os
import json
import logging
from typing import Optional, Dict, List

from fastmcp import FastMCP
from src.issues import IssueClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("redmine_mcp")

# Initialize FastMCP server
mcp = FastMCP("Redmine MCP Server")

# Global client instance
issue_client: Optional[IssueClient] = None

def initialize_client():
    """Initialize Redmine client from environment variables"""
    global issue_client
    
    redmine_url = os.getenv("REDMINE_URL")
    redmine_api_key = os.getenv("REDMINE_API_KEY")
    
    if not redmine_url or not redmine_api_key:
        raise ValueError("REDMINE_URL and REDMINE_API_KEY environment variables are required")
    
    issue_client = IssueClient(
        base_url=redmine_url,
        api_key=redmine_api_key,
        logger=logger
    )
    
    logger.info(f"Initialized Redmine client for {redmine_url}")

@mcp.tool()
async def redmine_create_issue(
    project_id: str,
    subject: str,
    description: str = None,
    tracker_id: int = None,
    status_id: int = None,
    priority_id: int = None,
    assigned_to_id: int = None
) -> str:
    """Create a new issue in Redmine"""
    if not issue_client:
        return "Error: Redmine client not initialized"
    
    try:
        issue_data = {"project_id": project_id, "subject": subject}
        if description: issue_data["description"] = description
        if tracker_id: issue_data["tracker_id"] = tracker_id
        if status_id: issue_data["status_id"] = status_id
        if priority_id: issue_data["priority_id"] = priority_id
        if assigned_to_id: issue_data["assigned_to_id"] = assigned_to_id
        
        result = issue_client.create_issue(issue_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating issue: {str(e)}"

@mcp.tool()
async def redmine_get_issue(issue_id: int, include: List[str] = None) -> str:
    """Get a specific issue by ID"""
    if not issue_client:
        return "Error: Redmine client not initialized"
    
    try:
        result = issue_client.get_issue(issue_id, include)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting issue {issue_id}: {str(e)}"

@mcp.tool()
async def redmine_list_issues(
    project_id: str = None,
    status_id: int = None,
    assigned_to_id: int = None,
    tracker_id: int = None,
    limit: int = None,
    offset: int = None
) -> str:
    """List issues with optional filtering"""
    if not issue_client:
        return "Error: Redmine client not initialized"
    
    try:
        params = {}
        if project_id: params["project_id"] = project_id
        if status_id: params["status_id"] = status_id
        if assigned_to_id: params["assigned_to_id"] = assigned_to_id
        if tracker_id: params["tracker_id"] = tracker_id
        if limit: params["limit"] = limit
        if offset: params["offset"] = offset
        
        result = issue_client.get_issues(params)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error listing issues: {str(e)}"

@mcp.tool()
async def redmine_update_issue(
    issue_id: int,
    subject: str = None,
    description: str = None,
    status_id: int = None,
    priority_id: int = None,
    assigned_to_id: int = None,
    notes: str = None
) -> str:
    """Update an existing issue"""
    if not issue_client:
        return "Error: Redmine client not initialized"
    
    try:
        issue_data = {}
        if subject: issue_data["subject"] = subject
        if description: issue_data["description"] = description
        if status_id: issue_data["status_id"] = status_id
        if priority_id: issue_data["priority_id"] = priority_id
        if assigned_to_id: issue_data["assigned_to_id"] = assigned_to_id
        if notes: issue_data["notes"] = notes
        
        result = issue_client.update_issue(issue_id, issue_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error updating issue {issue_id}: {str(e)}"

@mcp.tool()
async def redmine_delete_issue(issue_id: int) -> str:
    """Delete an issue"""
    if not issue_client:
        return "Error: Redmine client not initialized"
    
    try:
        result = issue_client.delete_issue(issue_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error deleting issue {issue_id}: {str(e)}"

@mcp.tool()
async def redmine_health_check() -> str:
    """Check Redmine server health and connectivity"""
    if not issue_client:
        return "Error: Redmine client not initialized"
    
    try:
        result = issue_client.health_check()
        return json.dumps({"healthy": result, "status": "Connected" if result else "Disconnected"}, indent=2)
    except Exception as e:
        return f"Health check failed: {str(e)}"

@mcp.tool()
async def redmine_get_current_user() -> str:
    """Get current authenticated user information"""
    if not issue_client:
        return "Error: Redmine client not initialized"
    
    try:
        result = issue_client.make_request("GET", "/users/current.json")
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting current user: {str(e)}"

async def main():
    """Main entry point following FastMCP best practices"""
    try:
        # Initialize the Redmine client
        initialize_client()
        
        # Test the connection
        if issue_client and issue_client.health_check():
            logger.info("Redmine connection verified - server ready")
        else:
            logger.warning("Redmine connection failed - check configuration")
        
        # Run the FastMCP server
        await mcp.run()
        
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        raise

if __name__ == "__main__":
    import asyncio
    
    # Handle container environments with existing event loops
    try:
        # Check if there's already a running event loop
        loop = asyncio.get_running_loop()
        # If we get here, there's already a loop running (like in Windsurf)
        try:
            import nest_asyncio
            nest_asyncio.apply()
            # Create a task in the existing loop
            task = loop.create_task(main())
            logger.info("Server started in container compatibility mode")
        except ImportError:
            logger.error("nest_asyncio required for container environments")
            logger.info("Run: pip install nest_asyncio")
    except RuntimeError:
        # No event loop running, we can start our own
        asyncio.run(main())
