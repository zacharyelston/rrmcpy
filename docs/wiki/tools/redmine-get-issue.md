# Tool: redmine-get-issue

**Description**: Retrieves detailed information about a specific issue by its ID, with optional related data inclusion.

## Parameters

### Required
- `issue_id` (integer): The unique identifier of the issue to retrieve

### Optional
- `include` (array): List of related data to include in the response
  - Valid values: `["children", "attachments", "relations", "changesets", "journals", "watchers"]`

## Returns

JSON string containing complete issue details including all specified related data.

## Example Usage

### Basic Issue Retrieval
```python
result = await mcp.call_tool(
    "redmine-get-issue",
    issue_id=123
)
```

### Issue with Related Data
```python
result = await mcp.call_tool(
    "redmine-get-issue",
    issue_id=123,
    include=["attachments", "journals", "relations"]
)
```

## Response Example

```json
{
  "issue": {
    "id": 123,
    "subject": "Application crashes on startup",
    "description": "Detailed description of the issue...",
    "project": {
      "id": 1,
      "name": "Main Project"
    },
    "tracker": {
      "id": 1,
      "name": "Bug"
    },
    "status": {
      "id": 2,
      "name": "In Progress"
    },
    "priority": {
      "id": 3,
      "name": "High"
    },
    "author": {
      "id": 1,
      "name": "John Doe"
    },
    "assigned_to": {
      "id": 5,
      "name": "Jane Smith"
    },
    "created_on": "2024-01-01T10:00:00Z",
    "updated_on": "2024-01-01T15:30:00Z",
    "done_ratio": 50,
    "estimated_hours": 8.0,
    "spent_hours": 4.0
  }
}
```

## Error Scenarios

- **Issue not found**: "Error getting issue 999: Issue not found"
- **Permission denied**: "Error getting issue 123: Access denied"
- **Invalid issue_id**: "Error getting issue abc: Invalid issue ID format"
- **Server error**: "Error getting issue 123: Internal server error"

## Include Options

### children
Returns sub-issues and their basic information
```json
"children": [
  {
    "id": 124,
    "subject": "Sub-task 1",
    "tracker": {"id": 2, "name": "Task"}
  }
]
```

### attachments
Returns uploaded files and documents
```json
"attachments": [
  {
    "id": 1,
    "filename": "screenshot.png",
    "filesize": 15234,
    "content_type": "image/png",
    "created_on": "2024-01-01T11:00:00Z"
  }
]
```

### journals
Returns issue history and comments
```json
"journals": [
  {
    "id": 1,
    "user": {"id": 1, "name": "John Doe"},
    "notes": "Updated status to In Progress",
    "created_on": "2024-01-01T12:00:00Z"
  }
]
```

## Notes

- Issue visibility depends on user permissions and project settings
- Include parameters are optional and can be combined
- Large issues with extensive history may have slower response times