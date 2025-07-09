#!/usr/bin/env python3
"""
Generate comprehensive parameter documentation for all MCP tools

This script extracts parameter information from all registered tools and
generates markdown documentation to help users understand what parameters
are accepted by each tool.
"""
import sys
import os
import inspect
import re
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.tool_registrations import ToolRegistrations
from src.core import AppConfig
from src.core.client_manager import ClientManager
from fastmcp import FastMCP


def extract_parameters_from_docstring(docstring: str) -> Dict[str, str]:
    """Extract parameter descriptions from docstring"""
    params = {}
    if not docstring:
        return params
    
    # Look for ACCEPTED PARAMETERS section
    param_section = re.search(r'ACCEPTED PARAMETERS:(.*?)(?:EXAMPLE|NOTE|$)', docstring, re.DOTALL)
    if param_section:
        param_text = param_section.group(1)
        # Parse bullet points
        param_lines = re.findall(r'[•\-]\s*(\w+)(?:\s*\(([^)]+)\))?\s*:\s*(.+)', param_text)
        for name, required, desc in param_lines:
            params[name] = {
                'required': 'required' in (required or ''),
                'description': desc.strip()
            }
    
    return params


def generate_tool_documentation():
    """Generate documentation for all MCP tools"""
    # Initialize components
    config = AppConfig.from_environment()
    logger = None
    mcp = FastMCP("Documentation Generator")
    client_manager = ClientManager(config, logger)
    client_manager.initialize_clients()
    
    # Register tools
    tool_registrations = ToolRegistrations(mcp, client_manager, logger)
    registered_tools = tool_registrations.register_all_tools()
    
    print("# Redmine MCP Tools Parameter Reference\n")
    print(f"Total tools available: {len(registered_tools)}\n")
    
    # Group tools by category
    categories = {}
    for tool_name in sorted(registered_tools):
        category = tool_name.split('-')[1] if '-' in tool_name else 'other'
        if category not in categories:
            categories[category] = []
        categories[category].append(tool_name)
    
    # Generate documentation for each category
    for category, tools in sorted(categories.items()):
        print(f"\n## {category.title()} Tools\n")
        
        for tool_name in sorted(tools):
            # Get tool info from MCP
            tool_info = None
            for tool in mcp.list_tools():
                if tool.name == tool_name:
                    tool_info = tool
                    break
            
            if tool_info:
                print(f"### {tool_name}\n")
                
                # Extract description
                if tool_info.description:
                    desc_lines = tool_info.description.strip().split('\n')
                    print(f"{desc_lines[0]}\n")
                
                # Extract parameters from docstring
                if hasattr(tool_info, 'function') and tool_info.function.__doc__:
                    params = extract_parameters_from_docstring(tool_info.function.__doc__)
                    if params:
                        print("**Parameters:**")
                        for name, info in params.items():
                            req = " *(required)*" if info['required'] else ""
                            print(f"- `{name}`{req}: {info['description']}")
                        print()
                
                # Extract example from docstring
                if hasattr(tool_info, 'function') and tool_info.function.__doc__:
                    example_match = re.search(r'EXAMPLE USAGE:(.*?)(?:NOTE:|$)', 
                                            tool_info.function.__doc__, re.DOTALL)
                    if example_match:
                        print("**Example:**")
                        print("```python")
                        print(example_match.group(1).strip())
                        print("```\n")


if __name__ == "__main__":
    generate_tool_documentation()
