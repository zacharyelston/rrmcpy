"""
Wiki client for Redmine MCP Server
Handles wiki-related operations
"""

import logging
from typing import Dict, List, Optional, Any
from ..base import RedmineBaseClient
from ..core.errors import ErrorHandler

class WikiClient(RedmineBaseClient):
    """
    Client for interacting with Redmine wiki functionality
    """
    
    def __init__(self, base_url: str, api_key: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the WikiClient
        
        Args:
            base_url: Base URL of the Redmine instance
            api_key: API key for authentication
            logger: Optional logger instance
        """
        super().__init__(base_url, api_key, logger)
        self.logger = logger or logging.getLogger(__name__)
        self.error_handler = ErrorHandler(self.logger)
    
    def list_wiki_pages(self, project_id: str) -> Dict[str, Any]:
        """
        List all wiki pages for a project
        
        Args:
            project_id: ID or identifier of the project
            
        Returns:
            Dict containing list of wiki pages or error information
        """
        endpoint = f"/projects/{project_id}/wiki/index.json"
        
        try:
            response = self.make_request('GET', endpoint)
            
            if 'error' in response:
                self.logger.error(f"Failed to list wiki pages: {response['error']}")
                return response
                
            return {
                'success': True,
                'pages': response.get('wiki_pages', [])
            }
            
        except Exception as e:
            error_msg = f"Error listing wiki pages: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return self.error_handler.handle_unexpected_error(error_msg)
    
    def get_wiki_page(self, project_id: str, page_name: str, version: Optional[int] = None) -> Dict[str, Any]:
        """
        Get a specific wiki page
        
        Args:
            project_id: ID or identifier of the project
            page_name: Name of the wiki page
            version: Optional version number of the page
            
        Returns:
            Dict containing the wiki page data or error information
        """
        endpoint = f"/projects/{project_id}/wiki/{page_name}.json"
        params = {}
        
        if version is not None:
            params['version'] = version
            
        try:
            response = self.make_request('GET', endpoint, params=params)
            
            if 'error' in response:
                self.logger.error(f"Failed to get wiki page {page_name}: {response['error']}")
                return response
                
            return {
                'success': True,
                'page': response.get('wiki_page', {})
            }
            
        except Exception as e:
            error_msg = f"Error getting wiki page {page_name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return self.error_handler.handle_unexpected_error(error_msg)
    
    def create_wiki_page(self, project_id: str, title: str, text: str, 
                        parent_title: Optional[str] = None, 
                        comments: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new wiki page
        
        Args:
            project_id: ID or identifier of the project
            title: Title of the new wiki page
            text: Content of the wiki page
            parent_title: Optional title of the parent page
            comments: Optional comments for the change
            
        Returns:
            Dict containing the created wiki page or error information
        """
        self.logger.info(f"Creating new wiki page with title: {title} in project: {project_id}")
        
        # First validate required fields are present and not None
        if project_id is None:
            return self.error_handler.handle_validation_error(
                'Project ID is required',
                field_errors={'project_id': 'Project ID cannot be None'},
                context={}
            )
            
        # Validate field types
        validation_error = self.validate_input(
            {'project_id': project_id, 'title': title, 'text': text},
            required_fields=['project_id', 'title', 'text'],
            field_types={
                'project_id': (str, int),
                'title': str,
                'text': str,
                'parent_title': (str, type(None)),
                'comments': (str, type(None))
            }
        )
        
        if validation_error:
            self.logger.error(f"Validation error: {validation_error}")
            return validation_error
            
        # Additional validation for empty title or text
        field_errors = {}
        if not title.strip():
            field_errors['title'] = 'Title cannot be empty'
        if not text.strip():
            field_errors['text'] = 'Content cannot be empty'
            
        if field_errors:
            return self.error_handler.handle_validation_error(
                'Validation failed: Empty field(s)',
                field_errors=field_errors,
                context={'project_id': project_id}
            )
            
        # Prepare the request data
        page_data = {
            'wiki_page': {
                'title': title,
                'text': text
            }
        }
        
        # Add optional fields if provided
        if parent_title:
            page_data['wiki_page']['parent_title'] = parent_title
            
        if comments:
            page_data['wiki_page']['comments'] = comments
        
        # Try PUT method first (standard method according to Redmine API docs)
        standard_endpoint = f"/projects/{project_id}/wiki/{title}.json"
        result = {'method_used': 'PUT'}  # Default method
        
        try:
            self.logger.debug(f"Attempting to create wiki page using PUT to {standard_endpoint}")
            response = self.make_request('PUT', standard_endpoint, data=page_data)
            
            if 'error' in response:
                error_msg = f"Failed to create wiki page with PUT method: {response.get('error', 'Unknown error')}"
                self.logger.warning(error_msg)
                # Continue to fallback method
            elif not response or (isinstance(response, dict) and not response):
                # Some Redmine versions return empty body on success
                self.logger.info(f"Successfully created wiki page {title} using PUT method (empty response)")
                return {
                    'success': True,
                    'page': {'title': title},
                    'method_used': 'PUT'
                }
            elif response and response.get('wiki_page'):
                # Successful creation with detailed response
                self.logger.info(f"Wiki page '{title}' created successfully using PUT method")
                return {
                    'success': True,
                    'page': response.get('wiki_page'),
                    'method_used': 'PUT'
                }
            else:
                self.logger.warning(f"PUT request succeeded but returned unexpected response: {response}")
                # Continue to fallback method
                
        except Exception as e:
            self.logger.warning(f"PUT method failed with error: {str(e)}. Trying POST method as fallback...")
            # Continue to fallback method

        # Fallback to POST method (might be supported in some custom Redmine implementations)
        fallback_endpoint = f"/projects/{project_id}/wiki.json"
        
        try:
            self.logger.debug(f"Attempting to create wiki page using POST to {fallback_endpoint}")
            response = self.make_request('POST', fallback_endpoint, data=page_data)
            
            if 'error' in response:
                error_msg = f"Both methods failed. PUT error already logged, POST error: {response.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
            elif not response or (isinstance(response, dict) and not response):
                # Some Redmine versions return empty body on success
                self.logger.info(f"Successfully created wiki page {title} using POST method (empty response)")
                return {
                    'success': True,
                    'page': {'title': title},
                    'method_used': 'POST'
                }
            elif response and response.get('wiki_page'):
                # Successful creation with POST method
                self.logger.info(f"Successfully created wiki page {title} using POST method")
                return {
                    'success': True,
                    'page': response.get('wiki_page'),
                    'method_used': 'POST'
                }
            else:
                # Unexpected but not error response
                self.logger.warning(f"Both methods completed but returned unexpected responses")
                return {
                    'success': True, 
                    'page': {'title': title},
                    'method_used': 'POST',
                    'response': response
                }
            
        except Exception as e:
            error_msg = f"Error creating wiki page (both methods failed): {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return self.error_handler.handle_unexpected_error(error_msg)
    
    def update_wiki_page(self, project_id: str, page_name: str, text: str, 
                        comments: Optional[str] = None, 
                        parent_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing wiki page
        
        Args:
            project_id: ID or identifier of the project
            page_name: Name of the wiki page to update
            text: New content for the wiki page
            comments: Optional comments for the change
            parent_title: Optional new parent page title
            
        Returns:
            Dict containing the updated wiki page or error information
        """
        self.logger.info(f"Updating wiki page {page_name} in project: {project_id}")
        
        # Validate required fields
        if project_id is None:
            return self.error_handler.handle_validation_error(
                'Project ID is required',
                field_errors={'project_id': 'Project ID cannot be None'},
                context={}
            )
            
        if page_name is None or not page_name.strip():
            return self.error_handler.handle_validation_error(
                'Page name is required',
                field_errors={'page_name': 'Page name cannot be empty'},
                context={'project_id': project_id}
            )
        
        # Validate field types
        validation_error = self.validate_input(
            {'project_id': project_id, 'page_name': page_name, 'text': text},
            required_fields=['project_id', 'page_name', 'text'],
            field_types={
                'project_id': (str, int),
                'page_name': str,
                'text': str,
                'comments': (str, type(None)),
                'parent_title': (str, type(None))
            }
        )
        
        if validation_error:
            self.logger.error(f"Validation error: {validation_error}")
            return validation_error
        
        # Additional validation for empty text
        if not text.strip():
            return self.error_handler.handle_validation_error(
                'Content cannot be empty',
                field_errors={'text': 'Content cannot be empty'},
                context={'project_id': project_id, 'page_name': page_name}
            )
        
        # Prepare the request data
        page_data = {
            'wiki_page': {
                'text': text
            }
        }
        
        # Add optional fields if provided
        if comments:
            page_data['wiki_page']['comments'] = comments
            
        if parent_title:
            page_data['wiki_page']['parent_title'] = parent_title
            
        endpoint = f"/projects/{project_id}/wiki/{page_name}.json"
        
        try:
            response = self.make_request('PUT', endpoint, data=page_data)
            
            if 'error' in response:
                error_msg = f"Failed to update wiki page: {response.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
            
            # Some Redmine versions return 204 with empty body on success
            if not response:
                return {
                    'success': True,
                    'message': f"Wiki page '{page_name}' updated successfully"
                }
            
            return {
                'success': True,
                'page': response.get('wiki_page', {'title': page_name})
            }
            
        except Exception as e:
            error_msg = f"Error updating wiki page: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return self.error_handler.handle_unexpected_error(error_msg)
    
    def delete_wiki_page(self, project_id: str, page_name: str) -> Dict[str, Any]:
        """
        Delete a wiki page
        
        Args:
            project_id: ID or identifier of the project
            page_name: Name of the wiki page to delete
            
        Returns:
            Dict containing success status or error information
        """
        self.logger.info(f"Deleting wiki page {page_name} from project: {project_id}")
        
        # Validate required fields
        if project_id is None or not str(project_id).strip():
            return self.error_handler.handle_validation_error(
                'Project ID is required',
                field_errors={'project_id': 'Project ID cannot be empty'},
                context={}
            )
            
        if page_name is None or not page_name.strip():
            return self.error_handler.handle_validation_error(
                'Page name is required',
                field_errors={'page_name': 'Page name cannot be empty'},
                context={'project_id': project_id}
            )
        
        # Validate field types
        validation_error = self.validate_input(
            {'project_id': project_id, 'page_name': page_name},
            required_fields=['project_id', 'page_name'],
            field_types={
                'project_id': (str, int),
                'page_name': str
            }
        )
        
        if validation_error:
            self.logger.error(f"Validation error: {validation_error}")
            return validation_error
        
        endpoint = f"/projects/{project_id}/wiki/{page_name}.json"
        
        try:
            response = self.make_request('DELETE', endpoint)
            
            if 'error' in response:
                error_msg = f"Failed to delete wiki page: {response.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
            
            # DELETE operations commonly return empty responses
            return {
                'success': True,
                'message': f"Wiki page '{page_name}' deleted successfully"
            }
            
        except Exception as e:
            error_msg = f"Error deleting wiki page: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return self.error_handler.handle_unexpected_error(error_msg)
