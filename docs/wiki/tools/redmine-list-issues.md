# Tool: redmine-list-issues

**Description**: Retrieves a filtered list of issues based on specified criteria with pagination support.

## Parameters

### All Optional
- `project_id` (string): Filter issues by specific project
- `status_id` (integer): Filter by issue status
- `assigned_to_id` (integer): Filter by assigned user
- `tracker_id` (integer): Filter by issue type/tracker
- `limit` (integer): Maximum number of results to return (default: 25)
- `offset` (integer): Starting position for pagination (default: 0)

## Returns

JSON string containing an array of issues matching the filter criteria, plus pagination metadata.

## Example Usage

### List All Issues
```python
result = await mcp.call_tool("redmine-list-issues")
```

### Project-Specific Issues
```python
result = await mcp.call_tool(
    "redmine-list-issues",
    project_id="p1",
    limit=10
)
```

### Filtered by Status and Assignment
```python
result = await mcp.call_tool(
    "redmine-list-issues",
    status_id=1,
    assigned_to_id=5,
    limit=20,
    offset=40
)
```

## Response Example

```json
{
  "issues": [
    {
      "id": 123,
      "subject": "Application crashes on startup",
      "project": {
        "id": 1,
        "name": "Main Project"
      },
      "tracker": {
        "id": 1,
        "name": "Bug"
      },
      "status": {
        "id": 1,
        "name": "New"
      },
      "priority": {
        "id": 2,
        "name": "Normal"
      },
      "author": {
        "id": 1,
        "name": "John Doe"
      },
      "created_on": "2024-01-01T10:00:00Z",
      "updated_on": "2024-01-01T10:00:00Z"
    }
  ],
  "total_count": 150,
  "offset": 0,
  "limit": 25
}
```

## Common Filter Combinations

### Open Issues in Project
```python
result = await mcp.call_tool(
    "redmine-list-issues",
    project_id="web-app",
    status_id=1
)
```

### My Assigned Issues
```python
result = await mcp.call_tool(
    "redmine-list-issues",
    assigned_to_id=current_user_id
)
```

### High Priority Bugs
```python
result = await mcp.call_tool(
    "redmine-list-issues",
    tracker_id=1,
    priority_id=4
)
```

## Pagination

Handle large result sets using limit and offset:

```python
# Get first page (issues 1-25)
page1 = await mcp.call_tool(
    "redmine-list-issues",
    limit=25,
    offset=0
)

# Get second page (issues 26-50)
page2 = await mcp.call_tool(
    "redmine-list-issues",
    limit=25,
    offset=25
)
```

## Error Scenarios

- **Invalid project_id**: "Error listing issues: Project not found"
- **Invalid status_id**: "Error listing issues: Invalid status specified"
- **Permission denied**: "Error listing issues: Access denied to project"
- **Invalid pagination**: "Error listing issues: Offset exceeds total count"

## Performance Notes

- Large projects may have thousands of issues - use pagination
- Specific filters improve response times
- Consider caching results for frequently accessed lists
- Default limit is 25 to balance performance and usability