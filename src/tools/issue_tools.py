"""
Issue management tools for Redmine MCP Server
"""
from typing import Dict, Any


class CreateIssueTool:
    """Tool for creating Redmine issues"""
    
    def __init__(self, service):
        self.service = service
        
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute issue creation"""
        return self.service.create_issue(arguments)


class GetIssueTool:
    """Tool for retrieving Redmine issues"""
    
    def __init__(self, service):
        self.service = service
        
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute issue retrieval"""
        issue_id = arguments.get('issue_id')
        include = arguments.get('include', [])
        return self.service.get_issue(issue_id, include)


class ListIssuesTool:
    """Tool for listing Redmine issues"""
    
    def __init__(self, service):
        self.service = service
        
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute issue listing"""
        params = arguments.get('params', {})
        return self.service.get_issues(params)


class UpdateIssueTool:
    """Tool for updating Redmine issues"""
    
    def __init__(self, service):
        self.service = service
        
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute issue update"""
        issue_id = arguments.get('issue_id')
        issue_data = arguments.get('issue_data', {})
        return self.service.update_issue(issue_id, issue_data)


class DeleteIssueTool:
    """Tool for deleting Redmine issues"""
    
    def __init__(self, service):
        self.service = service
        
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute issue deletion"""
        issue_id = arguments.get('issue_id')
        return self.service.delete_issue(issue_id)