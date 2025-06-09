"""
Redmine API module for Project functionality
Handles all operations related to Redmine projects
"""
from typing import Dict, List, Optional, Any, Union
from src.base import RedmineBaseClient


class ProjectClient(RedmineBaseClient):
    """Client for Redmine Project API operations"""
    
    def get_projects(self, params: Optional[Dict] = None) -> Dict:
        """
        Get a list of projects with optional filtering
        
        Args:
            params: Optional dictionary of query parameters for filtering
                   Can include: status, include, offset, limit
                   
        Returns:
            Dictionary containing projects data
        """
        return self.make_request('GET', 'projects.json', params=params)
    
    def get_project(self, project_id: Union[int, str], include: Optional[List[str]] = None) -> Dict:
        """
        Get a specific project by ID or identifier with optional includes
        
        Args:
            project_id: The ID or identifier of the project to retrieve
            include: Optional list of associations to include
                    Possible values: trackers, issue_categories, enabled_modules, etc.
                    
        Returns:
            Dictionary containing project data
        """
        params = {}
        if include:
            params['include'] = ','.join(include)
        return self.make_request('GET', f'projects/{project_id}.json', params=params)
    
    def create_project(self, project_data: Dict) -> Dict:
        """
        Create a new project
        
        Args:
            project_data: Dictionary containing project data
                         Required: name, identifier
                         Optional: description, homepage, is_public, parent_id,
                                  inherit_members, tracker_ids, issue_custom_field_ids, etc.
                                  
        Returns:
            Dictionary containing the created project data
        """
        return self.make_request('POST', 'projects.json', data={'project': project_data})
    
    def update_project(self, project_id: Union[int, str], project_data: Dict) -> Dict:
        """
        Update an existing project
        
        Args:
            project_id: The ID or identifier of the project to update
            project_data: Dictionary containing project data to update
                         Can include name, description, is_public, etc.
                         
        Returns:
            Empty dictionary on success
        """
        return self.make_request('PUT', f'projects/{project_id}.json', data={'project': project_data})
    
    def delete_project(self, project_id: Union[int, str]) -> Dict:
        """
        Delete a project
        
        Args:
            project_id: The ID or identifier of the project to delete
            
        Returns:
            Empty dictionary on success
        """
        return self.make_request('DELETE', f'projects/{project_id}.json')
    
    def get_project_memberships(self, project_id: Union[int, str]) -> Dict:
        """
        Get a list of memberships for a project
        
        Args:
            project_id: The ID or identifier of the project
            
        Returns:
            Dictionary containing project memberships
        """
        return self.make_request('GET', f'projects/{project_id}/memberships.json')
    
    def add_project_membership(self, project_id: Union[int, str], user_id: int, role_ids: List[int]) -> Dict:
        """
        Add a user to a project with specified roles
        
        Args:
            project_id: The ID or identifier of the project
            user_id: The ID of the user to add
            role_ids: List of role IDs to assign to the user
            
        Returns:
            Dictionary containing the created membership
        """
        membership_data = {
            'user_id': user_id,
            'role_ids': role_ids
        }
        return self.make_request('POST', f'projects/{project_id}/memberships.json', 
                               data={'membership': membership_data})
    
    def update_project_membership(self, membership_id: int, role_ids: List[int]) -> Dict:
        """
        Update a project membership
        
        Args:
            membership_id: The ID of the membership to update
            role_ids: List of role IDs to assign
            
        Returns:
            Empty dictionary on success
        """
        membership_data = {
            'role_ids': role_ids
        }
        return self.make_request('PUT', f'memberships/{membership_id}.json', 
                               data={'membership': membership_data})
    
    def delete_project_membership(self, membership_id: int) -> Dict:
        """
        Delete a project membership
        
        Args:
            membership_id: The ID of the membership to delete
            
        Returns:
            Empty dictionary on success
        """
        return self.make_request('DELETE', f'memberships/{membership_id}.json')
    
    def archive_project(self, project_id: Union[int, str]) -> Dict:
        """
        Archives a project using the dedicated archive endpoint
        
        Args:
            project_id: The ID or identifier of the project to archive
            
        Returns:
            Dictionary containing the archived project data
        """
        return self.make_request('PUT', f'projects/{project_id}/archive.json')
    
    def unarchive_project(self, project_id: Union[int, str]) -> Dict:
        """
        Unarchives a project using the dedicated unarchive endpoint
        
        Args:
            project_id: The ID or identifier of the project to unarchive
            
        Returns:
            Dictionary containing the unarchived project data
        """
        return self.make_request('PUT', f'projects/{project_id}/unarchive.json')
