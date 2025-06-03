# FastMCP Best Practices Guide

## Current Implementation Analysis

### What We Built (Complex Architecture)
```python
# Complex multi-layer approach with unnecessary abstractions
class RedmineMCPServer:
    def __init__(self):
        self.config = AppConfig()
        self.tool_registry = ToolRegistry()  # Custom layer
        self.clients = {}
        self.services = {}
        self.mcp = FastMCP("Redmine MCP Server")
    
    def _register_tools(self):
        # Mixing custom registry with FastMCP
        @self.mcp.tool("redmine-create-issue")
        async def create_issue(...):
            tool = self.tool_registry.get_tool("CreateIssueTool")  # Extra layer
            result = tool.execute(...)
            return json.dumps(result, indent=2)
```

### FastMCP Best Practice (Simple & Direct)
```python
# Clean, direct FastMCP implementation
from fastmcp import FastMCP

mcp = FastMCP("Redmine MCP Server")
issue_client = None  # Global client instance

@mcp.tool()
async def redmine_create_issue(project_id: str, subject: str, ...) -> str:
    """Create a new issue in Redmine"""
    try:
        issue_data = {"project_id": project_id, "subject": subject}
        result = issue_client.create_issue(issue_data)  # Direct call
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating issue: {str(e)}"

async def main():
    global issue_client
    issue_client = IssueClient(url, api_key)  # Simple initialization
    await mcp.run()
```

## Key Differences & Best Practices

### 1. Tool Registration
**❌ Avoid:** Custom tool registries, wrapper classes, indirect tool execution
**✅ Use:** Direct @mcp.tool() decorators, simple async functions

### 2. Client Management
**❌ Avoid:** Complex client dictionaries, service layers, dependency injection
**✅ Use:** Global client instances, direct API calls

### 3. Error Handling
**❌ Avoid:** Custom error classes, complex error propagation
**✅ Use:** Simple try/catch blocks, descriptive error strings

### 4. Configuration
**❌ Avoid:** Complex config classes, multiple configuration sources
**✅ Use:** Environment variables, simple initialization

### 5. Server Startup
**❌ Avoid:** Custom server wrappers, complex initialization sequences
**✅ Use:** Direct mcp.run(), minimal setup

## Container Compatibility

### Current Issue
FastMCP's `mcp.run()` conflicts with existing event loops in container environments.

### Solution
```python
if __name__ == "__main__":
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        import nest_asyncio
        nest_asyncio.apply()
        task = loop.create_task(main())
    except RuntimeError:
        asyncio.run(main())
```

## Recommended Architecture

```
fastmcp_server.py (210 lines)
├── FastMCP instance
├── Global client variables
├── @mcp.tool() decorated functions
├── Simple initialization
└── Container-safe main()

vs.

Current complex structure (1000+ lines)
├── src/mcp_server.py
├── src/core/
├── src/services/
├── src/tools/
└── Multiple abstraction layers
```

## Migration Benefits

1. **Simplicity**: 80% less code
2. **Maintainability**: Standard FastMCP patterns
3. **Compatibility**: Works with all MCP clients
4. **Performance**: Direct API calls, no middleware
5. **Debugging**: Clear execution path

## Recommendation

Replace the complex `src/mcp_server.py` with the simple `fastmcp_server.py` approach for:
- Better FastMCP compliance
- Universal MCP client compatibility
- Easier maintenance and debugging
- Standard patterns other developers expect