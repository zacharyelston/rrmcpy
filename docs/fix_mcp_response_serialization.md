# Fix for MCP Response Serialization Issues

## Problem Summary
1. The `redmine_create_issue` tool was returning empty dict `{}` instead of the created issue data
2. The `redmine_list_issues` tool was returning concatenated objects instead of a proper JSON array

## Root Cause Analysis
After investigating the FastMCP source code, I discovered that:
- FastMCP's `_convert_to_content` function converts tool results to MCP content objects
- For non-string results, it uses `pydantic_core.to_json` to serialize to JSON, then wraps in TextContent
- The issue appears to be with how complex objects (dicts/lists) are being serialized

## Solution Implemented
Created `fixed_mcp_server.py` that:
1. **Returns JSON strings instead of dictionaries/lists** - All tool functions now return `json.dumps(data, indent=2)`
2. **Added extensive debug logging** - To track the data flow through the system
3. **Simplified response handling** - Let FastMCP handle the TextContent wrapping of our JSON strings

## Key Changes

### Before (returning dict/list):
```python
@self.app.tool()
def redmine_create_issue(request: IssueCreateRequest) -> Dict[str, Any]:
    # ...
    return result.get('issue', {})  # Returns empty dict
```

### After (returning JSON string):
```python
@self.app.tool()
def redmine_create_issue(request: IssueCreateRequest) -> str:
    # ...
    issue = result.get('issue', {})
    return json.dumps(issue, indent=2)  # Returns JSON string
```

## Files Changed
1. Created `/src/fixed_mcp_server.py` - Fixed version with JSON string responses
2. Updated `/src/main.py` - Temporarily using fixed server for testing
3. Created documentation in `/docs/` for tracking the issue and fix

## Testing Required
1. Test create_issue to verify it returns full issue data
2. Test list_issues to verify it returns a proper JSON array
3. Verify no regression in other functionality
4. Monitor debug logs to understand the data flow

## Next Steps
1. Test with Claude to see if responses are now properly displayed
2. If successful, consider whether to:
   - Keep the JSON string approach
   - Investigate alternative solutions
   - Report issue to FastMCP maintainers
3. Update all tests to work with the new response format
4. Remove debug logging once issue is resolved

## Alternative Solutions Considered
1. **Using Pydantic response models** - Would require defining models for all responses
2. **Custom content conversion** - Override FastMCP's _convert_to_content
3. **Different MCP transport** - Try SSE or HTTP instead of stdio

## Lessons Learned
- FastMCP converts all non-string responses to JSON internally
- The MCP protocol expects specific content formats (TextContent, ImageContent, etc.)
- String responses are the simplest way to ensure predictable serialization
- Debug logging is essential for understanding data flow in MCP servers