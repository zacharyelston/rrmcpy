"""
Redmine API module for Group functionality
Handles all operations related to Redmine user groups
"""
from typing import Dict, List, Optional, Any, Union
from src.base import RedmineBaseClient


class GroupClient(RedmineBaseClient):
    """Client for Redmine Group API operations"""
    
    def get_groups(self, params: Optional[Dict] = None) -> Dict:
        """
        Get a list of groups with optional filtering
        
        Args:
            params: Optional dictionary of query parameters for filtering
                   
        Returns:
            Dictionary containing groups data
        """
        return self.make_request('GET', 'groups.json', params=params)
    
    def get_group(self, group_id: int, include: Optional[List[str]] = None) -> Dict:
        """
        Get a specific group by ID with optional includes
        
        Args:
            group_id: The ID of the group to retrieve
            include: Optional list of associations to include
                    Possible values: users, memberships
                    
        Returns:
            Dictionary containing group data
        """
        params = {}
        if include:
            params['include'] = ','.join(include)
        return self.make_request('GET', f'groups/{group_id}.json', params=params)
    
    def create_group(self, group_data: Dict) -> Dict:
        """
        Create a new group
        
        Args:
            group_data: Dictionary containing group data
                       Required: name
                       Optional: user_ids
                       
        Returns:
            Dictionary containing the created group data
        """
        return self.make_request('POST', 'groups.json', data={'group': group_data})
    
    def update_group(self, group_id: int, group_data: Dict) -> Dict:
        """
        Update an existing group
        
        Args:
            group_id: The ID of the group to update
            group_data: Dictionary containing group data to update
                       Can include name
                       
        Returns:
            Empty dictionary on success
        """
        return self.make_request('PUT', f'groups/{group_id}.json', data={'group': group_data})
    
    def delete_group(self, group_id: int) -> Dict:
        """
        Delete a group
        
        Args:
            group_id: The ID of the group to delete
            
        Returns:
            Empty dictionary on success
        """
        return self.make_request('DELETE', f'groups/{group_id}.json')
    
    def add_user_to_group(self, group_id: int, user_id: int) -> Dict:
        """
        Add a user to a group
        
        Args:
            group_id: The ID of the group
            user_id: The ID of the user to add
            
        Returns:
            Empty dictionary on success
        """
        return self.make_request('POST', f'groups/{group_id}/users.json', 
                               data={'user_id': user_id})
    
    def remove_user_from_group(self, group_id: int, user_id: int) -> Dict:
        """
        Remove a user from a group
        
        Args:
            group_id: The ID of the group
            user_id: The ID of the user to remove
            
        Returns:
            Empty dictionary on success
        """
        return self.make_request('DELETE', f'groups/{group_id}/users/{user_id}.json')