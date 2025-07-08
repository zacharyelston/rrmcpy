"""
Tools for wiki management
"""
import json
import logging
from typing import Dict, Any, Optional

class WikiTools:
    """Provides wiki management functionality as MCP tools"""
    
    @staticmethod
    def register_wiki_tools(mcp, client_manager, registered_tools, logger=None):
        """
        Register wiki management tools with FastMCP
        
        Args:
            mcp: FastMCP instance
            client_manager: Client manager instance
            registered_tools: List to track registered tools
            logger: Optional logger instance
        """
        wiki_client = client_manager.get_client('wiki')
        local_logger = logger or logging.getLogger("redmine_mcp_server.wiki_tools")
        local_logger.debug("Registering wiki tools")
        
        @mcp.tool("redmine-list-wiki-pages")
        async def list_wiki_pages(project_id: str):
            """List all wiki pages for a project"""
            try:
                if not project_id:
                    error = "project_id is required"
                    local_logger.error(f"MCP tool redmine-list-wiki-pages failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                
                result = wiki_client.list_wiki_pages(project_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                local_logger.error(f"Error listing wiki pages: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
        
        registered_tools.append("redmine-list-wiki-pages")
        
        @mcp.tool("redmine-get-wiki-page")
        async def get_wiki_page(project_id: str, page_name: str, version: int = None):
            """Get content of a specific wiki page"""
            try:
                if not project_id or not page_name:
                    error = "project_id and page_name are required"
                    local_logger.error(f"MCP tool redmine-get-wiki-page failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                
                result = wiki_client.get_wiki_page(project_id, page_name, version)
                return json.dumps(result, indent=2)
            except Exception as e:
                local_logger.error(f"Error getting wiki page: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
        
        registered_tools.append("redmine-get-wiki-page")
        
        @mcp.tool("redmine-create-wiki-page")
        async def create_wiki_page(project_id: str, page_name: str, text: str, 
                                 parent_title: str = None, comments: str = None):
            """Create a new wiki page"""
            try:
                if not project_id or not page_name or text is None:
                    error = "project_id, page_name, and text are required"
                    local_logger.error(f"MCP tool redmine-create-wiki-page failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                
                # Fix parameter order to match client method (title=page_name, parent_title first, then comments)
                result = wiki_client.create_wiki_page(project_id, page_name, text, 
                                                    parent_title=parent_title, comments=comments)
                return json.dumps(result, indent=2)
            except Exception as e:
                local_logger.error(f"Error creating wiki page: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
        
        registered_tools.append("redmine-create-wiki-page")
        
        @mcp.tool("redmine-update-wiki-page")
        async def update_wiki_page(project_id: str, page_name: str, text: str, 
                                 comments: str = None, parent_title: str = None):
            """Update an existing wiki page"""
            try:
                if not project_id or not page_name or text is None:
                    error = "project_id, page_name, and text are required"
                    local_logger.error(f"MCP tool redmine-update-wiki-page failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                
                result = wiki_client.update_wiki_page(project_id, page_name, text, 
                                                   comments=comments, parent_title=parent_title)
                return json.dumps(result, indent=2)
            except Exception as e:
                local_logger.error(f"Error updating wiki page: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
        
        registered_tools.append("redmine-update-wiki-page")
        
        @mcp.tool("redmine-delete-wiki-page")
        async def delete_wiki_page(project_id: str, page_name: str):
            """Delete a wiki page"""
            try:
                if not project_id or not page_name:
                    error = "project_id and page_name are required"
                    local_logger.error(f"MCP tool redmine-delete-wiki-page failed: {error}")
                    return json.dumps({"error": error}, indent=2)
                
                result = wiki_client.delete_wiki_page(project_id, page_name)
                return json.dumps(result, indent=2)
            except Exception as e:
                local_logger.error(f"Error deleting wiki page: {e}")
                return json.dumps({"error": str(e), "success": False}, indent=2)
        
        registered_tools.append("redmine-delete-wiki-page")
        
        return registered_tools
