# Tool: redmine-delete-issue

**Description**: Permanently removes an issue from the Redmine system. This operation is irreversible and requires appropriate permissions.

## Parameters

### Required
- `issue_id` (integer): The unique identifier of the issue to delete

## Returns

JSON string confirming the deletion operation, typically an empty object for successful deletions.

## Example Usage

### Delete Issue
```python
result = await mcp.call_tool(
    "redmine-delete-issue",
    issue_id=123
)
```

## Response Example

```json
{}
```

## Error Scenarios

- **Issue not found**: "Error deleting issue 999: Issue not found"
- **Permission denied**: "Error deleting issue 123: Insufficient permissions to delete issues"
- **Issue has dependencies**: "Error deleting issue 123: Cannot delete issue with child issues"
- **Server error**: "Error deleting issue 123: Internal server error"

## Permission Requirements

- User must have "Delete issues" permission in the project
- Some Redmine configurations restrict deletion based on issue status
- Administrator privileges may be required depending on project settings

## Important Considerations

### Data Loss Warning
- Deletion is permanent and cannot be undone
- All issue history, comments, and attachments are removed
- Related time entries may be affected depending on configuration

### Dependencies
- Issues with child issues cannot be deleted
- Related issues may reference the deleted issue
- Time tracking entries may become orphaned

### Audit Trail
- Deletion events may be logged in system audit logs
- Some organizations disable deletion for compliance reasons

## Alternative Approaches

### Close Instead of Delete
```python
# Consider closing instead of deleting for audit trail
result = await mcp.call_tool(
    "redmine-update-issue",
    issue_id=123,
    status_id=6,  # Closed status
    notes="Issue closed - duplicate of #456"
)
```

### Archive Project
For bulk cleanup, consider archiving entire projects rather than deleting individual issues.

## Notes

- Test deletion permissions in development environment first
- Consider organizational policies before implementing deletion workflows
- Some Redmine installations disable issue deletion entirely
- Always verify issue ID before deletion to prevent accidents