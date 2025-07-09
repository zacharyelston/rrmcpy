"""
Enhanced error handling for MCP tools

This module provides better error messages for parameter validation failures
by intercepting and improving the default Pydantic error messages.
"""
import inspect
import json
from typing import Callable, Dict, Any, List, Optional
from functools import wraps


class ParameterHelper:
    """Helper class to provide better parameter documentation"""
    
    @staticmethod
    def get_function_params(func: Callable) -> Dict[str, Any]:
        """Extract parameter information from a function"""
        sig = inspect.signature(func)
        params = {}
        
        for name, param in sig.parameters.items():
            if name in ['self', 'cls']:
                continue
                
            param_info = {
                'required': param.default == inspect.Parameter.empty,
                'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'any',
                'default': param.default if param.default != inspect.Parameter.empty else None
            }
            
            # Extract description from docstring if available
            if func.__doc__:
                # Simple extraction - look for "param_name:" in docstring
                import re
                pattern = rf'{name}:\s*(.+?)(?:\n|$)'
                match = re.search(pattern, func.__doc__, re.MULTILINE)
                if match:
                    param_info['description'] = match.group(1).strip()
            
            params[name] = param_info
            
        return params
    
    @staticmethod
    def format_param_list(params: Dict[str, Any]) -> str:
        """Format parameters into a readable list"""
        lines = []
        
        # Required parameters first
        for name, info in params.items():
            if info['required']:
                desc = info.get('description', f"{info['type']} parameter")
                lines.append(f"  - {name} (required): {desc}")
        
        # Optional parameters
        for name, info in params.items():
            if not info['required']:
                desc = info.get('description', f"{info['type']} parameter")
                default = f" (default: {info['default']})" if info['default'] is not None else ""
                lines.append(f"  - {name} (optional): {desc}{default}")
                
        return '\n'.join(lines)
    
    @staticmethod
    def generate_example(func_name: str, params: Dict[str, Any]) -> str:
        """Generate an example usage"""
        required_params = []
        optional_params = []
        
        for name, info in params.items():
            if info['required']:
                if 'str' in str(info['type']):
                    required_params.append(f'{name}="example"')
                elif 'int' in str(info['type']):
                    required_params.append(f'{name}=123')
                elif 'bool' in str(info['type']):
                    required_params.append(f'{name}=True')
                else:
                    required_params.append(f'{name}=value')
            else:
                # Show one optional parameter as example
                if len(optional_params) < 2:
                    if 'str' in str(info['type']):
                        optional_params.append(f'{name}="optional"')
                    elif 'int' in str(info['type']):
                        optional_params.append(f'{name}=1')
        
        all_params = required_params + optional_params
        return f"{func_name}({', '.join(all_params)})"


def enhanced_error_wrapper(tool_name: str, func: Callable) -> Callable:
    """Wrapper to provide enhanced error messages for MCP tools"""
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Try to call the original function
            return await func(*args, **kwargs)
        except Exception as e:
            error_str = str(e)
            
            # Check if this is a Pydantic validation error
            if "validation error" in error_str and "Unexpected keyword argument" in error_str:
                # Extract the invalid parameter name
                import re
                param_match = re.search(r'(\w+)\s*\n\s*Unexpected keyword argument', error_str)
                invalid_param = param_match.group(1) if param_match else "unknown"
                
                # Get function parameters
                params = ParameterHelper.get_function_params(func)
                param_list = ParameterHelper.format_param_list(params)
                example = ParameterHelper.generate_example(tool_name, params)
                
                # Build enhanced error message
                error_response = {
                    "error": f"Invalid parameter '{invalid_param}' for {tool_name}",
                    "message": f"The parameter '{invalid_param}' is not accepted by this tool.",
                    "accepted_parameters": param_list,
                    "example_usage": example,
                    "note": f"'{invalid_param}' might be a valid Redmine field, but it's not yet supported by this MCP tool.",
                    "success": False
                }
                
                return json.dumps(error_response, indent=2)
            
            # For other errors, return the original error
            return json.dumps({"error": str(e), "success": False}, indent=2)
    
    return wrapper


def apply_enhanced_errors(tool_registrations):
    """Apply enhanced error handling to all registered tools
    
    This function should be called after all tools are registered to wrap them
    with better error handling.
    """
    # This would need to be implemented based on how FastMCP stores registered tools
    # For now, we'll document the approach
    pass
