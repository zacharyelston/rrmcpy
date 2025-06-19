"""
Redmine API module for User functionality
Handles all operations related to Redmine users
"""
from typing import Dict, List, Optional, Any, Union
from src.base import RedmineBaseClient


class UserClient(RedmineBaseClient):
    """Client for Redmine User API operations"""
    
    def get_users(self, params: Optional[Dict] = None) -> Dict:
        """
        Get a list of users with optional filtering
        
        Args:
            params: Optional dictionary of query parameters for filtering
                   Can include: status, name, group_id, offset, limit
                   
        Returns:
            Dictionary containing users data
        """
        return self.make_request('GET', 'users.json', params=params)
    
    def get_user(self, user_id: int, include: Optional[List[str]] = None) -> Dict:
        """
        Get a specific user by ID with optional includes
        
        Args:
            user_id: The ID of the user to retrieve
            include: Optional list of associations to include
                    Possible values: memberships, groups
                    
        Returns:
            Dictionary containing user data
        """
        params = {}
        if include:
            params['include'] = ','.join(include)
        return self.make_request('GET', f'users/{user_id}.json', params=params)
    
    def create_user(self, user_data: Dict) -> Dict:
        """
        Create a new user
        
        Args:
            user_data: Dictionary containing user data
                      Required: login, firstname, lastname, mail, password
                      Optional: auth_source_id, mail_notification, 
                               must_change_passwd, generate_password, etc.
                      
        Returns:
            Dictionary containing the created user data
        """
        return self.make_request('POST', 'users.json', data={'user': user_data})
    
    def update_user(self, user_id: int, user_data: Dict) -> Dict:
        """
        Update an existing user
        
        Args:
            user_id: The ID of the user to update
            user_data: Dictionary containing user data to update
                      Can include firstname, lastname, mail, admin, etc.
                      
        Returns:
            Empty dictionary on success
        """
        return self.make_request('PUT', f'users/{user_id}.json', data={'user': user_data})
    
    def delete_user(self, user_id: int) -> Dict:
        """
        Delete a user
        
        Args:
            user_id: The ID of the user to delete
            
        Returns:
            Empty dictionary on success
        """
        return self.make_request('DELETE', f'users/{user_id}.json')
    
    def get_current_user(self) -> Dict:
        """
        Get the current user (based on API key)
        
        Returns:
            Dictionary containing current user data
        """
        return self.make_request('GET', 'users/current.json')
