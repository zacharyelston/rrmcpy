# Tool: redmine-create-issue

**Description**: Creates a new issue in the specified Redmine project with the provided details.

## Parameters

### Required
- `project_id` (string): The identifier of the project where the issue will be created
- `subject` (string): The title or summary of the issue

### Optional
- `description` (string): Detailed description of the issue
- `tracker_id` (integer): Type of issue tracker (bug, feature, support, etc.)
- `status_id` (integer): Initial status of the issue
- `priority_id` (integer): Priority level for the issue
- `assigned_to_id` (integer): User ID to assign the issue to

## Returns

JSON string containing the created issue with full details including:
- Issue ID and metadata
- Project information
- Status and priority details
- Creation timestamps
- Assignment information

## Example Usage

### Basic Issue Creation
```python
result = await mcp.call_tool(
    "redmine-create-issue",
    project_id="1",
    subject="Application crashes on startup"
)
```

### Detailed Issue Creation
```python
result = await mcp.call_tool(
    "redmine-create-issue",
    project_id="p1",
    subject="User authentication fails",
    description="Users cannot log in with valid credentials. Error appears in browser console.",
    tracker_id=1,
    priority_id=3,
    assigned_to_id=5
)
```

## Response Example

```json
{
  "issue": {
    "id": 123,
    "subject": "Application crashes on startup",
    "description": "",
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
      "name": "Admin User"
    },
    "created_on": "2024-01-01T10:00:00Z",
    "updated_on": "2024-01-01T10:00:00Z"
  }
}
```

## Error Scenarios

- **Invalid project_id**: "Error creating issue: Project not found"
- **Missing required fields**: "Error creating issue: Subject cannot be blank"
- **Permission denied**: "Error creating issue: User lacks permission to create issues in this project"
- **Invalid tracker_id**: "Error creating issue: Invalid tracker specified"
- **Server error**: "Error creating issue: Internal server error"

## Notes

- The created issue will use default values for optional parameters not specified
- Issue ID is automatically assigned by Redmine
- Creation timestamp is set by the server
- Author is determined by the authenticated API user