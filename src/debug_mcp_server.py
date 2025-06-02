"""
Debug version of the MCP server with enhanced logging to diagnose response issues
"""
import asyncio
import logging
import sys
import json
from typing import Any, Dict, List, Optional

from mcp.server import FastMCP
from mcp.server.models import InitializationOptions
from mcp import Tool
from pydantic import BaseModel, Field

from src.redmine_client import RedmineClient


# Pydantic models for proper type handling
class IssueCreateRequest(BaseModel):
    project_id: str = Field(description="Project identifier")
    subject: str = Field(description="Issue subject")
    description: Optional[str] = Field(default=None, description="Issue description")
    tracker_id: Optional[int] = Field(default=None, description="Tracker ID")
    status_id: Optional[int] = Field(default=None, description="Status ID")
    priority_id: Optional[int] = Field(default=None, description="Priority ID")
    assigned_to_id: Optional[int] = Field(default=None, description="Assigned user ID")


class RedmineDebugMCPServer:
    """
    Debug version of the FastMCP server with enhanced logging
    """
    
    def __init__(self, redmine_url: str, api_key: str):
        """
        Initialize the Redmine MCP Server
        
        Args:
            redmine_url: URL of the Redmine instance
            api_key: API key for Redmine authentication
        """
        self.redmine_url = redmine_url
        self.api_key = api_key
        
        # Configure detailed logging to stderr
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stderr
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redmine client
        self.redmine_client = RedmineClient(redmine_url, api_key, self.logger)
        
        # Initialize FastMCP
        self.app = FastMCP("Redmine Debug MCP Server")
        
        # Register tools after MCP initialization
        self._register_tools()
    
    def _register_tools(self):
        """Register all MCP tools with enhanced debug logging"""
        
        @self.app.tool()
        def redmine_debug_create_issue(request: IssueCreateRequest) -> Dict[str, Any]:
            """
            Create a new issue with debug logging
            
            Args:
                request: Issue creation parameters
                
            Returns:
                Created issue details
            """
            self.logger.debug(f"=== DEBUG CREATE ISSUE START ===")
            self.logger.debug(f"Request type: {type(request)}")
            self.logger.debug(f"Request data: {request}")
            
            try:
                issue_data = request.model_dump(exclude_none=True)
                self.logger.debug(f"Issue data after model_dump: {issue_data}")
                
                result = self.redmine_client.create_issue(issue_data)
                self.logger.debug(f"Raw result from redmine_client: {result}")
                self.logger.debug(f"Result type: {type(result)}")
                self.logger.debug(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
                
                if result.get('error'):
                    self.logger.error(f"Error in result: {result}")
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                
                issue_response = result.get('issue', {})
                self.logger.debug(f"Issue response extracted: {issue_response}")
                self.logger.debug(f"Issue response type: {type(issue_response)}")
                self.logger.debug(f"Issue response serialized: {json.dumps(issue_response, indent=2)}")
                
                # Try different return formats
                self.logger.debug(f"=== TRYING DIFFERENT RETURN FORMATS ===")
                
                # Option 1: Return as-is
                self.logger.debug(f"Returning issue_response as-is")
                return issue_response
                
            except Exception as e:
                self.logger.error(f"Exception in create_issue: {e}", exc_info=True)
                raise
            finally:
                self.logger.debug(f"=== DEBUG CREATE ISSUE END ===")
        
        @self.app.tool()
        def redmine_debug_list_issues(
            project_id: Optional[str] = None,
            limit: Optional[int] = 3
        ) -> List[Dict[str, Any]]:
            """
            List issues with debug logging
            
            Args:
                project_id: Filter by project identifier
                limit: Maximum number of issues to return
                
            Returns:
                List of issues
            """
            self.logger.debug(f"=== DEBUG LIST ISSUES START ===")
            self.logger.debug(f"Parameters: project_id={project_id}, limit={limit}")
            
            params = {"limit": limit}
            if project_id:
                params["project_id"] = project_id
            
            try:
                result = self.redmine_client.get_issues(params)
                self.logger.debug(f"Raw result from redmine_client: {type(result)}")
                self.logger.debug(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
                
                if result.get('error'):
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
                
                issues_list = result.get('issues', [])
                self.logger.debug(f"Issues list type: {type(issues_list)}")
                self.logger.debug(f"Issues list length: {len(issues_list)}")
                self.logger.debug(f"First issue (if any): {issues_list[0] if issues_list else 'No issues'}")
                
                # Log the serialized version
                self.logger.debug(f"Issues list serialized: {json.dumps(issues_list, indent=2)}")
                
                return issues_list
                
            except Exception as e:
                self.logger.error(f"Exception in list_issues: {e}", exc_info=True)
                raise
            finally:
                self.logger.debug(f"=== DEBUG LIST ISSUES END ===")
        
        @self.app.tool()
        def redmine_debug_test_simple() -> Dict[str, Any]:
            """
            Simple test tool that returns a hardcoded response
            
            Returns:
                Test response
            """
            self.logger.debug("=== DEBUG TEST SIMPLE ===")
            response = {
                "test": "response",
                "number": 42,
                "nested": {
                    "key": "value"
                }
            }
            self.logger.debug(f"Returning: {response}")
            return response
        
        @self.app.tool()
        def redmine_debug_test_list() -> List[Dict[str, Any]]:
            """
            Simple test tool that returns a hardcoded list
            
            Returns:
                Test list response
            """
            self.logger.debug("=== DEBUG TEST LIST ===")
            response = [
                {"id": 1, "name": "test1"},
                {"id": 2, "name": "test2"},
                {"id": 3, "name": "test3"}
            ]
            self.logger.debug(f"Returning: {response}")
            return response
    
    def run_stdio(self):
        """Run the MCP server with STDIO transport for MCP clients"""
        self.logger.info(f"Starting Redmine Debug MCP Server for {self.redmine_url}")
        # Use FastMCP's built-in run method - it handles STDIO by default
        self.app.run(transport="stdio")


def main():
    """Main entry point"""
    import os
    
    # Get configuration from environment
    redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
    redmine_api_key = os.environ.get('REDMINE_API_KEY')
    
    if not redmine_api_key:
        logging.error("REDMINE_API_KEY environment variable is required")
        sys.exit(1)
    
    # Create and run server
    server = RedmineDebugMCPServer(redmine_url, redmine_api_key)
    server.run_stdio()


if __name__ == '__main__':
    main()
