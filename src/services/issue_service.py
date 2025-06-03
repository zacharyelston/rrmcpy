"""
Issue service for business logic and validation
"""
from typing import Dict, Any, Optional, List
from .base_service import BaseService
from src.core.errors import ValidationError, RedmineAPIError


class IssueService(BaseService):
    """Service for issue-related business logic"""
    
    def __init__(self, config, issue_client, logger=None):
        super().__init__(config, logger)
        self.issue_client = issue_client
    
    def create_issue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new issue with validation"""
        try:
            # Validate required fields
            self.validate_required_fields(data, ['project_id', 'subject'])
            
            # Validate field types
            self.validate_field_type(data, 'tracker_id', int)
            self.validate_field_type(data, 'status_id', int)
            self.validate_field_type(data, 'priority_id', int)
            self.validate_field_type(data, 'assigned_to_id', int)
            
            # Business validation
            if len(data['subject'].strip()) < 3:
                raise ValidationError("Subject must be at least 3 characters long", field="subject")
            
            # Clean and prepare data
            clean_data = {
                'project_id': data['project_id'],
                'subject': data['subject'].strip(),
                'description': data.get('description', '').strip()
            }
            
            # Add optional fields
            for field in ['tracker_id', 'status_id', 'priority_id', 'assigned_to_id']:
                if field in data and data[field] is not None:
                    clean_data[field] = data[field]
            
            # Call API client
            result = self.issue_client.create_issue(clean_data)
            
            if result.get('error'):
                raise RedmineAPIError(result.get('message', 'Unknown API error'))
            
            return self.format_success_response(result.get('issue', {}))
            
        except Exception as e:
            return self.handle_service_error(e, "create_issue")
    
    def get_issue(self, issue_id: int, include: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get issue by ID with optional includes"""
        try:
            if not isinstance(issue_id, int) or issue_id <= 0:
                raise ValidationError("Issue ID must be a positive integer", field="issue_id")
            
            result = self.issue_client.get_issue(issue_id, include)
            
            if result.get('error'):
                raise RedmineAPIError(result.get('message', 'Unknown API error'))
            
            return self.format_success_response(result.get('issue', {}))
            
        except Exception as e:
            return self.handle_service_error(e, "get_issue")
    
    def list_issues(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List issues with optional filtering"""
        try:
            clean_filters = {}
            
            if filters:
                # Validate and clean filters
                if 'limit' in filters:
                    limit = filters['limit']
                    if isinstance(limit, str) and limit.isdigit():
                        limit = int(limit)
                    if not isinstance(limit, int) or limit <= 0 or limit > 100:
                        raise ValidationError("Limit must be between 1 and 100", field="limit")
                    clean_filters['limit'] = limit
                
                # Pass through other valid filters
                for field in ['project_id', 'status_id', 'assigned_to_id', 'tracker_id']:
                    if field in filters and filters[field] is not None:
                        clean_filters[field] = filters[field]
            
            result = self.issue_client.get_issues(clean_filters)
            
            if result.get('error'):
                raise RedmineAPIError(result.get('message', 'Unknown API error'))
            
            return self.format_success_response(result.get('issues', []))
            
        except Exception as e:
            return self.handle_service_error(e, "list_issues")
    
    def update_issue(self, issue_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing issue"""
        try:
            if not isinstance(issue_id, int) or issue_id <= 0:
                raise ValidationError("Issue ID must be a positive integer", field="issue_id")
            
            # Validate field types for update data
            self.validate_field_type(data, 'status_id', int)
            self.validate_field_type(data, 'priority_id', int)
            self.validate_field_type(data, 'assigned_to_id', int)
            
            # Business validation
            if 'subject' in data and len(data['subject'].strip()) < 3:
                raise ValidationError("Subject must be at least 3 characters long", field="subject")
            
            # Clean update data
            clean_data = {}
            for field in ['subject', 'description', 'status_id', 'priority_id', 'assigned_to_id', 'notes']:
                if field in data and data[field] is not None:
                    if field in ['subject', 'description', 'notes']:
                        clean_data[field] = str(data[field]).strip()
                    else:
                        clean_data[field] = data[field]
            
            if not clean_data:
                raise ValidationError("No valid update fields provided")
            
            result = self.issue_client.update_issue(issue_id, clean_data)
            
            if result.get('error'):
                raise RedmineAPIError(result.get('message', 'Unknown API error'))
            
            return self.format_success_response({"issue_id": issue_id, "updated": True})
            
        except Exception as e:
            return self.handle_service_error(e, "update_issue")
    
    def delete_issue(self, issue_id: int) -> Dict[str, Any]:
        """Delete an issue"""
        try:
            if not isinstance(issue_id, int) or issue_id <= 0:
                raise ValidationError("Issue ID must be a positive integer", field="issue_id")
            
            result = self.issue_client.delete_issue(issue_id)
            
            if result.get('error'):
                raise RedmineAPIError(result.get('message', 'Unknown API error'))
            
            return self.format_success_response({"issue_id": issue_id, "deleted": True})
            
        except Exception as e:
            return self.handle_service_error(e, "delete_issue")