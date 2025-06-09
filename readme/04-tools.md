# Tool Inventory

This document lists the available MCP tools in the Redmine MCP Server.

## Currently Implemented

### Issue Management
- ✅ `redmine-create-issue`: Creates a new issue in Redmine
- ✅ `redmine-get-issue`: Gets details of a specific issue
- ✅ `redmine-list-issues`: Lists issues with optional filters
- ✅ `redmine-update-issue`: Updates an existing issue
- ✅ `redmine-delete-issue`: Deletes an issue

### Version Management
- ✅ `redmine-list-versions`: Lists versions for a project
- ✅ `redmine-get-version`: Gets details of a specific version
- ✅ `redmine-create-version`: Creates a new version
- ✅ `redmine-update-version`: Updates an existing version
- ✅ `redmine-delete-version`: Deletes a version
- ✅ `redmine-get-issues-by-version`: Gets all issues for a specific version

### Project Management
- ✅ `redmine-create-project`: Creates a new project
- ✅ `redmine-update-project`: Updates an existing project
- ✅ `redmine-delete-project`: Deletes a project

### Server Information
- ✅ `redmine-health-check`: Checks Redmine API health
- ✅ `redmine-version-info`: Gets version and environment information
- ✅ `redmine-current-user`: Gets current authenticated user information

## Planned Tools

### User and Role Management
- [ ] `redmine-list-users`: Lists users with optional filters
- [ ] `redmine-get-user`: Gets details of a specific user
- [ ] `redmine-create-user`: Creates a new user
- [ ] `redmine-update-user`: Updates an existing user
- [ ] `redmine-add-user-to-project`: Adds a user to a project with specified role

### Document Management
- [ ] `redmine-list-wiki-pages`: Lists wiki pages for a project
- [ ] `redmine-get-wiki-page`: Gets a specific wiki page
- [ ] `redmine-create-wiki-page`: Creates a new wiki page
- [ ] `redmine-update-wiki-page`: Updates an existing wiki page
- [ ] `redmine-delete-wiki-page`: Deletes a wiki page

### Time Entries
- [ ] `redmine-list-time-entries`: Retrieves time entries with optional filtering
- [ ] `redmine-get-time-entry`: Fetches detailed information for a specified time entry
- [ ] `redmine-create-time-entry`: Creates a new time entry for an issue or project
- [ ] `redmine-update-time-entry`: Updates an existing time entry

### Server Administration
- ✅ `redmine-list-projects`: Lists all available projects
- [ ] `redmine-get-project-details`: Gets detailed information about a project
- [ ] `redmine-get-status-options`: Gets available status options