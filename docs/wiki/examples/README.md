# Examples and Tutorials

Working examples demonstrating real-world usage of the Redmine MCP Server.

## Quick Start Examples

### Basic Issue Management
```python
# Create an issue
result = await mcp.call_tool(
    "redmine-create-issue",
    project_id="web-app",
    subject="User login timeout",
    description="Users report timeout after 5 minutes of inactivity"
)

# Get issue details
issue = await mcp.call_tool("redmine-get-issue", issue_id=123)

# Update issue status
await mcp.call_tool(
    "redmine-update-issue",
    issue_id=123,
    status_id=3,
    notes="Fixed timeout configuration in user session module"
)
```

### Project Workflow
```python
# List open issues in project
open_issues = await mcp.call_tool(
    "redmine-list-issues",
    project_id="mobile-app",
    status_id=1,
    limit=20
)

# Bulk status update workflow
for issue in json.loads(open_issues)["issues"]:
    if "critical" in issue["subject"].lower():
        await mcp.call_tool(
            "redmine-update-issue",
            issue_id=issue["id"],
            priority_id=4,
            notes="Escalated to high priority"
        )
```

## Complete Applications

### 1. CLI Issue Manager
A command-line tool for managing Redmine issues.

```python
#!/usr/bin/env python3
"""
CLI Issue Manager - Command-line Redmine client using MCP
Usage: python issue_cli.py create "Bug in login" --project=web-app
"""
import asyncio
import argparse
import json
from mcp_client import MCPClient

class RedmineCLI:
    def __init__(self, mcp_server_path):
        self.mcp_client = MCPClient("python", [mcp_server_path])
    
    async def create_issue(self, subject, project_id, description=None):
        """Create a new issue"""
        result = await self.mcp_client.call_tool(
            "redmine-create-issue",
            project_id=project_id,
            subject=subject,
            description=description or ""
        )
        
        issue_data = json.loads(result)
        if "issue" in issue_data:
            issue = issue_data["issue"]
            print(f"Created issue #{issue['id']}: {issue['subject']}")
            return issue["id"]
        else:
            print(f"Failed to create issue: {result}")
            return None
    
    async def list_issues(self, project_id=None, status_id=None, assigned_to_me=False):
        """List issues with filters"""
        params = {}
        if project_id:
            params["project_id"] = project_id
        if status_id:
            params["status_id"] = status_id
        
        result = await self.mcp_client.call_tool("redmine-list-issues", **params)
        issues_data = json.loads(result)
        
        if "issues" in issues_data:
            for issue in issues_data["issues"]:
                status = issue["status"]["name"]
                priority = issue["priority"]["name"]
                print(f"#{issue['id']} [{status}] {issue['subject']} ({priority})")
        else:
            print("No issues found")
    
    async def update_issue(self, issue_id, **kwargs):
        """Update issue with provided fields"""
        result = await self.mcp_client.call_tool(
            "redmine-update-issue",
            issue_id=issue_id,
            **kwargs
        )
        print(f"Updated issue #{issue_id}")

async def main():
    parser = argparse.ArgumentParser(description="Redmine CLI Manager")
    parser.add_argument("action", choices=["create", "list", "update"])
    parser.add_argument("subject", nargs="?", help="Issue subject")
    parser.add_argument("--project", required=True, help="Project ID")
    parser.add_argument("--description", help="Issue description")
    parser.add_argument("--status", type=int, help="Status ID")
    parser.add_argument("--priority", type=int, help="Priority ID")
    parser.add_argument("--issue-id", type=int, help="Issue ID for updates")
    
    args = parser.parse_args()
    
    cli = RedmineCLI("fastmcp_server.py")
    await cli.mcp_client.connect()
    
    try:
        if args.action == "create":
            await cli.create_issue(args.subject, args.project, args.description)
        elif args.action == "list":
            await cli.list_issues(args.project, args.status)
        elif args.action == "update":
            kwargs = {}
            if args.status:
                kwargs["status_id"] = args.status
            if args.priority:
                kwargs["priority_id"] = args.priority
            await cli.update_issue(args.issue_id, **kwargs)
    finally:
        await cli.mcp_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Web Dashboard
A simple web interface for Redmine via MCP.

```python
"""
Web Dashboard - Simple web UI for Redmine via MCP
Tech stack: FastAPI backend + React frontend + MCP client integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import json
from mcp_client import MCPClient

app = FastAPI(title="Redmine Dashboard")

# MCP client instance
mcp_client = None

class IssueCreate(BaseModel):
    project_id: str
    subject: str
    description: str = ""
    priority_id: int = 2

class IssueUpdate(BaseModel):
    status_id: int = None
    priority_id: int = None
    notes: str = ""

@app.on_event("startup")
async def startup():
    global mcp_client
    mcp_client = MCPClient("python", ["fastmcp_server.py"])
    await mcp_client.connect()

@app.on_event("shutdown")
async def shutdown():
    if mcp_client:
        await mcp_client.disconnect()

@app.get("/api/health")
async def health_check():
    """Check Redmine connectivity"""
    result = await mcp_client.call_tool("redmine-health-check")
    health_data = json.loads(result)
    return {"status": "ok" if health_data.get("healthy") else "error"}

@app.get("/api/issues")
async def list_issues(project_id: str = None, status_id: int = None, limit: int = 25):
    """Get filtered list of issues"""
    params = {"limit": limit}
    if project_id:
        params["project_id"] = project_id
    if status_id:
        params["status_id"] = status_id
    
    result = await mcp_client.call_tool("redmine-list-issues", **params)
    return json.loads(result)

@app.get("/api/issues/{issue_id}")
async def get_issue(issue_id: int):
    """Get specific issue details"""
    result = await mcp_client.call_tool("redmine-get-issue", issue_id=issue_id)
    issue_data = json.loads(result)
    
    if "Error" in result:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue_data

@app.post("/api/issues")
async def create_issue(issue: IssueCreate):
    """Create new issue"""
    result = await mcp_client.call_tool(
        "redmine-create-issue",
        project_id=issue.project_id,
        subject=issue.subject,
        description=issue.description,
        priority_id=issue.priority_id
    )
    
    issue_data = json.loads(result)
    if "Error" in result:
        raise HTTPException(status_code=400, detail=result)
    return issue_data

@app.put("/api/issues/{issue_id}")
async def update_issue(issue_id: int, update: IssueUpdate):
    """Update existing issue"""
    params = {"issue_id": issue_id}
    if update.status_id:
        params["status_id"] = update.status_id
    if update.priority_id:
        params["priority_id"] = update.priority_id
    if update.notes:
        params["notes"] = update.notes
    
    result = await mcp_client.call_tool("redmine-update-issue", **params)
    if "Error" in result:
        raise HTTPException(status_code=400, detail=result)
    return {"message": "Issue updated successfully"}

# Serve React frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3. Automation Scripts
Common automation tasks using the MCP server.

```python
"""
Automation Examples - Scripts for common Redmine automation tasks
"""
import asyncio
import json
import csv
from datetime import datetime
from mcp_client import MCPClient

class RedmineAutomation:
    def __init__(self, mcp_server_path):
        self.mcp_client = MCPClient("python", [mcp_server_path])
    
    async def bulk_issue_creation(self, csv_file_path):
        """Create multiple issues from CSV file"""
        created_issues = []
        
        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                result = await self.mcp_client.call_tool(
                    "redmine-create-issue",
                    project_id=row["project_id"],
                    subject=row["subject"],
                    description=row.get("description", ""),
                    priority_id=int(row.get("priority_id", 2))
                )
                
                issue_data = json.loads(result)
                if "issue" in issue_data:
                    created_issues.append(issue_data["issue"]["id"])
                    print(f"Created issue #{issue_data['issue']['id']}")
                else:
                    print(f"Failed to create issue: {row['subject']}")
        
        return created_issues
    
    async def daily_status_report(self, project_id):
        """Generate daily status report for project"""
        # Get all open issues
        result = await self.mcp_client.call_tool(
            "redmine-list-issues",
            project_id=project_id,
            status_id=1  # Open status
        )
        
        issues_data = json.loads(result)
        if "issues" not in issues_data:
            return "No issues found"
        
        issues = issues_data["issues"]
        
        # Generate report
        report = f"Daily Status Report - {datetime.now().strftime('%Y-%m-%d')}\n"
        report += f"Project: {project_id}\n"
        report += f"Open Issues: {len(issues)}\n\n"
        
        # Group by priority
        priority_groups = {}
        for issue in issues:
            priority = issue["priority"]["name"]
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(issue)
        
        for priority, group_issues in priority_groups.items():
            report += f"{priority} Priority ({len(group_issues)} issues):\n"
            for issue in group_issues[:5]:  # Show top 5
                report += f"  #{issue['id']}: {issue['subject']}\n"
            if len(group_issues) > 5:
                report += f"  ... and {len(group_issues) - 5} more\n"
            report += "\n"
        
        return report
    
    async def issue_migration(self, from_project, to_project, issue_filter=None):
        """Migrate issues between projects"""
        # Note: This requires creating new issues and updating old ones
        # Real migration would need more sophisticated handling
        
        params = {"project_id": from_project}
        if issue_filter:
            params.update(issue_filter)
        
        result = await self.mcp_client.call_tool("redmine-list-issues", **params)
        issues_data = json.loads(result)
        
        migrated = []
        for issue in issues_data.get("issues", []):
            # Get full issue details
            full_issue = await self.mcp_client.call_tool(
                "redmine-get-issue",
                issue_id=issue["id"]
            )
            
            issue_detail = json.loads(full_issue)["issue"]
            
            # Create in new project
            new_issue = await self.mcp_client.call_tool(
                "redmine-create-issue",
                project_id=to_project,
                subject=f"[MIGRATED] {issue_detail['subject']}",
                description=f"Migrated from #{issue['id']}\n\n{issue_detail.get('description', '')}"
            )
            
            new_issue_data = json.loads(new_issue)
            if "issue" in new_issue_data:
                migrated.append({
                    "old_id": issue["id"],
                    "new_id": new_issue_data["issue"]["id"]
                })
                
                # Update old issue to reference migration
                await self.mcp_client.call_tool(
                    "redmine-update-issue",
                    issue_id=issue["id"],
                    notes=f"Issue migrated to project {to_project} as #{new_issue_data['issue']['id']}"
                )
        
        return migrated

async def run_automation_examples():
    """Run various automation examples"""
    automation = RedmineAutomation("fastmcp_server.py")
    await automation.mcp_client.connect()
    
    try:
        # Example 1: Daily status report
        print("Generating daily status report...")
        report = await automation.daily_status_report("web-app")
        print(report)
        
        # Example 2: Bulk creation (if CSV exists)
        # created = await automation.bulk_issue_creation("issues.csv")
        # print(f"Created {len(created)} issues")
        
    finally:
        await automation.mcp_client.disconnect()

if __name__ == "__main__":
    asyncio.run(run_automation_examples())
```

## Interactive Tutorial

### Step-by-Step Guide

#### Step 1: Setup and Health Check
```python
# Verify connection to Redmine
health = await mcp.call_tool("redmine-health-check")
print("Server status:", json.loads(health)["status"])

# Get current user info
user = await mcp.call_tool("redmine-get-current-user")
user_data = json.loads(user)["user"]
print(f"Connected as: {user_data['firstname']} {user_data['lastname']}")
```

#### Step 2: Project Exploration
```python
# List available projects (requires project listing implementation)
# For now, use known project IDs

# Check specific project by creating test issue
test_issue = await mcp.call_tool(
    "redmine-create-issue",
    project_id="demo",
    subject="Test Connectivity",
    description="Verifying MCP server connection"
)
```

#### Step 3: Issue Lifecycle
```python
# Create → Read → Update → Delete workflow
issue_id = None

# Create
result = await mcp.call_tool(
    "redmine-create-issue",
    project_id="demo",
    subject="Tutorial Issue",
    description="Learning MCP server usage"
)
issue_data = json.loads(result)
issue_id = issue_data["issue"]["id"]

# Read
issue_details = await mcp.call_tool("redmine-get-issue", issue_id=issue_id)
print("Created issue:", json.loads(issue_details)["issue"]["subject"])

# Update
await mcp.call_tool(
    "redmine-update-issue",
    issue_id=issue_id,
    status_id=2,
    notes="Updated via MCP tutorial"
)

# Verify update
updated_issue = await mcp.call_tool("redmine-get-issue", issue_id=issue_id)
print("Status:", json.loads(updated_issue)["issue"]["status"]["name"])
```

## Best Practices

### Error Handling
```python
async def safe_issue_creation(project_id, subject, description=""):
    """Create issue with proper error handling"""
    try:
        result = await mcp.call_tool(
            "redmine-create-issue",
            project_id=project_id,
            subject=subject,
            description=description
        )
        
        if "Error" in result:
            print(f"Failed to create issue: {result}")
            return None
        
        issue_data = json.loads(result)
        return issue_data["issue"]["id"]
        
    except Exception as e:
        print(f"Exception during issue creation: {e}")
        return None
```

### Bulk Operations
```python
async def process_issues_in_batches(issue_ids, batch_size=10):
    """Process large numbers of issues efficiently"""
    for i in range(0, len(issue_ids), batch_size):
        batch = issue_ids[i:i + batch_size]
        
        # Process batch
        for issue_id in batch:
            result = await mcp.call_tool("redmine-get-issue", issue_id=issue_id)
            # Process result...
        
        # Brief pause between batches
        await asyncio.sleep(0.1)
```

### Configuration Management
```python
class RedmineConfig:
    """Centralized configuration for automation scripts"""
    
    def __init__(self):
        self.projects = {
            "web": "web-application",
            "mobile": "mobile-app",
            "api": "backend-api"
        }
        
        self.statuses = {
            "new": 1,
            "in_progress": 2,
            "resolved": 3,
            "closed": 5
        }
        
        self.priorities = {
            "low": 1,
            "normal": 2,
            "high": 3,
            "urgent": 4
        }
    
    def get_project_id(self, alias):
        return self.projects.get(alias, alias)
```