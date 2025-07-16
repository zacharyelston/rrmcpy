#!/usr/bin/env python3
"""
Integration tests for the search functionality workflow
Tests the unified search feature across multiple content types
"""
import os
import sys
import unittest
import json
from unittest.mock import Mock, patch, MagicMock

# Handle import paths for both local development and CI environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from src.base import RedmineBaseClient
    from src.core.client_manager import ClientManager
    from src.core.service_manager import ServiceManager
    from src.services.search_service import SearchService
    from src.core.tool_registrations import register_search_tools
    from src.core.tool_registry import ToolRegistry
except ImportError:
    # Alternative import path for CI environment
    from rrmcpy.src.base import RedmineBaseClient
    from rrmcpy.src.core.client_manager import ClientManager
    from rrmcpy.src.core.service_manager import ServiceManager
    from rrmcpy.src.services.search_service import SearchService
    from rrmcpy.src.core.tool_registrations import register_search_tools
    from rrmcpy.src.core.tool_registry import ToolRegistry


class TestSearchWorkflow(unittest.TestCase):
    """Integration tests for search functionality workflow"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a client manager with mocked clients
        self.client_manager = ClientManager()
        self.service_manager = ServiceManager(self.client_manager)
        self.tool_registry = ToolRegistry()
        
        # Mock the Redmine client
        self.mock_redmine_client = MagicMock()
        self.client_manager.get_client = MagicMock(return_value=self.mock_redmine_client)
        
        # Set up mock responses for search operations
        self.mock_issue_response = {
            "issues": [
                {
                    "id": 123,
                    "subject": "Test search issue",
                    "description": "This is a test issue for search functionality",
                    "created_on": "2025-07-16T10:00:00Z",
                    "updated_on": "2025-07-16T11:00:00Z",
                    "project": {"id": 1, "name": "Test Project"}
                }
            ],
            "total_count": 1
        }
        
        self.mock_wiki_index = {
            "wiki_pages": [
                {"title": "SearchPage"},
                {"title": "OtherPage"}
            ]
        }
        
        self.mock_wiki_page = {
            "wiki_page": {
                "title": "SearchPage",
                "text": "This wiki page contains search terms",
                "created_on": "2025-07-15T10:00:00Z",
                "updated_on": "2025-07-15T11:00:00Z",
                "version": 1
            }
        }
        
        # Register the search tools
        register_search_tools(self.tool_registry, self.service_manager)
        
    def test_unified_search(self):
        """Test the unified search tool with mocked responses"""
        # Configure mock responses
        def side_effect(path, **kwargs):
            if path == "issues.json" and "subject" in kwargs.get("f", []):
                return self.mock_issue_response
            elif path.endswith("wiki/index.json"):
                return self.mock_wiki_index
            elif path.endswith("wiki/SearchPage.json"):
                return self.mock_wiki_page
            elif path.endswith("wiki/OtherPage.json"):
                return {"wiki_page": {"title": "OtherPage", "text": "No search terms here"}}
            return {}
            
        self.mock_redmine_client.get.side_effect = side_effect
        
        # Execute the unified search tool
        search_tool = self.tool_registry.get_tool("redmine-search")
        self.assertIsNotNone(search_tool, "Search tool was not registered properly")
        
        # Perform a search
        result = search_tool.execute({
            "query": "search",
            "content_types": ["issues", "wiki_pages"]
        })
        
        # Verify search results
        self.assertTrue(result["success"], "Search should succeed")
        self.assertIn("results", result["data"], "Results should be present")
        self.assertIn("metadata", result["data"], "Metadata should be present")
        
        # Verify we have results from both content types
        results = result["data"]["results"]
        result_types = [r["type"] for r in results]
        self.assertIn("issue", result_types, "Should have issue results")
        self.assertIn("wiki_page", result_types, "Should have wiki page results")
        
        # Verify search metadata
        metadata = result["data"]["metadata"]
        self.assertEqual(metadata["query"], "search", "Query should be preserved in metadata")
        self.assertTrue(metadata["total_count"] >= 2, "Should have at least 2 results")
        
        # Verify excerpts and highlighting
        for item in results:
            if "excerpt" in item:
                self.assertIn("<highlight>search</highlight>", item["excerpt"], 
                             "Search terms should be highlighted in excerpts")
    
    def test_search_with_project_filter(self):
        """Test search with project filter"""
        # Configure mock responses
        self.mock_redmine_client.get.side_effect = lambda path, **kwargs: (
            self.mock_issue_response if path == "issues.json" else {}
        )
        
        # Execute search with project filter
        search_tool = self.tool_registry.get_tool("redmine-search")
        result = search_tool.execute({
            "query": "search",
            "project_id": "test-project",
            "content_types": ["issues"]
        })
        
        # Verify search was called with project filter
        self.assertTrue(result["success"], "Search should succeed")
        self.assertTrue(len(result["data"]["results"]) > 0, "Should have search results")
        
        # Verify the project_id was passed to the client
        calls = self.mock_redmine_client.get.call_args_list
        found_project_filter = False
        for call in calls:
            args, kwargs = call
            if args and args[0] == "issues.json" and "project_id" in kwargs:
                found_project_filter = True
                self.assertEqual(kwargs["project_id"], "test-project", 
                                "Project ID should be passed to API call")
                break
                
        self.assertTrue(found_project_filter, "Project filter should be applied to search")
    
    def test_search_error_handling(self):
        """Test error handling in search workflow"""
        # Configure mock to raise an exception
        self.mock_redmine_client.get.side_effect = Exception("API connection error")
        
        # Execute search that should fail
        search_tool = self.tool_registry.get_tool("redmine-search")
        result = search_tool.execute({
            "query": "search",
            "content_types": ["issues"]
        })
        
        # Verify error handling
        self.assertFalse(result["success"], "Search should fail")
        self.assertIn("error", result, "Error message should be present")
        self.assertIn("API connection error", result["error"], 
                     "Error should contain exception message")


if __name__ == '__main__':
    unittest.main()
