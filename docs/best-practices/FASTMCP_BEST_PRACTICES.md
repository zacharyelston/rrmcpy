# FastMCP Best Practices Guide

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



## Recommended Architecture

```
fastmcp_server.py (210 lines)
├── FastMCP instance
├── Global client variables
├── @mcp.tool() decorated functions
├── Simple initialization
└── Container-safe main()
```

