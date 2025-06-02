# FastMCP Empty Response Bug - Claude Desktop Integration

## Bug Summary

When using FastMCP (jlowin/fastmcp) to build an MCP server, tool responses are not properly displayed in Claude Desktop. The `create_issue` type tools return an empty dict `{}` instead of the actual response data, and `list` type tools return concatenated JSON objects instead of a proper array format.

## Environment

- **FastMCP Version**: Unknown (latest from jlowin/fastmcp)
- **Python Version**: 3.13
- **OS**: macOS
- **MCP Transport**: stdio
- **MCP Client**: Claude Desktop
- **Test Environment**: Redmine MCP Server (https://redstone.redminecloud.net)

## Issue Description

### Symptoms

1. **Empty Response from Dictionary-returning Tools**
   - **Input**: `redmine_create_issue` with valid parameters
   - **Expected**: Full issue object with id, subject, description, etc.
   - **Actual**: `{}`

2. **Concatenated Objects in List-returning Tools**
   - **Input**: `redmine_list_issues` with limit=3
   - **Expected**: `[{issue1}, {issue2}, {issue3}]`
   - **Actual**: `{issue1}{issue2}{issue3}` (objects concatenated without array brackets)

### Investigation Findings

1. **FastMCP correctly converts responses to MCP protocol format**
   - Dict `{"id": 123}` → `TextContent(type='text', text='{"id": 123}')`
   - List `[{"id": 1}]` → `TextContent(type='text', text='[{"id": 1}]')`
   - Empty dict `{}` → `TextContent(type='text', text='{}')`

2. **Backend API is working correctly**
   - Redmine API returns proper responses (201 with full issue data, proper JSON arrays)
   - RedmineClient correctly receives and processes responses
   - Tool functions execute successfully and return expected data

3. **Issue is in MCP client interpretation layer**
   - FastMCP server logs show correct data being returned
   - Problem occurs only when responses are displayed in Claude Desktop

## Root Cause Analysis

The issue appears to be a compatibility problem between how FastMCP formats tool responses and how Claude's MCP client expects to receive them. FastMCP correctly follows the MCP protocol by converting non-string responses to JSON and wrapping them in TextContent objects, but Claude's client may be expecting a different format or may have issues parsing the TextContent when displaying to users.

### Key Code Path (from FastMCP)

```python
def _convert_to_content(
    result: Any,
    serializer: Callable[[Any], str] | None = None
) -> list[TextContent | ImageContent | EmbeddedResource]:
    # ...
    if not isinstance(result, str):
        if serializer is None:
            result = default_serializer(result)  # Uses pydantic_core.to_json
    return [TextContent(type="text", text=result)]
```

## Reproduction Steps

### Minimal Test Case

```python
from fastmcp import FastMCP

mcp = FastMCP("Test Server")

@mcp.tool()
def create_item() -> dict:
    """Create an item and return its details"""
    return {"id": 123, "name": "Test Item", "status": "created"}

@mcp.tool()
def list_items() -> list:
    """List all items"""
    return [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]

@mcp.tool()
def get_empty_dict() -> dict:
    """Return an empty dictionary"""
    return {}

if __name__ == "__main__":
    mcp.run()
```

### Steps to Reproduce

1. Save the above code as `test_server.py`
2. Configure Claude Desktop to use this MCP server
3. In Claude Desktop, call the tools:
   - `create_item()` - will show `{}`
   - `list_items()` - will show concatenated objects
   - `get_empty_dict()` - will show `{}`

## Workarounds Attempted

1. **Return JSON strings directly** - Still wrapped in TextContent, same display issues
2. **Use different return type annotations** - No change in behavior  
3. **Add custom serializer** - FastMCP uses the serializer but display issue persists

## Related Issues Research

### FastMCP Repository Issues Checked

- **#207**: "Allow alternative serialization to str when objects are returned" (Closed)
  - Discussed custom serialization options
  - Resulted in ability to provide custom serializers
  - Does not solve the Claude Desktop display issue

- **#290**: "use pydantic_core.to_json" (Merged)
  - Updated serialization to use pydantic_core
  - Analogous to official SDK change

- **#541**: "`client.list_resources()` not working" (Closed)
  - Different issue - about empty resource lists
  - Not related to response display

- **No existing issues found** specifically about Claude Desktop empty responses or this compatibility issue

## Impact

### Severity: HIGH

This prevents FastMCP servers from being usable with Claude Desktop in production, as users cannot see the results of their operations. The tools execute successfully on the backend but appear broken to users.

### Affected Users
- All developers using FastMCP to build MCP servers for Claude Desktop
- End users of these MCP servers who cannot see operation results

## Recommendations

1. **Report to jlowin/fastmcp**
   - Create issue with this reproduction case
   - Reference this investigation

2. **Test with Official MCP SDK**
   - Verify if issue is FastMCP-specific
   - Compare response handling implementation

3. **Contact Anthropic MCP Team**
   - May be a Claude Desktop client issue
   - Need clarification on expected response format

4. **Potential Fixes to Explore**
   - Custom response wrapper that Claude Desktop expects
   - Different TextContent formatting
   - Alternative to TextContent for structured data

## Additional Notes

- FastMCP 1.0 was incorporated into official MCP SDK, but this uses FastMCP 2.0 from jlowin
- Issue may be specific to stdio transport - other transports not tested
- Similar issues may affect other LLM clients, not just Claude Desktop
- The issue is not with the MCP protocol itself, but with client-side interpretation

## File References

- Bug report: `/Users/zacelston/AlZacAI/rrmcpy/bug-report-2025-05-30-19-29-30.yaml`
- Test scripts: `/Users/zacelston/AlZacAI/rrmcpy/debug/test_response_handling.py`
- FastMCP source: `/Users/zacelston/AlZacAI/fastmcp/src/fastmcp/tools/tool.py`
