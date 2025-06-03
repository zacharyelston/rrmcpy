"""
Issue management tools for Redmine MCP Server
"""
from typing import Dict, Any, List, Optional
from .base_tool import BaseTool


class CreateIssueTool(BaseTool):
    """Tool for creating new issues in Redmine"""
    
    def name(self) -> str:
        return "redmine-create-issue"
    
    def description(self) -> str:
        return "Create a new issue in a Redmine project"
    
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "ID or identifier of the project"
                },
                "subject": {
                    "type": "string",
                    "description": "Issue subject/title"
                },
                "description": {
                    "type": "string",
                    "description": "Issue description (optional)"
                },
                "tracker_id": {
                    "type": "integer",
                    "description": "Tracker ID (optional)"
                },
                "status_id": {
                    "type": "integer", 
                    "description": "Status ID (optional)"
                },
                "priority_id": {
                    "type": "integer",
                    "description": "Priority ID (optional)"
                },
                "assigned_to_id": {
                    "type": "integer",
                    "description": "User ID to assign the issue to (optional)"
                }
            },
            "required": ["project_id", "subject"]
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        return self.service.create_issue(kwargs)


class GetIssueTool(BaseTool):
    """Tool for retrieving a specific issue by ID"""
    
    def name(self) -> str:
        return "redmine-get-issue"
    
    def description(self) -> str:
        return "Get detailed information about a specific issue"
    
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "issue_id": {
                    "type": "integer",
                    "description": "ID of the issue to retrieve"
                },
                "include": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Additional data to include (children, attachments, relations, changesets, journals, watchers)"
                }
            },
            "required": ["issue_id"]
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        issue_id = kwargs.get("issue_id")
        include = kwargs.get("include")
        return self.service.get_issue(issue_id, include)


class ListIssuesTool(BaseTool):
    """Tool for listing issues with optional filtering"""
    
    def name(self) -> str:
        return "redmine-list-issues"
    
    def description(self) -> str:
        return "List issues with optional filtering and pagination"
    
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Filter by project ID"
                },
                "status_id": {
                    "type": "integer",
                    "description": "Filter by status ID"
                },
                "assigned_to_id": {
                    "type": "integer",
                    "description": "Filter by assigned user ID"
                },
                "tracker_id": {
                    "type": "integer",
                    "description": "Filter by tracker ID"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of issues to return (1-100, default: 25)"
                },
                "offset": {
                    "type": "integer",
                    "description": "Number of issues to skip (for pagination)"
                }
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        return self.service.list_issues(kwargs)


class UpdateIssueTool(BaseTool):
    """Tool for updating existing issues"""
    
    def name(self) -> str:
        return "redmine-update-issue"
    
    def description(self) -> str:
        return "Update an existing issue with new information"
    
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "issue_id": {
                    "type": "integer",
                    "description": "ID of the issue to update"
                },
                "subject": {
                    "type": "string",
                    "description": "New issue subject"
                },
                "description": {
                    "type": "string",
                    "description": "New issue description"
                },
                "status_id": {
                    "type": "integer",
                    "description": "New status ID"
                },
                "priority_id": {
                    "type": "integer",
                    "description": "New priority ID"
                },
                "assigned_to_id": {
                    "type": "integer",
                    "description": "New assigned user ID"
                },
                "notes": {
                    "type": "string",
                    "description": "Notes to add to the issue update"
                }
            },
            "required": ["issue_id"]
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        issue_id = kwargs.pop("issue_id")
        return self.service.update_issue(issue_id, kwargs)


class DeleteIssueTool(BaseTool):
    """Tool for deleting issues"""
    
    def name(self) -> str:
        return "redmine-delete-issue"
    
    def description(self) -> str:
        return "Delete an issue from Redmine"
    
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "issue_id": {
                    "type": "integer",
                    "description": "ID of the issue to delete"
                }
            },
            "required": ["issue_id"]
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        issue_id = kwargs.get("issue_id")
        return self.service.delete_issue(issue_id)