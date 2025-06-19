"""
Redmine API module for Roadmap functionality
Handles operations related to versions, roadmaps, and feature planning
"""
from typing import Dict, List, Optional, Any, Union
from src.base import RedmineBaseClient


class RoadmapClient(RedmineBaseClient):
    """Client for Redmine Roadmap API operations"""
    
    def get_roadmap(self, project_id: Union[int, str]) -> Dict:
        """
        Get the roadmap for a project (equivalent to all versions)
        
        Args:
            project_id: The ID or identifier of the project
            
        Returns:
            Dictionary containing roadmap data (versions)
        """
        return self.get_versions(project_id)
    
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
    
    def tag_issue_with_version(self, issue_id: int, version_id: int) -> Dict:
        """
        Tag an issue with a version (fixed_version_id)
        
        Args:
            issue_id: The ID of the issue to tag
            version_id: The ID of the version to tag the issue with
            
        Returns:
            Empty dictionary on success
        """
        issue_data = {
            "fixed_version_id": version_id
        }
        return self.make_request('PUT', f'issues/{issue_id}.json', 
                               data={'issue': issue_data})
    
    def get_issues_by_version(self, version_id: int) -> Dict:
        """
        Get all issues for a specific version
        
        Args:
            version_id: The ID of the version
            
        Returns:
            Dictionary containing issues data
        """
        return self.make_request('GET', 'issues.json', 
                               params={'fixed_version_id': version_id})
    
    def create_roadmap_version(self, project_id: Union[int, str], name: str, 
                             description: str = None, status: str = "open",
                             due_date: str = None, sharing: str = "none") -> Dict:
        """
        Convenience method to create a roadmap version
        
        Args:
            project_id: The ID or identifier of the project
            name: Name of the version (e.g., "v1.0", "Sprint 5")
            description: Optional description
            status: Status (open, locked, closed)
            due_date: Optional due date in YYYY-MM-DD format
            sharing: Sharing option (none, descendants, hierarchy, tree, system)
            
        Returns:
            Dictionary containing the created version data
        """
        version_data = {
            "project_id": project_id,
            "name": name,
            "status": status,
            "sharing": sharing
        }
        
        if description:
            version_data["description"] = description
            
        if due_date:
            version_data["due_date"] = due_date
            
        return self.create_version(version_data)
    
    def create_feature_roadmap(self, project_id: Union[int, str], versions: List[Dict]) -> List[Dict]:
        """
        Create multiple versions for a feature roadmap
        
        Args:
            project_id: The ID or identifier of the project
            versions: List of version data dictionaries, each containing:
                     - name: Name of the version
                     - description: Optional description
                     - status: Optional status (default: open)
                     - due_date: Optional due date
                     
        Returns:
            List of created versions data
        """
        results = []
        for version_data in versions:
            version_data["project_id"] = project_id
            result = self.create_version(version_data)
            results.append(result)
            
        return results
