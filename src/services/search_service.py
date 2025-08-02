"""
Search Service for enhanced search functionality in Redmine MCP.

This module implements a comprehensive search service as described in issue #766
and the Enhanced_Search_Functionality_Design wiki page.
"""

import logging
import time
from typing import Dict, List, Optional, Union, Any

from src.services.base_service import BaseService


class SearchResultProcessor:
    """
    Process and format search results from Redmine API.
    
    This class handles:
    - Excerpt extraction with context
    - Query term highlighting
    - Relevance calculation
    - Result normalization across content types
    """
    
    def process_results(self, results: Dict[str, Any], query: str, **kwargs) -> Dict[str, Any]:
        """
        Process raw search results:
        1. Extract relevant fields
        2. Format excerpts with highlighted query terms
        3. Calculate relevance scores (if not provided by API)
        4. Standardize result format across different content types
        5. Sort by relevance or other criteria
        
        Args:
            results: Raw results from Redmine API
            query: Original search query
            **kwargs: Additional processing options
            
        Returns:
            Processed and formatted search results
        """
        processed_results = []
        query_terms = self._extract_query_terms(query)
        
        # Process based on content type
        for result in results.get("results", []):
            content_type = result.get("type", "unknown")
            
            # Process based on content type
            if content_type == "issue":
                processed_result = self._process_issue_result(result, query_terms)
            elif content_type == "wiki_page":
                processed_result = self._process_wiki_result(result, query_terms)
            else:
                processed_result = self._process_generic_result(result, query_terms)
                
            processed_results.append(processed_result)
        
        # Sort results if specified
        sort_by = kwargs.get("sort_by", "relevance")
        if sort_by == "relevance":
            processed_results = sorted(
                processed_results, 
                key=lambda r: r.get("relevance_score", 0),
                reverse=True
            )
        elif sort_by in ["updated", "created"]:
            sort_field = "updated_on" if sort_by == "updated" else "created_on"
            processed_results = sorted(
                processed_results,
                key=lambda r: r.get(sort_field, ""),
                reverse=True
            )
            
        # Build metadata
        metadata = {
            "total_count": results.get("total_count", len(processed_results)),
            "returned_count": len(processed_results),
            "offset": kwargs.get("offset", 0),
            "content_types_searched": kwargs.get("content_types", ["unknown"]),
            "query": query
        }
        
        return {
            "results": processed_results,
            "metadata": metadata
        }
        
    def _extract_query_terms(self, query: str) -> List[str]:
        """Extract individual terms from query for highlighting"""
        # Basic term extraction - can be enhanced with NLP
        return [term.lower() for term in query.split() if len(term) > 2]
    
    def highlight_matches(self, text: str, query_terms: List[str]) -> str:
        """
        Highlight matching terms in text excerpts
        
        Args:
            text: Text to process
            query_terms: List of terms to highlight
            
        Returns:
            Text with highlighted terms using <highlight> tags
        """
        if not text or not query_terms:
            return text
            
        # Simple case-insensitive highlighting
        highlighted = text
        for term in query_terms:
            # Case-insensitive replacement with highlighting
            i = 0
            while i < len(highlighted):
                idx = highlighted[i:].lower().find(term.lower())
                if idx == -1:
                    break
                    
                idx += i
                matched_text = highlighted[idx:idx + len(term)]
                replacement = f"<highlight>{matched_text}</highlight>"
                highlighted = highlighted[:idx] + replacement + highlighted[idx + len(term):]
                i = idx + len(replacement)
                
        return highlighted
    
    def extract_excerpt(self, full_text: str, query_terms: List[str], context_size: int = 100) -> str:
        """
        Extract relevant excerpts from full text containing query terms
        
        Args:
            full_text: Complete text to extract from
            query_terms: Query terms to find
            context_size: Number of characters around match to include
            
        Returns:
            Excerpt with query terms and surrounding context
        """
        if not full_text or not query_terms:
            return ""
            
        # Find first occurrence of any term
        full_text_lower = full_text.lower()
        best_pos = -1
        best_term = None
        
        for term in query_terms:
            pos = full_text_lower.find(term.lower())
            if pos != -1 and (best_pos == -1 or pos < best_pos):
                best_pos = pos
                best_term = term
                
        if best_pos == -1:
            # No matches found, return start of text
            return full_text[:200] + "..." if len(full_text) > 200 else full_text
            
        # Calculate excerpt range
        start = max(0, best_pos - context_size)
        end = min(len(full_text), best_pos + len(best_term) + context_size)
        
        # Add ellipsis if excerpt doesn't start/end at text boundaries
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(full_text) else ""
        
        return prefix + full_text[start:end] + suffix
        
    def _process_issue_result(self, result: Dict[str, Any], query_terms: List[str]) -> Dict[str, Any]:
        """Process issue-specific result fields"""
        processed = self._process_generic_result(result, query_terms)
        
        # Add issue-specific fields
        if "description" in result:
            excerpt = self.extract_excerpt(result["description"], query_terms)
            processed["excerpt"] = self.highlight_matches(excerpt, query_terms)
            
        if "status" in result:
            processed["status"] = result["status"]
            
        return processed
        
    def _process_wiki_result(self, result: Dict[str, Any], query_terms: List[str]) -> Dict[str, Any]:
        """Process wiki-specific result fields"""
        processed = self._process_generic_result(result, query_terms)
        
        # Add wiki-specific fields
        if "text" in result:
            excerpt = self.extract_excerpt(result["text"], query_terms)
            processed["excerpt"] = self.highlight_matches(excerpt, query_terms)
            
        if "version" in result:
            processed["version"] = result["version"]
            
        return processed
        
    def _process_generic_result(self, result: Dict[str, Any], query_terms: List[str]) -> Dict[str, Any]:
        """Process fields common to all content types"""
        processed = {
            "id": result.get("id"),
            "type": result.get("type", "unknown"),
            "title": result.get("title", result.get("subject", "Untitled")),
            "url": result.get("url", ""),
            "created_on": result.get("created_on", ""),
            "updated_on": result.get("updated_on", "")
        }
        
        # Add project information if available
        if "project" in result:
            processed["project"] = result["project"]
            
        # Calculate basic relevance score if not provided
        if "relevance_score" in result:
            processed["relevance_score"] = result["relevance_score"]
        else:
            # Simple relevance calculation based on term frequency
            text_content = " ".join([
                str(result.get("title", "")),
                str(result.get("subject", "")),
                str(result.get("description", "")),
                str(result.get("text", ""))
            ]).lower()
            
            # Calculate score based on term frequency
            score = 0
            for term in query_terms:
                score += text_content.count(term.lower()) * (len(term) / 4)  # Weight by term length
                
            # Normalize score (0-1 range)
            processed["relevance_score"] = min(score / 10, 1.0) if score > 0 else 0.1
            
        return processed


class SearchCache:
    """
    Cache for search results to improve performance.
    
    Implements:
    - In-memory caching with TTL
    - Cache key generation from search parameters
    - Size-limited LRU-like cache eviction
    """
    
    def __init__(self, max_size: int = 100, ttl: int = 300):  # 5 minutes TTL by default
        """
        Initialize search cache
        
        Args:
            max_size: Maximum number of cached results
            ttl: Time to live in seconds
        """
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        
    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached results if they exist and haven't expired
        
        Args:
            cache_key: Cache key generated from search parameters
            
        Returns:
            Cached results or None if not found or expired
        """
        if cache_key not in self.cache:
            return None
            
        entry = self.cache[cache_key]
        timestamp = entry.get("timestamp", 0)
        
        # Check if entry has expired
        if time.time() - timestamp > self.ttl:
            # Remove expired entry
            del self.cache[cache_key]
            return None
            
        # Update timestamp to mark as recently used
        entry["timestamp"] = time.time()
        return entry.get("results")
        
    def set(self, cache_key: str, results: Dict[str, Any]) -> None:
        """
        Store search results in cache with timestamp
        
        Args:
            cache_key: Cache key generated from search parameters
            results: Search results to cache
        """
        # If cache is full, remove least recently used entry
        if len(self.cache) >= self.max_size and cache_key not in self.cache:
            # Find oldest entry
            oldest_key = min(self.cache, key=lambda k: self.cache[k].get("timestamp", 0))
            del self.cache[oldest_key]
            
        # Store results with timestamp
        self.cache[cache_key] = {
            "results": results,
            "timestamp": time.time()
        }
        
    def generate_cache_key(self, query: str, **kwargs) -> str:
        """
        Generate deterministic cache key from search parameters
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            String cache key
        """
        # Basic cache key generation
        key_parts = [f"q:{query.lower()}"]
        
        # Add important parameters to key
        for param in ["content_types", "project_id", "status_id", 
                      "limit", "offset", "include_description", 
                      "include_comments"]:
            if param in kwargs and kwargs[param] is not None:
                value = kwargs[param]
                if isinstance(value, list):
                    value = ",".join(sorted(value))
                key_parts.append(f"{param}:{value}")
                
        return "|".join(key_parts)


class SearchService(BaseService):
    """
    Search service for enhanced Redmine content search.
    
    Implements:
    - Unified search across multiple content types
    - Result processing and formatting
    - Search result caching
    - Error handling and validation
    """
    
    def __init__(self, client, logger=None):
        """
        Initialize the search service
        
        Args:
            client: RedmineClient instance for API interactions
            logger: Logger instance (optional)
        """
        # Initialize with required BaseService parameters
        logger = logger or logging.getLogger(__name__)
        
        super().__init__(client=client, logger=logger)
        self.result_processor = SearchResultProcessor()
        self.cache = SearchCache()
        
    def health_check(self):
        """
        Check if the search service is functioning properly
        
        Returns:
            dict: Status information including 'status' key with 'ok' or 'error'
        """
        try:
            # Simple health check - verify client connection
            if not self.client or not hasattr(self.client, 'url'):
                self.logger.error("Search service health check failed: No valid client")
                return {"status": "error", "message": "No valid client"}
                
            # Test connection to real Redmine API
            try:
                # Make a simple API call to verify connection
                response = self.client.get("projects.json", params={"limit": 1})
                if response and "projects" in response:
                    return {"status": "ok", "message": "Connected to Redmine API"}
                else:
                    return {"status": "error", "message": "Unable to retrieve data from Redmine API"}
            except Exception as e:
                return {"status": "error", "message": f"API connection error: {str(e)}"}
                
        except Exception as e:
            self.logger.error(f"Search service health check failed: {e}")
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}
        
    def search(self, query: str, content_types: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Main search method that orchestrates the search process
        
        Args:
            query: Search query string
            content_types: List of content types to search
                           ["issues", "wiki_pages", "documents", "projects"]
            **kwargs: Additional search parameters
                - project_id: Filter by project ID or identifier
                - status_id: Filter by status ("open", "closed", "all")
                - created_after: ISO date format
                - created_before: ISO date format
                - updated_after: ISO date format
                - updated_before: ISO date format
                - include_description: Include description in search
                - include_comments: Include comments in search
                - include_attachments: Include attachments in search
                - limit: Maximum results to return
                - offset: Results offset for pagination
                - sort_by: Sort order ("relevance", "updated", "created")
                - format_output: Whether to format output
                
        Returns:
            Processed search results
            
        Raises:
            ValueError: If search parameters are invalid
            SearchExecutionError: If search execution fails
        """
        # Set defaults
        if content_types is None:
            content_types = ["issues", "wiki_pages"]
            
        # Validate inputs
        self._validate_search_params(query, content_types, **kwargs)
        
        # Check cache
        cache_key = self.cache.generate_cache_key(query, content_types=content_types, **kwargs)
        cached_results = self.cache.get(cache_key)
        if cached_results:
            self.logger.debug(f"Cache hit for query: {query}")
            return cached_results
            
        # Execute search based on content types
        results = {"results": [], "total_count": 0}
        
        try:
            # Search issues if requested
            if "issues" in content_types:
                issue_results = self._search_issues(query, **kwargs)
                results["results"].extend(issue_results.get("results", []))
                results["total_count"] += issue_results.get("total_count", 0)
                
            # Search wiki pages if requested
            if "wiki_pages" in content_types:
                wiki_results = self._search_wiki_pages(query, **kwargs)
                results["results"].extend(wiki_results.get("results", []))
                results["total_count"] += wiki_results.get("total_count", 0)
                
            # Add other content types as implemented...
            
            # Apply pagination if needed
            limit = kwargs.get("limit", 100)
            offset = kwargs.get("offset", 0)
            results["results"] = results["results"][offset:offset + limit]
                
            # Process results
            processed_results = self.result_processor.process_results(
                results, query, content_types=content_types, **kwargs
            )
            
            # Cache results
            self.cache.set(cache_key, processed_results)
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            raise SearchExecutionError(f"Search execution failed: {str(e)}")
    
    def _search_issues(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute issue-specific search
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            Raw issue search results
        """
        try:
            # Extract issue-specific parameters
            project_id = kwargs.get("project_id")
            status_id = kwargs.get("status_id")
            
            # Call Redmine API through client
            params = {
                "q": query,
                "limit": kwargs.get("limit", 100),
                "offset": kwargs.get("offset", 0)
            }
            
            # Add optional filters
            if project_id:
                params["project_id"] = project_id
            if status_id:
                params["status_id"] = status_id
                
            # Add date filters if provided
            for date_param in ["created_on", "updated_on"]:
                date_after = kwargs.get(f"{date_param}_after")
                date_before = kwargs.get(f"{date_param}_before")
                
                if date_after:
                    params[f"{date_param}>="] = date_after
                if date_before:
                    params[f"{date_param}<="] = date_before
                    
            # Execute search via RedmineClient
            response = self.client.get("issues.json", params=params)
            
            if not response or "issues" not in response:
                self.logger.warning(f"No issue results found for query: {query}")
                return {"results": [], "total_count": 0}
                
            # Transform results to standard format
            results = []
            for issue in response["issues"]:
                result = {
                    "id": issue.get("id"),
                    "type": "issue",
                    "title": issue.get("subject", "Untitled Issue"),
                    "subject": issue.get("subject"),
                    "description": issue.get("description", ""),
                    "created_on": issue.get("created_on"),
                    "updated_on": issue.get("updated_on"),
                    "status": issue.get("status"),
                    "project": issue.get("project")
                }
                
                # Add URL
                base_url = self.client.url.rstrip("/")
                result["url"] = f"{base_url}/issues/{issue.get('id')}"
                
                results.append(result)
                
            return {
                "results": results,
                "total_count": response.get("total_count", len(results))
            }
            
        except Exception as e:
            self.logger.error(f"Issue search failed: {e}")
            # Return empty results rather than failing completely
            return {"results": [], "total_count": 0}
            
    def _search_wiki_pages(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute wiki-specific search
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            Raw wiki search results
        """
        try:
            # Wiki search requires project_id
            project_id = kwargs.get("project_id")
            
            if not project_id:
                self.logger.warning("Wiki search requires project_id parameter")
                return {"results": [], "total_count": 0}
                
            # First get list of wiki pages for the project
            response = self.client.get(f"projects/{project_id}/wiki/index.json")
            
            if not response or "wiki_pages" not in response:
                self.logger.warning(f"No wiki pages found for project: {project_id}")
                return {"results": [], "total_count": 0}
                
            # We'll need to get content for each page to search within them
            results = []
            total_checked = 0
            
            for wiki_page in response["wiki_pages"]:
                try:
                    # Get full page content
                    page_title = wiki_page.get("title")
                    page_response = self.client.get(
                        f"projects/{project_id}/wiki/{page_title}.json"
                    )
                    
                    if not page_response or "wiki_page" not in page_response:
                        continue
                        
                    page = page_response["wiki_page"]
                    total_checked += 1
                    
                    # Check if query is in title or text
                    text = page.get("text", "")
                    title = page.get("title", "")
                    
                    if (query.lower() in title.lower() or 
                            query.lower() in text.lower()):
                        
                        result = {
                            "id": title,  # Wiki pages use title as ID
                            "type": "wiki_page",
                            "title": title,
                            "text": text,
                            "created_on": page.get("created_on"),
                            "updated_on": page.get("updated_on"),
                            "version": page.get("version"),
                            "project": {"id": project_id, "name": project_id}
                        }
                        
                        # Add URL
                        base_url = self.client.url.rstrip("/")
                        result["url"] = f"{base_url}/projects/{project_id}/wiki/{page_title}"
                        
                        results.append(result)
                        
                except Exception as e:
                    self.logger.error(f"Error getting wiki page content: {e}")
                    continue
                    
            return {
                "results": results,
                "total_count": len(results)
            }
            
        except Exception as e:
            self.logger.error(f"Wiki search failed: {e}")
            # Return empty results rather than failing completely
            return {"results": [], "total_count": 0}
            
    def _validate_search_params(self, query: str, content_types: List[str], **kwargs) -> None:
        """
        Validate search parameters
        
        Args:
            query: Search query
            content_types: List of content types to search
            **kwargs: Additional search parameters
            
        Raises:
            ValueError: If any parameters are invalid
        """
        # Check required parameters
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
            
        # Validate content types
        valid_content_types = ["issues", "wiki_pages", "documents", "projects"]
        if content_types:
            for content_type in content_types:
                if content_type not in valid_content_types:
                    raise ValueError(f"Invalid content type: {content_type}")
                    
        # Validate limit and offset
        limit = kwargs.get("limit")
        if limit is not None and (not isinstance(limit, int) or limit < 1):
            raise ValueError("Limit must be a positive integer")
            
        offset = kwargs.get("offset")
        if offset is not None and (not isinstance(offset, int) or offset < 0):
            raise ValueError("Offset must be a non-negative integer")
            
        # Validate date parameters
        for date_param in ["created_after", "created_before", "updated_after", "updated_before"]:
            date_value = kwargs.get(date_param)
            if date_value and not self._is_valid_date_format(date_value):
                raise ValueError(f"Invalid date format for {date_param}: {date_value}")
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """
        Check if string is in valid ISO date format
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if valid date format, False otherwise
        """
        # Basic ISO date validation - can be enhanced
        try:
            # Check for YYYY-MM-DD format
            parts = date_str.split("-")
            if len(parts) != 3:
                return False
                
            year, month, day = parts
            
            # Basic validation
            if (len(year) != 4 or not year.isdigit() or
                    len(month) != 2 or not month.isdigit() or
                    len(day) != 2 or not day.isdigit()):
                return False
                
            # Check ranges
            if (int(month) < 1 or int(month) > 12 or
                    int(day) < 1 or int(day) > 31):
                return False
                
            return True
        except:
            return False


class SearchExecutionError(Exception):
    """Raised when search execution fails"""
    pass
