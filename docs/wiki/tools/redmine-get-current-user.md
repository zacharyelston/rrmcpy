# Tool: redmine-get-current-user

**Description**: Retrieves information about the currently authenticated user based on the provided API key.

## Parameters

None - this tool uses the configured API key to identify the current user.

## Returns

JSON string containing complete user profile information for the authenticated user.

## Example Usage

### Get Current User Info
```python
result = await mcp.call_tool("redmine-get-current-user")
```

## Response Example

```json
{
  "user": {
    "id": 1,
    "login": "admin",
    "firstname": "John",
    "lastname": "Doe",
    "mail": "john.doe@company.com",
    "created_on": "2020-01-15T09:30:00Z",
    "last_login_on": "2024-01-01T14:22:00Z",
    "api_key": "a1b2c3d4e5f6...",
    "status": 1,
    "groups": [
      {
        "id": 4,
        "name": "Developers"
      },
      {
        "id": 5,
        "name": "Project Managers"
      }
    ],
    "memberships": [
      {
        "id": 1,
        "project": {
          "id": 1,
          "name": "Main Project"
        },
        "roles": [
          {
            "id": 3,
            "name": "Developer"
          }
        ]
      }
    ]
  }
}
```

## Error Scenarios

- **Invalid API key**: "Error getting current user: Unauthorized access"
- **API key disabled**: "Error getting current user: Account disabled"
- **Server error**: "Error getting current user: Internal server error"
- **Network issue**: "Error getting current user: Connection failed"

## Use Cases

### Authentication Verification
```python
user_info = await mcp.call_tool("redmine-get-current-user")
if "user" in user_info:
    print(f"Authenticated as: {user['firstname']} {user['lastname']}")
```

### Permission Checking
```python
result = await mcp.call_tool("redmine-get-current-user")
user = json.loads(result)["user"]
user_groups = [group["name"] for group in user["groups"]]
if "Administrators" in user_groups:
    # Perform admin operations
```

### Project Access Validation
```python
result = await mcp.call_tool("redmine-get-current-user")
user = json.loads(result)["user"]
accessible_projects = [m["project"]["id"] for m in user["memberships"]]
```

## User Status Codes

- `1`: Active user
- `2`: Registered (pending activation)
- `3`: Locked

## Fields Explanation

### Basic Information
- `id`: Unique user identifier
- `login`: Username for authentication
- `firstname`, `lastname`: User's full name
- `mail`: Email address

### Activity Information  
- `created_on`: Account creation timestamp
- `last_login_on`: Most recent login time
- `status`: Account status (1=active, 2=registered, 3=locked)

### Permissions
- `groups`: Global user groups and their permissions
- `memberships`: Project-specific roles and access levels

## Notes

- API key permissions determine available user information
- Some fields may be restricted based on privacy settings
- User information reflects current state at time of request
- Useful for implementing role-based access control