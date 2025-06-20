# MCP Tool Reference

This section provides complete documentation for all available MCP tools in the Redmine MCP Server.

## Tool Categories

### Issue Management
- [redmine-create-issue](redmine-create-issue.md) - Create new issues
- [redmine-get-issue](redmine-get-issue.md) - Get issue details
- [redmine-list-issues](redmine-list-issues.md) - List and filter issues
- [redmine-update-issue](redmine-update-issue.md) - Update existing issues
- [redmine-delete-issue](redmine-delete-issue.md) - Delete issues

### Administration
- [redmine-health-check](redmine-health-check.md) - Check server connectivity
- [redmine-get-current-user](redmine-get-current-user.md) - Get authenticated user info

## Tool Naming Convention

All tools follow the pattern: `redmine-{action}-{entity}`

- **redmine**: Namespace prefix to avoid conflicts
- **action**: Operation type (create, get, list, update, delete)
- **entity**: Redmine object type (issue, project, user, etc.)

## Common Parameters

### Standard Fields
- `project_id` (string): Redmine project identifier
- `subject` (string): Title or summary text
- `description` (string): Detailed description
- `status_id` (integer): Status identifier
- `priority_id` (integer): Priority level identifier
- `assigned_to_id` (integer): User ID for assignment

### Filtering Parameters
- `limit` (integer): Maximum number of results
- `offset` (integer): Starting position for pagination
- `include` (array): Related data to include in response

## Response Format

All tools return JSON strings with consistent structure:

### Success Response
```json
{
  "issue": {
    "id": 123,
    "subject": "Issue title",
    "description": "Issue description",
    "status": {"id": 1, "name": "New"},
    "priority": {"id": 2, "name": "Normal"},
    "project": {"id": 1, "name": "Project Name"},
    "created_on": "2024-01-01T10:00:00Z",
    "updated_on": "2024-01-01T10:00:00Z"
  }
}
```

### Error Response
```
Error creating issue: Invalid project_id
```

## Usage Examples

### Basic Issue Creation
```python
result = await mcp.call_tool(
    "redmine-create-issue",
    project_id="1",
    subject="Bug report",
    description="Application crashes on startup"
)
```

### Filtered Issue Listing
```python
result = await mcp.call_tool(
    "redmine-list-issues",
    project_id="1",
    status_id=1,
    limit=10
)
```

## Authentication

All tools require proper Redmine API key configuration:

```bash
export REDMINE_URL="https://your-redmine.com"
export REDMINE_API_KEY="your-api-key"
```

## Error Handling

Tools handle common error scenarios:
- Invalid credentials (401)
- Insufficient permissions (403)
- Resource not found (404)
- Server errors (500)
- Network connectivity issues
- Invalid input parameters

Error messages are descriptive and actionable for troubleshooting.