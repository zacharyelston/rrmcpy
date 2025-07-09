#!/bin/bash
# Start work on a Redmine issue by creating a properly named branch
# Usage: ./scripts/start-issue.sh <issue-id> [type] [description]
# Example: ./scripts/start-issue.sh 649 bugfix parameter-validation

ISSUE_ID=$1
TYPE=${2:-bugfix}
DESCRIPTION=$3

if [ -z "$ISSUE_ID" ]; then
    echo "Usage: $0 <issue-id> [type] [description]"
    echo "Types: bugfix, feature, docs, refactor, hotfix"
    echo "Example: $0 649 bugfix parameter-validation"
    exit 1
fi

# Ensure we're in the project root
if [ ! -f "main.py" ]; then
    echo "Error: Not in project root directory"
    exit 1
fi

# Update main and create branch
echo "Updating main branch..."
git checkout main
git pull origin main

# Create branch name
BRANCH_NAME="$TYPE/$ISSUE_ID"
if [ -n "$DESCRIPTION" ]; then
    BRANCH_NAME="$BRANCH_NAME-$DESCRIPTION"
else
    BRANCH_NAME="$BRANCH_NAME-work"
fi

# Create and checkout branch
git checkout -b "$BRANCH_NAME"

echo ""
echo "✅ Created branch: $BRANCH_NAME"
echo ""
echo "Next steps:"
echo "1. Update issue #$ISSUE_ID status to 'In Progress' in Redmine"
echo "2. Make your changes"
echo "3. Commit with: git commit -m \"$TYPE: description (#$ISSUE_ID)\""
echo "4. Run tests: python test_mcp_server.py"
echo "5. Push with: git push -u origin $BRANCH_NAME"
