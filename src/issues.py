"""
Redmine API module for Issue functionality
Handles all operations related to Redmine issues
"""
import requests
from typing import Dict, List, Optional, Any, Union
from src.base import RedmineBaseClient


class IssueClient(RedmineBaseClient):
    """Client for Redmine Issue API operations"""
    
    def get_issues(self, params: Optional[Dict] = None) -> Dict:
        """
        Get a list of issues with optional filtering
        
        Args:
            params: Optional dictionary of query parameters for filtering
                   Can include: project_id, tracker_id, status_id, priority_id,
                   assigned_to_id, author_id, updated_on, etc.
                   
        Returns:
            Dictionary containing issues data
        """
        return self.make_request('GET', 'issues.json', params=params)
    
    def get_issue(self, issue_id: int, include: Optional[List[str]] = None) -> Dict:
        """
        Get a specific issue by ID with optional includes
        
        Args:
            issue_id: The ID of the issue to retrieve
            include: Optional list of associations to include
                    Possible values: children, attachments, relations,
                    changesets, journals, watchers
                    
        Returns:
            Dictionary containing issue data
        """
        params = {}
        if include:
            params['include'] = ','.join(include)
        return self.make_request('GET', f'issues/{issue_id}.json', params=params)
    
    def create_issue(self, issue_data: Dict) -> Dict:
        """
        Create a new issue
        
        Args:
            issue_data: Dictionary containing issue data
                       Required: project_id, subject
                       Optional: tracker_id, status_id, priority_id, description,
                                category_id, fixed_version_id, assigned_to_id,
                                parent_issue_id, custom_fields, etc.
                                
        Returns:
            Dictionary containing the created issue data
        """
        # Validate required fields
        validation_error = self.validate_input(
            issue_data, 
            required_fields=['project_id', 'subject'],
            field_types={
                'project_id': (int, str),
                'subject': str,
                'tracker_id': int,
                'status_id': int,
                'priority_id': int,
                'description': str
            }
        )
        
        if validation_error:
            return validation_error
        
        # Additional validation for issue-specific constraints
        if 'subject' in issue_data and len(issue_data['subject'].strip()) == 0:
            return self._create_error_response(
                "VALIDATION_ERROR",
                "Issue subject cannot be empty",
                400
            )
        
        result = self.make_request('POST', 'issues.json', data={'issue': issue_data})
        self.logger.debug(f"create_issue: result from make_request: {result}")

        # If result contains the full issue, return as is
        if isinstance(result, dict) and 'issue' in result:
            self.logger.debug("create_issue: returning full issue object")
            return result

        # If result contains an ID, fetch the issue by ID
        if isinstance(result, dict) and 'id' in result:
            self.logger.debug(f"create_issue: fetching issue by ID {result['id']}")
            try:
                issue = self.get_issue(result['id'])
                self.logger.debug(f"create_issue: fetched issue: {issue}")
                return issue
            except Exception as e:
                self.logger.error(f"Failed to fetch created issue with ID {result['id']}: {e}")
                return {"error": f"Created issue, but failed to fetch details for ID {result['id']}"}

        # If result is generic success, return a meaningful message
        if isinstance(result, dict) and result.get('success'):
            self.logger.debug("create_issue: returning error, could not retrieve issue details")
            return {"error": "Created issue, but could not retrieve issue details."}

        # Otherwise, return whatever was returned
        self.logger.debug("create_issue: returning fallback result")
        return result
    
    def update_issue(self, issue_id: int, issue_data: Dict) -> Dict:
        """
        Update an existing issue
        
        Args:
            issue_id: The ID of the issue to update
            issue_data: Dictionary containing issue data to update
                       Can include any issue attributes including notes for adding comments
                       
        Returns:
            Empty dictionary on success
        """
        return self.make_request('PUT', f'issues/{issue_id}.json', data={'issue': issue_data})
    
    def delete_issue(self, issue_id: int) -> Dict:
        """
        Delete an issue
        
        Args:
            issue_id: The ID of the issue to delete
            
        Returns:
            Empty dictionary on success
        """
        return self.make_request('DELETE', f'issues/{issue_id}.json')
    
    def add_attachment(self, issue_id: int, file_path: str, description: Optional[str] = None) -> Dict:
        """
        Add an attachment to an issue
        
        Args:
            issue_id: The ID of the issue to add attachment to
            file_path: Path to the file to upload
            description: Optional description for the attachment
            
        Returns:
            Dictionary containing attachment information
        """
        # First upload the file to get a token
        files = {'file': open(file_path, 'rb')}
        headers = self.headers.copy()
        # Remove Content-Type for multipart/form-data
        if 'Content-Type' in headers:
            del headers['Content-Type']
            
        url = f"{self.base_url}/uploads.json"
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        upload_data = response.json()
        
        # Now attach the uploaded file to the issue
        attachment_data = {
            'uploads': [{
                'token': upload_data['upload']['token'],
                'filename': upload_data['upload']['filename'],
                'description': description or ''
            }]
        }
        
        return self.update_issue(issue_id, attachment_data)