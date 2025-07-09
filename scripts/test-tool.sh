#!/bin/bash
# Test a specific MCP tool
# Usage: ./scripts/test-tool.sh <tool-name>
# Example: ./scripts/test-tool.sh redmine-create-issue

TOOL_NAME=$1

if [ -z "$TOOL_NAME" ]; then
    echo "Usage: $0 <tool-name>"
    echo "Example: $0 redmine-create-issue"
    echo ""
    echo "Available tools:"
    python -c "
import sys
sys.path.append('.')
try:
    from src.mcp_server import mcp
    tools = [tool.name for tool in mcp.list_tools()]
    for tool in sorted(tools):
        print(f'  - {tool}')
except Exception as e:
    print('Error listing tools:', e)
"
    exit 1
fi

echo "Testing tool: $TOOL_NAME"
echo ""

python -c "
import sys
sys.path.append('.')

try:
    from src.mcp_server import mcp
    
    # Find the tool
    tool = None
    for t in mcp.list_tools():
        if t.name == '$TOOL_NAME':
            tool = t
            break
    
    if not tool:
        print('❌ Tool not found: $TOOL_NAME')
        sys.exit(1)
    
    print(f'✅ Found tool: {tool.name}')
    print(f'   Description: {tool.description}')
    print(f'   Parameters:')
    
    if hasattr(tool, 'input_schema'):
        schema = tool.input_schema
        if 'properties' in schema:
            for param, details in schema['properties'].items():
                required = param in schema.get('required', [])
                param_type = details.get('type', 'any')
                desc = details.get('description', '')
                req_str = '[required]' if required else '[optional]'
                print(f'     - {param} ({param_type}) {req_str}: {desc}')
    
    print('')
    print('Tool is properly registered and ready to use.')
    
except Exception as e:
    print(f'❌ Error testing tool: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"
