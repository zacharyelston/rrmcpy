# GitHub Issue Draft for jlowin/fastmcp

## Title
Empty dict responses and malformed list responses when using FastMCP with Claude Desktop

## Labels
bug, compatibility, claude-desktop

## Issue Body

### Description

When using FastMCP to build an MCP server that's consumed by Claude Desktop, tool responses are not properly displayed:
- Tools that return dictionaries show as empty `{}` in Claude Desktop
- Tools that return lists show concatenated objects without array brackets

The tools execute successfully and FastMCP correctly formats the responses according to the MCP protocol, but Claude Desktop fails to display them properly.

### Environment

- **FastMCP Version**: Latest (please specify current version)
- **Python Version**: 3.13
- **OS**: macOS
- **MCP Transport**: stdio
- **MCP Client**: Claude Desktop

### Minimal Reproduction

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

if __name__ == "__main__":
    mcp.run()
```

### Expected Behavior

When calling these tools from Claude Desktop:
- `create_item()` should display: `{"id": 123, "name": "Test Item", "status": "created"}`
- `list_items()` should display: `[{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]`

### Actual Behavior

- `create_item()` displays: `{}`
- `list_items()` displays: `{"id": 1, "name": "Item 1"}{"id": 2, "name": "Item 2"}` (concatenated without array brackets)

### Investigation Details

I've traced through the code and found that FastMCP is correctly converting responses:
- Dict responses are serialized to JSON using `pydantic_core.to_json`
- The JSON string is wrapped in `TextContent(type="text", text=json_string)`
- This follows the MCP protocol specification

The issue appears to be in how Claude Desktop interprets these TextContent responses.

### Workarounds Attempted

1. Returning JSON strings directly - Same issue
2. Using custom serializers - Same issue
3. Different return type annotations - No effect

### Potential Impact

This issue prevents FastMCP servers from being effectively used with Claude Desktop, as users cannot see the results of their operations. While the operations succeed on the backend, they appear broken to users.

### Questions

1. Has this been tested with Claude Desktop specifically?
2. Are there known compatibility issues with Claude Desktop's MCP client?
3. Is there a recommended response format that works better with Claude Desktop?

### Related Information

I've checked existing issues and found some related to response serialization (#207, #290) but none that specifically address this Claude Desktop compatibility issue.

Happy to provide more debugging information or test potential fixes!
