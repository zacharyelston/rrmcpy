# DevOps Workflow for RRMCPY Development

## Overview
This document defines the standard workflow for implementing improvements and fixing issues in the rrmcpy project. All development follows a branch-per-issue pattern with clear traceability between Redmine issues and code changes.

## Core Workflow

### 1. Issue Selection and Assignment
- Check Redmine for assigned issues or select from backlog
- Priority order: High → Normal → Low  
- Focus on one issue at a time
- Update issue status to "In Progress" when starting

### 2. Branch Creation
Always create branches from main with issue ID in the name:

```bash
# Update main first
git checkout main
git pull origin main

# Create branch with pattern: {type}/{issueID}-{brief-description}
git checkout -b bugfix/649-parameter-validation
git checkout -b feature/682-parameter-audit
git checkout -b docs/683-sync-documentation
git checkout -b refactor/680-modular-architecture
```

### 3. Development Process

#### Research Phase
1. Review issue description and acceptance criteria
2. Check related issues for context
3. Document findings in issue comments
4. Create/update wiki pages for investigations

#### Implementation
Make small, atomic commits with issue references:

```bash
# Stage specific changes
git add -p src/tools/issue_tools.py

# Commit with issue reference
git commit -m "bugfix: add parent_issue_id parameter support (#649)

This allows proper parent-child relationships to be created
through the MCP interface.

Refs #649"
```

#### Testing
```bash
# Run unit tests after changes
python test_mcp_server.py

# Test specific functionality
python -m pytest tests/test_issue_tools.py::test_create_issue

# Manual testing with MCP
python main.py
```

### 4. Documentation Updates
Update docs in the same branch:

```bash
git add docs/architecture.md
git commit -m "docs: add wiki and template tools to architecture (#683)"
```

### 5. Push and Review
```bash
# Push branch to origin
git push -u origin bugfix/649-parameter-validation

# Create merge request
# Link to Redmine issue in MR description
```

### 6. Redmine Updates
- Add commit SHA references to issue notes
- Update issue status to "Resolved" 
- Document testing results
- Link to merge request

### 7. Post-Merge Cleanup
```bash
# Update local main
git checkout main
git pull origin main

# Delete local branch
git branch -d bugfix/649-parameter-validation

# Update issue status to "Closed" after verification
```

## Branch Naming Conventions

| Type | Prefix | Example | Use Case |
|------|--------|---------|----------|
| Bug Fix | `bugfix/` | `bugfix/649-parameter-validation` | Fixing reported bugs |
| Feature | `feature/` | `feature/660-remote-mcp-server` | New functionality |
| Documentation | `docs/` | `docs/683-sync-documentation` | Documentation updates |
| Refactor | `refactor/` | `refactor/680-modular-architecture` | Code improvements |
| Hotfix | `hotfix/` | `hotfix/681-critical-param-fix` | Urgent production fixes |

## Commit Message Format

```
{type}: {brief description} (#{issueID})

[Optional extended description explaining why and how]

[Footer with one of:]
Fixes #issueID      - Closes the issue when merged
Refs #issueID       - References without closing  
Part of #issueID    - For partial implementations
See also #issueID   - For related changes
```

### Examples:
```
bugfix: add parent_issue_id to create_issue parameters (#649)

This parameter was missing from the MCP tool definition,
preventing proper subtask creation through the API.

Fixes #649
```

```
docs: update architecture to include all 29 tools (#683)

- Add wiki management tools section
- Add template system tools section  
- Update tool count from 17 to 29
- Add missing project management tools

Fixes #683
```

## Testing Requirements

### Before Committing
- [ ] Unit tests pass
- [ ] Manual testing confirms fix
- [ ] No regression in existing functionality
- [ ] Code follows project style
- [ ] No debug code left (check for TODO, FIXME, print statements)

### Before Pushing  
- [ ] All commits reference issue numbers
- [ ] Branch is rebased on latest main
- [ ] Documentation updated if needed
- [ ] Tests are green

## Current Priority Issues

### High Priority - Parameter Validation Bugs
1. **#649** - Template parameters and parent_issue_id
   ```bash
   git checkout -b bugfix/649-parameter-validation
   # Fix: Add missing parameters to tool definitions
   ```

2. **#681** - done_ratio parameter
   ```bash
   git checkout -b bugfix/681-done-ratio-parameter
   # Fix: Add done_ratio to update_issue
   ```

3. **#682** - Complete parameter audit
   ```bash
   git checkout -b feature/682-parameter-audit
   # Create audit script and fix all missing parameters
   ```

### Medium Priority - Documentation
4. **#683** - Sync documentation with code
   ```bash
   git checkout -b docs/683-sync-documentation
   # Update docs to show all 29 tools
   ```

### Future Work
5. **#660** - Remote MCP server support
   ```bash
   git checkout -b feature/660-remote-mcp-server
   # Implement SSE/HTTP transport
   ```

## Helper Scripts

Create these in the `scripts/` directory:

### scripts/start-issue.sh
```bash
#!/bin/bash
# Usage: ./scripts/start-issue.sh 649 bugfix

ISSUE_ID=$1
TYPE=${2:-bugfix}
DESCRIPTION=$3

if [ -z "$ISSUE_ID" ]; then
    echo "Usage: $0 <issue-id> [type] [description]"
    exit 1
fi

git checkout main
git pull origin main
git checkout -b "$TYPE/$ISSUE_ID-${DESCRIPTION:-work}"

echo "Created branch: $TYPE/$ISSUE_ID-${DESCRIPTION:-work}"
echo "Remember to update issue #$ISSUE_ID status to 'In Progress'"
```

### scripts/pre-push-check.sh
```bash
#!/bin/bash
# Run checks before pushing

echo "Running pre-push checks..."

# Check for debug code
if grep -r "TODO\|FIXME\|XXX\|print(" src/; then
    echo "❌ Found debug code - please remove"
    exit 1
fi

# Run tests
if ! python test_mcp_server.py; then
    echo "❌ Tests failed"
    exit 1
fi

# Check commit messages for issue refs
if ! git log origin/main..HEAD --oneline | grep -E '#[0-9]+'; then
    echo "⚠️  Warning: No issue references found in commits"
fi

echo "✅ All checks passed!"
```

### scripts/test-tool.sh
```bash
#!/bin/bash
# Usage: ./scripts/test-tool.sh redmine-create-issue

TOOL=$1
python -c "
from src.tools.registry import get_tool
tool = get_tool('$TOOL')
if tool:
    print(f'Testing {tool.name}...')
    # Add specific test logic
else:
    print(f'Tool {TOOL} not found')
"
```

## Quick Commands Reference

```bash
# See current issue status
git branch --show-current

# Check what's changed
git status
git diff --staged

# Amend last commit (before pushing)
git commit --amend

# Interactive rebase to clean up commits
git rebase -i origin/main

# Search for code patterns
grep -r "parent_issue_id" src/
ag "done_ratio" --python

# Run specific test file
python -m pytest tests/test_issue_tools.py -v

# Check which tools are available
python -c "from src.tools import registry; print(registry.list_tools())"
```

## Issue Status Flow in Redmine
```
New → In Progress → Resolved → Closed
         ↓             ↓
      On Hold      Reopened
```

Update status as you progress through the workflow.

## Best Practices

1. **One Issue at a Time** - Focus on completing one issue before starting another
2. **Atomic Commits** - Each commit should be a logical unit of change
3. **Clear Messages** - Commit messages should explain what and why
4. **Test Early** - Run tests after each significant change
5. **Document Changes** - Update docs in the same PR as code changes
6. **Communicate** - Update Redmine issues with progress and blockers

## Emergency Hotfix Process

For critical production issues:

```bash
# Create hotfix directly from main
git checkout main
git pull origin main
git checkout -b hotfix/XXX-critical-description

# Make minimal fix
# Test thoroughly  
# Push immediately

# Create Redmine issue if none exists
# Mark as Critical priority
```

## Conclusion

Following this workflow ensures:
- Clear traceability between issues and code
- Consistent branch and commit practices
- Proper testing before merge
- Updated documentation
- Clean project history

For questions or suggestions, create an issue in Redmine or discuss in team meetings.
