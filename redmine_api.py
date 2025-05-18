"""
Redmine API client for interacting with the Redmine instance
Handles API calls to Redmine for issues, projects, versions, users, and groups
"""
import requests
import logging
import json
from typing import Dict, List, Optional, Any, Union

class RedmineAPI:
    """
    Client for interacting with the Redmine API
    """
    def __init__(self, base_url: str, api_key: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the Redmine API client
        
        Args:
            base_url: The base URL of the Redmine instance
            api_key: The API key for authentication
            logger: Optional logger instance for logging
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.logger = logger or logging.getLogger(__name__)
        
        # Common headers for all requests
        self.headers = {
            'X-Redmine-API-Key': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Redmine API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint to call
            data: Optional data to send in the request body
            params: Optional query parameters
            
        Returns:
            Dictionary containing the API response
        """
        url = f"{self.base_url}/{endpoint}"
        self.logger.debug(f"Making {method} request to {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, params=params)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, params=params)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making request to Redmine API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status code: {e.response.status_code}")
                self.logger.error(f"Response body: {e.response.text}")
            raise
    
    # ===== Issues API =====
    def get_issues(self, params: Optional[Dict] = None) -> Dict:
        """Get a list of issues with optional filtering"""
        return self._make_request('GET', 'issues.json', params=params)
    
    def get_issue(self, issue_id: int, include: Optional[List[str]] = None) -> Dict:
        """Get a specific issue by ID with optional includes"""
        params = {}
        if include:
            params['include'] = ','.join(include)
        return self._make_request('GET', f'issues/{issue_id}.json', params=params)
    
    def create_issue(self, issue_data: Dict) -> Dict:
        """Create a new issue"""
        return self._make_request('POST', 'issues.json', data={'issue': issue_data})
    
    def update_issue(self, issue_id: int, issue_data: Dict) -> Dict:
        """Update an existing issue"""
        return self._make_request('PUT', f'issues/{issue_id}.json', data={'issue': issue_data})
    
    def delete_issue(self, issue_id: int) -> Dict:
        """Delete an issue"""
        return self._make_request('DELETE', f'issues/{issue_id}.json')
    
    # ===== Projects API =====
    def get_projects(self, params: Optional[Dict] = None) -> Dict:
        """Get a list of projects with optional filtering"""
        return self._make_request('GET', 'projects.json', params=params)
    
    def get_project(self, project_id: Union[int, str], include: Optional[List[str]] = None) -> Dict:
        """Get a specific project by ID with optional includes"""
        params = {}
        if include:
            params['include'] = ','.join(include)
        return self._make_request('GET', f'projects/{project_id}.json', params=params)
    
    def create_project(self, project_data: Dict) -> Dict:
        """Create a new project"""
        return self._make_request('POST', 'projects.json', data={'project': project_data})
    
    def update_project(self, project_id: Union[int, str], project_data: Dict) -> Dict:
        """Update an existing project"""
        return self._make_request('PUT', f'projects/{project_id}.json', data={'project': project_data})
    
    def delete_project(self, project_id: Union[int, str]) -> Dict:
        """Delete a project"""
        return self._make_request('DELETE', f'projects/{project_id}.json')
    
    # ===== Versions API =====
    def get_versions(self, project_id: Union[int, str]) -> Dict:
        """Get versions for a project"""
        return self._make_request('GET', f'projects/{project_id}/versions.json')
    
    def get_version(self, version_id: int) -> Dict:
        """Get a specific version by ID"""
        return self._make_request('GET', f'versions/{version_id}.json')
    
    def create_version(self, version_data: Dict) -> Dict:
        """Create a new version"""
        # In Redmine API, versions are created through project endpoint
        project_id = version_data.get('project_id')
        if not project_id:
            raise ValueError("project_id is required for creating a version")
        
        return self._make_request('POST', f'projects/{project_id}/versions.json', 
                                data={'version': version_data})
    
    def update_version(self, version_id: int, version_data: Dict) -> Dict:
        """Update an existing version"""
        return self._make_request('PUT', f'versions/{version_id}.json', data={'version': version_data})
    
    def delete_version(self, version_id: int) -> Dict:
        """Delete a version"""
        return self._make_request('DELETE', f'versions/{version_id}.json')
    
    # ===== Users API =====
    def get_users(self, params: Optional[Dict] = None) -> Dict:
        """Get a list of users with optional filtering"""
        return self._make_request('GET', 'users.json', params=params)
    
    def get_user(self, user_id: int, include: Optional[List[str]] = None) -> Dict:
        """Get a specific user by ID with optional includes"""
        params = {}
        if include:
            params['include'] = ','.join(include)
        return self._make_request('GET', f'users/{user_id}.json', params=params)
    
    def create_user(self, user_data: Dict) -> Dict:
        """Create a new user"""
        return self._make_request('POST', 'users.json', data={'user': user_data})
    
    def update_user(self, user_id: int, user_data: Dict) -> Dict:
        """Update an existing user"""
        return self._make_request('PUT', f'users/{user_id}.json', data={'user': user_data})
    
    def delete_user(self, user_id: int) -> Dict:
        """Delete a user"""
        return self._make_request('DELETE', f'users/{user_id}.json')
    
    def get_current_user(self) -> Dict:
        """Get the current user (based on API key)"""
        return self._make_request('GET', 'users/current.json')
    
    # ===== Groups API =====
    def get_groups(self, params: Optional[Dict] = None) -> Dict:
        """Get a list of groups with optional filtering"""
        return self._make_request('GET', 'groups.json', params=params)
    
    def get_group(self, group_id: int, include: Optional[List[str]] = None) -> Dict:
        """Get a specific group by ID with optional includes"""
        params = {}
        if include:
            params['include'] = ','.join(include)
        return self._make_request('GET', f'groups/{group_id}.json', params=params)
    
    def create_group(self, group_data: Dict) -> Dict:
        """Create a new group"""
        return self._make_request('POST', 'groups.json', data={'group': group_data})
    
    def update_group(self, group_id: int, group_data: Dict) -> Dict:
        """Update an existing group"""
        return self._make_request('PUT', f'groups/{group_id}.json', data={'group': group_data})
    
    def delete_group(self, group_id: int) -> Dict:
        """Delete a group"""
        return self._make_request('DELETE', f'groups/{group_id}.json')
    
    def add_user_to_group(self, group_id: int, user_id: int) -> Dict:
        """Add a user to a group"""
        return self._make_request('POST', f'groups/{group_id}/users.json', 
                                data={'user_id': user_id})
    
    def remove_user_from_group(self, group_id: int, user_id: int) -> Dict:
        """Remove a user from a group"""
        return self._make_request('DELETE', f'groups/{group_id}/users/{user_id}.json')
