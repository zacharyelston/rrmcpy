"""
Mock data for testing the Redmine MCP Server
"""

PROJECTS = {
    "projects": [
        {
            "id": 1,
            "name": "Example Project",
            "identifier": "example",
            "description": "This is an example project",
            "status": 1,
            "is_public": True,
            "created_on": "2023-01-01T00:00:00Z",
            "updated_on": "2023-01-02T00:00:00Z"
        },
        {
            "id": 2,
            "name": "Another Project",
            "identifier": "another",
            "description": "This is another project",
            "status": 1,
            "is_public": True,
            "created_on": "2023-01-03T00:00:00Z",
            "updated_on": "2023-01-04T00:00:00Z"
        }
    ],
    "total_count": 2,
    "offset": 0,
    "limit": 25
}

ISSUES = {
    "issues": [
        {
            "id": 1,
            "project": {"id": 1, "name": "Example Project"},
            "tracker": {"id": 1, "name": "Bug"},
            "status": {"id": 1, "name": "New"},
            "priority": {"id": 2, "name": "Normal"},
            "author": {"id": 1, "name": "John Smith"},
            "subject": "Example issue",
            "description": "This is an example issue",
            "created_on": "2023-01-05T00:00:00Z",
            "updated_on": "2023-01-06T00:00:00Z"
        },
        {
            "id": 2,
            "project": {"id": 1, "name": "Example Project"},
            "tracker": {"id": 2, "name": "Feature"},
            "status": {"id": 2, "name": "In Progress"},
            "priority": {"id": 3, "name": "High"},
            "author": {"id": 1, "name": "John Smith"},
            "subject": "Another issue",
            "description": "This is another issue",
            "created_on": "2023-01-07T00:00:00Z",
            "updated_on": "2023-01-08T00:00:00Z"
        }
    ],
    "total_count": 2,
    "offset": 0,
    "limit": 25
}

USERS = {
    "users": [
        {
            "id": 1,
            "login": "jsmith",
            "firstname": "John",
            "lastname": "Smith",
            "mail": "jsmith@example.com",
            "created_on": "2023-01-01T00:00:00Z",
            "last_login_on": "2023-01-10T00:00:00Z"
        },
        {
            "id": 2,
            "login": "dlopper",
            "firstname": "Dave",
            "lastname": "Lopper",
            "mail": "dlopper@example.com",
            "created_on": "2023-01-02T00:00:00Z",
            "last_login_on": "2023-01-11T00:00:00Z"
        }
    ],
    "total_count": 2,
    "offset": 0,
    "limit": 25
}