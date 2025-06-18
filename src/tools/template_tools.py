"""
Template management tools for Redmine MCP Server
Provides issue creation from predefined templates
"""
import json
import os
from pathlib import Path
from string import Template
from typing import Dict, Any, Optional, List
import logging


class TemplateManager:
    """Manages issue templates for consistent issue creation"""
    
    def __init__(self, template_dir: Optional[str] = None):
        """Initialize template manager with template directory"""
        if template_dir is None:
            # Default to src/templates/issues relative to this file
            template_dir = Path(__file__).parent.parent / "templates" / "issues"
        self.template_dir = Path(template_dir)
        self.logger = logging.getLogger("redmine_mcp_server.template_manager")
        
    def list_templates(self) -> List[str]:
        """List available template names"""
        if not self.template_dir.exists():
            return []
        return [f.stem for f in self.template_dir.glob("*.json")]
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load a template by name"""
        template_path = self.template_dir / f"{template_name}.json"
        if not template_path.exists():
            raise ValueError(f"Template '{template_name}' not found")
            
        with open(template_path, 'r') as f:
            return json.load(f)
    
    def render_template(self, template_name: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Render a template with provided variables"""
        template_data = self.load_template(template_name)
        
        # Process string fields with template substitution
        rendered = {}
        for key, value in template_data.items():
            if isinstance(value, str):
                # Use safe_substitute to avoid KeyError on missing variables
                template = Template(value)
                rendered[key] = template.safe_substitute(variables)
            elif isinstance(value, dict):
                # Recursively process nested dictionaries
                rendered[key] = self._render_dict(value, variables)
            else:
                # Keep non-string values as-is
                rendered[key] = value
                
        return rendered
    
    def _render_dict(self, data: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively render dictionary values"""
        rendered = {}
        for key, value in data.items():
            if isinstance(value, str):
                template = Template(value)
                rendered[key] = template.safe_substitute(variables)
            elif isinstance(value, dict):
                rendered[key] = self._render_dict(value, variables)
            else:
                rendered[key] = value
        return rendered
    
    def validate_required_fields(self, template_name: str, variables: Dict[str, Any]) -> Optional[str]:
        """Validate that required variables are provided"""
        template_data = self.load_template(template_name)
        
        # Check for required_fields in template metadata
        required = template_data.get('_metadata', {}).get('required_variables', [])
        missing = [field for field in required if field not in variables]
        
        if missing:
            return f"Missing required fields: {', '.join(missing)}"
        return None


class CreateFromTemplateTool:
    """Tool for creating issues from templates"""
    
    def __init__(self, service, template_manager: Optional[TemplateManager] = None):
        self.service = service
        self.template_manager = template_manager or TemplateManager()
        self.logger = logging.getLogger("redmine_mcp_server.create_from_template_tool")
        
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute issue creation from template"""
        template_type = arguments.get('template_type')
        variables = arguments.get('variables', {})
        
        # Validate template exists
        available = self.template_manager.list_templates()
        if template_type not in available:
            return {
                "error": f"Template '{template_type}' not found. Available: {', '.join(available)}",
                "success": False
            }
        
        # Validate required fields
        validation_error = self.template_manager.validate_required_fields(template_type, variables)
        if validation_error:
            return {"error": validation_error, "success": False}
        
        try:
            # Render template with variables
            issue_data = self.template_manager.render_template(template_type, variables)
            
            # Remove metadata before creating issue
            if '_metadata' in issue_data:
                del issue_data['_metadata']
            
            # Create the issue
            result = self.service.create_issue(issue_data)
            
            # Add template info to successful result
            if isinstance(result, dict) and 'issue' in result:
                result['template_used'] = template_type
                result['variables_applied'] = variables
                
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create issue from template: {e}")
            return {"error": str(e), "success": False}


class CreateSubtasksTool:
    """Tool for creating standard subtasks for an issue"""
    
    def __init__(self, service, template_manager: Optional[TemplateManager] = None):
        self.service = service
        self.template_manager = template_manager or TemplateManager()
        self.logger = logging.getLogger("redmine_mcp_server.create_subtasks_tool")
        
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create subtasks for a parent issue"""
        parent_issue_id = arguments.get('parent_issue_id')
        subtask_template = arguments.get('subtask_template', 'default_subtasks')
        
        if not parent_issue_id:
            return {"error": "parent_issue_id is required", "success": False}
        
        try:
            # Get parent issue details
            parent = self.service.get_issue(parent_issue_id)
            if 'error' in parent:
                return {"error": f"Failed to get parent issue: {parent['error']}", "success": False}
            
            parent_data = parent['issue']
            
            # Load subtask template
            subtasks_config = self.template_manager.load_template(subtask_template)
            subtasks = subtasks_config.get('subtasks', [])
            
            created_subtasks = []
            
            for subtask_template in subtasks:
                # Prepare subtask data
                subtask_data = {
                    'project_id': parent_data['project']['id'],
                    'parent_issue_id': parent_issue_id,
                    'tracker_id': subtask_template.get('tracker_id', 3),  # Default to Support
                    'subject': f"{parent_data['subject']} - {subtask_template['subject']}",
                    'description': subtask_template.get('description', ''),
                    'assigned_to_id': subtask_template.get('assigned_to_id'),
                    'priority_id': parent_data['priority']['id']
                }
                
                # Create subtask
                result = self.service.create_issue(subtask_data)
                if 'issue' in result:
                    created_subtasks.append(result['issue'])
                else:
                    self.logger.warning(f"Failed to create subtask: {result}")
            
            return {
                "success": True,
                "parent_issue_id": parent_issue_id,
                "subtasks_created": len(created_subtasks),
                "subtasks": created_subtasks
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create subtasks: {e}")
            return {"error": str(e), "success": False}