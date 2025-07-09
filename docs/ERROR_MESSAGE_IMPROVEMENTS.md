# Improving Error Messages in Redmine MCP Tools

## Problem
FastMCP's parameter validation happens before our tool functions are called, resulting in unhelpful Pydantic validation error messages.

## Current Error Format
```
Error calling tool 'redmine-update-issue': 1 validation error for call[update_issue]
done_ratio
  Unexpected keyword argument [type=unexpected_keyword_argument, input_value='20', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/unexpected_keyword_argument
```

## Solutions Implemented

### 1. Enhanced Docstrings
Updated all tool docstrings to include:
- **ACCEPTED PARAMETERS** section with clear formatting
- Parameter descriptions with types and valid values
- **EXAMPLE USAGE** section with real examples
- Notes about related functionality

Example:
```python
"""Create a new issue in Redmine

ACCEPTED PARAMETERS:
• project_id (required): Project ID or identifier  
• subject (required): Issue subject/title
• description: Issue description/body text
• tracker_id: Type (1=Bug, 2=Feature, 3=Support)
• priority_id: Priority (1=Low, 2=Normal, 3=High)
...

EXAMPLE USAGE:
redmine-create-issue(
    project_id="rrmcpy",
    subject="Fix validation",
    priority_id=3
)
"""
```

### 2. Documentation Generation
Created `scripts/generate-tool-docs.py` to:
- Extract parameter info from all tools
- Generate comprehensive reference documentation
- Group tools by category
- Show examples for each tool

### 3. Future Improvements
Since we can't intercept FastMCP's validation:
1. Consider contributing to FastMCP to allow custom error handlers
2. Create a tool wrapper that validates before FastMCP
3. Add a help tool that shows parameters for other tools

## Impact
While we can't change the error messages directly, users now have:
- Clear parameter documentation in tool descriptions
- Examples showing correct usage
- Better understanding of what each parameter does
