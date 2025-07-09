#!/usr/bin/env python3
"""
Audit MCP tool parameters against standard Redmine API
Usage: python scripts/audit-parameters.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def audit_parameters():
    """Audit all MCP tools for missing Redmine API parameters"""
    
    print("🔍 Auditing MCP Tool Parameters")
    print("=" * 50)
    
    # Standard Redmine issue parameters
    standard_issue_params = {
        'create_issue': [
            'project_id', 'subject', 'description', 'tracker_id', 'status_id',
            'priority_id', 'assigned_to_id', 'parent_issue_id', 'done_ratio',
            'start_date', 'due_date', 'estimated_hours', 'category_id',
            'fixed_version_id', 'custom_fields', 'watcher_user_ids', 'is_private'
        ],
        'update_issue': [
            'issue_id', 'subject', 'description', 'tracker_id', 'status_id',
            'priority_id', 'assigned_to_id', 'parent_issue_id', 'done_ratio',
            'start_date', 'due_date', 'estimated_hours', 'category_id',
            'fixed_version_id', 'custom_fields', 'notes', 'private_notes'
        ]
    }
    
    try:
        from src.mcp_server import mcp
        
        # Get all tools
        tools = mcp.list_tools()
        tool_dict = {tool.name: tool for tool in tools}
        
        # Check issue tools
        for tool_name, expected_params in standard_issue_params.items():
            full_name = f"redmine-{tool_name.replace('_', '-')}"
            
            if full_name in tool_dict:
                tool = tool_dict[full_name]
                print(f"\n📋 Checking {full_name}:")
                
                # Get actual parameters
                actual_params = []
                if hasattr(tool, 'input_schema'):
                    schema = tool.input_schema
                    if 'properties' in schema:
                        actual_params = list(schema['properties'].keys())
                
                # Find missing parameters
                missing = [p for p in expected_params if p not in actual_params]
                extra = [p for p in actual_params if p not in expected_params]
                
                if missing:
                    print(f"   ❌ Missing parameters: {', '.join(missing)}")
                else:
                    print(f"   ✅ All standard parameters present")
                
                if extra:
                    print(f"   ℹ️  Extra parameters: {', '.join(extra)}")
                
            else:
                print(f"\n❌ Tool not found: {full_name}")
        
        # Summary of all tools
        print(f"\n📊 Tool Summary:")
        print(f"   Total tools available: {len(tools)}")
        
        # Group by category
        categories = {}
        for tool in tools:
            if tool.name.startswith('redmine-'):
                category = tool.name.split('-')[1]
                if category not in categories:
                    categories[category] = []
                categories[category].append(tool.name)
        
        for category, tool_names in sorted(categories.items()):
            print(f"   {category}: {len(tool_names)} tools")
        
    except Exception as e:
        print(f"❌ Error during audit: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "=" * 50)
    print("Audit complete! Check results above for missing parameters.")
    return 0

if __name__ == "__main__":
    sys.exit(audit_parameters())
