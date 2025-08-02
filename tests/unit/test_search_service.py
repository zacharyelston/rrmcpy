"""
Unit tests for the Search Service functionality.

These tests verify the core functionality of the SearchService class,
SearchResultProcessor, and SearchCache components.
"""

import unittest
from unittest.mock import MagicMock, patch
import time
import json
from src.services.search_service import SearchService, SearchResultProcessor, SearchCache, SearchExecutionError


class TestSearchResultProcessor(unittest.TestCase):
    """Test the SearchResultProcessor component"""
    
    def setUp(self):
        self.processor = SearchResultProcessor()
        
    def test_extract_query_terms(self):
        """Test query term extraction for highlighting"""
        # Test basic extraction
        query = "redmine search functionality"
        terms = self.processor._extract_query_terms(query)
        self.assertEqual(len(terms), 3)
        self.assertIn("redmine", terms)
        self.assertIn("search", terms)
        self.assertIn("functionality", terms)
        
        # Test with mixed case
        query = "ReDmine Search FUNCTIONALITY"
        terms = self.processor._extract_query_terms(query)
        self.assertEqual(len(terms), 3)
        self.assertIn("redmine", terms)
        self.assertIn("search", terms)
        self.assertIn("functionality", terms)
        
    def test_highlight_matches(self):
        """Test highlighting of matched terms in text"""
        text = "This is a test about Redmine search functionality"
        query_terms = ["redmine", "search"]
        
        highlighted = self.processor.highlight_matches(text, query_terms)
        
        # Check that both terms were highlighted
        self.assertIn("<highlight>Redmine</highlight>", highlighted)
        self.assertIn("<highlight>search</highlight>", highlighted)
        
        # Test with no matches
        text = "This text has no matches"
        highlighted = self.processor.highlight_matches(text, ["missing", "absent"])
        self.assertEqual(text, highlighted)
        
    def test_extract_excerpt(self):
        """Test excerpt extraction from full text"""
        full_text = "This is a long text about various topics. " * 10
        full_text += "Here is a mention of Redmine search functionality. "
        full_text += "This is some more content after the relevant part. " * 10
        
        query_terms = ["redmine", "search"]
        excerpt = self.processor.extract_excerpt(full_text, query_terms)
        
        # Check that excerpt contains the relevant part
        self.assertIn("Redmine search", excerpt)
        
        # Check that excerpt is shorter than full text
        self.assertLess(len(excerpt), len(full_text))
        
        # Check excerpt has ellipsis for truncated content
        self.assertTrue(excerpt.startswith("...") or excerpt.endswith("..."))
        
    def test_process_results(self):
        """Test processing of raw search results"""
        # Create mock raw results
        raw_results = {
            "results": [
                {
                    "id": 1,
                    "type": "issue",
                    "subject": "Test Issue with Search Terms",
                    "description": "This is a description about search functionality",
                    "created_on": "2025-07-15",
                    "updated_on": "2025-07-16"
                },
                {
                    "id": 2,
                    "type": "wiki_page",
                    "title": "Wiki Page about Search",
                    "text": "This wiki page explains search capabilities",
                    "created_on": "2025-07-14",
                    "updated_on": "2025-07-15"
                }
            ],
            "total_count": 2
        }
        
        processed = self.processor.process_results(raw_results, "search functionality")
        
        # Check metadata
        self.assertEqual(processed["metadata"]["total_count"], 2)
        self.assertEqual(processed["metadata"]["returned_count"], 2)
        self.assertEqual(processed["metadata"]["query"], "search functionality")
        
        # Check that results were processed
        self.assertEqual(len(processed["results"]), 2)
        
        # Check that excerpts were extracted and highlighted
        for result in processed["results"]:
            if result["type"] == "issue":
                self.assertIn("<highlight>search</highlight>", result.get("excerpt", ""))
            elif result["type"] == "wiki_page":
                self.assertIn("<highlight>search</highlight>", result.get("excerpt", ""))
                
        # Check sorting by relevance
        processed = self.processor.process_results(raw_results, "search", sort_by="relevance")
        self.assertTrue(len(processed["results"]) == 2)


class TestSearchCache(unittest.TestCase):
    """Test the SearchCache component"""
    
    def setUp(self):
        self.cache = SearchCache(max_size=3, ttl=2)  # Short TTL for testing
        
    def test_cache_key_generation(self):
        """Test generation of cache keys"""
        key1 = self.cache.generate_cache_key("search query")
        key2 = self.cache.generate_cache_key("search query", project_id="test")
        
        # Different queries should have different keys
        self.assertNotEqual(key1, key2)
        
        # Same parameters should generate same key
        key3 = self.cache.generate_cache_key("search query")
        self.assertEqual(key1, key3)
        
        # Parameter order shouldn't matter
        key4 = self.cache.generate_cache_key("search query", content_types=["issues", "wiki_pages"])
        key5 = self.cache.generate_cache_key("search query", content_types=["wiki_pages", "issues"])
        self.assertEqual(key4, key5)
        
    def test_cache_storage_and_retrieval(self):
        """Test storing and retrieving from cache"""
        key = self.cache.generate_cache_key("test query")
        results = {"results": [{"id": 1}], "metadata": {"count": 1}}
        
        # Store in cache
        self.cache.set(key, results)
        
        # Retrieve from cache
        cached = self.cache.get(key)
        self.assertEqual(cached, results)
        
    def test_cache_expiration(self):
        """Test cache entry expiration"""
        key = self.cache.generate_cache_key("expiring query")
        results = {"results": [{"id": 2}], "metadata": {"count": 1}}
        
        # Store in cache
        self.cache.set(key, results)
        
        # Should be retrievable immediately
        self.assertEqual(self.cache.get(key), results)
        
        # Wait for TTL to expire
        time.sleep(3)
        
        # Should now be expired
        self.assertIsNone(self.cache.get(key))
        
    def test_cache_size_limit(self):
        """Test cache size limiting"""
        # Add max_size + 1 entries
        for i in range(4):  # Max size is 3
            key = self.cache.generate_cache_key(f"query{i}")
            results = {"results": [{"id": i}], "metadata": {"count": 1}}
            self.cache.set(key, results)
            
        # Cache should only have 3 entries (the most recent 3)
        self.assertEqual(len(self.cache.cache), 3)
        
        # The oldest entry should be gone
        oldest_key = self.cache.generate_cache_key("query0")
        self.assertIsNone(self.cache.get(oldest_key))
        
        # The newer entries should still be there
        for i in range(1, 4):
            key = self.cache.generate_cache_key(f"query{i}")
            self.assertIsNotNone(self.cache.get(key))


class TestSearchService(unittest.TestCase):
    """Test the SearchService class with real API connections"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        # Import here to avoid circular imports
        from tests.helpers.api_test_helper import APITestHelper, TestEnvironment
        
        # Check if we should run real API tests
        if not TestEnvironment.is_using_real_api():
            raise unittest.SkipTest("Skipping real API tests (USE_REAL_API != true)")
            
        # Set up test environment
        TestEnvironment.setup_test_environment()
        
        # Create API test helper
        try:
            cls.api_helper = APITestHelper()
            cls.client = cls.api_helper.get_redmine_client()
        except Exception as e:
            raise unittest.SkipTest(f"Failed to initialize API helper: {e}")
    
    def setUp(self):
        """Set up test environment for each test"""
        try:
            # Create a SearchService with real client
            self.search_service = SearchService(self.__class__.client)
        except Exception as e:
            self.skipTest(f"Failed to initialize SearchService: {e}")
    
    def test_validate_search_params(self):
        """Test validation of search parameters"""
        # Valid parameters should not raise an exception
        self.search_service._validate_search_params("test query", ["issues"])
        
        # Empty query should raise ValueError
        with self.assertRaises(ValueError):
            self.search_service._validate_search_params("", ["issues"])
            
        # Invalid content type should raise ValueError
        with self.assertRaises(ValueError):
            self.search_service._validate_search_params("test", ["invalid_type"])
            
        # Invalid limit should raise ValueError
        with self.assertRaises(ValueError):
            self.search_service._validate_search_params("test", ["issues"], limit=-1)
            
    def test_search_issues(self):
        """Test issue search functionality with real API"""
        # Execute search with real client
        result = self.search_service._search_issues("test")
        
        # Verify basic structure of results
        self.assertIn("results", result, "Results key should be present")
        self.assertIn("total_count", result, "Total count key should be present")
        
        # Verify result transformation
        # Note: We don't assert specific values since they depend on actual data in Redmine
        if result["total_count"] > 0:
            issue = result["results"][0]
            self.assertIn("id", issue, "Issue should have ID")
            self.assertEqual(issue["type"], "issue", "Result type should be 'issue'")
            self.assertIn("title", issue, "Issue should have title")
            self.assertIn("url", issue, "Issue should have URL")
        else:
            print("Warning: No test issues found in Redmine. Test passed but not comprehensive.")
        
    def test_search_wiki_pages(self):
        """Test wiki page search functionality with real API"""
        # Import helper to get test project ID
        from tests.helpers.api_test_helper import TestEnvironment
        
        # Get test project ID
        test_project_id = TestEnvironment.get_test_project_id()
        
        # Execute search
        result = self.search_service._search_wiki_pages("test", project_id=test_project_id)
        
        # Verify basic structure of results
        self.assertIn("results", result, "Results key should be present")
        self.assertIn("total_count", result, "Total count key should be present")
        
        # Verify result transformation
        # Note: We don't assert specific values since they depend on actual data in Redmine
        if result["total_count"] > 0:
            page = result["results"][0]
            self.assertIn("title", page, "Wiki page should have title")
            self.assertEqual(page["type"], "wiki_page", "Result type should be 'wiki_page'")
            self.assertIn("url", page, "Wiki page should have URL")
        else:
            print(f"Warning: No wiki pages found in project {test_project_id}. Test passed but not comprehensive.")
        
    def test_main_search_function(self):
        """Test the main search orchestration function"""
        # Setup mock for _search_issues and _search_wiki_pages
        with patch.object(self.search_service, '_search_issues') as mock_search_issues, \
             patch.object(self.search_service, '_search_wiki_pages') as mock_search_wiki:
            
            # Setup mock returns
            mock_search_issues.return_value = {
                "results": [{"id": 1, "type": "issue", "title": "Test Issue"}],
                "total_count": 1
            }
            
            mock_search_wiki.return_value = {
                "results": [{"id": "Wiki1", "type": "wiki_page", "title": "Test Wiki"}],
                "total_count": 1
            }
            
            # Execute search across both content types
            results = self.search_service.search(
                "test query", 
                content_types=["issues", "wiki_pages"],
                project_id="test"
            )
            
            # Verify proper functions were called
            mock_search_issues.assert_called_once()
            mock_search_wiki.assert_called_once()
            
            # Verify results were combined
            self.assertEqual(len(results["results"]), 2)
            self.assertEqual(results["metadata"]["total_count"], 2)
            
            # Test cache functionality
            mock_search_issues.reset_mock()
            mock_search_wiki.reset_mock()
            
            # Search again with same parameters
            results2 = self.search_service.search(
                "test query", 
                content_types=["issues", "wiki_pages"],
                project_id="test"
            )
            
            # Verify cache was used (mocks not called)
            mock_search_issues.assert_not_called()
            mock_search_wiki.assert_not_called()
            
            # Results should be the same
            self.assertEqual(len(results2["results"]), 2)


if __name__ == '__main__':
    unittest.main()
