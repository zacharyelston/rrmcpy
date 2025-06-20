# Tool: redmine-update-issue

**Description**: Updates an existing issue with new information, including status changes, assignments, and field modifications.

## Parameters

### Required
- `issue_id` (integer): The unique identifier of the issue to update

### Optional
- `subject` (string): New title for the issue
- `description` (string): Updated description text
- `status_id` (integer): New status identifier
- `priority_id` (integer): New priority level
- `assigned_to_id` (integer): User ID for new assignment
- `notes` (string): Comment to add to issue history

## Returns

JSON string confirming the update operation, typically an empty object for successful updates.

## Example Usage

### Update Issue Status
```python
result = await mcp.call_tool(
    "redmine-update-issue",
    issue_id=123,
    status_id=3,
    notes="Resolved the startup crash issue"
)
```

### Reassign Issue
```python
result = await mcp.call_tool(
    "redmine-update-issue",
    issue_id=123,
    assigned_to_id=7,
    notes="Reassigning to development team lead"
)
```

### Multiple Field Update
```python
result = await mcp.call_tool(
    "redmine-update-issue",
    issue_id=123,
    subject="Application startup crash - RESOLVED",
    status_id=5,
    priority_id=1,
    notes="Fixed memory allocation issue in initialization code"
)
```

## Response Example

```json
{}
```

*Note: Successful updates typically return an empty object. Use `redmine-get-issue` to verify changes.*

## Common Update Scenarios

### Close Issue
```python
result = await mcp.call_tool(
    "redmine-update-issue",
    issue_id=123,
    status_id=5,
    notes="Issue resolved and tested"
)
```

### Add Progress Update
```python
result = await mcp.call_tool(
    "redmine-update-issue",
    issue_id=123,
    notes="Investigating root cause. Found potential memory leak in module X."
)
```

### Change Priority
```python
result = await mcp.call_tool(
    "redmine-update-issue",
    issue_id=123,
    priority_id=4,
    notes="Escalating priority due to customer impact"
)
```

## Error Scenarios

- **Issue not found**: "Error updating issue 999: Issue not found"
- **Permission denied**: "Error updating issue 123: Insufficient permissions"
- **Invalid status**: "Error updating issue 123: Invalid status transition"
- **Invalid user assignment**: "Error updating issue 123: User not found or not authorized"
- **Validation errors**: "Error updating issue 123: Subject cannot be blank"

## Field Validation

### Status Changes
- Must follow valid status transitions defined in Redmine workflow
- Some status changes may require specific permissions

### Assignment Validation
- User must exist and have access to the project
- User must have appropriate role permissions

### Required Fields
- Some projects may have required custom fields
- Validation depends on project and tracker configuration

## Notes

- Updates create journal entries in issue history
- Only specified fields are modified; others remain unchanged
- Timestamps are automatically updated by the server
- Custom fields can be updated using Redmine's custom field syntax