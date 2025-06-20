"""
Simple template tool using Redmine issues as templates
"""
import re
from typing import Dict, Any, Optional


class SimpleTemplateTool:
    """Tool for creating issues from Redmine template issues"""
    
    TEMPLATE_PROJECT_ID = 47  # Templates project
    
    def __init__(self, service):
        self.service = service
        
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create issue from template"""
        template_id = arguments.get('template_id')
        target_project = arguments.get('target_project', 'rrmcpy')
        replacements = arguments.get('replacements', {})
        
        if not template_id:
            return {"error": "template_id is required", "success": False}
        
        try:
            # Get template issue
            template_result = self.service.get_issue(template_id)
            if 'error' in template_result:
                return {"error": f"Failed to get template: {template_result['error']}", "success": False}
            
            template = template_result['issue']
            
            # Extract subject without "Template: Type - " prefix
            subject = template['subject']
            match = re.match(r'Template:\s*\w+\s*-\s*(.+)', subject)
            if match:
                subject = match.group(1)
            
            # Replace placeholders in subject and description
            description = template['description']
            
            for placeholder, value in replacements.items():
                placeholder_pattern = f'\\[{placeholder}\\]'
                subject = re.sub(placeholder_pattern, str(value), subject)
                description = re.sub(placeholder_pattern, str(value), description)
            
            # Create new issue
            issue_data = {
                'project_id': target_project,
                'subject': subject,
                'description': description,
                'tracker_id': arguments.get('tracker_id', template['tracker']['id']),
                'priority_id': arguments.get('priority_id', template['priority']['id'])
            }
            
            # Add optional fields
            if 'assigned_to_id' in arguments:
                issue_data['assigned_to_id'] = arguments['assigned_to_id']
            if 'parent_issue_id' in arguments:
                issue_data['parent_issue_id'] = arguments['parent_issue_id']
            
            result = self.service.create_issue(issue_data)
            
            if 'issue' in result:
                result['template_used'] = template_id
                result['replacements_applied'] = replacements
                
            return result
            
        except Exception as e:
            return {"error": str(e), "success": False}
