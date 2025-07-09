#!/bin/bash
# Pre-push checks to ensure code quality
# Usage: ./scripts/pre-push-check.sh

echo "🔍 Running pre-push checks..."
echo ""

FAILED=0

# Check for debug code
echo "Checking for debug code..."
if grep -r "TODO\|FIXME\|XXX" src/ 2>/dev/null | grep -v ".pyc"; then
    echo "❌ Found debug markers - consider removing or documenting in issues"
    FAILED=1
else
    echo "✅ No debug markers found"
fi

if grep -r "print(" src/ 2>/dev/null | grep -v ".pyc" | grep -v "# noqa"; then
    echo "❌ Found print statements - please use logging instead"
    FAILED=1
else
    echo "✅ No print statements found"
fi

echo ""

# Check for issue references in commits
echo "Checking commit messages..."
COMMITS_WITHOUT_REFS=$(git log origin/main..HEAD --oneline 2>/dev/null | grep -v -E '#[0-9]+' | wc -l)
if [ "$COMMITS_WITHOUT_REFS" -gt 0 ]; then
    echo "⚠️  Warning: $COMMITS_WITHOUT_REFS commits without issue references"
    git log origin/main..HEAD --oneline | grep -v -E '#[0-9]+'
else
    echo "✅ All commits reference issues"
fi

echo ""

# Run tests if test file exists
if [ -f "test_mcp_server.py" ]; then
    echo "Running tests..."
    if python test_mcp_server.py > /dev/null 2>&1; then
        echo "✅ Tests passed"
    else
        echo "❌ Tests failed - run 'python test_mcp_server.py' for details"
        FAILED=1
    fi
else
    echo "⚠️  No test_mcp_server.py found"
fi

echo ""

# Check branch naming
CURRENT_BRANCH=$(git branch --show-current)
if [[ ! "$CURRENT_BRANCH" =~ ^(bugfix|feature|docs|refactor|hotfix)/[0-9]+ ]]; then
    echo "⚠️  Branch name doesn't follow convention: $CURRENT_BRANCH"
    echo "   Expected: {type}/{issueID}-{description}"
fi

echo ""

# Summary
if [ $FAILED -eq 0 ]; then
    echo "✅ All checks passed! Ready to push."
else
    echo "❌ Some checks failed. Fix issues before pushing."
    exit 1
fi
