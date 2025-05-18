"""
Redmine API module for Version functionality
Handles all operations related to Redmine project versions
"""
from typing import Dict, List, Optional, Any, Union
from modules.base import RedmineBaseClient


class VersionClient(RedmineBaseClient):
    """Client for Redmine Version API operations"""
    
    def get_versions(self, project_id: Union[int, str]) -> Dict:
        """
        Get versions for a project
        
        Args:
            project_id: The ID or identifier of the project
            
        Returns:
            Dictionary containing versions data
        """
        return self.make_request('GET', f'projects/{project_id}/versions.json')
    
    def get_version(self, version_id: int) -> Dict:
        """
        Get a specific version by ID
        
        Args:
            version_id: The ID of the version to retrieve
            
        Returns:
            Dictionary containing version data
        """
        return self.make_request('GET', f'versions/{version_id}.json')
    
    def create_version(self, version_data: Dict) -> Dict:
        """
        Create a new version
        
        Args:
            version_data: Dictionary containing version data
                         Required: project_id, name
                         Optional: description, status, due_date, sharing
                         
        Returns:
            Dictionary containing the created version data
        """
        # In Redmine API, versions are created through project endpoint
        project_id = version_data.get('project_id')
        if not project_id:
            raise ValueError("project_id is required for creating a version")
        
        return self.make_request('POST', f'projects/{project_id}/versions.json', 
                               data={'version': version_data})
    
    def update_version(self, version_id: int, version_data: Dict) -> Dict:
        """
        Update an existing version
        
        Args:
            version_id: The ID of the version to update
            version_data: Dictionary containing version data to update
                         Can include name, description, status, due_date, sharing
                         
        Returns:
            Empty dictionary on success
        """
        return self.make_request('PUT', f'versions/{version_id}.json', 
                               data={'version': version_data})
    
    def delete_version(self, version_id: int) -> Dict:
        """
        Delete a version
        
        Args:
            version_id: The ID of the version to delete
            
        Returns:
            Empty dictionary on success
        """
        return self.make_request('DELETE', f'versions/{version_id}.json')